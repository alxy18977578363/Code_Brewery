import numpy as np
import pandas as pd

df = pd.read_csv("cleaned_mobike_shanghai_sample.csv")

# 统一时间格式并提取小时信息
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])
df['start_hour'] = df['start_time'].dt.hour
df['end_hour'] = df['end_time'].dt.hour
df['date'] = df['start_time'].dt.date

# 计算经纬度边界
min_lng = min(df['start_location_x'].min(), df['end_location_x'].min())
max_lng = max(df['start_location_x'].max(), df['end_location_x'].max())
min_lat = min(df['start_location_y'].min(), df['end_location_y'].min())
max_lat = max(df['start_location_y'].max(), df['end_location_y'].max())

# 构建网格分辨率
grid_size = 32
lng_interval = (max_lng - min_lng) / grid_size
lat_interval = (max_lat - min_lat) / grid_size

# 添加网格编号
df['start_grid_x'] = ((df['start_location_x'] - min_lng) // lng_interval).astype(int)
df['start_grid_y'] = ((df['start_location_y'] - min_lat) // lat_interval).astype(int)
df['end_grid_x'] = ((df['end_location_x'] - min_lng) // lng_interval).astype(int)
df['end_grid_y'] = ((df['end_location_y'] - min_lat) // lat_interval).astype(int)

# 限制边界在 0 到 31
df['start_grid_x'] = df['start_grid_x'].clip(0, grid_size - 1)
df['start_grid_y'] = df['start_grid_y'].clip(0, grid_size - 1)
df['end_grid_x'] = df['end_grid_x'].clip(0, grid_size - 1)
df['end_grid_y'] = df['end_grid_y'].clip(0, grid_size - 1)

# 分别统计 inflow（作为终点）和 outflow（作为起点）
inflow = df.groupby(['date','end_hour', 'end_grid_x', 'end_grid_y']).size().reset_index(name='inflow')
outflow = df.groupby(['date','start_hour', 'start_grid_x', 'start_grid_y']).size().reset_index(name='outflow')

# 合并 inflow 和 outflow 到统一网格-时间坐标
inflow.rename(columns={'end_hour': 'hour', 'end_grid_x': 'grid_x', 'end_grid_y': 'grid_y'}, inplace=True)
outflow.rename(columns={'start_hour': 'hour', 'start_grid_x': 'grid_x', 'start_grid_y': 'grid_y'}, inplace=True)

flow_df = pd.merge(inflow, outflow, on=['date','hour', 'grid_x', 'grid_y'], how='outer').fillna(0)
flow_df[['inflow', 'outflow']] = flow_df[['inflow', 'outflow']].astype(int)

# 保存到新文件
output_path = "merged_data.csv"
flow_df.to_csv(output_path, index=False)

