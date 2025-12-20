import numpy as np
np.random.seed(42)
import tensorflow as tf
tf.random.set_seed(42)

from keras import regularizers
from keras import backend as K
from keras.models import Model, load_model
from keras.layers import Input, Dense, Dropout, BatchNormalization
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

import argparse
import numpy as np
import sys
from scipy.sparse import vstack, csc_matrix
from utils import dataLoading, aucPerformance, writeResults, get_data_from_svmlight_file
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import time

MAX_INT = np.iinfo(np.int32).max
data_format = 0

def dev_network_deep_improved(input_shape):
    '''
    改进的深层网络架构，添加批归一化和dropout
    '''
    x_input = Input(shape=input_shape)
    
    # 第一层
    x = Dense(256, activation='relu', kernel_regularizer=regularizers.l2(0.001))(x_input)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)
    
    # 第二层
    x = Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.001))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    
    # 第三层
    x = Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.001))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.1)(x)
    
    # 输出层
    output = Dense(1, activation='linear', name='score')(x)
    
    return Model(x_input, output)

def dev_network_s_improved(input_shape):
    '''
    改进的浅层网络
    '''
    x_input = Input(shape=input_shape)
    x = Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.001))(x_input)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    x = Dense(32, activation='relu', kernel_regularizer=regularizers.l2(0.001))(x)
    output = Dense(1, activation='linear', name='score')(x)
    return Model(x_input, output)

def focal_deviation_loss(y_true, y_pred, alpha=0.99, gamma=2.0):
    '''
    结合Focal Loss和Deviation Loss，专门针对极度不平衡数据
    alpha: 类别权重，接近1表示对少数类(欺诈)更关注
    gamma: 聚焦参数，减少易分类样本的权重
    '''
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    
    # Z-score标准化
    mean = tf.reduce_mean(y_pred)
    std = tf.math.reduce_std(y_pred) + 1e-10
    dev = (y_pred - mean) / std
    
    # 计算基础损失
    # 正常样本：希望dev接近负值（低于均值）
    # 欺诈样本：希望dev接近正值（高于均值）
    inlier_loss = tf.square(tf.maximum(dev, 0.0))  # 正常样本的dev应该是负的
    outlier_loss = tf.square(tf.maximum(-dev, 0.0))  # 欺诈样本的dev应该是正的
    
    # Focal weight: 对于难分类样本给予更多关注
    inlier_prob = tf.nn.sigmoid(-dev)  # 正常样本的置信度
    outlier_prob = tf.nn.sigmoid(dev)   # 欺诈样本的置信度
    
    focal_weight_inlier = tf.pow(1 - inlier_prob, gamma)
    focal_weight_outlier = tf.pow(1 - outlier_prob, gamma)
    
    # 组合损失，大幅提高欺诈样本权重
    # alpha权重 + focal权重 + 额外的类别权重
    weighted_loss = (1 - alpha) * focal_weight_inlier * inlier_loss + \
                    alpha * focal_weight_outlier * outlier_loss * 200.0  # 从100提高到200
    
    return K.mean(weighted_loss)

def deviation_network(input_shape, network_depth):
    '''
    构建改进的deviation network
    '''
    if network_depth == 4:
        model = dev_network_deep_improved(input_shape)
    elif network_depth == 2:
        model = dev_network_s_improved(input_shape)
    else:
        sys.exit("请使用network_depth=2或4")
    
    # 使用Adam优化器，学习率降低以更稳定训练
    optimizer = Adam(learning_rate=0.0005, clipnorm=1.0)
    model.compile(loss=focal_deviation_loss, optimizer=optimizer)
    return model

