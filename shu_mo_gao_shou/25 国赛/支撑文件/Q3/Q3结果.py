import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings


# 设置中文字体
warnings.filterwarnings('ignore')
plt.rcParams['font.family'] = 'Kaiti'
plt.rcParams['axes.unicode_minus'] = False # 显示负号

# 数据
df = pd.read_csv('Q3/q3_optimization_results.csv')

# 创建可视化图表 - 2x2布局
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('各BMI分组最佳NIPT检测时间分析', fontsize=18, fontweight='bold', y=0.98)

# 1. 最佳检测时间（孕周）柱状图
bars = ax1.bar(df['bmi_group'], df['optimal_detection_time'], 
               color=['#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.8, edgecolor='black', linewidth=1)
ax1.set_title('最佳检测时间（孕周）', fontsize=14, fontweight='bold', pad=20)
ax1.set_ylabel('孕周', fontsize=12)
ax1.set_xlabel('BMI分组', fontsize=12)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# 在柱子上添加数值标签
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
             f'{height:.2f}周', ha='center', va='bottom', fontweight='bold', fontsize=10)

# 2. 最佳检测时间（天数）折线图
line = ax2.plot(df['bmi_group'], df['optimal_detection_time_days'], 
                marker='o', linewidth=3, markersize=10, color='#FF9F1C', 
                markerfacecolor='white', markeredgewidth=2, markeredgecolor='#FF9F1C')
ax2.set_title('最佳检测时间（天数）', fontsize=14, fontweight='bold', pad=20)
ax2.set_ylabel('天数', fontsize=12)
ax2.set_xlabel('BMI分组', fontsize=12)
ax2.grid(alpha=0.3, linestyle='--')

# 在折线点上添加数值标签
for i, (group, days) in enumerate(zip(df['bmi_group'], df['optimal_detection_time_days'])):
    ax2.text(i, days + 1.5, f'{days:.1f}天', ha='center', va='bottom', 
             fontweight='bold', fontsize=10, bbox=dict(boxstyle="round,pad=0.2", 
             facecolor="yellow", alpha=0.7))

# 3. 样本数量饼图
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
wedges, texts, autotexts = ax3.pie(df['sample_count'], labels=df['bmi_group'], 
                                   autopct='%1.1f%%', colors=colors, startangle=90,
                                   textprops={'fontsize': 11, 'fontweight': 'bold'})
ax3.set_title('各分组样本数量分布', fontsize=14, fontweight='bold', pad=20)

# 4. BMI与检测时间关系折线图（替换原来的散点图）
ax4.plot(df['bmi_group'], df['optimal_detection_time'], 's-', linewidth=3, 
         markersize=10, color='#E74C3C', markerfacecolor='white', 
         markeredgewidth=2, markeredgecolor='#E74C3C')
ax4.set_title('BMI分组与最佳检测时间关系', fontsize=14, fontweight='bold', pad=20)
ax4.set_xlabel('BMI分组', fontsize=12)
ax4.set_ylabel('最佳检测时间（孕周）', fontsize=12)
ax4.grid(alpha=0.3, linestyle='--')

# 添加数值标注
for i, (group, time) in enumerate(zip(df['bmi_group'], df['optimal_detection_time'])):
    ax4.annotate(f'{time:.2f}周', (i, time), xytext=(0, 12), 
                textcoords='offset points', ha='center', fontweight='bold',
                fontsize=10, bbox=dict(boxstyle="round,pad=0.3", 
                facecolor="lightyellow", alpha=0.8))

# 调整布局
plt.tight_layout()
plt.subplots_adjust(top=0.93, hspace=0.3, wspace=0.25)

# 添加总结文字框
summary_text = (
    '📊 分析结论：\n'
    '• 高BMI组需要最晚检测（18.48周），比低BMI组晚2.64周\n'
    '• 检测时间与BMI呈明显正相关关系\n'
    '• 中BMI组样本数量最多（117例），占总样本46.3%\n'
    '• 所有分组均采用多目标优化策略，确保风险最小化\n'
    '• 最小时间间隔设置为6天，保证临床可行性'
)

plt.figtext(0.1, 0.02, summary_text, fontsize=11, style='italic', 
           bbox=dict(boxstyle="round,pad=0.8", facecolor="lightgray", 
           edgecolor="gray", alpha=0.8))

# 在图表下方添加数据表格
col_labels = ['BMI分组', '最佳检测时间', '检测天数', '样本数量', '平均BMI', 'BMI范围']
table_data = []

for i in range(len(df)):
    table_data.append([
        f'组{int(df["bmi_group"].iloc[i])}',
        f"{df['optimal_detection_time'].iloc[i]:.2f}周",
        f"{df['optimal_detection_time_days'].iloc[i]:.1f}天",
        f"{int(df['sample_count'].iloc[i])}例",
        f"{df['mean_bmi'].iloc[i]:.2f}",
        df['bmi_range'].iloc[i]
    ])

# 在图表外单独创建表格
plt.figure(figsize=(10, 3))
plt.axis('off')
table = plt.table(cellText=table_data, colLabels=col_labels, 
                 cellLoc='center', loc='center', 
                 bbox=[0, 0, 1, 1])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)
