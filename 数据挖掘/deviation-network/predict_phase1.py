import numpy as np
from keras.models import Model
from devnet import deviation_network, load_model_weight_predict
from sklearn.preprocessing import StandardScaler
import pickle

def predict_phase1():
    """
    使用已训练好的优化模型对phase1测试集进行预测
    关键：必须使用与训练时相同的标准化参数
    """
    print("=" * 60)
    print("开始预测 Phase1 测试集")
    print("=" * 60)
    
    # 步骤 1: 加载完整数据集
    print("\n步骤 1: 加载数据...")
    data = np.load('phase1_gdata.npz')
    x = data['x']
    y = data['y'].flatten()
    train_mask = data['train_mask']
    test_mask = data['test_mask']
    
    print(f"总节点数: {len(y)}")
    print(f"训练样本数: {len(train_mask)}")
    print(f"测试样本数: {len(test_mask)}")
    
    # 步骤 2: 使用与训练时相同的标准化方式
    print("\n步骤 2: 标准化特征...")
    print("⚠️  关键: 必须使用训练集的均值和标准差来标准化测试集")
    
    # 获取训练集中的前景节点（用于计算标准化参数）
    train_foreground_mask = np.isin(np.arange(len(y)), train_mask) & ((y == 0) | (y == 1))
    train_indices = np.where(train_foreground_mask)[0]
    x_train_foreground = x[train_indices]
    
    # 使用训练集拟合StandardScaler
    scaler = StandardScaler()
    scaler.fit(x_train_foreground)
    
    # 标准化全部数据
    x_normalized = scaler.transform(x)
    
    # 获取标准化后的测试数据
    x_test = x_normalized[test_mask]
    
    print(f"测试集形状: {x_test.shape}")
    print(f"特征维度: {x_test.shape[1]}")
    print(f"标准化后特征范围: [{x_test.min():.4f}, {x_test.max():.4f}]")
    
    # 步骤 3: 加载多个训练好的模型并集成预测
    print("\n步骤 3: 加载训练好的模型...")
    
    runs = 3  # 与训练时的runs参数一致
    network_depth = 4  # 与训练时的网络深度一致
    input_shape = (x_test.shape[1],)
    
    all_scores = []
    
    for i in range(runs):
        model_name = f"./model/devnet_phase1_foreground_normalised_{network_depth}d_optimized_run{i}.h5"
        
        try:
            print(f"\n加载模型 {i+1}/{runs}: {model_name}")
            
            # 设置全局data_format
            import devnet
            devnet.data_format = 0
            
            # 加载模型并预测
            scores = load_model_weight_predict(model_name, input_shape, network_depth, x_test)
            scores = scores.flatten()
            
            print(f"  ✓ 模型 {i+1} 预测完成")
            print(f"    异常分数范围: [{scores.min():.4f}, {scores.max():.4f}]")
            print(f"    异常分数均值: {scores.mean():.4f}")
            print(f"    异常分数标准差: {scores.std():.4f}")
            
            all_scores.append(scores)
            
        except Exception as e:
            print(f"  ✗ 加载模型 {i+1} 失败: {e}")
            print(f"    请确保已训练模型: python devnet.py")
            if i == 0:  # 如果第一个模型都加载失败，则退出
                return
    
    if len(all_scores) == 0:
        print("\n✗ 没有成功加载任何模型，无法预测")
        return
    
    # 步骤 4: 集成多个模型的预测结果
    print(f"\n步骤 4: 集成 {len(all_scores)} 个模型的预测...")
    
    # 使用平均值集成
    scores_mean = np.mean(all_scores, axis=0)
    scores_std = np.std(all_scores, axis=0)
    
    print(f"集成后异常分数范围: [{scores_mean.min():.4f}, {scores_mean.max():.4f}]")
    print(f"集成后异常分数均值: {scores_mean.mean():.4f}")
    print(f"集成后异常分数标准差: {scores_mean.std():.4f}")
    print(f"预测不确定性(模型间标准差)均值: {scores_std.mean():.4f}")
    
    # 步骤 5: 转换为概率格式
    print("\n步骤 5: 转换为提交格式...")
    
    # 使用sigmoid将分数映射到[0,1]
    # 为了增加区分度，可以对分数进行缩放
    temperature = 1.0  # 温度参数，可以调整以改变概率的陡峭程度
    prob_fraud = 1 / (1 + np.exp(-scores_mean / temperature))
    prob_normal = 1 - prob_fraud
    
    # 组合成提交格式 (N, 2)
    submission = np.column_stack([prob_normal, prob_fraud])
    
    print(f"提交文件形状: {submission.shape}")
    print(f"P(class=0) 范围: [{submission[:, 0].min():.6f}, {submission[:, 0].max():.6f}]")
    print(f"P(class=1) 范围: [{submission[:, 1].min():.6f}, {submission[:, 1].max():.6f}]")
    print(f"概率和检查: 最小={submission.sum(axis=1).min():.6f}, 最大={submission.sum(axis=1).max():.6f}")
    
    # 步骤 6: 保存提交文件
    print("\n步骤 6: 保存提交文件...")
    output_path = 'submission_devnet_phase1_optimized.npy'
    np.save(output_path, submission.astype(np.float32))
    print(f"✓ 提交文件已保存: {output_path}")
    
    # 步骤 7: 统计分析
    print("\n" + "=" * 60)
    print("预测结果统计分析")
    print("=" * 60)
    
    # 不同阈值下的预测分布
    print("\n不同阈值下的欺诈预测分布:")
    thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
    for threshold in thresholds:
        fraud_count = (prob_fraud > threshold).sum()
        percentage = fraud_count / len(x_test) * 100
        print(f"  P(欺诈) > {threshold:.1f}: {fraud_count:6d} 样本 ({percentage:5.2f}%)")
    
    # Top-K 高风险样本
    print("\nTop-K 高风险样本:")
    top_k_values = [100, 500, 1000, 5000]
    sorted_indices = np.argsort(prob_fraud)[::-1]
    for k in top_k_values:
        if k <= len(prob_fraud):
            top_k_mean_prob = prob_fraud[sorted_indices[:k]].mean()
            print(f"  Top-{k:4d} 平均欺诈概率: {top_k_mean_prob:.4f}")
    
    # 分位数分析
    print("\n欺诈概率分位数:")
    percentiles = [50, 75, 90, 95, 99]
    for p in percentiles:
        value = np.percentile(prob_fraud, p)
        print(f"  {p:2d}th percentile: {value:.6f}")
    
    # 预测质量检查
    print("\n预测质量检查:")
    prob_range = prob_fraud.max() - prob_fraud.min()
    print(f"  欺诈概率范围: {prob_range:.6f}")
    if prob_range < 0.3:
        print("  ⚠️  警告: 区分度较低，可能需要进一步优化模型")
    elif prob_range < 0.6:
        print("  ⚠️  注意: 区分度中等")
    else:
        print("  ✓  区分度良好")
    
    # 熵分析
    epsilon = 1e-10
    entropy = -np.mean(
        prob_normal * np.log(prob_normal + epsilon) + 
        prob_fraud * np.log(prob_fraud + epsilon)
    )
    print(f"  平均熵: {entropy:.4f}")
    if entropy > 0.6:
        print("  ⚠️  预测不确定性较高")
    else:
        print("  ✓  预测确定性较好")
    
    # 保存详细结果用于分析
    print("\n步骤 8: 保存详细分析结果...")
    detailed_results = {
        'test_mask': test_mask,
        'scores_mean': scores_mean,
        'scores_std': scores_std,
        'prob_fraud': prob_fraud,
        'prob_normal': prob_normal,
        'submission': submission
    }
    np.savez('prediction_details.npz', **detailed_results)
    print("✓ 详细结果已保存: prediction_details.npz")
    
    print("\n" + "=" * 60)
    print("预测完成！")
    print("=" * 60)
    
    return submission

if __name__ == "__main__":
    predict_phase1()