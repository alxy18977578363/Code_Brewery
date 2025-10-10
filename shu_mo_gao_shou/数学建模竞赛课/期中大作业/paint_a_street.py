import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import numpy as np

def plot_trajectory_on_map(traj_file):
    # 读取轨迹数据
    data = []
    with open(traj_file, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 3:
                time, lon, lat = parts
                data.append({'longitude': float(lon), 'latitude': float(lat)})
    df = pd.DataFrame(data)
    
    # 创建轨迹的LineString
    coordinates = list(zip(df['longitude'], df['latitude']))
    trajectory = LineString(coordinates)
    
    # 计算地图中心点（使用轨迹的平均经纬度）
    center_lat = np.mean(df['latitude'])
    center_lon = np.mean(df['longitude'])
    
    # 获取地图数据（10公里半径范围）
    graph = ox.graph_from_point(
        (center_lat, center_lon),
        dist=5000,  # 5公里半径
        network_type='drive'
    )
    
    # 绘制地图
    fig, ax = ox.plot_graph(graph, show=False, close=False, edge_color='gray', node_size=0)
    
    # 绘制轨迹（使用红色）
    x, y = trajectory.xy
    ax.plot(x, y, color='red', linewidth=3, label='Trajectory')
    
    # 添加图例和标题
    ax.legend(loc='upper right')
    plt.title(f'Trajectory Visualization: {traj_file}')
    
    # 显示图形
    plt.show()

if __name__ == '__main__':
    # 使用示例
    traj_file = "20080528091033.txt"  
    plot_trajectory_on_map(traj_file)