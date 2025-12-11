import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.family'] = 'SimHei'

##################################################
#
#       1. RENAME COLUMNS
#
##################################################
def rename_columns():
    # 从Excel文件加载数据集
    age_data = pd.read_excel('data/age.xlsx')
    strength_data = pd.read_excel('data/strength.xlsx')
    element_data = pd.read_excel('data/element.xlsx')

    # 统一列名规范
    age_data.rename(columns={'No.': 'number'}, inplace=True)
    strength_data.rename(columns={'serial_number': 'number'}, inplace=True)

    # 输出处理后的列名结构
    print("Age data columns:", age_data.columns)
    print("Strength data columns:", strength_data.columns)
    print("Element data columns:", element_data.columns)

    # 导出处理后的数据文件
    age_data.to_excel('data/age_modified.xlsx', index=False)
    strength_data.to_excel('data/strength_modified.xlsx', index=False)
    
    return age_data, strength_data, element_data

    
##################################################
#
#       2. MERGE TABLES
#
##################################################

def merge_tables():
    # 读取已处理的数据文件
    age_df = pd.read_excel('data/age_modified.xlsx')
    strength_df = pd.read_excel('data/strength_modified.xlsx')
    element_df = pd.read_excel('data/element.xlsx')

    # 执行数据合并操作,采用左连接保留所有元素数据
    temp_df = element_df.merge(age_df, on='number', how='left')
    integrated_df = temp_df.merge(strength_df, on='number', how='left')

    # 输出合并结果
    print(integrated_df)

    # 导出整合数据
    integrated_df.to_excel('data/integrated_concrete_data.xlsx', index=False)

def visualize_scatter_plot(df, X_feature, Y_feature):
    # 验证必需列是否存在
    if X_feature not in df.columns or Y_feature not in df.columns:
        print("数据框中未找到所需列。")
        return

    # 提取绘图所需数据并清除空值
    plot_data = df[['number', X_feature, Y_feature]].dropna()

    # 创建散点图画布
    plt.figure(figsize=(10, 6))

    # 绘制带回归线的散点图
    sns.regplot(x=X_feature, y=Y_feature, data=plot_data)

    # 设置图表标题和坐标轴
    plt.title(f'{X_feature} 与 {Y_feature} 关系散点图')
    plt.xlabel(X_feature)
    plt.ylabel(Y_feature)

    # 展示图表
    plt.show()

def visualize_avg_bar_plot(df, X_feature, Y_feature):

    if X_feature not in df.columns or Y_feature not in df.columns:
        print("数据框中未找到所需列。")
        return

    # 分组计算平均值
    avg_by_group = df.groupby(X_feature)[Y_feature].mean()
    # 重置索引便于绘图
    avg_data = avg_by_group.reset_index()

    # 绘制柱状图
    avg_data.plot(kind='bar', x=X_feature, y=Y_feature, legend=False)

    # 配置图表样式
    plt.title(f'{X_feature} 分组的平均 {Y_feature}')
    plt.xlabel(X_feature)
    plt.ylabel(Y_feature)

    # 添加网格线
    plt.grid(True, linestyle=':', alpha=0.7)

    # 展示图表
    plt.show()


import re
def remove_brackets_and_contents(text, brackets='()'):
    # 参数类型检查
    if not isinstance(text, str):
        raise ValueError("输入必须为字符串类型。")

    # 处理空字符串情况
    if not text:
        return text

    # 构建正则表达式匹配模式
    open_char = re.escape(brackets[0])
    close_char = re.escape(brackets[1])
    regex_pattern = r'{0}[^{0}{1}\n\r]*{1}'.format(open_char, close_char)

    # 执行替换操作
    cleaned_text = re.sub(regex_pattern, '', text)

    # 输出处理信息
    if cleaned_text == text:
        print("字符串中未发现括号内容。")

    return cleaned_text

def visualize_heatmap(df):
    col_names = df.columns.tolist()
    # 移除列名中的单位信息
    for col in col_names:
        cleaned_col = remove_brackets_and_contents(col, '()')
        df.rename(columns={col: cleaned_col}, inplace=True)

    # 生成相关系数矩阵
    correlation_mat = df.corr()

    # 创建热力图
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_mat, annot=True, fmt=".2f", cmap='coolwarm', cbar=True)

    # 添加图表标题
    plt.title('数据相关性热力图')

    # 显示结果
    plt.show()

if __name__ == '__main__':
    rename_columns()
    merge_tables()

    final_df = pd.read_excel('data/integrated_concrete_data.xlsx')

    visualize_scatter_plot(final_df, 'Superplasticizer (component 5)(kg in a m^3 mixture)', 
                          'Fly Ash (component 3)(kg in a m^3 mixture)')
    visualize_avg_bar_plot(final_df, 'Age (day)', 
                          'Cement (component 1)(kg in a m^3 mixture)')

    visualize_heatmap(final_df)