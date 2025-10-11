import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# 设置中文字体和样式
plt.rcParams['font.family'] = 'Kaiti'  # 使用更通用的字体
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

def wait_for_user():
    """等待用户按键继续"""
    input("\n按 Enter 键继续...")
    plt.close('all')  # 关闭所有图表

def load_and_explore_data(filename):
    """加载数据并进行基本探索"""
    df = pd.read_csv(f'archive/{filename}.csv')
    
    print("=" * 60)
    print("数据基本信息")
    print("=" * 60)
    print(f"数据形状: {df.shape}")
    print(f"学生数量: {len(df)}")
    print("\n数据列名:")
    print(df.columns.tolist())
    
    print("\n数据前5行:")
    print(df.head())
    
    print("\n数据类型:")
    print(df.dtypes)
    
    print("\n缺失值统计:")
    print(df.isnull().sum())
    
    print("\n数据描述统计:")
    print(df.describe())
    
    return df

def plot_target_distribution(df):
    """绘制目标变量分布"""
    print("\n正在绘制目标变量分布图表...")
    
    # 图表1: 考试成绩分布
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.hist(df['exam_score'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    plt.axvline(df['exam_score'].mean(), color='red', linestyle='--', label=f'均值: {df["exam_score"].mean():.2f}')
    plt.axvline(df['exam_score'].median(), color='green', linestyle='--', label=f'中位数: {df["exam_score"].median():.2f}')
    plt.xlabel('考试成绩')
    plt.ylabel('频数')
    plt.title('考试成绩分布')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 2)
    plt.boxplot(df['exam_score'])
    plt.ylabel('考试成绩')
    plt.title('考试成绩箱线图')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 3)
    sns.kdeplot(df['exam_score'], fill=True, alpha=0.7)
    plt.xlabel('考试成绩')
    plt.ylabel('密度')
    plt.title('考试成绩核密度估计')
    
    plt.subplot(2, 2, 4)
    sorted_scores = np.sort(df['exam_score'])
    y_vals = np.arange(len(sorted_scores)) / float(len(sorted_scores))
    plt.plot(sorted_scores, y_vals, linewidth=2)
    plt.xlabel('考试成绩')
    plt.ylabel('累积概率')
    plt.title('考试成绩累积分布函数')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 图表2: 更多分布图表
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    stats.probplot(df['exam_score'], dist="norm", plot=plt)
    plt.title('考试成绩QQ图(正态性检验)')
    
    plt.subplot(1, 2, 2)
    sns.violinplot(y=df['exam_score'])
    plt.ylabel('考试成绩')
    plt.title('考试成绩小提琴图')
    
    plt.tight_layout()
    plt.show()
    
    # 输出统计信息
    print("\n考试成绩统计:")
    print(f"均值: {df['exam_score'].mean():.2f}")
    print(f"中位数: {df['exam_score'].median():.2f}")
    print(f"标准差: {df['exam_score'].std():.2f}")
    print(f"最小值: {df['exam_score'].min():.2f}")
    print(f"最大值: {df['exam_score'].max():.2f}")
    print(f"偏度: {df['exam_score'].skew():.2f}")
    print(f"峰度: {df['exam_score'].kurtosis():.2f}")

def plot_feature_distributions(df):
    """绘制各个特征的分布"""
    print("\n正在绘制特征分布图表...")
    
    features = ['hours_studied', 'sleep_hours', 'attendance_percent', 'previous_scores']
    
    # 分两个图表显示特征分布
    for i in range(0, len(features), 2):
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        current_features = features[i:i+2]
        
        for j, feature in enumerate(current_features):
            axes[j].hist(df[feature], bins=15, alpha=0.7, color=f'C{i+j}', edgecolor='black')
            axes[j].axvline(df[feature].mean(), color='red', linestyle='--', 
                           label=f'均值: {df[feature].mean():.2f}')
            axes[j].set_xlabel(feature.replace('_', ' ').title())
            axes[j].set_ylabel('频数')
            axes[j].set_title(f'{feature.replace("_", " ").title()} 分布')
            axes[j].legend()
            axes[j].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    # 特征统计信息
    print("\n特征统计信息:")
    for feature in features:
        print(f"\n{feature.replace('_', ' ').title()}:")
        print(f"  均值: {df[feature].mean():.2f}")
        print(f"  标准差: {df[feature].std():.2f}")
        print(f"  范围: {df[feature].min():.2f} - {df[feature].max():.2f}")