def batch_generator_sup_extreme_imbalanced(x, outlier_indices, inlier_indices, batch_size, nb_batch, rng):
    """
    极度不平衡数据的batch生成器
    大幅提高欺诈样本比例到50%
    """
    rng = np.random.RandomState(rng.randint(MAX_INT, size=1))
    counter = 0
    
    # 提高到50%异常样本
    n_outliers_per_batch = int(batch_size * 0.5)
    n_inliers_per_batch = batch_size - n_outliers_per_batch
    
    while True:
        if data_format == 0:
            ref, training_labels = input_batch_generation_imbalanced(
                x, outlier_indices, inlier_indices,
                n_inliers_per_batch, n_outliers_per_batch, rng
            )
        else:
            ref, training_labels = input_batch_generation_imbalanced_sparse(
                x, outlier_indices, inlier_indices,
                n_inliers_per_batch, n_outliers_per_batch, rng
            )
        counter += 1
        yield (ref, training_labels)
        if counter > nb_batch:
            counter = 0

def input_batch_generation_imbalanced(x_train, outlier_indices, inlier_indices,
                                      n_inliers, n_outliers, rng):
    '''
    改进的batch生成，使用SMOTE类似的过采样
    '''
    dim = x_train.shape[1]
    batch_size = n_inliers + n_outliers
    ref = np.empty((batch_size, dim))
    training_labels = np.zeros(batch_size)
    
    # 正常样本
    inlier_sample_ids = rng.choice(len(inlier_indices), n_inliers, replace=True)
    ref[:n_inliers] = x_train[inlier_indices[inlier_sample_ids]]
    
    # 欺诈样本：使用过采样 + 轻微扰动来增加多样性
    outlier_sample_ids = rng.choice(len(outlier_indices), n_outliers, replace=True)
    outlier_samples = x_train[outlier_indices[outlier_sample_ids]]
    
    # 添加轻微的高斯噪声增强
    noise_level = 0.05
    noise = rng.normal(0, noise_level, outlier_samples.shape)
    outlier_samples_augmented = outlier_samples + noise * np.std(outlier_samples, axis=0)
    
    ref[n_inliers:] = outlier_samples_augmented
    training_labels[n_inliers:] = 1
    
    # 打乱
    shuffle_idx = rng.permutation(batch_size)
    ref = ref[shuffle_idx]
    training_labels = training_labels[shuffle_idx]
    
    return ref, training_labels

def input_batch_generation_imbalanced_sparse(x_train, outlier_indices, inlier_indices,
                                             n_inliers, n_outliers, rng):
    '''
    稀疏数据版本
    '''
    batch_size = n_inliers + n_outliers
    ref_indices = np.empty(batch_size, dtype=int)
    training_labels = np.zeros(batch_size)
    
    inlier_sample_ids = rng.choice(len(inlier_indices), n_inliers, replace=True)
    ref_indices[:n_inliers] = inlier_indices[inlier_sample_ids]
    
    outlier_sample_ids = rng.choice(len(outlier_indices), n_outliers, replace=True)
    ref_indices[n_inliers:] = outlier_indices[outlier_sample_ids]
    training_labels[n_inliers:] = 1
    
    shuffle_idx = rng.permutation(batch_size)
    ref_indices = ref_indices[shuffle_idx]
    training_labels = training_labels[shuffle_idx]
    
    ref = x_train[ref_indices, :].toarray()
    return ref, training_labels

def load_model_weight_predict(model_name, input_shape, network_depth, x_test):
    '''
    加载模型权重并预测
    '''
    model = deviation_network(input_shape, network_depth)
    model.load_weights(model_name)
    scoring_network = Model(inputs=model.input, outputs=model.output)
    
    if data_format == 0:
        scores = scoring_network.predict(x_test, batch_size=1024, verbose=1)
    else:
        data_size = x_test.shape[0]
        scores = np.zeros([data_size, 1])
        count = 512
        i = 0
        while i < data_size:
            subset = x_test[i:count].toarray()
            scores[i:count] = scoring_network.predict(subset)
            if i % 1024 == 0:
                print(f"预测进度: {i}/{data_size}")
            i = count
            count += 512
            if count > data_size:
                count = data_size
    return scores

def inject_noise(seed, n_out, random_seed):
    '''
    注入噪声数据
    '''
    rng = np.random.RandomState(random_seed)
    n_sample, dim = seed.shape
    swap_ratio = 0.05
    n_swap_feat = int(swap_ratio * dim)
    noise = np.empty((n_out, dim))
    for i in np.arange(n_out):
        outlier_idx = rng.choice(n_sample, 2, replace=False)
        o1 = seed[outlier_idx[0]]
        o2 = seed[outlier_idx[1]]
        swap_feats = rng.choice(dim, n_swap_feat, replace=False)
        noise[i] = o1.copy()
        noise[i, swap_feats] = o2[swap_feats]
    return noise

