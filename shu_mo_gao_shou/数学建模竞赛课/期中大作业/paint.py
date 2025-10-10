import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import os
import numpy as np

def to_paint(traj_dir, num_files=None):
    """
    绘制轨迹数据
    
    Args:
        traj_dir (str): 轨迹文件所在的文件夹
        num_files (int, optional): 要绘制的文件数量。如果为None，则绘制所有文件。
    """
    files = [f for f in os.listdir(traj_dir) if f.endswith(".txt")]
    
    # 如果指定了 num_files，则只取前 num_files 个文件
    if num_files is not None and num_files > 0:
        files = files[:num_files]
    
    # 存储所有轨迹的坐标点
    all_lats = []
    all_lons = []
    trajectories = []  # 存储每条轨迹的LineString

    # 遍历所有文件，加载轨迹数据
    for file in files:
        filepath = os.path.join(traj_dir, file)
        data = []
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    time, lon, lat = parts
                    data.append({'longitude': float(lon), 'latitude': float(lat)})
        df = pd.DataFrame(data)

        # 存储当前轨迹的坐标点
        coordinates = list(zip(df['longitude'], df['latitude']))
        line = LineString(coordinates)
        trajectories.append(line)

        # 收集所有经纬度用于计算绘图范围
        all_lons.extend(df['longitude'])
        all_lats.extend(df['latitude'])

    # 如果没有数据，直接返回
    if not trajectories:
        print("No valid trajectory data found!")
        return

    # 创建图形
    plt.figure(figsize=(12, 8))

    # 为每条轨迹分配随机颜色
    colors = plt.cm.tab20(np.linspace(0, 1, len(trajectories)))

    # 绘制所有轨迹
    for i, line in enumerate(trajectories):
        x, y = line.xy
        plt.plot(x, y, color=colors[i], linewidth=2)

    # 设置图形范围，增加5%的边距
    lon_margin = (max(all_lons) - min(all_lons)) * 0.05
    lat_margin = (max(all_lats) - min(all_lats)) * 0.05
    
    plt.xlim(min(all_lons) - lon_margin, max(all_lons) + lon_margin)
    plt.ylim(min(all_lats) - lat_margin, max(all_lats) + lat_margin)

    # 添加图例和标题
    plt.legend(loc='upper right')
    plt.title(f'Trajectories (Total: {len(trajectories)})')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    
    # 添加网格
    plt.grid(True, linestyle='--', alpha=0.7)

    # 显示图形
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    traj_dir = "cleaned"
    to_paint(traj_dir, num_files=100)  