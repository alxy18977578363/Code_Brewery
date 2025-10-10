import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import warnings
import torch
import random
from tensorflow.keras.models import Model
from tensorflow.keras.layers import TimeDistributed, Dot
from tensorflow.keras.layers import Input, Dense, LSTM, Conv1D, Dropout, Multiply, Permute, RepeatVector, Activation, \
    Flatten, Lambda, Concatenate
from tensorflow.keras import backend as K
from tensorflow.keras.losses import Huber
from tensorflow.keras.layers import Reshape, Conv2D, MaxPooling2D
import holidays
from sklearn.preprocessing import StandardScaler

# 随机种子
warnings.filterwarnings('ignore')
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.manual_seed(99)
np.random.seed(99)
random.seed(99)
print("随机种子")


# 评估指标R2
def r2_keras(y_true, y_pred):
    SS_res = K.sum(K.square(y_true - y_pred))
    SS_tot = K.sum(K.square(y_true - K.mean(y_true)))
    return (1 - SS_res / (SS_tot + K.epsilon()))


# 数据预处理

def process_shared_bike_data(raw_df, n_grids=10,
                             q_low=0.01, q_high=0.99,
                             min_span=0.001,
                             coord_precision=6):  # 精度参数

    df = raw_df.copy()

    #  时间处理增强
    df['start_time'] = pd.to_datetime(
        df['start_time'],
        format='%Y-%m-%d %H:%M:%S',
        errors='coerce'
    )
    df['end_time'] = pd.to_datetime(
        df['end_time'],
        format='%Y-%m-%d %H:%M:%S',
        errors='coerce'
    )

    # 异常值过滤
    time_mask = df[['start_time', 'end_time']].notna().all(axis=1)
    if time_mask.sum() == 0:
        invalid_samples = raw_df.loc[~time_mask].sample(min(5, len(raw_df)))
        print("无效时间样本示例：")
        print(invalid_samples[['start_time', 'end_time']])
        raise ValueError("时间解析失败，请检查上述样本的时间格式")
    df = df[time_mask].copy()
    if df.empty:
        raise ValueError("时间解析失败或所有时间数据无效，请检查原始数据格式")

    # 坐标精度处理（新增关键模块）
    #def reduce_precision(series, precision):

       # return series.round(precision)

    # df['start_location_x'] = reduce_precision(df['start_location_x'], coord_precision)
    # df['start_location_y'] = reduce_precision(df['start_location_y'], coord_precision)
    # df['end_location_x'] = reduce_precision(df['end_location_x'], coord_precision)
    # df['end_location_y'] = reduce_precision(df['end_location_y'], coord_precision)

    # 空间分桶优化
    def get_safe_bins(series, n_bins, min_span=0.005):

        if series.nunique() <= n_bins:
            return np.sort(series.unique())

        # K-means分箱
        data = series.dropna().values.reshape(-1, 1)
        kmeans = KMeans(n_clusters=n_bins, n_init=10, random_state=42)
        kmeans.fit(data)
        centers = np.sort(kmeans.cluster_centers_.flatten())

        # 生成严格递增的分箱边界
        bins = []
        current = centers[0] - min_span  # 左边界
        for center in centers:
            bins.append(current)
            current = center + min_span  # 右边界
        bins.append(current)
        bins = np.clip(bins, series.min() - 1e-5, series.max() + 1e-5)
        return np.unique(bins)

    # 生成分箱边界

    start_lat_bins = get_safe_bins(df['start_location_x'], n_grids, min_span)
    start_lon_bins = get_safe_bins(df['start_location_y'], n_grids, min_span)
    end_lat_bins = get_safe_bins(df['end_location_x'], n_grids, min_span)
    end_lon_bins = get_safe_bins(df['end_location_y'], n_grids, min_span)

    # 执行分箱操作
    def safe_binning(data, col, bins):

        # 生成严格递增的分箱边界
        bins = np.sort(np.unique(bins))
        # 强制严格递增处理
        for i in range(1, len(bins)):
            if bins[i] <= bins[i - 1]:
                bins[i] = bins[i - 1] + 1e-8
        # 扩展边界以包含所有可能值
        extended_bins = np.concatenate([[-np.inf], bins, [np.inf]])
        return pd.cut(data[col], extended_bins, labels=False, include_lowest=True)

    df['start_lat_bin'] = safe_binning(df, 'start_location_x', start_lat_bins)
    df['start_lon_bin'] = safe_binning(df, 'start_location_y', start_lon_bins)
    df['end_lat_bin'] = safe_binning(df, 'end_location_x', end_lat_bins)
    df['end_lon_bin'] = safe_binning(df, 'end_location_y', end_lon_bins)

    # 双流聚合增强
    def enhanced_aggregation(df, time_col, lat_bin, lon_bin, prefix, n_grids):

        valid_mask = (df[lat_bin] >= 0) & (df[lon_bin] >= 0)
        grouped = df[valid_mask].groupby([
            pd.Grouper(key=time_col, freq='h'),
            lat_bin,
            lon_bin
        ]).size()

        # 生成完整时间范围
        start_time = df[time_col].min()
        end_time = df[time_col].max()
        full_time = pd.date_range(
            start=start_time.floor('h'),
            end=end_time.ceil('h'),
            freq='h'
        )

        # 生成所有可能的分箱组合
        all_lat = np.arange(n_grids)
        all_lon = np.arange(n_grids)

        # 创建完整的MultiIndex
        full_index = pd.MultiIndex.from_product(
            [full_time, all_lat, all_lon],
            names=[time_col, lat_bin, lon_bin]
        )

        # 重新索引并填充缺失值
        grouped = grouped.reindex(full_index, fill_value=0)

        # 转换为宽格式（时间 x 分箱组合）
        grouped = grouped.unstack([lat_bin, lon_bin])

        # 生成列名
        grouped.columns = [f"{prefix}_{lat}_{lon}" for lat, lon in grouped.columns]

        return grouped

    # 执行聚合

    start_demand = enhanced_aggregation(df, 'start_time', 'start_lat_bin', 'start_lon_bin', 'depart', n_grids)
    end_supply = enhanced_aggregation(df, 'end_time', 'end_lat_bin', 'end_lon_bin', 'arrive', n_grids)

    # 时间特征
    time_features = pd.DataFrame({
        'hour': start_demand.index.hour,
        'weekday': start_demand.index.weekday,
        'is_weekend': (start_demand.index.weekday >= 5).astype(int),
        'time_sin': np.sin(2 * np.pi * start_demand.index.hour / 24),
        'time_cos': np.cos(2 * np.pi * start_demand.index.hour / 24),
        'is_holiday': start_demand.index.to_series().apply(
            lambda x: x in holidays.CN()).astype(int)
    }, index=start_demand.index)

    # 校验
    assert np.all(np.diff(start_lat_bins) > 0), "纬度分箱非严格递增"
    assert np.all(np.diff(start_lon_bins) > 0), "经度分箱非严格递增"

    assert len(start_lat_bins) >= 2, "纬度分箱数不足"
    assert len(start_lon_bins) >= 2, "经度分箱数不足"
    assert start_lat_bins[-1] > start_lat_bins[0], "纬度分箱无效"
    assert start_lon_bins[-1] > start_lon_bins[0], "经度分箱无效"

    return (
        pd.concat([start_demand, end_supply, time_features], axis=1),
        start_lat_bins, start_lon_bins,
        end_lat_bins, end_lon_bins
    )