def inject_noise_sparse(seed, n_out, random_seed):
    '''
    稀疏数据注入噪声
    '''
    rng = np.random.RandomState(random_seed)
    n_sample, dim = seed.shape
    swap_ratio = 0.05
    n_swap_feat = int(swap_ratio * dim)
    seed = seed.tocsc()
    noise = csc_matrix((n_out, dim))
    for i in np.arange(n_out):
        outlier_idx = rng.choice(n_sample, 2, replace=False)
        o1 = seed[outlier_idx[0]]
        o2 = seed[outlier_idx[1]]
        swap_feats = rng.choice(dim, n_swap_feat, replace=False)
        noise[i] = o1.copy()
        noise[i, swap_feats] = o2[0, swap_feats]
    return noise.tocsr()

def run_devnet(args):
    names = args.data_set.split(',')
    network_depth = int(args.network_depth)
    random_seed = args.ramdn_seed
    
    for nm in names:
        runs = args.runs
        rauc = np.zeros(runs)
        ap = np.zeros(runs)
        filename = nm.strip()
        global data_format
        data_format = int(args.data_format)
        
        # 加载数据
        if data_format == 0:
            x, labels = dataLoading(args.input_path + filename + ".csv")
        else:
            x, labels = get_data_from_svmlight_file(args.input_path + filename + ".svm")
            x = x.tocsr()
        
        # **关键改进：数据标准化**
        print("正在标准化特征...")
        if data_format == 0:
            scaler = StandardScaler()
            x = scaler.fit_transform(x)
        
        outlier_indices = np.where(labels == 1)[0]
        outliers = x[outlier_indices]
        n_outliers_org = outliers.shape[0]
        
        print(f"\n{'='*60}")
        print(f"数据集: {filename}")
        print(f"总样本数: {len(labels)}")
        print(f"欺诈样本数: {n_outliers_org}")
        print(f"正常样本数: {len(labels) - n_outliers_org}")
        print(f"不平衡比例: 1:{(len(labels) - n_outliers_org) / n_outliers_org:.2f}")
        print(f"{'='*60}\n")
        
        train_time = 0
        test_time = 0
        
        for i in np.arange(runs):
            x_train, x_test, y_train, y_test = train_test_split(
                x, labels, test_size=0.2, random_state=42+i, stratify=labels
            )
            
            print(f"\n{'='*60}")
            print(f"{filename}: 第 {i+1}/{runs} 轮")
            print(f"{'='*60}")
            
            outlier_indices = np.where(y_train == 1)[0]
            inlier_indices = np.where(y_train == 0)[0]
            n_outliers = len(outlier_indices)
            
            print(f"训练集大小: {x_train.shape[0]}")
            print(f"  - 欺诈样本: {n_outliers} ({n_outliers/len(y_train)*100:.2f}%)")
            print(f"  - 正常样本: {len(inlier_indices)} ({len(inlier_indices)/len(y_train)*100:.2f}%)")
            
            # 减少或取消噪声注入
            n_noise = 0  # 暂时取消噪声注入
            
            rng = np.random.RandomState(random_seed + i)
            
            if n_noise > 0:
                if data_format == 0:
                    noises = inject_noise(outliers, n_noise, random_seed + i)
                    x_train = np.append(x_train, noises, axis=0)
                else:
                    noises = inject_noise_sparse(outliers, n_noise, random_seed + i)
                    x_train = vstack([x_train, noises])
                y_train = np.append(y_train, np.zeros((n_noise,)))
            
            outlier_indices = np.where(y_train == 1)[0]
            inlier_indices = np.where(y_train == 0)[0]
            
            print(f"最终训练集: {len(y_train)} 样本")
            
            # 训练模型
            start_time = time.time()
            input_shape = x_train.shape[1:]
            epochs = args.epochs
            batch_size = args.batch_size
            nb_batch = args.nb_batch
            
            model = deviation_network(input_shape, network_depth)
            print(model.summary())
            
            model_name = f"./model/devnet_{filename}_{network_depth}d_optimized_run{i}.h5"
            
            # 改进的callbacks
            callbacks = [
                ModelCheckpoint(model_name, monitor='loss', save_best_only=True, 
                              save_weights_only=True, verbose=1),
                ReduceLROnPlateau(monitor='loss', factor=0.5, patience=10, 
                                 min_lr=1e-6, verbose=1),
                EarlyStopping(monitor='loss', patience=20, restore_best_weights=True, verbose=1)
            ]
            
            history = model.fit(
                batch_generator_sup_extreme_imbalanced(
                    x_train, outlier_indices, inlier_indices,
                    batch_size, nb_batch, rng
                ),
                steps_per_epoch=nb_batch,
                epochs=epochs,
                callbacks=callbacks,
                verbose=1
            )
            
            train_time += time.time() - start_time
            
            # 预测
            start_time = time.time()
            scores = load_model_weight_predict(model_name, input_shape, network_depth, x_test)
            test_time += time.time() - start_time
            
            rauc[i], ap[i] = aucPerformance(scores, y_test)
            
            print(f"\n第 {i+1} 轮结果:")
            print(f"  AUC-ROC: {rauc[i]:.4f}")
            print(f"  AUC-PR:  {ap[i]:.4f}")
            print(f"  异常分数范围: [{scores.min():.4f}, {scores.max():.4f}]")
            print(f"  异常分数标准差: {scores.std():.4f}")
        
        mean_auc = np.mean(rauc)
        std_auc = np.std(rauc)
        mean_aucpr = np.mean(ap)
        std_aucpr = np.std(ap)
        train_time = train_time / runs
        test_time = test_time / runs
        
        print(f"\n{'='*60}")
        print(f"最终结果汇总")
        print(f"{'='*60}")
        print(f"平均 AUC-ROC: {mean_auc:.4f} ± {std_auc:.4f}")
        print(f"平均 AUC-PR:  {mean_aucpr:.4f} ± {std_aucpr:.4f}")
        print(f"平均训练时间: {train_time:.2f} 秒")
        print(f"平均测试时间: {test_time:.2f} 秒")
        print(f"{'='*60}\n")
        
        writeResults(
            filename + '_' + str(network_depth) + '_optimized',
            x.shape[0], x.shape[1], x_train.shape[0],
            n_outliers_org, len(outlier_indices),
            network_depth, mean_auc, mean_aucpr,
            std_auc, std_aucpr, train_time, test_time,
            path=args.output
        )

