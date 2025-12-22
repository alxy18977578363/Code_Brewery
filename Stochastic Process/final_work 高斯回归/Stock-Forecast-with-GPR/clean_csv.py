import os
import pandas as pd

def clean_csv_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path, header=0)
            columns = list(df.columns)
            # 需要的原始列顺序：Date, Close/Last, Volume, Open, High, Low
            # 目标顺序：Date, Open, High, Low, Close, Volume
            # 检查并重命名
            if 'Close/Last' in columns:
                df = df.rename(columns={'Close/Last': 'Close'})
            # 重新排序
            target_order = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            # 某些文件可能Volume在最后
            missing_cols = [col for col in target_order if col not in df.columns]
            if missing_cols:
                print(f'Skipped (missing columns {missing_cols}): {file_path}')
                continue
            df = df[target_order]
            # 去掉$符号
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = df[col].astype(str).str.replace('$', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df.to_csv(file_path, index=False)
            print(f'Processed: {file_path}')

if __name__ == '__main__':
    clean_csv_folder('./Data')
    print('All files processed.')
