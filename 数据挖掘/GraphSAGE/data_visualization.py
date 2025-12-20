import os
# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import networkx as nx
from torch_geometric.utils import to_networkx
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class DataVisualizer:
    def __init__(self, data_path='data/phase1_gdata.npz'):
        """初始化数据可视化器"""
        self.data_path = data_path
        self.data = None
        self.load_data()

    def load_data(self):
        """加载图数据"""
        print("正在加载数据...")
        self.data = np.load(self.data_path)

        # 数据预处理
        self.data['x'][self.data['x'] == -1] = 0

        print(f"数据加载完成！")
        print(f"节点数量: {self.data['x'].shape[0]}")
        print(f"特征维度: {self.data['x'].shape[1]}")
        print(f"边数量: {self.data['edge_index'].shape[0]}")

    def get_basic_info(self):
        """获取数据集基本信息"""
        info = {}
        info['节点总数'] = self.data['x'].shape[0]
        info['特征维度'] = self.data['x'].shape[1]
        info['边总数'] = self.data['edge_index'].shape[0]
        info['训练样本数'] = len(self.data['train_mask'])
        info['测试样本数'] = len(self.data['test_mask'])
        info['边类型数'] = len(np.unique(self.data['edge_type']))
        info['时间跨度(天)'] = np.max(self.data['edge_timestamp']) - np.min(self.data['edge_timestamp']) + 1

        # 标签分布
        labels = self.data['y'][self.data['train_mask']]
        unique_labels, counts = np.unique(labels, return_counts=True)
        info['标签分布'] = dict(zip(unique_labels, counts))

        return info

    def plot_label_distribution(self):
        """绘制标签分布图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # 训练集标签分布
        train_labels = self.data['y'][self.data['train_mask']]
        unique_labels, counts = np.unique(train_labels, return_counts=True)
        label_names = ['正常用户', '欺诈用户', '背景用户1', '背景用户2']

        colors = ['#4CAF50', '#FF5722', '#2196F3', '#FF9800']
        bars1 = ax1.bar([label_names[i] for i in unique_labels], counts, color=colors[:len(unique_labels)])
        ax1.set_title('训练集标签分布', fontsize=14, fontweight='bold')
        ax1.set_ylabel('数量', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)

        # 在柱状图上添加数值
        for bar, count in zip(bars1, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                    f'{count}\n({count/len(train_labels)*100:.1f}%)',
                    ha='center', va='bottom', fontsize=10)

        # 饼图
        ax2.pie(counts, labels=[label_names[i] for i in unique_labels],
                autopct='%1.1f%%', colors=colors[:len(unique_labels)], startangle=90)
        ax2.set_title('训练集标签比例', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig('analysis/label_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()

    def plot_feature_analysis(self):
        """分析节点特征"""
        features = self.data['x']
        feature_names = [f'特征_{i+1}' for i in range(features.shape[1])]

        fig, axes = plt.subplots(3, 3, figsize=(20, 15))
        axes = axes.flatten()

        for i in range(min(9, features.shape[1])):
            ax = axes[i]

            # 绘制特征分布直方图
            ax.hist(features[:, i], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_title(f'{feature_names[i]} 分布', fontsize=12, fontweight='bold')
            ax.set_xlabel('特征值', fontsize=10)
            ax.set_ylabel('频次', fontsize=10)
            ax.grid(True, alpha=0.3)

            # 添加统计信息
            mean_val = np.mean(features[:, i])
            std_val = np.std(features[:, i])
            ax.axvline(mean_val, color='red', linestyle='--', alpha=0.8, label=f'均值: {mean_val:.2f}')
            ax.legend(fontsize=9)

        # 隐藏多余的子图
        for i in range(features.shape[1], len(axes)):
            axes[i].set_visible(False)

        plt.tight_layout()
        plt.savefig('analysis/feature_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()

        # 特征相关性热力图
        plt.figure(figsize=(15, 12))
        correlation_matrix = np.corrcoef(features.T)

        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.2f', cbar_kws={"shrink": .8})
        plt.title('特征相关性热力图', fontsize=16, fontweight='bold')
        plt.xlabel('特征索引', fontsize=12)
        plt.ylabel('特征索引', fontsize=12)
        plt.tight_layout()
        plt.savefig('analysis/feature_correlation.png', dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()

    def plot_edge_analysis(self):
        """分析边信息"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # 边类型分布
        edge_types = self.data['edge_type']
        unique_types, type_counts = np.unique(edge_types, return_counts=True)

        axes[0, 0].bar(unique_types, type_counts, color='lightcoral', alpha=0.8)
        axes[0, 0].set_title('边类型分布', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('边类型', fontsize=12)
        axes[0, 0].set_ylabel('数量', fontsize=12)
        axes[0, 0].grid(True, alpha=0.3)

        # 时间戳分布
        timestamps = self.data['edge_timestamp']
        axes[0, 1].hist(timestamps, bins=50, color='gold', alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('边时间戳分布', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('时间(天)', fontsize=12)
        axes[0, 1].set_ylabel('频次', fontsize=12)
        axes[0, 1].grid(True, alpha=0.3)

        # 每种类型的边随时间分布
        axes[1, 0].boxplot([timestamps[edge_types == t] for t in unique_types[:10]],
                          labels=unique_types[:10])
        axes[1, 0].set_title('各边类型的时间分布', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('边类型', fontsize=12)
        axes[1, 0].set_ylabel('时间(天)', fontsize=12)
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)

        # 节点度分布
        edge_index = self.data['edge_index']
        degrees = np.bincount(edge_index.flatten(), minlength=self.data['x'].shape[0])

        axes[1, 1].hist(degrees, bins=50, color='lightgreen', alpha=0.7, edgecolor='black')
        axes[1, 1].set_title('节点度分布', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('度', fontsize=12)
        axes[1, 1].set_ylabel('节点数量', fontsize=12)
        axes[1, 1].set_yscale('log')
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('analysis/edge_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()

    def plot_temporal_analysis(self):
        """时间序列分析"""
        edge_timestamp = self.data['edge_timestamp']
        edge_type = self.data['edge_type']

        fig, axes = plt.subplots(2, 1, figsize=(16, 12))

        # 每日边数量趋势
        unique_days, day_counts = np.unique(edge_timestamp, return_counts=True)

        axes[0].plot(unique_days, day_counts, marker='o', linewidth=2, markersize=4, color='blue')
        axes[0].set_title('每日边数量趋势', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('时间(天)', fontsize=12)
        axes[0].set_ylabel('边数量', fontsize=12)
        axes[0].grid(True, alpha=0.3)

        # 添加移动平均线
        window_size = 7
        moving_avg = np.convolve(day_counts, np.ones(window_size)/window_size, mode='valid')
        axes[0].plot(unique_days[window_size-1:], moving_avg, 'r-', linewidth=3, label=f'{window_size}天移动平均')
        axes[0].legend()

        # 各类型边的时间分布热力图
        type_time_matrix = np.zeros((len(np.unique(edge_type)), len(unique_days)))

        for i, t in enumerate(np.unique(edge_type)):
            for j, day in enumerate(unique_days):
                type_time_matrix[i, j] = np.sum((edge_type == t) & (edge_timestamp == day))

        im = axes[1].imshow(type_time_matrix, aspect='auto', cmap='YlOrRd', interpolation='nearest')
        axes[1].set_title('各类型边的时间热力图', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('时间(天)', fontsize=12)
        axes[1].set_ylabel('边类型', fontsize=12)

        # 设置坐标轴
        axes[1].set_xticks(np.arange(0, len(unique_days), max(1, len(unique_days)//10)))
        axes[1].set_xticklabels(unique_days[::max(1, len(unique_days)//10)])
        axes[1].set_yticks(np.arange(len(np.unique(edge_type))))
        axes[1].set_yticklabels(np.unique(edge_type))

        plt.colorbar(im, ax=axes[1], label='边数量')
        plt.tight_layout()
        plt.savefig('analysis/temporal_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()

    def create_interactive_dashboard(self):
        """创建交互式仪表板"""
        try:
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('标签分布', '节点度分布', '边类型分布', '时间趋势'),
                specs=[[{"type": "pie"}, {"type": "histogram"}],
                       [{"type": "bar"}, {"type": "scatter"}]]
            )

            # 标签分布饼图
            train_labels = self.data['y'][self.data['train_mask']]
            unique_labels, counts = np.unique(train_labels, return_counts=True)
            label_names = ['正常用户', '欺诈用户', '背景用户']

            fig.add_trace(go.Pie(
                labels=[label_names[i] if i < len(label_names) else f'类别{i}' for i in unique_labels],
                values=counts,
                name="标签分布"
            ), row=1, col=1)

            # 节点度分布直方图
            edge_index = self.data['edge_index']
            degrees = np.bincount(edge_index.flatten(), minlength=self.data['x'].shape[0])

            fig.add_trace(go.Histogram(
                x=degrees,
                name="节点度分布",
                nbinsx=50
            ), row=1, col=2)

            # 边类型分布柱状图
            edge_types = self.data['edge_type']
            unique_types, type_counts = np.unique(edge_types, return_counts=True)

            fig.add_trace(go.Bar(
                x=unique_types,
                y=type_counts,
                name="边类型分布"
            ), row=2, col=1)

            # 时间趋势散点图
            timestamps = self.data['edge_timestamp']
            unique_days, day_counts = np.unique(timestamps, return_counts=True)

            fig.add_trace(go.Scatter(
                x=unique_days,
                y=day_counts,
                mode='lines+markers',
                name="每日边数量",
                line=dict(width=2),
                marker=dict(size=6)
            ), row=2, col=2)

            # 更新布局
            fig.update_layout(
                title_text="金融反欺诈数据集可视化仪表板",
                title_x=0.5,
                height=800,
                showlegend=True
            )

            # 保存为HTML文件
            fig.write_html("analysis/interactive_dashboard.html")
            print("交互式仪表板已保存至 analysis/interactive_dashboard.html")

            # 尝试显示图表，如果失败则跳过
            try:
                fig.show()
            except Exception as e:
                print(f"无法显示交互式图表: {e}")

        except Exception as e:
            print(f"创建交互式仪表板时出错: {e}")
            print("跳过交互式仪表板创建...")

    def generate_summary_report(self):
        """生成数据摘要报告"""
        info = self.get_basic_info()

        print("="*60)
        print("           金融反欺诈数据集可视化分析报告")
        print("="*60)

        print(f"\n📊 数据集基本信息:")
        print(f"   • 节点总数: {info['节点总数']:,}")
        print(f"   • 特征维度: {info['特征维度']}")
        print(f"   • 边总数: {info['边总数']:,}")
        print(f"   • 训练样本数: {info['训练样本数']:,}")
        print(f"   • 测试样本数: {info['测试样本数']:,}")
        print(f"   • 边类型数: {info['边类型数']}")
        print(f"   • 时间跨度: {info['时间跨度(天)']}天")

        print(f"\n🏷️ 标签分布:")
        total_train = info['训练样本数']
        for label, count in info['标签分布'].items():
            percentage = count / total_train * 100
            label_name = ['正常用户', '欺诈用户', '背景用户1', '背景用户2'][label] if label < 4 else f'类别{label}'
            print(f"   • {label_name}: {count:,} ({percentage:.2f}%)")

        print(f"\n📈 数据质量指标:")
        features = self.data['x']
        print(f"   • 特征缺失值比例: {np.mean(features == 0) * 100:.2f}%")

        degrees = np.bincount(self.data['edge_index'].flatten(), minlength=features.shape[0])
        print(f"   • 平均节点度: {np.mean(degrees):.2f}")
        print(f"   • 最大节点度: {np.max(degrees):,}")

        print("\n" + "="*60)
        print("分析完成！可视化图表已保存至 'analysis/' 目录")
        print("="*60)

    def run_all_analysis(self):
        """运行所有分析"""
        print("开始进行数据可视化分析...")

        # 创建analysis目录
        if not os.path.exists('analysis'):
            os.makedirs('analysis')

        # 生成摘要报告
        self.generate_summary_report()

        # 绘制各种图表
        print("\n正在生成标签分布图...")
        try:
            self.plot_label_distribution()
        except Exception as e:
            print(f"生成标签分布图时出错: {e}")

        print("正在分析特征分布...")
        try:
            self.plot_feature_analysis()
        except Exception as e:
            print(f"分析特征分布时出错: {e}")

        print("正在分析边信息...")
        try:
            self.plot_edge_analysis()
        except Exception as e:
            print(f"分析边信息时出错: {e}")

        print("正在进行时间序列分析...")
        try:
            self.plot_temporal_analysis()
        except Exception as e:
            print(f"进行时间序列分析时出错: {e}")

        print("正在创建交互式仪表板...")
        try:
            self.create_interactive_dashboard()
        except Exception as e:
            print(f"创建交互式仪表板时出错: {e}")

        print("\n✅ 所有分析完成！")

# 主程序
if __name__ == "__main__":
    # 创建可视化器实例
    visualizer = DataVisualizer()

    # 运行完整分析
    visualizer.run_all_analysis()