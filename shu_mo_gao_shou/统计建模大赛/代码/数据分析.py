import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sklearn.preprocessing import StandardScaler
import pandas as pd
import matplotlib
matplotlib.rc("font",family='YouYuan')

df = pd.read_csv('mobike_shanghai_sample_updated.csv')

# 处理时间字段
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])

# 提取小时作为时间特征
df['hour'] = df['start_time'].dt.hour

# 计算骑行时长（分钟）
df['duration_min'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60

# 计算骑行距离（使用起点和终点的经纬度计算直线距离）
def haversine(lon1, lat1, lon2, lat2):
    # 地球半径（公里）
    R = 6371.0
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2.0)**2
    return R * 2 * np.arcsin(np.sqrt(a))

df['distance_km'] = haversine(df['start_location_x'], df['start_location_y'],
                              df['end_location_x'], df['end_location_y'])

# 构建用于小提琴图的特征数据
plot_df = df[['hour', 'distance_km', 'duration_min']].copy()
plot_df.rename(columns={'hour': '时间', 
                        'distance_km': '骑行距离（km）', 'duration_min': '骑行时长（min）'}, inplace=True)

# 为“用户数量”做一点加工：每个用户出现一次，模拟注册人数（可选处理）
plot_df['用户数量'] = 1  # 所有值为1，可以用计数表达每小时数量

# 准备绘图数据
violin_df = plot_df[['时间', '骑行距离（km）', '骑行时长（min）']]
scaler = StandardScaler()
scaled_data = scaler.fit_transform(violin_df)
scaled_df = pd.DataFrame(scaled_data, columns=violin_df.columns)

# 转为长格式以便绘图
long_df = pd.melt(scaled_df, var_name='特征', value_name='标准化值')

# 绘图
# 使用之前整理好的 long_df 数据重新绘图
plt.figure(figsize=(12, 5))  # 拉长图像比例（宽12，高5）
sns.violinplot(x='特征', y='标准化值', data=long_df, inner='quartile', color='gray')
plt.ylim(-1, 5)  # 缩小Y轴范围
plt.title("图：数值特征小提琴图", fontsize=14)
plt.xlabel("特征")
plt.ylabel("标准化后的值")
plt.tight_layout()
plt.show()


import seaborn as sns
import numpy as np
import pandas as pd

# 提取经纬度数据
longitude = df['start_location_x']
latitude = df['start_location_y']

# 创建一个包含经纬度的 DataFrame
path_df = pd.DataFrame({
    'Longitude': longitude,
    'Latitude': latitude
})
# 获取更精确的经纬度范围，聚焦密集区域
min_longitude_focused, max_longitude_focused = path_df['Longitude'].quantile(0.05), path_df['Longitude'].quantile(0.95)
min_latitude_focused, max_latitude_focused = path_df['Latitude'].quantile(0.05), path_df['Latitude'].quantile(0.95)

# 绘制更加聚焦的热力图
plt.figure(figsize=(10, 8))

# 使用 seaborn 的 hexbin 来绘制热力图，并进一步聚焦
plt.hexbin(path_df['Longitude'], path_df['Latitude'], gridsize=50, cmap='YlGnBu')

# 添加颜色条
plt.colorbar(label='Density')

# 设置标题和标签
plt.title("Focused Bike Ride Path Heatmap", fontsize=16, weight='bold')
plt.xlabel("Longitude", fontsize=14)
plt.ylabel("Latitude", fontsize=14)

# 设置坐标轴范围，进一步聚焦密集区域
plt.xlim(min_longitude_focused - 0.005, max_longitude_focused + 0.005)
plt.ylim(min_latitude_focused - 0.005, max_latitude_focused + 0.005)

# 显示图表
plt.tight_layout()
plt.show()