def plot_feature_vs_target(df):
    """绘制特征与目标变量的关系"""
    print("\n正在绘制特征与目标变量关系图表...")
    
    features = ['hours_studied', 'sleep_hours', 'attendance_percent', 'previous_scores']
    
    # 分两个图表显示
    for i in range(0, len(features), 2):
        plt.figure(figsize=(12, 5))
        current_features = features[i:i+2]
        
        for j, feature in enumerate(current_features, 1):
            plt.subplot(1, 2, j)
            
            # 散点图
            plt.scatter(df[feature], df['exam_score'], alpha=0.6, s=50)
            
            # 添加趋势线
            z = np.polyfit(df[feature], df['exam_score'], 1)
            p = np.poly1d(z)
            plt.plot(df[feature], p(df[feature]), "r--", linewidth=2, 
                    label=f'趋势线 (r = {df[feature].corr(df["exam_score"]):.3f})')
            
            plt.xlabel(feature.replace('_', ' ').title())
            plt.ylabel('考试成绩')
            plt.title(f'{feature.replace("_", " ").title()} vs 考试成绩')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    # 输出相关系数
    print("\n特征与考试成绩的相关系数:")
    for feature in features:
        corr = df[feature].corr(df['exam_score'])
        print(f"  {feature.replace('_', ' ').title()}: {corr:.3f}")

def plot_correlation_analysis(df):
    """绘制相关性分析"""
    print("\n正在绘制相关性分析图表...")
    
    # 选择数值列进行相关性分析
    numeric_cols = ['hours_studied', 'sleep_hours', 'attendance_percent', 'previous_scores', 'exam_score']
    corr_matrix = df[numeric_cols].corr()
    
    # 图表1: 相关性热力图
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                square=True, fmt='.3f', cbar_kws={"shrink": .8})
    plt.title('特征相关性热力图')
    plt.tight_layout()
    plt.show()
    
    # 图表2: 与考试成绩的相关性
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    exam_corr = corr_matrix['exam_score'].drop('exam_score')
    exam_corr.sort_values().plot(kind='barh', color='lightcoral')
    plt.axvline(0, color='black', linewidth=0.8)
    plt.xlabel('相关系数')
    plt.title('各特征与考试成绩的相关性')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    features = ['hours_studied', 'sleep_hours', 'attendance_percent', 'previous_scores']
    feature_corr_with_exam = [corr_matrix.loc[f, 'exam_score'] for f in features]
    plt.bar(features, feature_corr_with_exam, color=plt.cm.RdYlBu_r(np.array(feature_corr_with_exam)))
    plt.xticks(rotation=45)
    plt.ylabel('与考试成绩的相关系数')
    plt.title('特征对考试成绩的影响强度')
    
    plt.tight_layout()
    plt.show()
    
    # 输出相关性分析
    print("\n详细相关性分析:")
    print(corr_matrix)

