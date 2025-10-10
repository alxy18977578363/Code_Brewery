import pandas as pd
from geopy.distance import geodesic
import numpy as np
import datetime as datetime

def check_valid_speed(df, max_speed=250):
    """
    检查轨迹点速度是否合法，筛除异常速度数据。
    :param df: 包含timestamp、latitude、longitude的DataFrame
    :param max_speed: 设定的最大合理速度（km/h）
    :return: 只保留速度正常的轨迹点
    """
    # 按时间戳升序排列
    df = df.sort_values('timestamp').reset_index(drop=True)

    prev_point = None  # 上一个点
    valid_indices = []  # 保存有效点的索引

    # 遍历每一行轨迹点
    for idx, row in df.iterrows():
        if prev_point is not None:
            # 计算当前点与上一个点的时间差（小时）
            time_diff = (row['timestamp'] - prev_point['timestamp']).total_seconds() / 3600

            # 计算两点间的地理距离（千米）
            dist = geodesic(
                (prev_point['latitude'], prev_point['longitude']),
                (row['latitude'], row['longitude'])
            ).kilometers

            # 计算速度，筛除速度异常的点
            if time_diff > 0 and (dist / time_diff) <= max_speed:
                valid_indices.append(idx)
        else:
            # 第一个点直接保留
            valid_indices.append(idx)

        prev_point = row

    # 返回筛选后的数据
    return df.loc[valid_indices]

def readtxt(file_path, delimiter=','):
    """
    读取没有表头的轨迹数据文件
    :param file_path: 文件路径
    :param delimiter: 分隔符（默认逗号）
    :return: DataFrame对象
    """
    column_names = ['timestamp', 'longitude', 'latitude']
    # 读取csv文件
    df = pd.read_csv(file_path, delimiter=delimiter, header=None, names=column_names)
    return df

def clean_timestamp(df):
    """
    标准化时间戳格式
    :param df: 包含'timestamp'列的DataFrame
    :return: 时间戳合法化后的DataFrame
    """
    try:
        # 尝试按ISO8601格式解析
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
    except:
        try:
            # 尝试按Unix时间戳解析
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        except:
            # 最后尝试自动解析，无法解析的置为NaT
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # 删除无法解析的时间戳数据
    df = df.dropna(subset=['timestamp'])
    return df

def validate_coordinates(df):
    """
    检查经纬度是否在合理范围内
    :param df: 包含'longitude'和'latitude'列的DataFrame
    :return: 经纬度合法化后的DataFrame
    """
    # 将经纬度列强制转为数值型，非法的会被置为NaN
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')

    # 合理范围：经度[-180,180]，纬度[-90,90]
    valid_lon = (df['longitude'] >= -180) & (df['longitude'] <= 180)
    valid_lat = (df['latitude'] >= -90) & (df['latitude'] <= 90)

    # 只保留经纬度都合理的行
    df = df[valid_lon & valid_lat]
    return df

def filter_by_row_count(df,rows = 2):
    """
    如果DataFrame的元组（行数）少于2个，就返回false，不要这个数据
    :param df: 输入的DataFrame
    :return: 如果行数>=2，返回原DataFrame；否则，返回空的DataFrame
    """
    if df.shape[0] < rows:
        return False
    else:
        return True

def total_clean(data_folder, index_file):
    """
    对指定文件夹中的多个轨迹文件进行批量清洗
    :param data_folder: 原始轨迹文件所在文件夹
    :param index_file: 记录轨迹文件名的索引文件
    """
    try:
        # 打开索引文件，读取每一行的文件名（后18位）
        with open(index_file, 'r') as f:
            file_names = [line.strip()[-18:] for line in f if len(line.strip()) >= 18]
    except FileNotFoundError:
        print(f"索引文件不存在: {index_file}")
        return

    # 遍历每个轨迹文件
    for file_name in file_names:
        file_path = data_folder + file_name

        # 读取轨迹数据
        df = readtxt(file_path, ',')

        # 去重（删除完全相同的行）
        df = df.drop_duplicates()

        # 去掉过少的数据
        if not filter_by_row_count(df):
            continue

        # 清洗时间戳
        df = clean_timestamp(df)

        # 校验经纬度
        df = validate_coordinates(df)

        # 检查并剔除速度异常的点
        df = check_valid_speed(df)

        # 保存清洗后的文件
        clean_path = f'D:\\my_download\\轨迹预测\\cleaned\\{file_name}'
        df.to_csv(clean_path, index=False)

if __name__ == '__main__':
    # 设置数据文件夹路径和索引文件路径
    data_folder = 'D:\\my_download\\轨迹预测\\train\\'
    index_file = 'train_files.txt'
    # 批量清洗轨迹数据
    total_clean(data_folder, index_file)
