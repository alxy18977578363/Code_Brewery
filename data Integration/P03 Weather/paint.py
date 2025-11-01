import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def visualize_static_weather(csv_file='上海天气_202509.csv'):
    """可视化静态网页爬取的天气数据（9月份温度变化）"""
    # 读取数据
    df = pd.read_csv(csv_file)
    
    # 数据预处理
    df['日期'] = df['日期'].str.split(' ').str[0]
    df['最高温'] = df['最高温'].str.replace('℃', '').astype(int)
    df['最低温'] = df['最低温'].str.replace('℃', '').astype(int)

    # 创建图形
    plt.figure(figsize=(14, 8))

    # 绘制温度曲线
    plt.plot(df['日期'], df['最高温'], marker='o', linewidth=2, markersize=6, 
             label='最高温', color='#FF6B6B', alpha=0.8)
    plt.plot(df['日期'], df['最低温'], marker='s', linewidth=2, markersize=6, 
             label='最低温', color='#4ECDC4', alpha=0.8)

    # 填充温度区域
    plt.fill_between(df['日期'], df['最高温'], df['最低温'], alpha=0.2, color='#FFE66D')

    # 设置图形属性
    plt.title('上海市2025年9月温度变化曲线图', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('温度 (℃)', fontsize=12)
    plt.legend(fontsize=11)
    plt.xticks(df['日期'][::3], rotation=45)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()

    # 显示图形
    plt.show()

    # 打印统计信息
    print(f"\n9月温度统计信息:")
    print(f"最高温平均: {df['最高温'].mean():.1f}℃")
    print(f"最低温平均: {df['最低温'].mean():.1f}℃")
    print(f"月最高温: {df['最高温'].max()}℃ (日期: {df.loc[df['最高温'].idxmax(), '日期']})")
    print(f"月最低温: {df['最低温'].min()}℃ (日期: {df.loc[df['最低温'].idxmin(), '日期']})")


def visualize_dynamic_weather(csv_file="上海逐小时天气预报.csv"):
    """可视化动态网页爬取的天气数据（逐小时温度变化）"""
    # 读取数据
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    # 数据预处理
    df['温度数值'] = df['温度'].str.extract('(\d+)').astype(float)
    
    # 创建图表
    plt.figure(figsize=(12, 6))
    
    # 绘制温度曲线
    plt.plot(df['时间'], df['温度数值'], marker='o', linewidth=2, 
             label='温度', color='#6A5ACD', markersize=5)
    
    # 设置图表属性
    plt.title('上海逐小时温度变化', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('时间', fontsize=12)
    plt.ylabel('温度 (°C)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=11)
    plt.tight_layout()
    
    # 显示图表
    plt.show()
    
def plot_provincial_capitals_temperature(csv_file='weather_data.csv', target_date='11月2日', 
                                      figsize=(16, 10), save_path=None):
    """
    绘制各省会城市指定日期的最高气温和最低气温柱形图
    
    参数:
    csv_file: str, CSV文件路径
    target_date: str, 目标日期，默认为'11月2日'
    figsize: tuple, 图表尺寸，默认为(16, 10)
    save_path: str, 图片保存路径，默认为None不保存
    
    返回:
    capital_df: DataFrame, 处理后的省会城市数据
    """
    
    # 定义省会城市列表
    provincial_capitals = {
        '北京': '北京',
        '天津': '天津',
        '河北': '石家庄',
        '山西': '太原',
        '内蒙古': '呼和浩特',
        '辽宁': '沈阳',
        '吉林': '长春',
        '黑龙江': '哈尔滨',
        '上海': '上海',
        '江苏': '南京',
        '浙江': '杭州',
        '安徽': '合肥',
        '福建': '福州',
        '江西': '南昌',
        '山东': '济南',
        '河南': '郑州',
        '湖北': '武汉',
        '湖南': '长沙',
        '广东': '广州',
        '广西': '南宁',
        '海南': '海口',
        '重庆': '重庆',
        '四川': '成都',
        '贵州': '贵阳',
        '云南': '昆明',
        '西藏': '拉萨',
        '陕西': '西安',
        '甘肃': '兰州',
        '青海': '西宁',
        '宁夏': '银川',
        '新疆': '乌鲁木齐',
        '香港': '香港'
    }
    
    # 读取数据
    try:
        df = pd.read_csv(csv_file)
        print(f"成功读取数据，共{len(df)}条记录")
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None
    
    # 筛选指定日期的数据
    date_data = df[df['日期'].str.contains(target_date, na=False)]
    print(f"找到{target_date}的数据{len(date_data)}条")
    
    # 提取省会城市数据
    capital_data = []
    for province, capital in provincial_capitals.items():
        capital_weather = date_data[
            (date_data['省份'] == province) & 
            (date_data['城市'] == capital)
        ]
        if not capital_weather.empty:
            capital_data.append(capital_weather.iloc[0])
        else:
            print(f"未找到{province}{capital}的数据")
    
    # 创建省会城市数据框
    capital_df = pd.DataFrame(capital_data)
    
    if capital_df.empty:
        print("未找到任何省会城市数据")
        return None
    
    # 处理气温数据（转换为数值）
    def parse_temperature(temp_str):
        if pd.isna(temp_str) or temp_str == '' or temp_str == '--':
            return np.nan
        try:
            # 移除可能的特殊字符并转换为整数
            return int(str(temp_str).replace('°C', '').strip())
        except:
            return np.nan
    
    capital_df['最高气温_数值'] = capital_df['白天气温'].apply(parse_temperature)
    capital_df['最低气温_数值'] = capital_df['夜间气温'].apply(parse_temperature)
    
    # 移除气温为NaN的数据
    capital_df = capital_df.dropna(subset=['最高气温_数值', '最低气温_数值'])
    
    if capital_df.empty:
        print("所有数据都包含无效的气温值")
        return None
    
    # 按最高气温排序
    capital_df = capital_df.sort_values('最高气温_数值', ascending=False)
    
    # 绘制柱形图
    fig, ax = plt.subplots(figsize=figsize)
    
    # 设置柱形图的位置和宽度
    x = np.arange(len(capital_df))
    width = 0.35
    
    # 绘制最高气温和最低气温柱形图
    bars1 = ax.bar(x - width/2, capital_df['最高气温_数值'], width, label='最高气温', color='#FF6B6B', alpha=0.8)
    bars2 = ax.bar(x + width/2, capital_df['最低气温_数值'], width, label='最低气温', color='#4ECDC4', alpha=0.8)
    
    # 设置图表标题和标签
    ax.set_xlabel('城市', fontsize=12)
    ax.set_ylabel('气温 (°C)', fontsize=12)
    ax.set_title(f'各省会城市{target_date}最高气温和最低气温对比', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{row['省份']}\n{row['城市']}" for _, row in capital_df.iterrows()], 
                      rotation=45, ha='right', fontsize=10)
    
    # 添加图例
    ax.legend(fontsize=12)
    
    # 在柱子上添加数值标签
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}°C',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    add_value_labels(bars1)
    add_value_labels(bars2)
    
    # 添加网格线
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存到: {save_path}")
    
    # 显示图表
    plt.show()
    
    # 打印统计信息
    print_statistics(capital_df, target_date)
    
    return capital_df

def print_statistics(capital_df, target_date):
    """打印统计信息"""
    print(f"\n{'='*50}")
    print(f"{target_date}省会城市气温统计")
    print(f"{'='*50}")
    print(f"共包含 {len(capital_df)} 个省会城市的数据")
    print(f"\n气温统计:")
    print(f"最高气温范围: {capital_df['最高气温_数值'].min()}°C - {capital_df['最高气温_数值'].max()}°C")
    print(f"最低气温范围: {capital_df['最低气温_数值'].min()}°C - {capital_df['最低气温_数值'].max()}°C")
    print(f"平均最高气温: {capital_df['最高气温_数值'].mean():.1f}°C")
    print(f"平均最低气温: {capital_df['最低气温_数值'].mean():.1f}°C")
    print(f"平均昼夜温差: {(capital_df['最高气温_数值'] - capital_df['最低气温_数值']).mean():.1f}°C")
    
    # 显示前5个最热和最冷的城市
    print(f"\n最高气温前5名:")
    top5_hot = capital_df.nlargest(5, '最高气温_数值')[['省份', '城市', '最高气温_数值']]
    for i, (_, row) in enumerate(top5_hot.iterrows(), 1):
        print(f"  {i}. {row['城市']}({row['省份']}): {row['最高气温_数值']}°C")
    
    print(f"\n最低气温前5名:")
    top5_cold = capital_df.nsmallest(5, '最低气温_数值')[['省份', '城市', '最低气温_数值']]
    for i, (_, row) in enumerate(top5_cold.iterrows(), 1):
        print(f"  {i}. {row['城市']}({row['省份']}): {row['最低气温_数值']}°C")
    
    # 昼夜温差最大的城市
    capital_df['昼夜温差'] = capital_df['最高气温_数值'] - capital_df['最低气温_数值']
    print(f"\n昼夜温差前5名:")
    top5_diff = capital_df.nlargest(5, '昼夜温差')[['省份', '城市', '最高气温_数值', '最低气温_数值', '昼夜温差']]
    for i, (_, row) in enumerate(top5_diff.iterrows(), 1):
        print(f"  {i}. {row['城市']}({row['省份']}): {row['昼夜温差']}°C ({row['最高气温_数值']}°C / {row['最低气温_数值']}°C)")


if __name__ == "__main__":
    """主函数"""
    try:
        # 可视化静态网页数据
        print("正在可视化静态网页天气数据...")
        visualize_static_weather('上海天气_202509.csv')
        
        # 可视化动态网页数据
        print("\n正在可视化动态网页天气数据...")
        visualize_dynamic_weather('上海逐小时天气预报.csv')
        
        print("\n所有可视化完成！")
        
    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
    except Exception as e:
        print(f"可视化过程中出现错误: {e}")

    result_df = plot_provincial_capitals_temperature()