# 创建双输出序列数据
def create_dual_sequences(data, time_steps, n_grids):
    X, y_depart, y_arrive = [], [], []
    grid_cols = n_grids * n_grids

    for i in range(len(data) - time_steps):
        # 输入包含历史所有特征
        X.append(data.iloc[i:i + time_steps].values)

        # 预测下一个时刻的出发和到达需求
        target_idx = i + time_steps
        y_depart.append(data.iloc[target_idx, :grid_cols].values)  # 前N²列为出发需求
        y_arrive.append(data.iloc[target_idx, grid_cols:2 * grid_cols].values)  # 中间N²列为到达供给

    return np.array(X), [np.array(y_depart), np.array(y_arrive)]


# 双流时空预测模型


def build_dual_stream_model(time_steps, input_dims, n_grids):
    inputs = Input(shape=(time_steps, input_dims))

    # 特征分解
    depart_features = Lambda(lambda x: x[..., :n_grids ** 2])(inputs)
    arrive_features = Lambda(lambda x: x[..., n_grids ** 2:2 * n_grids ** 2])(inputs)
    time_features = Lambda(lambda x: x[..., -6:])(inputs)  # 时间特征

    # 空间特征提取（CNN）
    # 处理出发需求的空间特征
    depart_reshaped = Reshape((time_steps, n_grids, n_grids, 1))(depart_features)
    depart_cnn = TimeDistributed(
        Conv2D(16, (3, 3), activation='relu', padding='same')
    )(depart_reshaped)
    depart_cnn = TimeDistributed(MaxPooling2D(2))(depart_cnn)
    depart_cnn = TimeDistributed(
        Conv2D(32, (3, 3), activation='relu', padding='same')
    )(depart_cnn)
    depart_cnn = TimeDistributed(MaxPooling2D(2))(depart_cnn)
    depart_cnn = TimeDistributed(Flatten())(depart_cnn)

    # 处理到达供给的空间特征
    arrive_reshaped = Reshape((time_steps, n_grids, n_grids, 1))(arrive_features)
    arrive_cnn = TimeDistributed(
        Conv2D(16, (3, 3), activation='relu', padding='same')
    )(arrive_reshaped)
    arrive_cnn = TimeDistributed(MaxPooling2D(2))(arrive_cnn)
    arrive_cnn = TimeDistributed(
        Conv2D(32, (3, 3), activation='relu', padding='same')
    )(arrive_cnn)
    arrive_cnn = TimeDistributed(MaxPooling2D(2))(arrive_cnn)
    arrive_cnn = TimeDistributed(Flatten())(arrive_cnn)

    #  特征融合
    combined = Concatenate(axis=-1)([depart_cnn, arrive_cnn, time_features])

    #  时间特征提取（LSTM）
    lstm_out = LSTM(128, return_sequences=True)(combined)

    #  注意力机制
    # 时间注意力
    attention = TimeDistributed(Dense(1, activation='tanh'))(lstm_out)
    attention = Flatten()(attention)
    attention = Activation('softmax')(attention)
    attention = RepeatVector(lstm_out.shape[-1])(attention)
    attention = Permute([2, 1])(attention)
    context = Multiply()([lstm_out, attention])
    context = Lambda(lambda x: K.sum(x, axis=1))(context)

    # 双输出层
    depart_output = Dense(n_grids ** 2, activation='linear', name='depart')(context)
    arrive_output = Dense(n_grids ** 2, activation='linear', name='arrive')(context)

    # 模型编译
    model = Model(inputs=inputs, outputs=[depart_output, arrive_output])
    model.compile(
        optimizer='adam',
        loss={'depart': Huber(), 'arrive': Huber()},
        loss_weights=[0.6, 0.4],
        metrics={n: [r2_keras, 'mae'] for n in ['depart', 'arrive']}
    )
    return model


