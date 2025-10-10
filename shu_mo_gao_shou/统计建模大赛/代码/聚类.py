import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import geopandas as gpd
import matplotlib
matplotlib.rc("font",family='YouYuan')


def load_data(filepath):
    """加载共享单车订单数据"""
    df = pd.read_csv(filepath)  # 改为 read_csv
    
    # 提取所有起点和终点坐标
    start_points = df[['start_location_x', 'start_location_y']].values
    end_points = df[['end_location_x', 'end_location_y']].values
    all_points = np.vstack([start_points, end_points])
    
    return all_points

def dbscan_clustering(points, eps=0.005, min_samples=10):
    """DBSCAN密度聚类"""
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(points)
    labels = db.labels_
    
    # 统计聚类结果
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    
    print(f'DBSCAN聚类结果: {n_clusters}个簇, {n_noise}个噪声点')
    
    # 可视化
    plt.scatter(points[:, 0], points[:, 1], c=labels, cmap='viridis', s=5)
    plt.title('DBSCAN聚类结果')
    plt.xlabel('经度')
    plt.ylabel('纬度')
    plt.show()
    
    return labels, n_clusters

def kmeans_clustering(points, n_clusters):
    """K-Means聚类"""
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(points)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_
    
    # 计算轮廓系数
    silhouette_avg = silhouette_score(points, labels)
    print(f'K-Means轮廓系数: {silhouette_avg:.3f}')
    
    # 读取上海行政区划数据
    china = gpd.read_file("gadm41_CHN.gpkg", layer="ADM_ADM_1")
    shanghai = china[china['NAME_1'] == 'Shanghai']

    # 设置画布
    fig, ax = plt.subplots(figsize=(10, 10))

    # 绘制上海地图
    shanghai.plot(ax=ax, color='#e0f3ff', edgecolor='black', linewidth=1)

    # 绘制 K-Means 聚类点，按标签着色
    sc = ax.scatter(points[:, 0], points[:, 1], c=labels, cmap='viridis', s=5, alpha=0.8)

    # 绘制聚类中心，使用红色 X
    ax.scatter(centers[:, 0], centers[:, 1], c='red', marker='x', s=100, label='聚类中心')

    # 添加标题和坐标轴标签
    ax.set_title('K-Means 聚类结果叠加上海地图', fontsize=16, fontweight='bold')
    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')

    # 添加颜色条
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label('Cluster ID')

    # 去掉坐标轴线
    ax.set_axis_off()

    # 调整布局
    plt.tight_layout()
    plt.show()

    return labels, centers

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

    # 获取硬聚类标签(每个点属于隶属度最高的簇)
    labels = np.argmax(U, axis=1)
    
    # 计算轮廓系数
    silhouette_avg = silhouette_score(data, labels)
    print(f'FCM轮廓系数: {silhouette_avg:.3f}')
    
    # 设置画布
    fig, ax = plt.subplots(figsize=(10, 10))

    # 绘制 FCM 聚类点，按标签着色
    sc = ax.scatter(data[:, 0], data[:, 1], c=labels, cmap='viridis', s=5, alpha=0.8)

    # 绘制聚类中心，使用红色 X
    ax.scatter(centers[:, 0], centers[:, 1], c='red', marker='x', s=100, label='聚类中心')

    # 添加标题和坐标轴标签
    ax.set_title('FCM 聚类结果', fontsize=16, fontweight='bold')
    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')

    # 添加颜色条
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label('Cluster ID')

    # 去掉坐标轴线
    ax.set_axis_off()

    # 调整布局
    plt.tight_layout()
    plt.show()
    return centers, U, labels, sse  # 按这个顺序返回

def main(filepath):
    # 1. 加载数据
    points = load_data(filepath)
    
    # 2. DBSCAN聚类确定站点范围
    print("\n=== 第一步: DBSCAN聚类确定站点范围 ===")
    db_labels, n_clusters = dbscan_clustering(points)
    
    # 去除噪声点
    core_samples_mask = np.zeros_like(db_labels, dtype=bool)
    core_samples_mask[db_labels != -1] = True
    core_points = points[core_samples_mask]
    
    # 3. FCM确定站点位置
    print("\n=== 第二步: FCM确定站点位置 ===")
    centers, _, kmeans_labels, _ = fcm(core_points, n_clusters)

    # 保存站点信息
    fcm_centers_df = pd.DataFrame(centers, columns=['longitude', 'latitude'])
    fcm_centers_df.to_csv('station_centers.csv', index=False)
    print("FCM聚类中心已保存到 station_centers.csv")

    kmeans_labels, station_centers = kmeans_clustering(core_points, n_clusters)
    
    # 4. 对站点进行区域划分
    print("\n=== 第三步: 站点区域划分 ===")
    # 假设将站点划分为3个调度区域(可根据实际情况调整)
    n_zones = 3
    zone_labels, zone_centers = kmeans_clustering(station_centers, n_zones)
    
    
    # 输出结果
    print("\n=== 最终结果 ===")
    stations_df = pd.DataFrame({
        'station_id': range(len(station_centers)),
        'longitude': station_centers[:, 0],
        'latitude': station_centers[:, 1],
        'zone_id': zone_labels[np.argsort(kmeans_labels)]
    })
    
    print("\n站点分布及所属区域:")
    print(stations_df)
    
    

if __name__ == "__main__":
    # 替换为您的Excel文件路径
    filepath = "mobike_shanghai_sample_updated.csv" 
    main(filepath)