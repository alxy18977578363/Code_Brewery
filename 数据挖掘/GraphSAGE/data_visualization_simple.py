import os
# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib后端为Agg，避免GUI问题
import matplotlib
matplotlib.use('Agg')

class SimpleDataVisualizer:
    def __init__(self, data_path='data/phase1_gdata.npz'):
        """初始化数据可视化器"""
        self.data_path = data_path
        self.data = None
        self.load_data()

    def load_data(self):
        """加载图数据"""
        print("Loading data...")
        self.data = np.load(self.data_path)

        # 数据预处理
        self.data['x'][self.data['x'] == -1] = 0

        print(f"Data loaded successfully!")
        print(f"Nodes: {self.data['x'].shape[0]}")
        print(f"Features: {self.data['x'].shape[1]}")
        print(f"Edges: {self.data['edge_index'].shape[0]}")

    def generate_basic_info(self):
        """生成数据集基本信息"""
        info = {}
        info['Total Nodes'] = self.data['x'].shape[0]
        info['Feature Dimensions'] = self.data['x'].shape[1]
        info['Total Edges'] = self.data['edge_index'].shape[0]
        info['Train Samples'] = len(self.data['train_mask'])
        info['Test Samples'] = len(self.data['test_mask'])
        info['Edge Types'] = len(np.unique(self.data['edge_type']))
        info['Time Span (days)'] = np.max(self.data['edge_timestamp']) - np.min(self.data['edge_timestamp']) + 1

        # 标签分布
        labels = self.data['y'][self.data['train_mask']]
        unique_labels, counts = np.unique(labels, return_counts=True)
        info['Label Distribution'] = dict(zip(unique_labels, counts))

        return info

    def plot_label_distribution(self):
        """绘制标签分布图"""
        print("Generating label distribution plots...")

        train_labels = self.data['y'][self.data['train_mask']]
        unique_labels, counts = np.unique(train_labels, return_counts=True)
        label_names = ['Normal', 'Fraud', 'Background1', 'Background2']

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # 柱状图
        colors = ['#4CAF50', '#FF5722', '#2196F3', '#FF9800']
        bars = ax1.bar([label_names[i] if i < len(label_names) else f'Class{i}' for i in unique_labels],
                      counts, color=colors[:len(unique_labels)])
        ax1.set_title('Training Set Label Distribution', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Count', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)

        # 添加数值标签
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                    f'{count}\n({count/len(train_labels)*100:.1f}%)',
                    ha='center', va='bottom', fontsize=10)

        # 饼图
        ax2.pie(counts,
               labels=[label_names[i] if i < len(label_names) else f'Class{i}' for i in unique_labels],
               autopct='%1.1f%%', colors=colors[:len(unique_labels)], startangle=90)
        ax2.set_title('Training Set Label Percentage', fontsize=14, fontweight='bold')

        plt.tight_layout()

        # 确保目录存在
        if not os.path.exists('analysis'):
            os.makedirs('analysis')

        plt.savefig('analysis/label_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Label distribution plot saved to analysis/label_distribution.png")

    def plot_feature_analysis(self):
        """分析节点特征"""
        print("Analyzing feature distributions...")
        features = self.data['x']

        fig, axes = plt.subplots(3, 3, figsize=(20, 15))
        axes = axes.flatten()

        for i in range(min(9, features.shape[1])):
            ax = axes[i]

            # 绘制特征分布
            ax.hist(features[:, i], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_title(f'Feature {i+1} Distribution', fontsize=12, fontweight='bold')
            ax.set_xlabel('Feature Value', fontsize=10)
            ax.set_ylabel('Frequency', fontsize=10)
            ax.grid(True, alpha=0.3)

            # 添加统计信息
            mean_val = np.mean(features[:, i])
            std_val = np.std(features[:, i])
            ax.axvline(mean_val, color='red', linestyle='--', alpha=0.8,
                      label=f'Mean: {mean_val:.2f}')
            ax.legend(fontsize=9)

        # 隐藏多余的子图
        for i in range(features.shape[1], len(axes)):
            axes[i].set_visible(False)

        plt.tight_layout()
        plt.savefig('analysis/feature_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Feature analysis plots saved to analysis/feature_analysis.png")

    def plot_edge_analysis(self):
        """分析边信息"""
        print("Analyzing edge information...")
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # 边类型分布
        edge_types = self.data['edge_type']
        unique_types, type_counts = np.unique(edge_types, return_counts=True)

        axes[0, 0].bar(unique_types, type_counts, color='lightcoral', alpha=0.8)
        axes[0, 0].set_title('Edge Type Distribution', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Edge Type', fontsize=12)
        axes[0, 0].set_ylabel('Count', fontsize=12)
        axes[0, 0].grid(True, alpha=0.3)

        # 时间戳分布
        timestamps = self.data['edge_timestamp']
        axes[0, 1].hist(timestamps, bins=50, color='gold', alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('Edge Timestamp Distribution', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Time (days)', fontsize=12)
        axes[0, 1].set_ylabel('Frequency', fontsize=12)
        axes[0, 1].grid(True, alpha=0.3)

        # 节点度分布
        edge_index = self.data['edge_index']
        degrees = np.bincount(edge_index.flatten(), minlength=self.data['x'].shape[0])

        axes[1, 0].hist(degrees, bins=50, color='lightgreen', alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('Node Degree Distribution', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Degree', fontsize=12)
        axes[1, 0].set_ylabel('Number of Nodes', fontsize=12)
        axes[1, 0].set_yscale('log')
        axes[1, 0].grid(True, alpha=0.3)

        # 度分布统计
        ax = axes[1, 1]
        degree_stats = [
            ['Min', np.min(degrees)],
            ['Max', np.max(degrees)],
            ['Mean', np.mean(degrees)],
            ['Median', np.median(degrees)],
            ['Std', np.std(degrees)]
        ]

        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=degree_stats,
                        colLabels=['Statistic', 'Value'],
                        cellLoc='center',
                        loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)
        ax.set_title('Degree Statistics', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()
        plt.savefig('analysis/edge_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Edge analysis plots saved to analysis/edge_analysis.png")

    def plot_temporal_analysis(self):
        """时间序列分析"""
        print("Performing temporal analysis...")
        edge_timestamp = self.data['edge_timestamp']

        fig, axes = plt.subplots(2, 1, figsize=(16, 12))

        # 每日边数量趋势
        unique_days, day_counts = np.unique(edge_timestamp, return_counts=True)

        axes[0].plot(unique_days, day_counts, marker='o', linewidth=2, markersize=4, color='blue')
        axes[0].set_title('Daily Edge Count Trend', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Time (days)', fontsize=12)
        axes[0].set_ylabel('Edge Count', fontsize=12)
        axes[0].grid(True, alpha=0.3)

        # 添加移动平均线
        window_size = 7
        if len(day_counts) >= window_size:
            moving_avg = np.convolve(day_counts, np.ones(window_size)/window_size, mode='valid')
            axes[0].plot(unique_days[window_size-1:], moving_avg, 'r-', linewidth=3,
                        label=f'{window_size}-day Moving Average')
            axes[0].legend()

        # 活跃度统计
        ax = axes[1]

        # 计算基本统计信息
        temporal_stats = [
            ['Total Days', len(unique_days)],
            ['Avg Daily Edges', np.mean(day_counts)],
            ['Max Daily Edges', np.max(day_counts)],
            ['Min Daily Edges', np.min(day_counts)],
            ['Peak Day', unique_days[np.argmax(day_counts)]]
        ]

        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=temporal_stats,
                        colLabels=['Metric', 'Value'],
                        cellLoc='center',
                        loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)
        ax.set_title('Temporal Statistics', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()
        plt.savefig('analysis/temporal_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Temporal analysis plots saved to analysis/temporal_analysis.png")

    def print_summary_report(self):
        """打印数据摘要报告"""
        info = self.generate_basic_info()

        print("="*60)
        print("    Financial Anti-Fraud Dataset Visualization Analysis Report")
        print("="*60)

        print(f"\nDataset Basic Information:")
        print(f"   * Total Nodes: {info['Total Nodes']:,}")
        print(f"   * Feature Dimensions: {info['Feature Dimensions']}")
        print(f"   * Total Edges: {info['Total Edges']:,}")
        print(f"   * Train Samples: {info['Train Samples']:,}")
        print(f"   * Test Samples: {info['Test Samples']:,}")
        print(f"   * Edge Types: {info['Edge Types']}")
        print(f"   * Time Span: {info['Time Span (days)']} days")

        print(f"\nLabel Distribution:")
        total_train = info['Train Samples']
        for label, count in info['Label Distribution'].items():
            percentage = count / total_train * 100
            label_name = ['Normal', 'Fraud', 'Background1', 'Background2'][label] if label < 4 else f'Class{label}'
            print(f"   * {label_name}: {count:,} ({percentage:.2f}%)")

        print(f"\nData Quality Metrics:")
        features = self.data['x']
        print(f"   * Missing Value Ratio: {np.mean(features == 0) * 100:.2f}%")

        degrees = np.bincount(self.data['edge_index'].flatten(), minlength=features.shape[0])
        print(f"   * Average Node Degree: {np.mean(degrees):.2f}")
        print(f"   * Max Node Degree: {np.max(degrees):,}")
        print(f"   * Median Node Degree: {np.median(degrees):.2f}")

        print("\n" + "="*60)
        print("Analysis completed! Visualization charts saved to 'analysis/' directory")
        print("="*60)

    def run_all_analysis(self):
        """运行所有分析"""
        print("Starting data visualization analysis...")

        # 创建analysis目录
        if not os.path.exists('analysis'):
            os.makedirs('analysis')

        # 生成摘要报告
        self.print_summary_report()

        # 绘制各种图表
        print("\nGenerating label distribution plots...")
        try:
            self.plot_label_distribution()
        except Exception as e:
            print(f"Error generating label distribution: {e}")

        print("Analyzing feature distributions...")
        try:
            self.plot_feature_analysis()
        except Exception as e:
            print(f"Error analyzing features: {e}")

        print("Analyzing edge information...")
        try:
            self.plot_edge_analysis()
        except Exception as e:
            print(f"Error analyzing edges: {e}")

        print("Performing temporal analysis...")
        try:
            self.plot_temporal_analysis()
        except Exception as e:
            print(f"Error in temporal analysis: {e}")

        print("\nAll analysis completed!")
        print("Check the 'analysis/' directory for generated plots.")

# 主程序
if __name__ == "__main__":
    # 创建可视化器实例
    visualizer = SimpleDataVisualizer()

    # 运行完整分析
    visualizer.run_all_analysis()