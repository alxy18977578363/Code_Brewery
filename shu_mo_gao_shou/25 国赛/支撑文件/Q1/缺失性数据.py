import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


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
    plt.title('各特征数据完整性统计', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('特征', fontsize=14)
    plt.ylabel('数据数量', fontsize=14)
    plt.xticks(x, stats_df['特征'], rotation=90, fontsize=10)
    plt.legend(fontsize=12)
    
    # 添加网格
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 在柱子上添加数值标签（只在有数值的地方显示）
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
    return plt

# 绘制缺失热力图
def plot_missing_heatmap(df):
    # 创建图形
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # 创建缺失值矩阵（1表示缺失，0表示存在）
    missing_matrix = df.isnull().astype(int)
    
    # 绘制热力图
    sns.heatmap(missing_matrix, 
                cmap=['#f0f0f0', '#ff6b6b'],  # 更柔和的颜色
                cbar_kws={'label': '缺失状态', 'ticks': [0, 1]},
                ax=ax)
    
    # 设置标题和标签
    ax.set_title('缺失值分布热力图\n(白色: 有数据, 红色: 缺失数据)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('特征', fontsize=12)
    ax.set_ylabel('样本索引', fontsize=12)
    
    # 设置坐标轴标签
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=10)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
    
    # 设置颜色条标签
    cbar = ax.collections[0].colorbar
    cbar.set_ticklabels(['有数据', '缺失数据'])
    
    # 添加网格线（可选）
    ax.grid(False)
    
    plt.tight_layout()
    return plt


# 新增：绘制异常值箱线图（基于3σ定理）
def plot_outlier_boxplot(df):
    # 选择数值型列
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # 计算异常值阈值（基于3σ定理）
    outlier_stats = []
    for col in numeric_cols:
        data = df[col].dropna()
        if len(data) > 0:
            mean = data.mean()
            std = data.std()
            upper_bound = mean + 3 * std
            lower_bound = mean - 3 * std
            
            # 识别异常值
            outliers = data[(data > upper_bound) | (data < lower_bound)]
            outlier_count = len(outliers)
            outlier_percentage = round(outlier_count / len(data) * 100, 2)
            
            outlier_stats.append({
                '特征': col,
                '异常值数量': outlier_count,
                '异常值比例(%)': outlier_percentage,
                '上界(μ+3σ)': upper_bound,
                '下界(μ-3σ)': lower_bound
            })
    
    # 创建异常值统计表
    outlier_stats_df = pd.DataFrame(outlier_stats)
    
    # 绘制箱线图
    plt.figure(figsize=(16, 10))
    
    # 选择异常值比例最高的前20个特征进行可视化
    if len(outlier_stats_df) > 20:
        display_cols = outlier_stats_df.nlargest(20, '异常值数量')['特征'].tolist()
    else:
        display_cols = numeric_cols
    
    # 创建箱线图
    boxplot_data = df[display_cols].select_dtypes(include=[np.number])
    sns.boxplot(data=boxplot_data, orient='h')
    
    # 设置标题和标签
    plt.title('基于3σ定理的异常值检测箱线图', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('数值范围', fontsize=14)
    plt.ylabel('特征', fontsize=14)
    
    # 添加网格
    plt.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    return plt, outlier_stats_df

# 主函数
def main():
    # 读取数据（这里使用示例数据，你可以替换为实际读取Excel的代码）
    df = pd.read_excel('附件.xlsx', sheet_name=0)
    
    print("数据形状:", df.shape)
    total_count = len(df)
    print("总数据量:", total_count)
    
    # 分析缺失值
    stats_df = analyze_missing_data(df)
    print("\n数据完整性统计:")
    print(stats_df)
    
    # 绘制双柱状图
    double_bar_plot = plot_double_bar_chart(stats_df, total_count)
    double_bar_plot.savefig('image/data_completeness_bar.png', dpi=300, bbox_inches='tight')
    double_bar_plot.show()
    
    # 绘制热力图
    heatmap_plot = plot_missing_heatmap(df)
    heatmap_plot.savefig('image/missing_values_heatmap.png', dpi=300, bbox_inches='tight')
    heatmap_plot.show()
    
    # 新增：绘制异常值箱线图
    boxplot_plot, outlier_stats_df = plot_outlier_boxplot(df)
    boxplot_plot.savefig('image/outlier_boxplot.png', dpi=300, bbox_inches='tight')
    boxplot_plot.show()
    
    # 保存统计结果到Excel
    print("\n分析结果已保存到 data_completeness_analysis.xlsx")
    
    # 保存异常值统计结果
    outlier_stats_df.to_excel('outlier_analysis.xlsx', index=False)
    print("异常值分析结果已保存到 outlier_analysis.xlsx")


if __name__ == "__main__":
    main()