# 可视化函数
def plot_dual_heatmaps(true_depart, true_arrive, pred_depart, pred_arrive,
                       start_lat_bins, start_lon_bins,  # 新增起点分箱参数
                       end_lat_bins, end_lon_bins):  # 新增终点分箱参数

    plt.figure(figsize=(18, 12))

    # - 出发需求热力图 -
    # 真实出发需求（使用起点分箱）
    plt.subplot(2, 2, 1)
    sns.heatmap(
        true_depart.reshape(len(start_lat_bins) - 1, -1).T,  # 纬度分箱数作为行数
        xticklabels=np.round(start_lat_bins, 2),  # 纬度标签
        yticklabels=np.round(start_lon_bins, 2),  # 经度标签
        cmap='Reds'
    )
    plt.title('True Departure Demand (Start Bins)')

    # 预测出发需求
    plt.subplot(2, 2, 2)
    sns.heatmap(
        pred_depart.reshape(len(start_lat_bins) - 1, -1).T,
        xticklabels=np.round(start_lat_bins, 2),
        yticklabels=np.round(start_lon_bins, 2),
        cmap='Reds'
    )
    plt.title('Predicted Departure (Start Bins)')

    # - 到达供给热力图 -
    # 真实到达供给（使用终点分箱）
    plt.subplot(2, 2, 3)
    sns.heatmap(
        true_arrive.reshape(len(end_lat_bins) - 1, -1).T,  # 使用终点分箱
        xticklabels=np.round(end_lat_bins, 2),
        yticklabels=np.round(end_lon_bins, 2),
        cmap='Blues'
    )
    plt.title('True Arrival Supply (End Bins)')

    # 预测到达供给
    plt.subplot(2, 2, 4)
    sns.heatmap(
        pred_arrive.reshape(len(end_lat_bins) - 1, -1).T,
        xticklabels=np.round(end_lat_bins, 2),
        yticklabels=np.round(end_lon_bins, 2),
        cmap='Blues'
    )
    plt.title('Predicted Arrival (End Bins)')

    plt.tight_layout()
    plt.show()


