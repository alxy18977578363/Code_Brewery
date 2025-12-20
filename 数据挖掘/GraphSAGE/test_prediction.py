"""
测试预测功能的脚本
"""
import numpy as np
import torch
from SAGE import load_data, SAGE, Trainer

def test_prediction(model_path):
    """测试预测功能"""
    print("开始测试预测功能...")

    # 加载数据
    loader_train, loader_test, data, test_mask = load_data()

    # 加载模型
    
    

    # 创建训练器
    trainer = Trainer(model, loader_train, loader_test, data, test_mask)


    # 测试预测功能
    print("\n测试预测功能...")
    predictions = trainer.predict_test_nodes('test_predictions.npy')

    # 验证结果
    print(f"\n验证结果:")
    print(f"预测结果shape: {predictions.shape}")
    print(f"预测结果数据类型: {predictions.dtype}")
    print(f"预测结果范围: [{predictions.min():.4f}, {predictions.max():.4f}]")
    print(f"每行概率和: {predictions.sum(axis=1)[:5]}...")  # 显示前5个样本

    # 检查保存的文件
    try:
        loaded_predictions = np.load('test_predictions.npy')
        print(f"\n从文件加载的预测结果shape: {loaded_predictions.shape}")
        print("文件保存成功！")
    except Exception as e:
        print(f"文件加载失败: {e}")

if __name__ == '__main__':
    test_prediction()