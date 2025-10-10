import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

#绘制列与多个其他列的散点图
def plot_scatter_with_fixed_column(file_path, fixed_column, compare_columns):

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
            print("文件有误")
            return

        # 检查列是否存在
        all_columns = [fixed_column] + compare_columns
        missing_cols = [col for col in all_columns if col not in df.columns]
        if missing_cols:
            print(f"以下列在文件中不存在: {', '.join(missing_cols)}")
            # 更新有效列
            fixed_column = fixed_column if fixed_column in df.columns else None
            compare_columns = [col for col in compare_columns if col in df.columns]

        data = df[all_columns].dropna()
        file_dir = os.path.dirname(file_path)
        # 绘制散点图
        plot_scatter_grid(data, fixed_column, compare_columns, file_dir)

        return data

    except Exception as e:    #报错提醒
        print(f"出错：{str(e)}")
        import traceback
        traceback.print_exc()
        return None

    #绘制散点图网格
def plot_scatter_grid(data, fixed_column, compare_columns, save_dir):

    try:
        n = len(compare_columns)

        ncols = 4  #每行展示4个图
        nrows = int(np.ceil(n / ncols))

        fig_height = 5 * nrows
        fig, axes = plt.subplots(nrows, ncols, figsize=(16, fig_height))
        fig.suptitle(f'{fixed_column}与其他变量的关系', fontsize=16, y=0.98)

        if nrows == 1:
            axes = axes.reshape(1, -1)

        for i, col in enumerate(compare_columns):
            # 计算子图位置
            row = i // ncols
            col_idx = i % ncols
            ax = axes[row, col_idx]

            # 绘制散点图
            sns.scatterplot(x=col, y=fixed_column, data=data, ax=ax, alpha=0.6)

            # 添加趋势线
            sns.regplot(x=col, y=fixed_column, data=data, ax=ax,
                        scatter=False, color='red', line_kws={'alpha': 0.7})

            # 添加标题和标签
            ax.set_title(f'{fixed_column} vs {col}', fontsize=12)
            ax.set_xlabel(col, fontsize=10)
            ax.set_ylabel(fixed_column, fontsize=10)

            # 计算相关系数
            corr = data[col].corr(data[fixed_column])
            ax.text(0.05, 0.95, f'相关系数: {corr:.2f}',
                    transform=ax.transAxes, fontsize=10,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            # 添加网格线
            ax.grid(True, alpha=0.3)

        for i in range(len(compare_columns), nrows * ncols):
            row = i // ncols
            col_idx = i % ncols
            axes[row, col_idx].set_visible(False)


        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.subplots_adjust(hspace=0.4, wspace=0.3)

        # 保存图片
        scatter_file = os.path.join(save_dir, f'{fixed_column}_与其他变量关系.png')
        plt.savefig(scatter_file, dpi=300, bbox_inches='tight')
        plt.show()

        print(f"散点图已保存")

    except Exception as e:
        print(f"出错: {str(e)}")



if __name__ == "__main__":
    file_path = "D:\\国赛\\CUMCM2025Problems\\C题\\问题一\\男胎怀孕检测数据(2).csv"
    fixed_column = "Y染色体浓度" # 固定列（作为y轴）
    compare_columns = [
        "年龄", "孕妇BMI", "原始读段数", "在参考基因组上比对的比例",
        "重复读段的比例", "GC含量", "Y染色体的Z值",
         "X染色体浓度", "被过滤掉读段数的比例","孕周天数"
    ]

    # 绘制散点图
    data = plot_scatter_with_fixed_column(file_path, fixed_column, compare_columns)
    plt.show()