parser = argparse.ArgumentParser()
parser.add_argument("--network_depth", choices=['2', '4'], default='4', 
                    help="网络深度 (推荐使用4)")
parser.add_argument("--batch_size", type=int, default=256, 
                    help="batch大小 (降低到256以增加更新频率)")
parser.add_argument("--nb_batch", type=int, default=50, 
                    help="每轮的batch数量 (增加到50)")
parser.add_argument("--epochs", type=int, default=200, 
                    help="训练轮数 (增加到200)")
parser.add_argument("--runs", type=int, default=3, 
                    help="重复实验次数 (先用3次快速测试)")
parser.add_argument("--known_outliers", type=int, default=9768, 
                    help="已知异常数量")
parser.add_argument("--cont_rate", type=float, default=0.0, 
                    help="污染率 (设为0取消噪声注入)")
parser.add_argument("--input_path", type=str, default='./dataset/', 
                    help="数据集路径")
parser.add_argument("--data_set", type=str, default='phase1_foreground_normalised', 
                    help="数据集名称")
parser.add_argument("--data_format", choices=['0', '1'], default='0', 
                    help="数据格式")
parser.add_argument("--output", type=str, default='./results/devnet_phase1_optimized.csv', 
                    help="输出文件路径")
parser.add_argument("--ramdn_seed", type=int, default=42, 
                    help="随机种子")
args = parser.parse_args()
run_devnet(args)