plt.title('优化结果数据汇总', fontsize=12, fontweight='bold', pad=20)
plt.tight_layout()

plt.show()

# 显示关键统计数据
print("=" * 60)
print("📈 关键统计信息：")
print("=" * 60)
print(f"总样本数：{df['sample_count'].sum()}例")
print(f"平均检测时间：{df['optimal_detection_time'].mean():.2f}周")
print(f"检测时间范围：{df['optimal_detection_time'].min():.2f} - {df['optimal_detection_time'].max():.2f}周")
print(f"时间差异：高BMI组比低BMI组晚{df['optimal_detection_time'].iloc[2] - df['optimal_detection_time'].iloc[0]:.2f}周")


# 后面是敏感性分析

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class SensitivityVisualizer:
    """敏感性分析可视化类"""
    
    def __init__(self, sensitivity_data):
        """
        初始化可视化器
        
        参数:
            sensitivity_data: 敏感性分析结果的DataFrame或文件路径
        """
        if isinstance(sensitivity_data, str):
            self.data = pd.read_csv(sensitivity_data)
        else:
            self.data = sensitivity_data.copy()
        
        # 添加BMI类别标签
        bmi_labels = {0: '低BMI组', 1: '中BMI组', 2: '高BMI组'}
        self.data['bmi_group_label'] = self.data['bmi_group'].map(bmi_labels)
    
    def plot_parameter_sensitivity(self, save_path=None):
        """绘制参数敏感性分析图"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        parameters = self.data['parameter'].unique()
        colors = sns.color_palette("Set2", 3)
        
        for i, param in enumerate(parameters):
            if i >= 4:
                break
                
            param_data = self.data[self.data['parameter'] == param]
            
            for j, bmi_group in enumerate([0, 1, 2]):
                group_data = param_data[param_data['bmi_group'] == bmi_group]
                axes[i].plot(group_data['parameter_value'], 
                           group_data['optimal_detection_time_weeks'],
                           'o-', label=f'BMI组 {bmi_group}', color=colors[j],
                           markersize=8, linewidth=2)
            
            axes[i].set_xlabel(f'{param} 参数值', fontsize=12)
            axes[i].set_ylabel('最优检测时机 (孕周)', fontsize=12)
            axes[i].set_title(f'{param} 参数敏感性分析', fontsize=14, fontweight='bold')
            axes[i].legend()
            axes[i].grid(True, alpha=0.3)
        
        # 移除多余的子图
        for i in range(len(parameters), 4):
            fig.delaxes(axes[i])
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    
    
    
    def create_summary_table(self):
        """创建敏感性分析摘要表"""
        summary_data = []
        
        for param in self.data['parameter'].unique():
            for bmi_group in sorted(self.data['bmi_group'].unique()):
                param_data = self.data[(self.data['parameter'] == param) & 
                                     (self.data['bmi_group'] == bmi_group)]
                
                if not param_data.empty:
                    min_time = param_data['optimal_detection_time_weeks'].min()
                    max_time = param_data['optimal_detection_time_weeks'].max()
                    range_time = max_time - min_time
                    mean_time = param_data['optimal_detection_time_weeks'].mean()
                    
                    summary_data.append({
                        '参数': param,
                        'BMI组': bmi_group,
                        '最小检测周数': f'{min_time:.1f}',
                        '最大检测周数': f'{max_time:.1f}',
                        '变化范围': f'{range_time:.1f}',
                        '平均检测周数': f'{mean_time:.1f}',
                        '敏感性等级': '高' if range_time > 1.0 else ('中' if range_time > 0.5 else '低')
                    })
        
        return pd.DataFrame(summary_data)
    
    def generate_all_visualizations(self, output_dir='./Q3/sensitivity_plots'):
        """生成所有可视化图表"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("生成敏感性分析可视化图表...")
        
        # 生成各图表
        self.plot_parameter_sensitivity(save_path=f'{output_dir}/parameter_sensitivity.png')
        
        
        # 生成摘要表
        summary_table = self.create_summary_table()
        summary_table.to_csv(f'{output_dir}/sensitivity_summary.csv', 
                           index=False, encoding='utf-8-sig')
        
        print("可视化图表生成完成！")
        return summary_table


# 加载数据
visualizer = SensitivityVisualizer('Q3/sensitivity_analysis_results.csv')
    
# 生成所有可视化
summary = visualizer.generate_all_visualizations()
    
# 显示摘要表
print("\n=== 敏感性分析摘要 ===")
print(summary.to_string(index=False))