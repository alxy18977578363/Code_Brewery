import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
import matplotlib as mpl

# 读取文件

df = pd.read_excel(r"D:\国赛\CUMCM2025Problems\C题\问题一\男胎怀孕检测数据(2).xlsx")

# 选择列
selected_cols = ['年龄', '身高','体重','孕妇BMI', 'GC含量','原始读段数', '在参考基因组上比对的比例','重复读段的比例','唯一比对的读段数','13号染色体的Z值','18号染色体的Z值','21号染色体的Z值',  'X染色体的Z值','X染色体浓度','13号染色体的GC含量','18号染色体的GC含量','21号染色体的GC含量','被过滤掉读段数的比例','染色体的非整倍体']

# 验证选择列是否存在
v_cols = [col for col in selected_cols if col in df.columns]
if not v_cols:
    print("没有找到指定的列名")
    exit()

print(f"将只对以下列进行spearman相关性分析: {', '.join(v_cols)}")

# 创建斯皮尔曼相关系数空矩阵和p值空矩阵
spearman_m = pd.DataFrame(index=v_cols, columns=v_cols)
p_m = pd.DataFrame(index=v_cols, columns=v_cols)

# 填充斯皮尔曼相关系数矩阵和p值矩阵
for i, col1 in enumerate(v_cols):
    for j, col2 in enumerate(v_cols):
        if i == j:
            # 对角线为自己与自己分析，直接填充为1
            spearman_m.loc[col1, col2] = 1.0
            p_m.loc[col1, col2] = 0.0
        elif i < j:
            # 仅计算上三角部分，然后对称到下三角
            v_data = df[[col1, col2]].dropna()
            if len(v_data) >= 3:
                corr, p_value = spearmanr(v_data[col1], v_data[col2])
                spearman_m.loc[col1, col2] = corr
                spearman_m.loc[col2, col1] = corr
                p_m.loc[col1, col2] = p_value
                p_m.loc[col2, col1] = p_value
            else:
                spearman_m.loc[col1, col2] = np.nan
                spearman_m.loc[col2, col1] = np.nan
                p_m.loc[col1, col2] = np.nan
                p_m.loc[col2, col1] = np.nan

# 转换数值类型
spearman_m = spearman_m.astype(float)
p_m = p_m.astype(float)


print("\n斯皮尔曼相关系数矩阵:")
print(spearman_m.round(3))

print("\nP值矩阵:")
print(p_m.round(4))

# 创建显著性标记矩阵
significance_m = pd.DataFrame(index=v_cols, columns=v_cols)
for i in range(len(v_cols)):
    for j in range(len(v_cols)):
        if i == j:
            significance_m.iloc[i, j] = ""
        else:
            p_val = p_m.iloc[i, j]
            if pd.isna(p_val):
                significance_m.iloc[i, j] = ""
            elif p_val < 0.001:
                significance_m.iloc[i, j] = "***"
            elif p_val < 0.01:
                significance_m.iloc[i, j] = "**"
            elif p_val < 0.05:
                significance_m.iloc[i, j] = "*"
            else:
                significance_m.iloc[i, j] = ""

# 绘制热力图
plt.figure(figsize=(12, 10))
heatmap = sns.heatmap(
    spearman_m,
    annot=False,
    cmap='coolwarm',
    vmin=-1, vmax=1,
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": 0.8}
)

# 添加显著性标记
for i in range(len(v_cols)):
    for j in range(len(v_cols)):
        if i != j:
            corr_value = spearman_m.iloc[i, j]
            if not pd.isna(corr_value):
                text = f"{corr_value:.2f}{significance_m.iloc[i, j]}"
                heatmap.text(j + 0.5, i + 0.5, text,
                             ha="center", va="center",
                             color="black", fontsize=10)
            else:
                heatmap.text(j + 0.5, i + 0.5, "NA",
                             ha="center", va="center",
                             color="black", fontsize=10)
        else:
            heatmap.text(j + 0.5, i + 0.5, "1.00",
                         ha="center", va="center",
                         color="black", fontsize=10)


plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei']# 设置中文字体支持
plt.rcParams['axes.unicode_minus'] = False
plt.title('斯皮尔曼相关系数矩阵（带显著性标记）', fontsize=16)
plt.xticks(fontsize=10, rotation=45, ha='right')
plt.yticks(fontsize=10, rotation=0)


plt.figtext(0.5, 0.01,
            "显著性标记: *** p<0.001, ** p<0.01, * p<0.05",
            ha="center", fontsize=10)


plt.tight_layout()
plt.subplots_adjust(bottom=0.1)
plt.savefig('spearman_correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.show()


plt.tight_layout()
plt.subplots_adjust(bottom=0.1)


# 创建带显著性标记的相关系数矩阵
combined_m = pd.DataFrame(index=v_cols, columns=v_cols)
for i in range(len(v_cols)):
    for j in range(len(v_cols)):
        if i == j:
            combined_m.iloc[i, j] = "1.00"
        else:
            corr = spearman_m.iloc[i, j]
            sig = significance_m.iloc[i, j]
            if pd.isna(corr):
                combined_m.iloc[i, j] = "NA"
            else:
                combined_m.iloc[i, j] = f"{corr:.2f}{sig}"


# 保存路径
output = r'D:\国赛\CUMCM2025Problems\C题'
path = os.path.join(output, "斯皮尔曼.xlsx")
try:
    with pd.ExcelWriter(path) as writer:
        # 相关系数矩阵
        spearman_m.round(3).to_excel(writer, sheet_name='斯皮尔曼相关系数')

        # p值矩阵
        p_m.round(4).to_excel(writer, sheet_name='P值矩阵')

        # 带显著性标记的相关系数矩阵
        combined_m.to_excel(writer, sheet_name='相关系数(带显著性)')

        # 显著性说明
        pd.DataFrame({
            '显著性标记': ['***', '**', '*'],
            '含义': ['p < 0.001', 'p < 0.01', 'p < 0.05']
        }).to_excel(writer, sheet_name='显著性说明', index=False)

    print(f"文件已保存至: {path}")
except Exception as e:
    print(f"保存文件失败: {e}")
