import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Bidirectional, LSTM, Dense, Dropout, Reshape
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import os
import joblib
from tensorflow.keras.losses import Huber  # 导入Huber损失函数

# 确保使用GPU加速
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

class TrajectoryPredictor:
    def __init__(self, seq_length=10, pred_length=1):
        self.seq_length = seq_length
        self.pred_length = pred_length
        self.scaler = MinMaxScaler()
        self.model = None
        self.time_scaler = MinMaxScaler()  # 单独的时间缩放器

    def load_trajectory(self, file_path):
        if not os.path.exists(file_path):
            return None

        data = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line == 'MASK':
                    data.append(('MASK', np.nan, np.nan))
                else:
                    timestamp, longitude, latitude = line.split(',')
                    data.append((pd.to_datetime(timestamp), float(longitude), float(latitude)))

        df = pd.DataFrame(data, columns=['timestamp', 'longitude', 'latitude'])
        
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
        
        return df

    def preprocess_data(self, file_paths):
        dfs = []
        for file_path in file_paths:
            df = self.load_trajectory(file_path)
            if df is None:
                continue
            dfs.append(df)

        full_df = pd.concat(dfs, ignore_index=True)
        
        # 分离时间和其他特征进行缩放
        time_features = full_df[['time_diff']]
        spatial_features = full_df[['longitude', 'latitude', 'speed', 'bearing']]
        
        if not hasattr(self.scaler, 'data_min_'):
            self.scaler.fit(spatial_features)
            self.time_scaler.fit(time_features)

        scaled_spatial = self.scaler.transform(spatial_features)
        scaled_time = self.time_scaler.transform(time_features)
        
        # 合并缩放后的特征
        scaled_data = np.hstack([scaled_spatial, scaled_time])
        
        return full_df, scaled_data

    def create_sequences(self, data):
        X, y = [], []
        for i in range(len(data) - self.seq_length - self.pred_length + 1):
            X_seq = data[i:i+self.seq_length]
            y_seq = data[i+self.seq_length : i+self.seq_length+self.pred_length, :2]  # 只预测经纬度
            X.append(X_seq)
            y.append(y_seq)

        X = np.array(X)
        y = np.array(y)
        return X, y

    def build_model(self, input_shape):
        model = Sequential([ 
            Bidirectional(LSTM(128, return_sequences=True, kernel_initializer='he_normal'), 
                         input_shape=input_shape),
            Dropout(0.2),
            Bidirectional(LSTM(64, return_sequences=True)),
            Dropout(0.2),
            Bidirectional(LSTM(32)),
            Dense(64, activation='relu'),
            Dropout(0.1),
            Dense(2 * self.pred_length),  # 只预测经纬度
            Reshape((self.pred_length, 2))
        ])

        # 使用混合精度训练
        policy = tf.keras.mixed_precision.Policy('mixed_float16')
        tf.keras.mixed_precision.set_global_policy(policy)

        optimizer = tf.keras.optimizers.Adam(learning_rate=0.001, clipnorm=1.0)
        model.compile(optimizer=optimizer, loss=Huber())  # 修改为Huber损失
        
        return model

    def train(self, train_full_files, epochs=100, batch_size=64):
        _, full_scaled = self.preprocess_data(train_full_files)
        X_train, y_train = self.create_sequences(full_scaled)
        
        self.model = self.build_model((self.seq_length, X_train.shape[2]))
        
        # 添加回调函数
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True),
            ModelCheckpoint('best_model.h5', save_best_only=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)
        ]
        
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=callbacks,
            verbose=1
        )
        
        return history

    def predict_masked_points(self, masked_file):
        df = self.load_trajectory(masked_file)
        if df is None:
            return None
            
        # 找出被masked的位置
        mask_indices = df[df['timestamp'] == 'MASK'].index
        
        # 预处理数据
        time_features = df[['time_diff']]
        spatial_features = df[['longitude', 'latitude', 'speed', 'bearing']]

        # 用已知数据填充masked行（简单线性插值）
        spatial_features = spatial_features.interpolate()
        time_features = time_features.interpolate()
        
        scaled_spatial = self.scaler.transform(spatial_features)
        scaled_time = self.time_scaler.transform(time_features)
        scaled_data = np.hstack([scaled_spatial, scaled_time])
        
        # 对每个masked点进行预测
        for idx in mask_indices:
            # 取前seq_length个点作为输入
            start_idx = max(0, idx - self.seq_length)
            input_seq = scaled_data[start_idx:idx]
            
            # 如果不够seq_length，在前面填充
            if len(input_seq) < self.seq_length:
                padding = np.tile(input_seq[0], (self.seq_length - len(input_seq), 1))
                input_seq = np.vstack([padding, input_seq])
                
            # 预测
            input_seq = input_seq.reshape(1, self.seq_length, -1)
            pred = self.model.predict(input_seq)
            
            # 只取最后一个预测点（因为我们可能预测多个点）
            pred_point = pred[0, -1, :]
            
            # 反归一化经纬度
            pred_spatial = self.scaler.inverse_transform(
                np.hstack([
                    pred_point.reshape(-1, 2),
                    np.zeros((1, 2))  # 为speed和bearing填充0
                ])
            )[:, :2]
            
            # 更新数据
            df.loc[idx, ['longitude', 'latitude']] = pred_spatial[0]
            
        return df

    def save_model(self, filepath):
        self.model.save(filepath)
        joblib.dump(self.scaler, 'scaler.pkl')
        joblib.dump(self.time_scaler, 'time_scaler.pkl')

    def save_trajectory(df, output_file_path):
        # 格式化保存为原始TXT格式
        with open(output_file_path, 'w') as f:
            for _, row in df.iterrows():
                line = f"{row['timestamp']},{row['longitude']},{row['latitude']}\n"
                f.write(line)

if __name__ == '__main__':

    # 初始化参数
    SEQ_LENGTH = 10
    PRED_LENGTH = 1
    
    # 文件路径设置
    BASE_PATH = "D:\\my_download\\轨迹预测\\"
    
    # 加载文件列表
    def load_file_list(file_path):
        with open(file_path, 'r') as f:
            return [os.path.basename(line.strip()) for line in f]
    
    train_paths = load_file_list(BASE_PATH + "train_files.txt")
    test_paths = load_file_list(BASE_PATH + "test_files.txt")
    
    # 构建完整路径
    train_masked_files = [BASE_PATH + "train_masked\\" + p for p in train_paths]
    train_full_files = [BASE_PATH + "cleaned\\" + p for p in train_paths]
    test_masked_files = [BASE_PATH + "test_masked\\" + p for p in test_paths]
    
    # 初始化预测器
    predictor = TrajectoryPredictor(seq_length=SEQ_LENGTH, pred_length=PRED_LENGTH)
    
    # 训练模型
    print("Training model...")
    predictor.train(train_full_files, epochs=10)
    
    
    print("保存模型")
    predictor.save_model(BASE_PATH + "model.h5")
