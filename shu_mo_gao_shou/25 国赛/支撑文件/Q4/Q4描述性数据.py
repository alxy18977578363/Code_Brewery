import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据（使用Q4.py中的数据处理流程）
df4 = pd.read_excel('./附件.xlsx', sheet_name=1)

# 先得到孕周的天数
def convert_gestational_week(week_str):
    """
    将孕周字符串转换为天数
    格式示例: '12w+3d', '15w', '20+4' 等
    """
    if pd.isna(week_str):
        return float('nan')
    
    week_str = str(week_str).lower().strip()
    
    try:
        if '+' in week_str:
            parts = week_str.split('+')
            weeks = int(parts[0].replace('w', '').replace('周', ''))
            days = int(parts[1].replace('d', '').replace('天', ''))
            return weeks * 7 + days
        elif 'w' in week_str or '周' in week_str:
            weeks = int(week_str.replace('w', '').replace('周', ''))
            return weeks * 7
        else:
            # 尝试直接转换为数字（可能是纯周数）
            try:
                weeks = float(week_str)
                return weeks * 7
            except:
                return float('nan')
    except:
        return float('nan')

# 应用转换函数
df4['孕周天数'] = df4['检测孕周'].apply(convert_gestational_week)

# 剔除GC含量异常的数据（正常范围40%~60%）
gc_normal_lower = 0.395
gc_normal_upper = 0.60
df4 = df4[(df4['GC含量'] >= gc_normal_lower) & (df4['GC含量'] <= gc_normal_upper)].copy()

# 剔除10周以下和26周以上的数据
lower_bound = 10 * 7  # 10周
upper_bound = 25 * 7  # 25周
df4 = df4[(df4['孕周天数'] >= lower_bound) & (df4['孕周天数'] < upper_bound)].copy()

# 增加标签列
df4['标签'] = df4['染色体的非整倍体'].apply(
    lambda x: 1 if pd.notna(x) and str(x).strip() != '' else 0
)

# 删除无用列
cols_to_drop = []
for col in df4.columns:
    if df4[col].isna().all():
        cols_to_drop.append(col)

if cols_to_drop:
    df4 = df4.drop(columns=cols_to_drop)

# 分析缺失值
def analyze_missing_data(df):
    # 计算每列的缺失值数量
    missing_count = df.isnull().sum()
    total_count = len(df)
    valid_count = total_count - missing_count
    
    # 创建统计表
    stats_df = pd.DataFrame({
        '特征': missing_count.index,
        '总数据量': total_count,
        '有效数据量': valid_count,
        '缺失数据量': missing_count,
        '缺失比例(%)': (missing_count / total_count * 100).round(2)
    })
    
    return stats_df

# 绘制双柱状图
def plot_double_bar_chart(stats_df, total_count):
    plt.figure(figsize=(16, 10))
    
    # 设置位置和宽度
    x = np.arange(len(stats_df))
    width = 0.35
    
    # 创建双柱状图
    bars1 = plt.bar(x - width/2, stats_df['有效数据量'], width, 
                   label='有效数据量', color='lightblue', alpha=0.8)
    bars2 = plt.bar(x + width/2, stats_df['缺失数据量'], width, 
                   label='缺失数据量', color='lightcoral', alpha=0.8)
    
    # 设置图表标题和标签
    plt.title('女胎数据各特征数据完整性统计', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('特征', fontsize=14)
    plt.ylabel('数据数量', fontsize=14)
    plt.xticks(x, stats_df['特征'], rotation=90, fontsize=10)
    plt.legend(fontsize=12)
    
    # 添加网格
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 在柱子上添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', fontsize=8)
    
    # 添加总数据量参考线
    plt.axhline(y=total_count, color='gray', linestyle='--', alpha=0.7, 
                label=f'总数据量: {total_count}')
    
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig('女胎数据完整性统计.png', dpi=300, bbox_inches='tight')
    plt.show()

# 绘制缺失热力图
def plot_missing_heatmap(df):
    # 创建图形
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # 创建缺失值矩阵（1表示缺失，0表示存在）
    missing_matrix = df.isnull().astype(int)
    
    # 绘制热力图
    sns.heatmap(missing_matrix, 
                cmap=['#f0f0f0', '#ff6b6b'],
                cbar_kws={'label': '缺失状态', 'ticks': [0, 1]},
                ax=ax)
    
    # 设置标题和标签
    ax.set_title('女胎数据缺失值分布热力图\n(白色: 有数据, 红色: 缺失数据)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('特征', fontsize=12)
    ax.set_ylabel('样本索引', fontsize=12)
    
    # 设置坐标轴标签
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=10)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
    
    # 设置颜色条标签
    cbar = ax.collections[0].colorbar
    cbar.set_ticklabels(['有数据', '缺失数据'])
    
    plt.tight_layout()
    plt.savefig('女胎数据缺失值热力图.png', dpi=300, bbox_inches='tight')
    plt.show()

# 绘制缺失比例饼图
def plot_missing_pie_chart(stats_df):
    # 计算总体缺失情况
    total_missing = stats_df['缺失数据量'].sum()
    total_valid = stats_df['有效数据量'].sum()
    total_data = total_missing + total_valid
    
    # 创建饼图
    plt.figure(figsize=(10, 8))
    labels = ['有效数据', '缺失数据']
    sizes = [total_valid, total_missing]
    colors = ['#66b3ff', '#ff9999']
    explode = (0, 0.1)  # 突出显示缺失数据
    
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')
    plt.title('女胎数据总体缺失情况', fontsize=16, fontweight='bold', pad=20)
    plt.savefig('女胎数据总体缺失情况.png', dpi=300, bbox_inches='tight')
    plt.show()

# 主函数
def main():
    print("数据形状:", df4.shape)
    total_count = len(df4)
    print("总数据量:", total_count)
    
    # 分析缺失值
    stats_df = analyze_missing_data(df4)
    print("\n数据完整性统计:")
    print(stats_df)
    
    # 保存统计结果
    stats_df.to_excel('女胎数据完整性分析.xlsx', index=False)
    
    # 绘制图表
    plot_double_bar_chart(stats_df, total_count)
    plot_missing_heatmap(df4)
    plot_missing_pie_chart(stats_df)
    
    # 打印缺失最严重的特征
    print("\n缺失最严重的5个特征:")
    missing_top5 = stats_df.nlargest(5, '缺失比例(%)')
    for _, row in missing_top5.iterrows():
        print(f"{row['特征']}: {row['缺失比例(%)']}% 缺失")

if __name__ == "__main__":
    main()