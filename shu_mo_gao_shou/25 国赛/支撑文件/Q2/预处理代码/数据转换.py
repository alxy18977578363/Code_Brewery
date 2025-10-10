import pandas as pd

# 读取文件
df = pd.read_excel("D:\\国赛\\CUMCM2025Problems\\C题\\附件.xlsx")
target_column = '染色体的非整倍体'

# 检查列是否存在
if target_column in df.columns:
    mask = df[target_column].notna() & (df[target_column].astype(str).str.strip() != '')

    df[target_column] = mask.astype(int)

    # 保存修改后的数据到新文件（或覆盖原文件）
    df.to_csv('D:\\国赛\\CUMCM2025Problems\\C题\\女胎数据.csv', index=False) 
    print("已保存到男胎怀孕检测数据.csv")
else:
    print(f"不存在列 '{target_column}'")
