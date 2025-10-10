import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
import matplotlib
matplotlib.rc("font",family='YouYuan')



# 读取数据
data = pd.read_csv('mobike_shanghai_sample_updated.csv')

# 提取起点和终点坐标
start_coords = data[['start_location_x', 'start_location_y']].values
end_coords = data[['end_location_x', 'end_location_y']].values
all_coords = np.vstack([start_coords, end_coords])      # 垂直堆叠在一起


# 模糊C均值聚类(FCM)实现
def fcm(data, c, m=2, max_iter=100, error=1e-5):
    """
    模糊C均值聚类算法实现
    
    参数:
        data: 输入数据 (n_samples, n_features)
        c: 聚类数量
        m: 模糊度参数(>1)
        max_iter: 最大迭代次数
        error: 收敛阈值
        
    返回:
        聚类中心, 隶属度矩阵
    """
    n = data.shape[0]           # 样本数量
    
    # 随机初始化隶属度矩阵
    U = np.random.rand(n, c)        
    U = U / np.sum(U, axis=1, keepdims=True)        # 归一化
    
    for _ in range(max_iter):
        # 计算聚类中心
        centers = np.dot(U.T ** m, data) / np.sum(U.T ** m, axis=1, keepdims=True)
        
        # 计算距离
        dist = cdist(data, centers, 'euclidean')
        dist = np.fmax(dist, np.finfo(np.float64).eps)
        
        # 更新隶属度矩阵
        U_new = 1.0 / (dist ** (2/(m-1)))
        U_new = U_new / np.sum(U_new, axis=1, keepdims=True)
        
        # 检查收敛
        if np.max(np.abs(U_new - U)) < error:
            break
            
        U = U_new
    
    # 计算SSE
    sse = np.sum((U ** m) * (dist ** 2))
    
    return centers, U, sse

# 考虑时间维度的模糊聚类
def temporal_fcm(data, timestamps, c=3, time_windows=24):
    """
    考虑时间维度的模糊聚类
    在时间维度上属于混合类型，故将时间维度上的稳定聚类中心作为消除时间差异的聚类中心
    
    参数:
        data: 空间坐标数据
        timestamps: 对应的时间戳
        c: 聚类数量
        time_windows: 时间窗口数量(按小时划分)
        
    返回:
        最终聚类中心, 所有时间窗口的聚类中心
    """
    # 将时间转换为小时
    hours = pd.to_datetime(timestamps).hour.values
    
    # 存储每个时间窗口的聚类中心
    time_centers = []
    
    for h in range(time_windows):
        # 获取当前时间窗口的数据
        mask = (hours == h)
        if np.sum(mask) < c:  # 数据量太少则跳过
            continue
            
        window_data = data[mask]        # 获取当前时间窗口的数据
        
        # 对当前时间窗口进行FCM聚类
        centers, _, _ = fcm(window_data, c=c)
        time_centers.append(centers)
    
    # 将所有时间窗口的聚类中心再次聚类，得到稳定的最终聚类中心
    all_centers = np.vstack(time_centers)       # 每个时间段得到三个聚类中心
    final_centers, _, _ = fcm(all_centers, c=c)
    
    return final_centers, time_centers

# 提取时间信息(使用开始时间)
start_timestamps = data['start_time'].values
end_timestamps = data['end_time'].values
timestamps = np.concatenate([start_timestamps, end_timestamps])     # 合并起点和终点时间戳


# 进行时间感知的FCM聚类
final_centers, time_centers = temporal_fcm(all_coords, timestamps, c=3)

print("最终聚类中心(消除时间差异后的稳定中心):")
print(final_centers)

# 使用最终聚类中心对所有数据进行分类
distances = cdist(all_coords, final_centers, 'euclidean')
cluster_labels = np.argmin(distances, axis=1)       # 划分类别，距离最小的下标为其类

# 统计每个簇的点数和使用频率
cluster_counts = np.bincount(cluster_labels)
usage_frequency = cluster_counts / len(all_coords)

# 按照使用频率排序确定区域类型
sorted_indices = np.argsort(usage_frequency)[::-1]  # 从高到低排序
region_types = ['高频(H)', '平常(A)', '低频(L)']
region_colors = ['red', 'green', 'blue']

# 创建区域类型映射字典
region_map = {sorted_indices[0]: '高频(H)', 
              sorted_indices[1]: '平常(A)', 
              sorted_indices[2]: '低频(L)'}



###  可视化结果
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap


# 创建自定义颜色映射
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']  # 红、青绿、天蓝
region_colors = [colors[sorted_indices.tolist().index(i)] for i in range(3)]

# 1. 改进的聚类结果可视化
plt.figure(figsize=(14, 12))

# 绘制所有点并按区域类型着色
for i in range(3):
    mask = (cluster_labels == i)
    plt.scatter(all_coords[mask, 0], all_coords[mask, 1], 
                c=region_colors[i], s=8, alpha=0.4, 
                label=f'{region_map[i]}区域 (占比:{usage_frequency[i]:.1%})')

# 绘制聚类中心并标注区域类型
for i, center in enumerate(final_centers):
    plt.scatter(center[0], center[1], c='black', s=300, marker='*', edgecolors='gold', linewidths=1.5)
    plt.text(center[0], center[1], f'{region_map[i]}\n中心', 
             fontsize=14, weight='bold', ha='center', va='center',
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.3'))

plt.xlabel('经度', fontsize=14)
plt.ylabel('纬度', fontsize=14)
plt.title('上海共享自行车使用区域聚类分析\n(基于时间感知的模糊C均值聚类)', fontsize=16, pad=20)
plt.legend(fontsize=12, markerscale=2)
plt.grid(True, alpha=0.2)
plt.tight_layout()

# 添加版权信息
plt.figtext(0.5, 0.01, "数据来源: 上海摩拜单车样本数据 | 分析方法: 时间感知FCM聚类", 
            ha="center", fontsize=10, color='gray')

plt.show()

# 状态转移矩阵
def Markov_matrix(start_labels,end_labels,c):
    # 3. 构建转移计数矩阵 (原文未明确给出公式，但描述了"各区域转入量与区域总转出量之比")
    # 初始化3x3的转移计数矩阵
    transition_counts = np.zeros((c, c), dtype=int)

    # 统计所有行程的转移情况
    for start_r, end_r in zip(start_labels, end_labels):
        transition_counts[start_r, end_r] += 1

    # 4. 计算转移概率矩阵 (原文第2页公式(10)-(13)描述的马尔科夫过程)
    # 转移概率 = 从区域i到区域j的转移次数 / 区域i的总转出次数
    transition_matrix = transition_counts / transition_counts.sum(axis=1, keepdims=True)

    # 精确求解稳定状态（代替最小二乘法）
    A = np.vstack([(transition_matrix.T - np.eye(c)), np.ones(c)])
    b = np.hstack([np.zeros(c), 1])
    steady_state = np.linalg.lstsq(A, b, rcond=None)[0]
    
    return transition_matrix, steady_state



# 计算起点到聚类中心的距离
start_distances = cdist(data[['start_location_x', 'start_location_y']].values, final_centers, 'euclidean')
start_labels = np.argmin(start_distances, axis=1)  # 每个起点的区域类型

# 计算终点到聚类中心的距离
end_distances = cdist(data[['end_location_x', 'end_location_y']].values, final_centers, 'euclidean')
end_labels = np.argmin(end_distances, axis=1)  # 每个终点的区域类型

transition_matrix,steady_state = Markov_matrix(start_labels,end_labels,3)
print(transition_matrix)
print(steady_state)