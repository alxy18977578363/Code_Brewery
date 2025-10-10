import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取Excel文件
file_path = r"女胎数据.xlsx"
df = pd.read_excel(file_path)

# 选择要分析的列（替换为你的列名或列索引）
col_name = '染色体的非整倍体'

# 初始化计数器
count_T13 = 0
count_T18 = 0
count_T21 = 0
non_empty_rows = 0
empty_rows = 0

# 遍历指定列的所有单元格
for cell in df[col_name]:
    # 检查单元格是否为空
    if pd.isna(cell):
        empty_rows += 1
        continue

    non_empty_rows += 1
    cell_str = str(cell).upper()  # 转换为字符串并统一为大写

    # 统计各代码出现次数（包括组合形式）
    count_T13 += cell_str.count('T13')
    count_T18 += cell_str.count('T18')
    count_T21 += cell_str.count('T21')

labels = ['T13', 'T18', 'T21', '有异常', '无异常']
values = [count_T13, count_T18, count_T21, non_empty_rows, empty_rows]
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

plt.figure(figsize=(12, 6))
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
# 绘制柱状图
bars = plt.bar(labels, values, color=colors)

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2., height,
             f'{height}',
             ha='center', va='bottom', fontsize=10)

plt.title('染色体的非整倍体', fontsize=14)
plt.ylabel('频数', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
