import os
# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
from collections import Counter, defaultdict
import itertools
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib后端为Agg，避免GUI问题
import matplotlib
matplotlib.use('Agg')

class DetailedDataAnalyzer:
    def __init__(self, data_path='data/phase1_gdata.npz'):
        """初始化详细数据分析器"""
        self.data_path = data_path
        self.data = None
        self.graph_stats = {}
        self.load_data()
        self.compute_graph_statistics()

    def load_data(self):
        """加载图数据"""
        print("Loading detailed dataset...")
        self.data = np.load(self.data_path)

        # 数据预处理
        self.data['x'][self.data['x'] == -1] = 0

        print(f"Dataset loaded:")
        print(f"  - Total nodes: {self.data['x'].shape[0]:,}")
        print(f"  - Feature dimensions: {self.data['x'].shape[1]}")
        print(f"  - Total edges: {self.data['edge_index'].shape[0]:,}")
        print(f"  - Train samples: {len(self.data['train_mask']):,}")
        print(f"  - Test samples: {len(self.data['test_mask']):,}")

        # 打印边索引格式信息
        print(f"  - Edge index shape: {self.data['edge_index'].shape}")
        print(f"  - Edge type shape: {self.data['edge_type'].shape}")

    def compute_graph_statistics(self):
        """计算图结构统计信息"""
        print("Computing graph statistics...")

        # 计算入度和出度
        edge_index = self.data['edge_index']
        num_nodes = self.data['x'].shape[0]

        # 确保edge_index是正确的形状
        if len(edge_index.shape) == 2 and edge_index.shape[1] == 2:
            in_degrees = np.bincount(edge_index[:, 1], minlength=num_nodes)
            out_degrees = np.bincount(edge_index[:, 0], minlength=num_nodes)
        else:
            print("Warning: Unexpected edge_index shape, using degree calculation fallback")
            flat_edges = edge_index.flatten()
            in_degrees = np.bincount(flat_edges, minlength=num_nodes)
            out_degrees = np.bincount(flat_edges, minlength=num_nodes)

        total_degrees = in_degrees + out_degrees

        self.graph_stats = {
            'in_degrees': in_degrees,
            'out_degrees': out_degrees,
            'total_degrees': total_degrees,
            'avg_in_degree': np.mean(in_degrees[in_degrees > 0]),
            'avg_out_degree': np.mean(out_degrees[out_degrees > 0]),
            'max_in_degree': np.max(in_degrees),
            'max_out_degree': np.max(out_degrees),
            'clustering_coeff': None
        }

    def analyze_label_distribution_detailed(self):
        """详细分析标签分布"""
        print("Analyzing detailed label distribution...")

        fig = plt.figure(figsize=(20, 16))

        # 获取训练和测试数据的标签
        train_mask = self.data['train_mask']
        test_mask = self.data['test_mask']
        train_labels = self.data['y'][train_mask]

        # 1. 整体标签分布
        ax1 = plt.subplot(3, 3, 1)
        unique_labels, counts = np.unique(train_labels, return_counts=True)
        label_names = ['Normal', 'Fraud', 'Background1', 'Background2']
        colors = ['#4CAF50', '#FF5722', '#2196F3', '#FF9800']

        bars = ax1.bar([label_names[i] if i < len(label_names) else f'Class{i}' for i in unique_labels],
                      counts, color=colors[:len(unique_labels)])
        ax1.set_title('Training Label Distribution', fontweight='bold')
        ax1.set_ylabel('Count')
        ax1.tick_params(axis='x', rotation=45)

        # 添加数值标签
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                    f'{count}\n({count/len(train_labels)*100:.1f}%)',
                    ha='center', va='bottom', fontsize=9)

        # 2. 饼图
        ax2 = plt.subplot(3, 3, 2)
        explode = [0.1, 0.3, 0.1, 0.1]  # 让欺诈用户部分突出
        ax2.pie(counts,
               labels=[label_names[i] if i < len(label_names) else f'Class{i}' for i in unique_labels],
               autopct='%1.2f%%', colors=colors[:len(unique_labels)],
               startangle=90, explode=explode[:len(unique_labels)])
        ax2.set_title('Label Percentage Distribution', fontweight='bold')

        # 3. 对数尺度分布
        ax3 = plt.subplot(3, 3, 3)
        ax3.bar(range(len(unique_labels)), counts, color=colors[:len(unique_labels)])
        ax3.set_yscale('log')
        ax3.set_title('Label Distribution (Log Scale)', fontweight='bold')
        ax3.set_ylabel('Count (log scale)')
        ax3.set_xticks(range(len(unique_labels)))
        ax3.set_xticklabels([label_names[i] if i < len(label_names) else f'Class{i}' for i in unique_labels],
                           rotation=45)

        # 4. 类别不平衡比率
        ax4 = plt.subplot(3, 3, 4)
        if len(unique_labels) > 1:
            majority_count = max(counts)
            minority_ratios = [majority_count / count for count in counts]
            bars = ax4.bar(range(len(unique_labels)), minority_ratios,
                          color=colors[:len(unique_labels)])
            ax4.set_title('Class Imbalance Ratios\n(Majority/Minority)', fontweight='bold')
            ax4.set_ylabel('Imbalance Ratio')
            ax4.set_xticks(range(len(unique_labels)))
            ax4.set_xticklabels([label_names[i] if i < len(label_names) else f'Class{i}' for i in unique_labels],
                               rotation=45)
            ax4.grid(True, alpha=0.3)

            # 添加数值标签
            for bar, ratio in zip(bars, minority_ratios):
                ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(minority_ratios)*0.01,
                        f'{ratio:.1f}:1', ha='center', va='bottom', fontsize=9)

        # 5. 训练集 vs 测试集大小对比
        ax5 = plt.subplot(3, 3, 5)
        sizes = [len(train_mask), len(test_mask)]
        labels = ['Training Set', 'Test Set']
        colors_comparison = ['#2E7D32', '#1976D2']
        bars = ax5.bar(labels, sizes, color=colors_comparison)
        ax5.set_title('Dataset Split Comparison', fontweight='bold')
        ax5.set_ylabel('Number of Samples')

        # 添加数值标签
        for bar, size in zip(bars, sizes):
            ax5.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(sizes)*0.01,
                    f'{size:,}', ha='center', va='bottom', fontweight='bold')

        # 6. 测试集标签分布预测（都是-100）
        ax6 = plt.subplot(3, 3, 6)
        test_labels = self.data['y'][test_mask]
        unique_test, test_counts = np.unique(test_labels, return_counts=True)
        ax6.bar(['Unknown'], test_counts, color='gray')
        ax6.set_title('Test Set Labels', fontweight='bold')
        ax6.set_ylabel('Count')

        # 7. 如果有背景用户，分析背景用户细分
        ax7 = plt.subplot(3, 3, 7)
        background_masks = train_labels > 1
        if np.any(background_masks):
            bg_labels = train_labels[background_masks]
            bg_unique, bg_counts = np.unique(bg_labels, return_counts=True)
            bg_names = [f'Background{i}' for i in bg_unique]
            ax7.bar(bg_names, bg_counts, color=colors[2:2+len(bg_unique)])
            ax7.set_title('Background Users Breakdown', fontweight='bold')
            ax7.set_ylabel('Count')
            ax7.tick_params(axis='x', rotation=45)
        else:
            ax7.text(0.5, 0.5, 'No Background Users', ha='center', va='center',
                    transform=ax7.transAxes, fontsize=12)
            ax7.set_title('Background Users Breakdown', fontweight='bold')

        # 8. 统计摘要表格
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('tight')
        ax8.axis('off')

        # 计算详细统计
        total_samples = len(train_labels)
        fraud_ratio = counts[1] / total_samples if 1 in unique_labels else 0
        normal_ratio = counts[0] / total_samples if 0 in unique_labels else 0

        summary_data = [
            ['Total Training Samples', f'{total_samples:,}'],
            ['Total Test Samples', f'{len(test_mask):,}'],
            ['Fraud Ratio', f'{fraud_ratio*100:.3f}%'],
            ['Normal Ratio', f'{normal_ratio*100:.2f}%'],
            ['Imbalance Ratio', f'{max(counts)/min(counts[counts>0]):.1f}:1' if len(counts) > 1 else 'N/A'],
            ['Unique Labels', str(len(unique_labels))]
        ]

        table = ax8.table(cellText=summary_data,
                         colLabels=['Metric', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        # 9. 类别分布的小提琴图模拟
        ax9 = plt.subplot(3, 3, 9)
        # 简单的分布展示
        for i, (label, count) in enumerate(zip(unique_labels, counts)):
            # 创建一些模拟数据来展示分布
            sample_size = min(count // 100, 1000)  # 采样大小
            if sample_size > 0:
                noise = np.random.normal(i, 0.2, sample_size)
                ax9.scatter(noise, np.random.normal(0, 0.1, sample_size),
                           alpha=0.3, s=1, color=colors[i])
        ax9.set_title('Label Distribution Density', fontweight='bold')
        ax9.set_xlabel('Label Class')
        ax9.set_yticks([])
        ax9.set_xticks(range(len(unique_labels)))
        ax9.set_xticklabels([label_names[i] if i < len(label_names) else f'Class{i}' for i in unique_labels])

        plt.tight_layout()
        plt.savefig('analysis/detailed_label_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Detailed label analysis saved to analysis/detailed_label_analysis.png")

    def analyze_graph_structure(self):
        """分析图结构特征"""
        print("Analyzing graph structure...")

        fig = plt.figure(figsize=(20, 16))

        # 1. 度分布直方图（对数尺度）
        ax1 = plt.subplot(3, 3, 1)
        degrees = self.graph_stats['total_degrees']
        ax1.hist(degrees[degrees > 0], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax1.set_title('Degree Distribution (Log-Log)', fontweight='bold')
        ax1.set_xlabel('Degree (log scale)')
        ax1.set_ylabel('Frequency (log scale)')
        ax1.grid(True, alpha=0.3)

        # 2. 入度 vs 出度散点图
        ax2 = plt.subplot(3, 3, 2)
        in_deg = self.graph_stats['in_degrees']
        out_deg = self.graph_stats['out_degrees']

        # 采样以便可视化
        sample_size = min(10000, len(in_deg))
        sample_indices = np.random.choice(len(in_deg), sample_size, replace=False)
        ax2.scatter(in_deg[sample_indices], out_deg[sample_indices], alpha=0.5, s=1)
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.set_title('In-degree vs Out-degree', fontweight='bold')
        ax2.set_xlabel('In-degree (log scale)')
        ax2.set_ylabel('Out-degree (log scale)')
        ax2.grid(True, alpha=0.3)

        # 3. 度分布的累积分布函数
        ax3 = plt.subplot(3, 3, 3)
        sorted_degrees = np.sort(degrees)
        cumulative = np.arange(1, len(sorted_degrees) + 1) / len(sorted_degrees)
        ax3.plot(sorted_degrees, cumulative, linewidth=2)
        ax3.set_xscale('log')
        ax3.set_title('Degree Cumulative Distribution', fontweight='bold')
        ax3.set_xlabel('Degree (log scale)')
        ax3.set_ylabel('Cumulative Probability')
        ax3.grid(True, alpha=0.3)

        # 4. 度分布统计摘要
        ax4 = plt.subplot(3, 3, 4)
        degree_stats = [
            ['Mean', f'{np.mean(degrees):.2f}'],
            ['Median', f'{np.median(degrees):.2f}'],
            ['Std Dev', f'{np.std(degrees):.2f}'],
            ['Min', f'{np.min(degrees)}'],
            ['Max', f'{np.max(degrees)}'],
            ['95th Percentile', f'{np.percentile(degrees, 95):.2f}'],
            ['99th Percentile', f'{np.percentile(degrees, 99):.2f}']
        ]

        ax4.axis('tight')
        ax4.axis('off')
        table = ax4.table(cellText=degree_stats,
                         colLabels=['Statistic', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        ax4.set_title('Degree Statistics', fontweight='bold')

        # 5. 高度数节点分析
        ax5 = plt.subplot(3, 3, 5)
        high_degree_threshold = np.percentile(degrees, 99)
        high_degree_nodes = degrees >= high_degree_threshold

        ax5.hist([degrees[~high_degree_nodes], degrees[high_degree_nodes]],
                bins=30, label=['Regular Nodes', 'High-Degree Nodes'],
                color=['blue', 'red'], alpha=0.7)
        ax5.set_yscale('log')
        ax5.set_title(f'High-Degree Nodes (>{high_degree_threshold:.0f})', fontweight='bold')
        ax5.set_xlabel('Degree')
        ax5.set_ylabel('Frequency (log scale)')
        ax5.legend()
        ax5.grid(True, alpha=0.3)

        # 6. 节点度数分布（不同类型）
        ax6 = plt.subplot(3, 3, 6)
        train_mask = self.data['train_mask']
        train_labels = self.data['y'][train_mask]

        colors = ['#4CAF50', '#FF5722', '#2196F3', '#FF9800']

        for i, label in enumerate([0, 1]):  # 只显示正常和欺诈用户
            label_mask = train_labels == label
            label_indices = train_mask[label_mask]
            if len(label_indices) > 0:
                label_degrees = self.graph_stats['total_degrees'][label_indices]
                label_degrees_filtered = label_degrees[label_degrees > 0]
                if len(label_degrees_filtered) > 0:
                    ax6.hist(label_degrees_filtered, bins=30, alpha=0.7,
                            label=['Normal', 'Fraud'][i], color=colors[i])

        ax6.set_yscale('log')
        ax6.set_title('Degree Distribution by Label', fontweight='bold')
        ax6.set_xlabel('Degree')
        ax6.set_ylabel('Frequency (log scale)')
        ax6.legend()
        ax6.grid(True, alpha=0.3)

        # 7. 图密度分析（简化版）
        ax7 = plt.subplot(3, 3, 7)
        num_nodes = len(degrees)
        num_edges = self.data['edge_index'].shape[0]

        # 计算基本的图密度
        max_possible_edges = num_nodes * (num_nodes - 1)
        density = num_edges / max_possible_edges

        # 显示密度信息
        ax7.bar(['Graph Density'], [density], color='orange', alpha=0.7)
        ax7.set_title('Overall Graph Density', fontweight='bold')
        ax7.set_ylabel('Density')
        ax7.set_yscale('log')
        ax7.grid(True, alpha=0.3)

        # 8. 边类型分析
        ax8 = plt.subplot(3, 3, 8)
        edge_types = self.data['edge_type']
        unique_types, type_counts = np.unique(edge_types, return_counts=True)

        ax8.bar(unique_types, type_counts, color='lightcoral', alpha=0.8)
        ax8.set_title('Edge Type Distribution', fontweight='bold')
        ax8.set_xlabel('Edge Type')
        ax8.set_ylabel('Count')
        ax8.grid(True, alpha=0.3)

        # 9. 节点分类统计
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('tight')
        ax9.axis('off')

        # 计算图统计
        total_nodes = num_nodes
        isolated_nodes = np.sum(degrees == 0)
        active_nodes = total_nodes - isolated_nodes

        graph_summary = [
            ['Total Nodes', f'{total_nodes:,}'],
            ['Active Nodes', f'{active_nodes:,}'],
            ['Isolated Nodes', f'{isolated_nodes:,}'],
            ['Isolation Rate', f'{isolated_nodes/total_nodes*100:.2f}%'],
            ['Total Edges', f'{num_edges:,}'],
            ['Avg Degree', f'{np.mean(degrees[degrees>0]):.2f}'],
            ['Edge Types', str(len(unique_types))],
            ['Graph Density', f'{density:.2e}']
        ]

        table = ax9.table(cellText=graph_summary,
                         colLabels=['Graph Metric', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        plt.tight_layout()
        plt.savefig('analysis/graph_structure_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Graph structure analysis saved to analysis/graph_structure_analysis.png")

    def analyze_fraud_patterns(self):
        """分析欺诈模式"""
        print("Analyzing fraud patterns...")

        fig = plt.figure(figsize=(20, 16))

        train_mask = self.data['train_mask']
        train_labels = self.data['y'][train_mask]
        features = self.data['x']
        edge_index = self.data['edge_index']
        edge_types = self.data['edge_type']
        edge_timestamp = self.data['edge_timestamp']

        fraud_mask = train_labels == 1
        normal_mask = train_labels == 0

        fraud_indices = train_mask[fraud_mask]
        normal_indices = train_mask[normal_mask]

        # 1. 欺诈用户的度分布对比
        ax1 = plt.subplot(3, 3, 1)
        fraud_degrees = self.graph_stats['total_degrees'][fraud_indices]
        normal_degrees = self.graph_stats['total_degrees'][normal_indices]

        # 采样正常用户以便比较
        sample_size = min(len(fraud_degrees)*10, len(normal_degrees))
        if sample_size > 0:
            normal_sample = np.random.choice(normal_degrees, sample_size, replace=False)

            ax1.hist([normal_sample, fraud_degrees], bins=30, alpha=0.7,
                    label=['Normal Users', 'Fraud Users'],
                    color=['#4CAF50', '#FF5722'])
            ax1.set_title('Degree Distribution: Fraud vs Normal', fontweight='bold')
            ax1.set_xlabel('Degree')
            ax1.set_ylabel('Frequency')
            ax1.set_yscale('log')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

        # 2. 欺诈用户特征分析
        ax2 = plt.subplot(3, 3, 2)
        if len(fraud_indices) > 0 and len(normal_indices) > 0:
            fraud_features = features[fraud_indices]
            normal_features = features[normal_indices[:min(len(normal_indices), len(fraud_indices)*5)]]

            feature_means_fraud = np.mean(fraud_features, axis=0)
            feature_means_normal = np.mean(normal_features, axis=0)
            feature_diff = feature_means_fraud - feature_means_normal

            x_pos = np.arange(len(feature_diff))
            ax2.bar(x_pos, feature_diff, alpha=0.7, color='red')
            ax2.set_title('Feature Difference (Fraud - Normal)', fontweight='bold')
            ax2.set_xlabel('Feature Index')
            ax2.set_ylabel('Mean Difference')
            ax2.grid(True, alpha=0.3)

            # 标记差异最大的特征
            max_diff_idx = np.argmax(np.abs(feature_diff))
            ax2.axvline(max_diff_idx, color='blue', linestyle='--', alpha=0.8)
            ax2.text(max_diff_idx, max(0, feature_diff[max_diff_idx]),
                    f'Max diff: {feature_diff[max_diff_idx]:.3f}',
                    ha='center', va='bottom' if feature_diff[max_diff_idx] > 0 else 'top')

        # 3. 时间模式分析
        ax3 = plt.subplot(3, 3, 3)

        # 分析涉及欺诈用户的边的时间分布
        if len(fraud_indices) > 0:
            fraud_edges_mask = np.isin(edge_index[:, 0], fraud_indices) | np.isin(edge_index[:, 1], fraud_indices)
            fraud_edge_times = edge_timestamp[fraud_edges_mask]

            # 分析正常用户的边的时间分布（采样）
            normal_edges_mask = ~np.isin(edge_index[:, 0], fraud_indices) & ~np.isin(edge_index[:, 1], fraud_indices)
            normal_edge_times = edge_timestamp[normal_edges_mask]

            # 采样正常边数据以便可视化
            sample_size = min(len(fraud_edge_times)*5, len(normal_edge_times))
            if sample_size > 0:
                normal_edge_times_sample = np.random.choice(normal_edge_times, sample_size, replace=False)

                ax3.hist([normal_edge_times_sample, fraud_edge_times], bins=50, alpha=0.7,
                        label=['Normal Edges', 'Fraud-related Edges'],
                        color=['#4CAF50', '#FF5722'])
                ax3.set_title('Temporal Pattern: Fraud vs Normal', fontweight='bold')
                ax3.set_xlabel('Time (days)')
                ax3.set_ylabel('Frequency')
                ax3.set_yscale('log')
                ax3.legend()
                ax3.grid(True, alpha=0.3)

        # 4. 边类型模式分析
        ax4 = plt.subplot(3, 3, 4)

        if len(fraud_indices) > 0:
            # 欺诈用户相关的边类型
            fraud_edges_mask = np.isin(edge_index[:, 0], fraud_indices) | np.isin(edge_index[:, 1], fraud_indices)
            fraud_edge_types = edge_types[fraud_edges_mask]

            normal_edges_mask = ~np.isin(edge_index[:, 0], fraud_indices) & ~np.isin(edge_index[:, 1], fraud_indices)
            normal_edge_types = edge_types[normal_edges_mask]

            unique_types = np.unique(edge_types)
            fraud_type_counts = [np.sum(fraud_edge_types == t) for t in unique_types]
            normal_type_counts = [np.sum(normal_edge_types == t) for t in unique_types]

            width = 0.35
            x = np.arange(len(unique_types))
            ax4.bar(x - width/2, normal_type_counts, width, label='Normal', alpha=0.7, color='#4CAF50')
            ax4.bar(x + width/2, fraud_type_counts, width, label='Fraud', alpha=0.7, color='#FF5722')
            ax4.set_title('Edge Type Patterns: Fraud vs Normal', fontweight='bold')
            ax4.set_xlabel('Edge Type')
            ax4.set_ylabel('Count')
            ax4.set_yscale('log')
            ax4.set_xticks(x)
            ax4.legend()
            ax4.grid(True, alpha=0.3)

        # 5. 特征相关性分析（简化版）
        ax5 = plt.subplot(3, 3, 5)

        if len(fraud_indices) > 10:  # 需要足够的样本
            fraud_features = features[fraud_indices]
            if fraud_features.shape[0] > 1:
                fraud_corr = np.corrcoef(fraud_features.T)

                # 显示相关性矩阵的热力图
                im = ax5.imshow(fraud_corr, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
                ax5.set_title('Fraud Users Feature Correlation', fontweight='bold')
                ax5.set_xlabel('Feature Index')
                ax5.set_ylabel('Feature Index')

                # 添加颜色条
                cbar = plt.colorbar(im, ax=ax5)
                cbar.set_label('Correlation')

        # 6. 欺诈用户活跃度时间分析
        ax6 = plt.subplot(3, 3, 6)

        if len(fraud_indices) > 0:
            # 计算每个时间段的欺诈活动
            unique_times = np.unique(edge_timestamp)
            fraud_activity = []
            normal_activity = []

            sample_times = unique_times[::max(1, len(unique_times)//100)]  # 采样时间点

            for time in sample_times:
                time_mask = edge_timestamp == time
                time_edges = edge_index[time_mask]

                fraud_count = np.sum(np.isin(time_edges[:, 0], fraud_indices)) + \
                             np.sum(np.isin(time_edges[:, 1], fraud_indices))
                normal_count = np.sum(time_mask) - fraud_count

                fraud_activity.append(fraud_count)
                normal_activity.append(normal_count)

            if len(fraud_activity) > 0:
                ax6.plot(sample_times, fraud_activity, 'r-', label='Fraud Activity', linewidth=2)
                ax6.plot(sample_times, normal_activity, 'g-', label='Normal Activity', linewidth=2)
                ax6.set_title('Activity Timeline: Fraud vs Normal', fontweight='bold')
                ax6.set_xlabel('Time (days)')
                ax6.set_ylabel('Activity Count')
                ax6.set_yscale('log')
                ax6.legend()
                ax6.grid(True, alpha=0.3)

        # 7. 欺诈特征重要性（简化版）
        ax7 = plt.subplot(3, 3, 7)

        if len(fraud_indices) > 10 and len(normal_indices) > 10:
            # 计算每个特征的区分度
            feature_importance = []

            for i in range(min(10, features.shape[1])):  # 只分析前10个特征
                fraud_feature = features[fraud_indices, i]
                normal_feature = features[normal_indices[:min(len(normal_indices), len(fraud_indices)*5)], i]

                # 使用简单的均值差异作为重要性指标
                mean_diff = abs(np.mean(fraud_feature) - np.mean(normal_feature))
                feature_importance.append(mean_diff)

            if len(feature_importance) > 0:
                x_pos = np.arange(len(feature_importance))
                ax7.bar(x_pos, feature_importance, color='orange', alpha=0.7)
                ax7.set_title('Feature Importance (Mean Difference)', fontweight='bold')
                ax7.set_xlabel('Feature Index')
                ax7.set_ylabel('Mean Difference')
                ax7.grid(True, alpha=0.3)

        # 8. 欺诈网络结构分析
        ax8 = plt.subplot(3, 3, 8)

        if len(fraud_indices) > 0:
            # 分析欺诈用户之间的连接
            fraud_to_fraud_edges = 0
            fraud_to_normal_edges = 0

            # 采样边以便加速计算
            sample_edges = edge_index[np.random.choice(len(edge_index), min(100000, len(edge_index)), replace=False)]

            for edge in sample_edges:
                is_fraud_a = edge[0] in fraud_indices
                is_fraud_b = edge[1] in fraud_indices

                if is_fraud_a and is_fraud_b:
                    fraud_to_fraud_edges += 1
                elif (is_fraud_a and not is_fraud_b) or (not is_fraud_a and is_fraud_b):
                    fraud_to_normal_edges += 1

            edge_types_analysis = ['Fraud-Fraud', 'Fraud-Normal']
            edge_counts = [fraud_to_fraud_edges, fraud_to_normal_edges]

            ax8.bar(edge_types_analysis, edge_counts, color=['red', 'orange'], alpha=0.7)
            ax8.set_title('Fraud Network Connection Types', fontweight='bold')
            ax8.set_ylabel('Edge Count')
            ax8.set_yscale('log')
            ax8.grid(True, alpha=0.3)

        # 9. 欺诈模式总结
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('tight')
        ax9.axis('off')

        # 计算关键统计
        if len(fraud_indices) > 0:
            avg_fraud_degree = np.mean(self.graph_stats['total_degrees'][fraud_indices])
            avg_normal_degree = np.mean(self.graph_stats['total_degrees'][normal_indices]) if len(normal_indices) > 0 else 0

            pattern_summary = [
                ['Total Fraud Users', f'{len(fraud_indices):,}'],
                ['Fraud Ratio', f'{len(fraud_indices)/len(train_indices)*100:.3f}%'],
                ['Avg Fraud Degree', f'{avg_fraud_degree:.2f}'],
                ['Avg Normal Degree', f'{avg_normal_degree:.2f}'],
                ['Degree Ratio (F/N)', f'{avg_fraud_degree/avg_normal_degree:.2f}' if avg_normal_degree > 0 else 'N/A'],
                ['Most Important Feature', 'Feature analysis'],
                ['Fraud Network Density', 'Calculated above'],
                ['Pattern Type', 'Graph-based fraud']
            ]
        else:
            pattern_summary = [
                ['Total Fraud Users', '0'],
                ['Fraud Ratio', '0%'],
                ['Analysis Status', 'No fraud data found'],
                ['', ''],
                ['', ''],
                ['', ''],
                ['', ''],
                ['', '']
            ]

        table = ax9.table(cellText=pattern_summary,
                         colLabels=['Fraud Pattern', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        plt.tight_layout()
        plt.savefig('analysis/fraud_pattern_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Fraud pattern analysis saved to analysis/fraud_pattern_analysis.png")

    def analyze_temporal_patterns(self):
        """深度时间序列分析"""
        print("Analyzing temporal patterns...")

        fig = plt.figure(figsize=(20, 16))

        edge_timestamp = self.data['edge_timestamp']
        edge_types = self.data['edge_type']

        # 1. 整体时间序列分析
        ax1 = plt.subplot(3, 3, 1)
        unique_days, day_counts = np.unique(edge_timestamp, return_counts=True)

        ax1.plot(unique_days, day_counts, linewidth=1, alpha=0.7, color='blue', label='Daily Edge Count')

        # 添加趋势线
        if len(unique_days) > 3:
            z = np.polyfit(unique_days, day_counts, min(3, len(unique_days)-1))
            p = np.poly1d(z)
            ax1.plot(unique_days, p(unique_days), "r--", linewidth=2, label='Trend')

        ax1.set_title('Overall Temporal Trend with Polynomial Fit', fontweight='bold')
        ax1.set_xlabel('Time (days)')
        ax1.set_ylabel('Edge Count')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. 活动强度分布
        ax2 = plt.subplot(3, 3, 2)
        ax2.hist(day_counts, bins=30, alpha=0.7, color='green', edgecolor='black')
        ax2.set_title('Daily Activity Distribution', fontweight='bold')
        ax2.set_xlabel('Daily Edge Count')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)

        # 3. 移动平均分析
        ax3 = plt.subplot(3, 3, 3)

        # 不同窗口大小的移动平均
        windows = [7, 14, 30]
        colors = ['red', 'green', 'blue']

        for window, color in zip(windows, colors):
            if len(day_counts) >= window:
                moving_avg = np.convolve(day_counts, np.ones(window)/window, mode='valid')
                ax3.plot(unique_days[window-1:], moving_avg, linewidth=2,
                        label=f'{window}-day MA', color=color)

        ax3.set_title('Moving Averages with Different Windows', fontweight='bold')
        ax3.set_xlabel('Time (days)')
        ax3.set_ylabel('Moving Average')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. 周模式分析
        ax4 = plt.subplot(3, 3, 4)
        if len(unique_days) >= 7:
            # 按星期几分组
            weekly_pattern = []
            for day_of_week in range(7):
                weekly_mask = unique_days % 7 == day_of_week
                if np.any(weekly_mask):
                    weekly_avg = np.mean(day_counts[weekly_mask])
                    weekly_pattern.append(weekly_avg)
                else:
                    weekly_pattern.append(0)

            weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            bars = ax4.bar(weekdays, weekly_pattern, color='green', alpha=0.7)
            ax4.set_title('Weekly Pattern', fontweight='bold')
            ax4.set_ylabel('Average Daily Edge Count')
            ax4.tick_params(axis='x', rotation=45)
            ax4.grid(True, alpha=0.3)

            # 添加数值标签
            for bar, value in zip(bars, weekly_pattern):
                if value > 0:
                    ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(weekly_pattern)*0.01,
                            f'{value:.0f}', ha='center', va='bottom', fontsize=9)

        # 5. 边类型的时间演化
        ax5 = plt.subplot(3, 3, 5)

        # 选择前几种主要边类型进行分析
        unique_types = np.unique(edge_types)[:5]  # 只分析前5种类型

        for edge_type in unique_types:
            type_mask = edge_types == edge_type
            type_timestamps = edge_timestamp[type_mask]

            if len(type_timestamps) > 0:
                # 对时间戳进行聚合
                unique_type_days, type_day_counts = np.unique(type_timestamps, return_counts=True)

                # 重采样到与整体数据相同的时间点
                type_daily = np.zeros(len(unique_days))
                for day, count in zip(unique_type_days, type_day_counts):
                    day_idx = np.where(unique_days == day)[0]
                    if len(day_idx) > 0:
                        type_daily[day_idx[0]] = count

                ax5.plot(unique_days, type_daily,
                        label=f'Type {edge_type}', alpha=0.7, linewidth=1)

        ax5.set_title('Edge Type Evolution Over Time', fontweight='bold')
        ax5.set_xlabel('Time (days)')
        ax5.set_ylabel('Edge Count')
        ax5.legend()
        ax5.grid(True, alpha=0.3)

        # 6. 波动性分析
        ax6 = plt.subplot(3, 3, 6)

        # 计算滚动标准差
        window = 14
        if len(day_counts) >= window:
            rolling_std = []
            for i in range(window-1, len(day_counts)):
                window_data = day_counts[i-window+1:i+1]
                rolling_std.append(np.std(window_data))

            ax6.plot(unique_days[window-1:], rolling_std, color='purple', linewidth=2)
            ax6.set_title(f'{window}-day Rolling Volatility', fontweight='bold')
            ax6.set_xlabel('Time (days)')
            ax6.set_ylabel('Standard Deviation')
            ax6.grid(True, alpha=0.3)

            # 添加平均线
            ax6.axhline(np.mean(rolling_std), color='red', linestyle='--', alpha=0.7, label='Mean Volatility')
            ax6.legend()

        # 7. 异常检测
        ax7 = plt.subplot(3, 3, 7)

        # 使用Z-score检测异常
        z_scores = np.abs(stats.zscore(day_counts))
        threshold = 2
        anomaly_mask = z_scores > threshold

        ax7.plot(unique_days, day_counts, 'b-', linewidth=1, alpha=0.7, label='Normal')
        ax7.scatter(unique_days[anomaly_mask], day_counts[anomaly_mask],
                   color='red', s=50, alpha=0.8, label='Anomalies', zorder=5)

        ax7.axhline(np.mean(day_counts) + threshold*np.std(day_counts),
                   color='orange', linestyle='--', alpha=0.7, label=f'{threshold}σ threshold')
        ax7.axhline(np.mean(day_counts) - threshold*np.std(day_counts),
                   color='orange', linestyle='--', alpha=0.7)

        ax7.set_title('Anomaly Detection in Time Series', fontweight='bold')
        ax7.set_xlabel('Time (days)')
        ax7.set_ylabel('Edge Count')
        ax7.legend()
        ax7.grid(True, alpha=0.3)

        # 8. 时间统计摘要
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('tight')
        ax8.axis('off')

        # 计算时间相关统计
        time_stats = [
            ['Time Span', f'{np.max(unique_days) - np.min(unique_days) + 1} days'],
            ['Total Active Days', f'{len(unique_days)}'],
            ['Avg Daily Edges', f'{np.mean(day_counts):.0f}'],
            ['Peak Daily Edges', f'{np.max(day_counts):.0f}'],
            ['Min Daily Edges', f'{np.min(day_counts):.0f}'],
            ['Std Dev', f'{np.std(day_counts):.0f}'],
            ['Anomaly Days (>2σ)', f'{np.sum(anomaly_mask)}'],
            ['Anomaly Ratio', f'{np.sum(anomaly_mask)/len(day_counts)*100:.1f}%']
        ]

        table = ax8.table(cellText=time_stats,
                         colLabels=['Time Statistic', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        ax8.set_title('Temporal Statistics Summary', fontweight='bold')

        # 9. 活动强度热力图（简化版）
        ax9 = plt.subplot(3, 3, 9)

        # 创建时间段x星期几的热力图
        if len(unique_days) >= 14:  # 至少需要两周的数据
            # 将时间分成段
            num_periods = min(10, len(unique_days) // 7)  # 最多10个时间段
            period_length = len(unique_days) // num_periods

            heat_data = np.zeros((7, num_periods))  # 7天 x N个时间段
            weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

            for i in range(num_periods):
                start_idx = i * period_length
                end_idx = min((i + 1) * period_length, len(unique_days))

                for j in range(start_idx, end_idx):
                    if j < len(day_counts):
                        day_of_week = unique_days[j] % 7
                        heat_data[day_of_week, i] += day_counts[j]

                # 对每个时间段求平均
                if end_idx > start_idx:
                    heat_data[:, i] /= (end_idx - start_idx)

            im = ax9.imshow(heat_data, cmap='YlOrRd', aspect='auto')
            ax9.set_title('Activity Intensity Heatmap', fontweight='bold')
            ax9.set_xlabel('Time Period')
            ax9.set_ylabel('Day of Week')
            ax9.set_yticks(range(7))
            ax9.set_yticklabels(weekdays)

            # 添加颜色条
            cbar = plt.colorbar(im, ax=ax9)
            cbar.set_label('Average Edge Count')

        plt.tight_layout()
        plt.savefig('analysis/temporal_pattern_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Temporal pattern analysis saved to analysis/temporal_pattern_analysis.png")

    def generate_comprehensive_report(self):
        """生成综合分析报告"""
        print("Generating comprehensive analysis report...")

        report = []
        report.append("="*80)
        report.append("           COMPREHENSIVE FINANCIAL ANTI-FRAUD DATASET ANALYSIS")
        report.append("="*80)

        # 数据集基本信息
        report.append("\n" + "="*40 + " DATASET OVERVIEW " + "="*40)
        report.append(f"• Total Nodes: {self.data['x'].shape[0]:,}")
        report.append(f"• Feature Dimensions: {self.data['x'].shape[1]}")
        report.append(f"• Total Edges: {self.data['edge_index'].shape[0]:,}")
        report.append(f"• Training Samples: {len(self.data['train_mask']):,}")
        report.append(f"• Test Samples: {len(self.data['test_mask']):,}")
        report.append(f"• Edge Types: {len(np.unique(self.data['edge_type']))}")

        # 标签分布分析
        train_mask = self.data['train_mask']
        train_labels = self.data['y'][train_mask]
        unique_labels, counts = np.unique(train_labels, return_counts=True)

        report.append("\n" + "="*40 + " LABEL DISTRIBUTION " + "="*40)
        total_train = len(train_labels)
        label_names = ['Normal Users', 'Fraud Users', 'Background Users Type 1', 'Background Users Type 2']

        for label, count in zip(unique_labels, counts):
            percentage = count / total_train * 100
            if label < len(label_names):
                report.append(f"• {label_names[label]}: {count:,} ({percentage:.3f}%)")
            else:
                report.append(f"• Class {label}: {count:,} ({percentage:.3f}%)")

        # 类别不平衡分析
        if len(counts) > 1:
            imbalance_ratio = max(counts) / min(counts[counts > 0])
            fraud_count = counts[1] if 1 in unique_labels else 0
            fraud_ratio = fraud_count / total_train * 100

            report.append(f"\n• Class Imbalance Ratio: {imbalance_ratio:.1f}:1")
            report.append(f"• Fraud Detection Difficulty: {'High' if fraud_ratio < 2 else 'Medium' if fraud_ratio < 5 else 'Low'}")

        # 图结构分析
        report.append("\n" + "="*40 + " GRAPH STRUCTURE " + "="*40)
        degrees = self.graph_stats['total_degrees']
        isolated_nodes = np.sum(degrees == 0)
        active_nodes = len(degrees) - isolated_nodes

        report.append(f"• Active Nodes: {active_nodes:,} ({active_nodes/len(degrees)*100:.2f}%)")
        report.append(f"• Isolated Nodes: {isolated_nodes:,} ({isolated_nodes/len(degrees)*100:.2f}%)")
        report.append(f"• Average Degree: {np.mean(degrees[degrees > 0]):.2f}")
        report.append(f"• Median Degree: {np.median(degrees):.2f}")
        report.append(f"• Maximum Degree: {np.max(degrees):,}")
        report.append(f"• High-Degree Nodes (>99th percentile): {np.sum(degrees > np.percentile(degrees, 99)):,}")

        # 时间分析
        edge_timestamp = self.data['edge_timestamp']
        unique_days, day_counts = np.unique(edge_timestamp, return_counts=True)

        report.append("\n" + "="*40 + " TEMPORAL ANALYSIS " + "="*40)
        report.append(f"• Time Span: {np.max(unique_days) - np.min(unique_days) + 1} days")
        report.append(f"• Active Days: {len(unique_days)}")
        report.append(f"• Average Daily Activity: {np.mean(day_counts):.0f} edges")
        report.append(f"• Peak Daily Activity: {np.max(day_counts):,} edges")
        report.append(f"• Activity Volatility (Std): {np.std(day_counts):.0f}")

        # 欺诈模式分析
        fraud_mask = train_labels == 1
        fraud_indices = train_mask[fraud_mask]

        report.append("\n" + "="*40 + " FRAUD PATTERN ANALYSIS " + "="*40)
        report.append(f"• Total Fraud Users: {len(fraud_indices):,}")

        if len(fraud_indices) > 0:
            fraud_degrees = self.graph_stats['total_degrees'][fraud_indices]
            normal_mask = train_labels == 0
            normal_indices = train_mask[normal_mask]
            normal_degrees = self.graph_stats['total_degrees'][normal_indices]

            report.append(f"• Average Fraud User Degree: {np.mean(fraud_degrees):.2f}")
            report.append(f"• Average Normal User Degree: {np.mean(normal_degrees):.2f}")
            report.append(f"• Degree Ratio (Fraud/Normal): {np.mean(fraud_degrees)/np.mean(normal_degrees):.2f}")

        # 特征质量分析
        features = self.data['x']

        report.append("\n" + "="*40 + " FEATURE QUALITY " + "="*40)
        report.append(f"• Missing Value Rate: {np.mean(features == 0) * 100:.2f}%")

        # 计算特征方差
        feature_variances = np.var(features, axis=0)
        low_variance_features = np.sum(feature_variances < 0.01)

        report.append(f"• Low Variance Features (<0.01): {low_variance_features}/{len(feature_variances)}")
        report.append(f"• Average Feature Variance: {np.mean(feature_variances):.4f}")

        # 数据质量评分
        report.append("\n" + "="*40 + " DATA QUALITY SCORE " + "="*40)

        quality_scores = []

        # 完整性评分
        completeness = (1 - np.mean(features == 0)) * 100
        quality_scores.append(('Completeness', completeness))

        # 连通性评分
        connectivity = active_nodes / len(degrees) * 100
        quality_scores.append(('Connectivity', connectivity))

        # 时间覆盖率评分
        time_coverage = len(unique_days) / (np.max(unique_days) - np.min(unique_days) + 1) * 100
        quality_scores.append(('Time Coverage', time_coverage))

        # 标签质量评分（基于不平衡程度）
        if len(counts) > 1:
            balance_score = min(counts) / max(counts) * 100
        else:
            balance_score = 100
        quality_scores.append(('Label Balance', balance_score))

        for score_name, score_value in quality_scores:
            report.append(f"• {score_name}: {score_value:.1f}/100")

        overall_quality = np.mean([score for _, score in quality_scores])
        report.append(f"\n• Overall Data Quality Score: {overall_quality:.1f}/100")

        # 建议
        report.append("\n" + "="*40 + " RECOMMENDATIONS " + "="*40)

        if 'imbalance_ratio' in locals() and imbalance_ratio > 100:
            report.append("• HIGH PRIORITY: Address severe class imbalance (ratio > 100:1)")
            report.append("  - Use oversampling (SMOTE) for fraud cases")
            report.append("  - Apply class weighting in loss function")
            report.append("  - Consider anomaly detection approaches")

        if isolated_nodes / len(degrees) > 0.5:
            report.append("• MEDIUM PRIORITY: Many isolated nodes detected")
            report.append("  - Consider node feature-only models for isolated nodes")
            report.append("  - Investigate reasons for isolation")

        if completeness < 90:
            report.append("• MEDIUM PRIORITY: High missing value rate detected")
            report.append("  - Implement proper missing value imputation")
            report.append("  - Consider missing value indicators as features")

        if overall_quality < 70:
            report.append("• GENERAL: Consider additional data preprocessing")
        elif overall_quality > 85:
            report.append("• GOOD: Dataset quality is acceptable for modeling")

        report.append("\n" + "="*80)
        report.append("                     END OF ANALYSIS REPORT")
        report.append("="*80)

        # 保存报告
        with open('analysis/comprehensive_report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        # 同时打印到控制台（简化版本）
        print("\n" + "="*60)
        print("        COMPREHENSIVE ANALYSIS SUMMARY")
        print("="*60)
        print(f"Dataset: {self.data['x'].shape[0]:,} nodes, {self.data['edge_index'].shape[0]:,} edges")
        print(f"Fraud ratio: {len(fraud_indices)/len(train_indices)*100:.3f}%")
        print(f"Overall quality score: {overall_quality:.1f}/100")
        print(f"Full report saved to: analysis/comprehensive_report.txt")
        print("="*60)

    def run_complete_analysis(self):
        """运行完整分析"""
        print("Starting comprehensive data analysis...")

        # 确保目录存在
        if not os.path.exists('analysis'):
            os.makedirs('analysis')

        # 运行所有分析
        try:
            self.analyze_label_distribution_detailed()
        except Exception as e:
            print(f"Error in label distribution analysis: {e}")

        try:
            self.analyze_graph_structure()
        except Exception as e:
            print(f"Error in graph structure analysis: {e}")

        try:
            self.analyze_fraud_patterns()
        except Exception as e:
            print(f"Error in fraud pattern analysis: {e}")

        try:
            self.analyze_temporal_patterns()
        except Exception as e:
            print(f"Error in temporal pattern analysis: {e}")

        try:
            self.generate_comprehensive_report()
        except Exception as e:
            print(f"Error generating comprehensive report: {e}")

        print("\n" + "="*60)
        print("COMPREHENSIVE ANALYSIS COMPLETED!")
        print("All charts and reports saved to 'analysis/' directory")
        print("="*60)

# 主程序
if __name__ == "__main__":
    analyzer = DetailedDataAnalyzer()
    analyzer.run_complete_analysis()