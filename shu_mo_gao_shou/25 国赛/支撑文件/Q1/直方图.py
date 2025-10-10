import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import stats

def analyze_columns(file_path, columns):
    try:
        # 读取Excel文件
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except:
                try:
                    df = pd.read_csv(file_path, encoding='gbk')
                except:
                    df = pd.read_csv(file_path, encoding='latin1')
        else:
            print("错误: 不支持的文件格式。请使用Excel(.xlsx/.xls)或CSV(.csv)文件")
            return

        # 检查列是否存在
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            print(f"警告: 以下列在文件中不存在: {', '.join(missing_cols)}")
            columns = [col for col in columns if col in df.columns]

        if len(columns) == 0:
            print("错误: 没有有效的列名")
            return

        data = df[columns].dropna()
        stats_df = pd.DataFrame(index=columns)

        # 计算各项统计指标
        stats_df['最小值'] = data.min()
        stats_df['最大值'] = data.max()
        stats_df['均值'] = data.mean()
        stats_df['中位数'] = data.median()
        stats_df['标准差'] = data.std()
        stats_df['偏度'] = data.skew()
        stats_df['峰度'] = data.kurtosis()
        stats_df['样本量'] = data.count()

        # 正态性检验结果
        shapiro_results = []
        for col in columns:
            _, p_value = stats.shapiro(data[col])
            shapiro_results.append(p_value)

        stats_df['Shapiro-Wilk p值'] = shapiro_results
        stats_df['正态分布'] = stats_df['Shapiro-Wilk p值'] > 0.05

        # 文件所在目录
        file_dir = os.path.dirname(file_path)
        stats_file = os.path.join(file_dir, '统计指标汇总.xlsx')

        # 保存统计指标表格
        stats_df.to_excel(stats_file)
        print(f"统计指标已保存为: {stats_file}")

        # 绘制直方图
        plot_histograms(data, file_dir)

        return stats_df

    except Exception as e:
        print(f"出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def plot_histograms(data, save_dir):
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'SimSun']
    plt.rcParams['axes.unicode_minus'] = False
    try:
        columns = data.columns
        n = len(columns)
        ncols = 4
        nrows = int(np.ceil(n / ncols))
        fig_height = 4 * nrows
        fig, axes = plt.subplots(nrows, ncols, figsize=(16, fig_height))
        fig.suptitle('变量分布直方图', fontsize=16, y=0.98)
        if nrows == 1:
            axes = axes.reshape(1, -1)

        for i, col in enumerate(columns):
            row = i // ncols
            col_idx = i % ncols
            ax = axes[row, col_idx]

            col_data = data[col].dropna()

            ax.hist(col_data, bins=20, color='skyblue', edgecolor='black', alpha=0.7)

            ax.set_title(f'{col}分布', fontsize=12)
            ax.set_xlabel(col, fontsize=10)
            ax.set_xlim(col_data.min(), col_data.max())  # 设置x轴范围
            ax.set_ylabel('频数', fontsize=10)
            ax.grid(axis='y', alpha=0.3)

            mean_val = col_data.mean()
            median_val = col_data.median()

            ax.axvline(mean_val, color='red', linestyle='--', linewidth=1, label=f'均值: {mean_val:.2f}')
            ax.axvline(median_val, color='green', linestyle='-', linewidth=1, label=f'中位数: {median_val:.2f}')

            ax.legend(fontsize=8)

        for i in range(len(columns), nrows * ncols):
            row = i // ncols
            col_idx = i % ncols
            axes[row, col_idx].set_visible(False)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.subplots_adjust(hspace=0.4, wspace=0.3)

        hist_file = os.path.join(save_dir, '变量分布直方图.png')
        plt.savefig(hist_file, dpi=300, bbox_inches='tight')
        plt.show()

        print(f"直方图已保存为: {hist_file}")

    except Exception as e:
        print(f"绘制直方图时发生错误: {str(e)}")

if __name__ == "__main__":
    file_path = "D:\\国赛\\CUMCM2025Problems\\C题\\问题一\\男胎怀孕检测数据(2).csv"
    selected_cols = [
        "年龄", "孕妇BMI", "原始读段数", "在参考基因组上比对的比例",
        "重复读段的比例",  "GC含量", "Y染色体的Z值",
        "Y染色体浓度", "X染色体浓度", "被过滤掉读段数的比例", "孕周天数"
    ]

    stats_df = analyze_columns(file_path, selected_cols)

    if stats_df is not None:
        print("\n统计指标汇总:")
        print(stats_df)

        stats_csv = os.path.join(os.path.dirname(file_path), '统计指标汇总.csv')
        stats_df.to_csv(stats_csv)
        print("统计指标已保存")