import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import os

# 确保使用GPU加速
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# 加载Scaler
scaler = joblib.load('scaler.pkl')
time_scaler = joblib.load('time_scaler.pkl')

# 加载已训练的模型
model = load_model('model.h5')

def load_trajectory(file_path):
    if not os.path.exists(file_path):
        return None

    data = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line == 'MASK':
                data.append((np.nan, np.nan, np.nan))
            else:
                timestamp, longitude, latitude = line.split(',')
                data.append((pd.to_datetime(timestamp), float(longitude), float(latitude)))

    df = pd.DataFrame(data, columns=['timestamp', 'longitude', 'latitude'])

    # 找出被MASK的位置
    mask_indices = df[pd.isna(df['longitude'])].index

    # 将'MASK'替换为NaT（Not a Time），方便后续处理
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['timestamp'] = df['timestamp'].interpolate(method='linear')
    df['longitude'] = df['longitude'].interpolate(method='linear')
    df['latitude'] = df['latitude'].interpolate(method='linear')

    # 计算速度和方向变化作为额外特征
    df['time_diff'] = df['timestamp'].diff().dt.total_seconds().fillna(0)
    df['distance'] = np.sqrt(
        (df['longitude'].diff()**2) + (df['latitude'].diff()**2)
    ).fillna(0)
    df['speed'] = df['distance'] / (df['time_diff'] + 1e-6)  # 避免除以0
    df['bearing'] = np.arctan2(
        df['latitude'].diff(), 
        df['longitude'].diff()
    ).fillna(0)
    
    return df, mask_indices

def preprocess_data(df):
    # 分离时间和其他特征进行缩放
    time_features = df[['time_diff']]
    spatial_features = df[['longitude', 'latitude', 'speed', 'bearing']]

    # 用Scaler进行归一化
    scaled_spatial = scaler.transform(spatial_features)
    scaled_time = time_scaler.transform(time_features)

    # 合并缩放后的特征
    scaled_data = np.hstack([scaled_spatial, scaled_time])
    
    return df, scaled_data

def create_sequences(data, seq_length=10):
    X = []
    for i in range(len(data) - seq_length):
        X_seq = data[i:i+seq_length]
        X.append(X_seq)
    X = np.array(X)
    return X

def predict_masked_points(masked_file, seq_length=10):
    df, mask_indices = load_trajectory(masked_file)
    if df is None:
        return None

    # 预处理数据
    _, scaled_data = preprocess_data(df)
    
    # 对每个masked点进行预测
    for idx in mask_indices:
        # 取前seq_length个点作为输入
        start_idx = max(0, idx - seq_length)
        input_seq = scaled_data[start_idx:idx]

        # 如果不够seq_length，在前面填充
        if len(input_seq) < seq_length:
            padding = np.tile(input_seq[0], (seq_length - len(input_seq), 1))
            input_seq = np.vstack([padding, input_seq])

        # 预测
        input_seq = input_seq.reshape(1, seq_length, -1)
        pred = model.predict(input_seq)

        # 反归一化经纬度
        # 反归一化经纬度
        pred_spatial = scaler.inverse_transform(
        np.hstack([pred[0, -1, :2].reshape(1, -1), np.zeros((1, 2))])
        )[:, :2]


        # 更新数据
        df.loc[idx, ['longitude', 'latitude']] = pred_spatial[0]
        
    return df

def save_trajectory(df, output_file_path):
    # 格式化保存为原始TXT格式
    with open(output_file_path, 'w') as f:
        for _, row in df.iterrows():
            line = f"{row['timestamp']},{row['longitude']},{row['latitude']}\n"
            f.write(line)

# 1. 批量加载文件夹中的所有txt文件
def load_all_txt_files(folder_path):
    all_txt = []
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            all_txt.append(file_path)

    return all_txt

# 预测
if __name__ == '__main__':
    SEQ_LENGTH = 10
    PRED_LENGTH = 1
    
    # 文件路径设置
    BASE_PATH = "D:\\my_download\\轨迹预测\\"
    
    masked_files = load_all_txt_files("D:\\my_download\\轨迹预测\\test_masked")

    # 预测
    print("Predicting test data...")


    for masked_file in masked_files:
        output_file = BASE_PATH + "pred\\" + masked_file[-18:]

        predicted_df = predict_masked_points(masked_file)

        # 保存结果
        if predicted_df is not None:
            # 保存预测结果
            save_trajectory(predicted_df, output_file)