def plot_multivariate_analysis(df):
    """多变量分析"""
    print("\n正在绘制多变量分析图表...")
    
    # 图表1: 学习时间 vs 睡眠时间
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(df['hours_studied'], df['sleep_hours'], 
                        c=df['exam_score'], cmap='viridis', alpha=0.7, s=60)
    plt.colorbar(scatter, label='考试成绩')
    plt.xlabel('学习时间')
    plt.ylabel('睡眠时间')
    plt.title('学习时间 vs 睡眠时间 (颜色:考试成绩)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # 图表2: 出勤率 vs 先前成绩
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(df['attendance_percent'], df['previous_scores'], 
                        c=df['exam_score'], cmap='plasma', alpha=0.7, s=60)
    plt.colorbar(scatter, label='考试成绩')
    plt.xlabel('出勤率')
    plt.ylabel('先前成绩')
    plt.title('出勤率 vs 先前成绩 (颜色:考试成绩)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # 图表3: 多变量编码图
    plt.figure(figsize=(10, 6))
    sizes = (df['hours_studied'] - df['hours_studied'].min()) / (df['hours_studied'].max() - df['hours_studied'].min()) * 100 + 10
    scatter = plt.scatter(df['previous_scores'], df['exam_score'], 
                        c=df['attendance_percent'], s=sizes, alpha=0.6, cmap='coolwarm')
    plt.colorbar(scatter, label='出勤率')
    plt.xlabel('先前成绩')
    plt.ylabel('考试成绩')
    plt.title('先前成绩 vs 考试成绩\n(颜色:出勤率, 大小:学习时间)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # 图表4: 分组箱线图
    plt.figure(figsize=(10, 6))
    df['study_group'] = pd.cut(df['hours_studied'], bins=5, labels=['很低', '较低', '中等', '较高', '很高'])
    sns.boxplot(data=df, x='study_group', y='exam_score')
    plt.xlabel('学习时间分组')
    plt.ylabel('考试成绩')
    plt.title('不同学习时间分组的考试成绩分布')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_outlier_analysis(df):
    """异常值分析"""
    print("\n正在绘制异常值分析图表...")
    
    features = ['hours_studied', 'sleep_hours', 'attendance_percent', 'previous_scores', 'exam_score']
    
    # 图表1: 箱线图
    plt.figure(figsize=(12, 6))
    df_melted = df[features].melt(var_name='特征', value_name='值')
    sns.boxplot(data=df_melted, x='特征', y='值')
    plt.xticks(rotation=45)
    plt.title('各特征箱线图（异常值检测）')
    plt.tight_layout()
    plt.show()
    
    # 图表2: 异常值统计
    plt.figure(figsize=(10, 6))
    z_scores = np.abs(stats.zscore(df[features]))
    outlier_counts = (z_scores > 3).sum(axis=0)
    plt.bar(features, outlier_counts, color='lightcoral')
    plt.xlabel('特征')
    plt.ylabel('异常值数量 (Z-score > 3)')
    plt.title('各特征的异常值数量')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    # 输出异常值信息
    print("\n异常值分析 (Z-score > 3):")
    for i, feature in enumerate(features):
        print(f"  {feature}: {outlier_counts[i]} 个异常值")

def generate_summary_report(df):
    """生成数据观测总结报告"""
    print("\n" + "=" * 60)
    print("数据观测总结报告")
    print("=" * 60)
    
    # 基本统计
    print(f"数据集大小: {df.shape[0]} 个样本, {df.shape[1]} 个特征")
    print(f"考试成绩范围: {df['exam_score'].min():.1f} - {df['exam_score'].max():.1f}")
    
    # 相关性总结
    corr_with_target = df.corr()['exam_score'].sort_values(ascending=False)
    strongest_positive = corr_with_target.index[1]  # 排除自身
    strongest_corr = corr_with_target.iloc[1]
    
    print(f"\n关键发现:")
    print(f"1. 与考试成绩最相关的特征: {strongest_positive} (r = {strongest_corr:.3f})")
    print(f"2. 学习时间平均: {df['hours_studied'].mean():.1f} 小时")
    print(f"3. 睡眠时间平均: {df['sleep_hours'].mean():.1f} 小时")
    print(f"4. 出勤率平均: {df['attendance_percent'].mean():.1f}%")
    print(f"5. 先前成绩平均: {df['previous_scores'].mean():.1f}")
    
    # 数据质量
    missing_values = df.isnull().sum().sum()
    print(f"\n数据质量:")
    print(f"缺失值总数: {missing_values}")
    print(f"数据完整性: {(1 - missing_values / (df.shape[0] * df.shape[1])) * 100:.1f}%")

def main():
    """主函数"""
    print("开始学生考试成绩数据可视化分析...")
    print("每个图表会单独显示，查看完毕后按 Enter 键继续下一个图表")
    
    # 加载数据
    df = load_and_explore_data('student_exam_scores')
    wait_for_user()
    
    # 目标变量分布分析
    print("\n正在分析目标变量分布...")
    plot_target_distribution(df)
    wait_for_user()
    
    # 特征分布分析
    print("\n正在分析特征分布...")
    plot_feature_distributions(df)
    wait_for_user()
    
    # 特征与目标变量关系
    print("\n正在分析特征与目标变量关系...")
    plot_feature_vs_target(df)
    wait_for_user()
    
    # 相关性分析
    print("\n正在进行相关性分析...")
    plot_correlation_analysis(df)
    wait_for_user()
    
    # 多变量分析
    print("\n正在进行多变量分析...")
    plot_multivariate_analysis(df)
    wait_for_user()
    
    # 异常值分析
    print("\n正在进行异常值分析...")
    plot_outlier_analysis(df)
    wait_for_user()
    
    # 生成总结报告
    generate_summary_report(df)
    
    print("\n" + "=" * 60)
    print("数据观测可视化完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
