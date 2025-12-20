import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def prepare_phase1_data():
    """
    将phase1_gdata.npz转换为DevNet可用的CSV格式
    只保留前景节点(Class 0和Class 1)用于二分类
    """
    # 加载数据
    data = np.load('phase1_gdata.npz')
    
    x = data['x']  # (4024623, 17)
    y = data['y'].flatten()  # (4024623,)
    
    # 只保留前景节点: Class 0 (正常) 和 Class 1 (欺诈)
    # 排除测试样本(-100)和背景用户(Class 2, 3)
    foreground_mask = (y == 0) | (y == 1)
    
    x_foreground = x[foreground_mask]
    y_foreground = y[foreground_mask]
    
    print(f"前景节点总数: {len(y_foreground)}")
    print(f"正常用户(Class 0): {np.sum(y_foreground == 0)}")
    print(f"欺诈用户(Class 1): {np.sum(y_foreground == 1)}")
    print(f"不平衡比例: 1:{np.sum(y_foreground == 0) / np.sum(y_foreground == 1):.2f}")
    
    # 创建DataFrame
    feature_cols = [f'feat_{i}' for i in range(x_foreground.shape[1])]
    df = pd.DataFrame(x_foreground, columns=feature_cols)
    df['class'] = y_foreground
    
    # 保存为CSV
    output_path = './dataset/phase1_foreground_normalised.csv'
    df.to_csv(output_path, index=False)
    print(f"数据已保存到: {output_path}")
    
    return df

if __name__ == "__main__":
    prepare_phase1_data()