# 主程序
if __name__ == "__main__":
    RAW_DATA_PATH = r"cleaned_mobike_shanghai_sample.csv"  # 原始数据路径
    SAVE_DIR = r"models"  # 结果保存路径

    os.makedirs(SAVE_DIR, exist_ok=True)

    # 参数配置
    N_GRIDS = 10
    TIME_STEPS = 48
    BATCH_SIZE = 32
    EPOCHS = 200
    STRIDE = 3
    LEARNING_RATE = 1e-4

    # 1. 数据加载与预处理
    raw_data = pd.read_csv(RAW_DATA_PATH)
    processed_df, start_lat_bins, start_lon_bins, end_lat_bins, end_lon_bins = process_shared_bike_data(raw_data,
                                                                                                        N_GRIDS)

    # 2. 创建序列数据集
    X, y = create_dual_sequences(processed_df, TIME_STEPS, N_GRIDS)
    scaler = StandardScaler()
    X = scaler.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
    print(f"数据形状: X={X.shape}, y_depart={y[0].shape}, y_arrive={y[1].shape}")


    # 3. 按时间顺序划分数据集
    def temporal_split(data, y_targets, test_size=0.2):
        split_idx = int(len(data) * (1 - test_size))
        X_train, X_test = data[:split_idx], data[split_idx:]
        y_train = [y[:split_idx] for y in y_targets]
        y_test = [y[split_idx:] for y in y_targets]
        return X_train, X_test, y_train, y_test


    X_train, X_test, y_train, y_test = temporal_split(X, y, test_size=0.2)

    # 从训练集中划分验证集

    val_split_idx = int(len(X_train) * 0.8)
    X_val = X_train[val_split_idx:]
    y_val = [
        y_train[0][val_split_idx:],  # depart
        y_train[1][val_split_idx:]  # arrive
    ]
    X_train = X_train[:val_split_idx]
    y_train = [
        y_train[0][:val_split_idx],
        y_train[1][:val_split_idx]
    ]

    # 4. 构建模型
    model = build_dual_stream_model(
        time_steps=TIME_STEPS,
        input_dims=X_train.shape[2],
        n_grids=N_GRIDS
    )

    # 5. 训练配置
#我删掉了callback

    # 6. 模型训练
    history = model.fit(
        X_train, {'depart': y_train[0], 'arrive': y_train[1]},
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_val, {'depart': y_val[0], 'arrive': y_val[1]}),
      
        verbose=1
    )

    # 7. 保存训练过程可视化
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['depart_r2_keras'], label='Train Departure R²')
    plt.plot(history.history['val_depart_r2_keras'], label='Val Departure R²')
    plt.title('Departure Prediction R²')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history['arrive_r2_keras'], label='Train Arrival R²')
    plt.plot(history.history['val_arrive_r2_keras'], label='Val Arrival R²')
    plt.title('Arrival Prediction R²')
    plt.legend()
    plt.savefig(os.path.join(SAVE_DIR, 'training_metrics.png'))  # 保存训练图表
    plt.close()

    # 8. 生成预测并保存结果
    sample_idx = 100
    depart_pred, arrive_pred = model.predict(X_val[sample_idx:sample_idx + 1])

    # 保存预测结果
    np.savez(
        os.path.join(SAVE_DIR, 'prediction_results.npz'),
        depart_pred=depart_pred,
        arrive_pred=arrive_pred,
        start_lat_bins=start_lat_bins,
        start_lon_bins=start_lon_bins,
        end_lat_bins=end_lat_bins,
        end_lon_bins=end_lon_bins
    )

    # 可视化保存
    plot_dual_heatmaps(
        y_val[0][sample_idx], y_val[1][sample_idx],
        depart_pred[0], arrive_pred[0],
        start_lat_bins, start_lon_bins,
        end_lat_bins, end_lon_bins
    )
    plt.savefig(os.path.join(SAVE_DIR, 'prediction_heatmap.png'))  # 保存热力图
    plt.close()

    print("原始数据量:", len(raw_data))
    print("处理后数据量:", len(processed_df))
    print("特征维度:", processed_df.shape[1])
