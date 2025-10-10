import pandas as pd
data = pd.read_csv("mobike_shanghai_sample_updated.csv")

# print(data.isnull().sum())          # 统计缺失值

# 删除含有缺失值的行
data.dropna(inplace=True)

# 处理数据类型
data['start_time'] = pd.to_datetime(data['start_time'])
data['end_time'] = pd.to_datetime(data['end_time'])
data['start_location_x'] = data['start_location_x'].astype(float)
data['start_location_y'] = data['start_location_y'].astype(float)
data['end_location_x'] = data['end_location_x'].astype(float)
data['end_location_y'] = data['end_location_y'].astype(float)

# 去除重复的行
data.drop_duplicates(inplace=True)

# 检查数据范围是否正确
invalid_time = data[data['start_time']> data['end_time']]
if invalid_time.empty:
    print("数据范围正确")
else:
    print("数据范围有误") 


# 计算时间差
data['time_diff'] = data['end_time'] - data['start_time']

# 去掉时间差超过一天或者不足一分钟的数据
filtered_data = data[(data['time_diff'] <= pd.Timedelta(days=1)) & (data['time_diff'] >= pd.Timedelta(minutes=1))]


# 提取需要的列
selected_columns = filtered_data[['start_time','end_time', 'start_location_x', 'start_location_y','end_location_x','end_location_y']]
# 保存结果
selected_columns.to_csv("cleaned_mobike_shanghai_sample.csv", index=False)