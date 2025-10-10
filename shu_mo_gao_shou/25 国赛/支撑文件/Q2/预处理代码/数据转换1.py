#获得是否误检
import pandas as pd

# 读取文件
df = pd.read_csv("D:\\国赛\\CUMCM2025Problems\\C题\\男胎怀孕检测数据(5).csv")  # 替换为你的文件路径
col1 = '染色体的非整倍体'
col2 = '胎儿是否健康'
result_col = '是否误检'

# 检查所有列是否存在
required_cols = [col1, col2]
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    print(f"错误：文件中不存在列 {', '.join(missing_cols)}")
else:
    df[result_col] = (df[col1].fillna('NaN').astype(str) == df[col2].fillna('NaN').astype(str)).astype(int)

    # 保存文件
    df.to_excel('D:\\国赛\\CUMCM2025Problems\\C题\\男胎怀孕检测数据(5).xlsx', index=False)
    print(f"结果已保存到output_file.csv的'{result_col}'列")