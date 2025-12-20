import os
# 设置环境变量解决OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib后端为Agg，避免GUI问题
import matplotlib
matplotlib.use('Agg')

class FinalDetailedAnalyzer:
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

    def compute_graph_statistics(self):
        """计算图结构统计信息"""
        print("Computing graph statistics...")

        # 安全地获取边索引
        edge_index = self.data['edge_index']
        num_nodes = self.data['x'].shape[0]

        # 检查edge_index的形状
        if len(edge_index.shape) == 2 and edge_index.shape[1] == 2:
            print("Using 2D edge index format")
            in_degrees = np.bincount(edge_index[:, 1], minlength=num_nodes)
            out_degrees = np.bincount(edge_index[:, 0], minlength=num_nodes)
        elif len(edge_index.shape) == 1:
            print("Using 1D edge index format (flattened)")
            # 假设是扁平化的格式，每两个元素代表一条边
            if len(edge_index) % 2 == 0:
                edge_pairs = edge_index.reshape(-1, 2)
                in_degrees = np.bincount(edge_pairs[:, 1], minlength=num_nodes)
                out_degrees = np.bincount(edge_pairs[:, 0], minlength=num_nodes)
            else:
                print("Warning: Unexpected 1D edge index length, using fallback")
                in_degrees = np.bincount(edge_index, minlength=num_nodes)
                out_degrees = np.bincount(edge_index, minlength=num_nodes)
        else:
            print(f"Warning: Unexpected edge_index shape {edge_index.shape}, using fallback")
            flat_edges = edge_index.flatten()
            in_degrees = np.bincount(flat_edges, minlength=num_nodes)
            out_degrees = np.bincount(flat_edges, minlength=num_nodes)

        total_degrees = in_degrees + out_degrees

        self.graph_stats = {
            'in_degrees': in_degrees,
            'out_degrees': out_degrees,
            'total_degrees': total_degrees,
            'avg_in_degree': np.mean(in_degrees[in_degrees > 0]) if np.any(in_degrees > 0) else 0,
            'avg_out_degree': np.mean(out_degrees[out_degrees > 0]) if np.any(out_degrees > 0) else 0,
            'max_in_degree': np.max(in_degrees),
            'max_out_degree': np.max(out_degrees),
        }

    def analyze_features_deep(self):
        """深度特征分析"""
        print("Performing deep feature analysis...")

        fig = plt.figure(figsize=(20, 16))

        features = self.data['x']
        train_mask = self.data['train_mask']
        train_labels = self.data['y'][train_mask]

        # 1. 特征分布概览
        ax1 = plt.subplot(3, 4, 1)
        feature_means = np.mean(features, axis=0)
        feature_stds = np.std(features, axis=0)

        x_pos = np.arange(len(feature_means))
        ax1.bar(x_pos, feature_means, yerr=feature_stds, alpha=0.7, color='skyblue', capsize=3)
        ax1.set_title('Feature Means with Standard Deviation', fontweight='bold')
        ax1.set_xlabel('Feature Index')
        ax1.set_ylabel('Mean Value')
        ax1.grid(True, alpha=0.3)

        # 2. 特征方差分析
        ax2 = plt.subplot(3, 4, 2)
        feature_variances = np.var(features, axis=0)
        ax2.bar(x_pos, feature_variances, alpha=0.7, color='lightcoral')
        ax2.set_title('Feature Variances', fontweight='bold')
        ax2.set_xlabel('Feature Index')
        ax2.set_ylabel('Variance')
        ax2.grid(True, alpha=0.3)

        # 标记低方差特征
        low_var_threshold = 0.01
        low_var_mask = feature_variances < low_var_threshold
        ax2.axhline(low_var_threshold, color='red', linestyle='--', alpha=0.7, label=f'Threshold: {low_var_threshold}')
        ax2.legend()

        # 3. 缺失值分析
        ax3 = plt.subplot(3, 4, 3)
        missing_rates = np.mean(features == 0, axis=0) * 100
        ax3.bar(x_pos, missing_rates, alpha=0.7, color='orange')
        ax3.set_title('Missing Value Rates (%)', fontweight='bold')
        ax3.set_xlabel('Feature Index')
        ax3.set_ylabel('Missing Rate (%)')
        ax3.grid(True, alpha=0.3)

        # 4. 特征相关性热力图
        ax4 = plt.subplot(3, 4, 4)
        correlation_matrix = np.corrcoef(features.T)

        im = ax4.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        ax4.set_title('Feature Correlation Matrix', fontweight='bold')
        ax4.set_xlabel('Feature Index')
        ax4.set_ylabel('Feature Index')

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax4)
        cbar.set_label('Correlation')

        # 5-8. 详细特征分布（前4个主要特征）
        for i in range(min(4, features.shape[1])):
            ax = plt.subplot(3, 4, 5 + i)

            # 整体分布
            ax.hist(features[:, i], bins=50, alpha=0.7, color='skyblue',
                   label='All', density=True)

            # 按标签分组
            fraud_mask = train_labels == 1
            normal_mask = train_labels == 0

            if np.any(fraud_mask):
                fraud_features = features[train_mask[fraud_mask], i]
                if len(fraud_features) > 0:
                    ax.hist(fraud_features, bins=30, alpha=0.5, color='red',
                           label='Fraud', density=True)

            if np.any(normal_mask):
                normal_features = features[train_mask[normal_mask], i]
                if len(normal_features) > 0:
                    # 采样正常用户以便可视化
                    sample_size = min(len(fraud_features) * 10, len(normal_features)) if np.any(fraud_mask) else len(normal_features)
                    if sample_size > 0:
                        normal_sample = np.random.choice(normal_features, sample_size, replace=False)
                        ax.hist(normal_sample, bins=30, alpha=0.5, color='green',
                               label='Normal', density=True)

            ax.set_title(f'Feature {i+1} Distribution by Label', fontweight='bold')
            ax.set_xlabel('Feature Value')
            ax.set_ylabel('Density')
            ax.legend()
            ax.grid(True, alpha=0.3)

        # 9. 特征重要性（基于方差）
        ax9 = plt.subplot(3, 4, 9)
        importance_scores = feature_variances * (1 - missing_rates/100)  # 方差 * 完整性
        sorted_idx = np.argsort(importance_scores)[::-1]

        ax9.bar(range(len(importance_scores)), importance_scores[sorted_idx], color='purple', alpha=0.7)
        ax9.set_title('Feature Importance (Variance × Completeness)', fontweight='bold')
        ax9.set_xlabel('Feature Rank')
        ax9.set_ylabel('Importance Score')
        ax9.grid(True, alpha=0.3)

        # 10. 特征类型分析
        ax10 = plt.subplot(3, 4, 10)

        # 将特征分类为不同类型
        feature_types = {
            'Binary': np.sum(np.all((features == 0) | (features == 1), axis=0)),
            'Categorical': np.sum(np.max(features, axis=0) <= 10) - np.sum(np.all((features == 0) | (features == 1), axis=0)),
            'Continuous': features.shape[1] - np.sum(np.max(features, axis=0) <= 10)
        }

        ax10.bar(feature_types.keys(), feature_types.values(),
                color=['blue', 'green', 'orange'], alpha=0.7)
        ax10.set_title('Feature Type Distribution', fontweight='bold')
        ax10.set_ylabel('Number of Features')
        ax10.grid(True, alpha=0.3)

        # 11. 特征统计摘要
        ax11 = plt.subplot(3, 4, 11)
        ax11.axis('tight')
        ax11.axis('off')

        feature_summary = [
            ['Total Features', str(features.shape[1])],
            ['Low Variance Features', f'{np.sum(low_var_mask)}'],
            ['High Missing Rate (>50%)', f'{np.sum(missing_rates > 50)}'],
            ['Binary Features', f'{feature_types["Binary"]}'],
            ['Categorical Features', f'{feature_types["Categorical"]}'],
            ['Continuous Features', f'{feature_types["Continuous"]}'],
            ['Avg Correlation', f'{np.mean(np.abs(correlation_matrix[~np.eye(correlation_matrix.shape[0], dtype=bool)])):.3f}']
        ]

        table = ax11.table(cellText=feature_summary,
                          colLabels=['Feature Statistic', 'Value'],
                          cellLoc='center',
                          loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        # 12. 特征建议
        ax12 = plt.subplot(3, 4, 12)
        ax12.axis('tight')
        ax12.axis('off')

        recommendations = []
        if np.sum(low_var_mask) > 0:
            recommendations.append(f"Remove {np.sum(low_var_mask)} low-variance features")
        if np.sum(missing_rates > 50) > 0:
            recommendations.append(f"Address {np.sum(missing_rates > 50)} high-missing features")
        if feature_types['Binary'] > 0:
            recommendations.append(f"Consider encoding for {feature_types['Binary']} binary features")

        if not recommendations:
            recommendations.append("Feature quality looks good")

        rec_text = '\n'.join([f"• {rec}" for rec in recommendations])
        ax12.text(0.1, 0.5, 'Feature Engineering Recommendations:\n\n' + rec_text,
                 transform=ax12.transAxes, fontsize=11, verticalalignment='center')
        ax12.set_title('Recommendations', fontweight='bold')

        plt.tight_layout()
        plt.savefig('analysis/deep_feature_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Deep feature analysis saved to analysis/deep_feature_analysis.png")

    def analyze_graph_structure_fixed(self):
        """修复版图结构分析"""
        print("Analyzing graph structure (fixed version)...")

        fig = plt.figure(figsize=(20, 16))

        degrees = self.graph_stats['total_degrees']
        in_degrees = self.graph_stats['in_degrees']
        out_degrees = self.graph_stats['out_degrees']

        # 1. 度分布直方图
        ax1 = plt.subplot(3, 3, 1)
        ax1.hist(degrees[degrees > 0], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax1.set_title('Degree Distribution (Log-Log)', fontweight='bold')
        ax1.set_xlabel('Degree (log scale)')
        ax1.set_ylabel('Frequency (log scale)')
        ax1.grid(True, alpha=0.3)

        # 2. 入度 vs 出度对比
        ax2 = plt.subplot(3, 3, 2)

        # 采样以便可视化
        sample_size = min(10000, len(in_degrees))
        sample_indices = np.random.choice(len(in_degrees), sample_size, replace=False)

        ax2.scatter(in_degrees[sample_indices], out_degrees[sample_indices], alpha=0.5, s=1)
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.set_title('In-degree vs Out-degree', fontweight='bold')
        ax2.set_xlabel('In-degree (log scale)')
        ax2.set_ylabel('Out-degree (log scale)')
        ax2.grid(True, alpha=0.3)

        # 3. 累积度分布
        ax3 = plt.subplot(3, 3, 3)
        sorted_degrees = np.sort(degrees)
        cumulative = np.arange(1, len(sorted_degrees) + 1) / len(sorted_degrees)
        ax3.plot(sorted_degrees, cumulative, linewidth=2, color='blue')
        ax3.set_xscale('log')
        ax3.set_title('Degree Cumulative Distribution', fontweight='bold')
        ax3.set_xlabel('Degree (log scale)')
        ax3.set_ylabel('Cumulative Probability')
        ax3.grid(True, alpha=0.3)

        # 4. 度统计表格
        ax4 = plt.subplot(3, 3, 4)
        ax4.axis('tight')
        ax4.axis('off')

        degree_stats = [
            ['Mean Degree', f'{np.mean(degrees):.2f}'],
            ['Median Degree', f'{np.median(degrees):.2f}'],
            ['Std Deviation', f'{np.std(degrees):.2f}'],
            ['Minimum Degree', f'{np.min(degrees)}'],
            ['Maximum Degree', f'{np.max(degrees):,}'],
            ['95th Percentile', f'{np.percentile(degrees, 95):.2f}'],
            ['99th Percentile', f'{np.percentile(degrees, 99):.2f}']
        ]

        table = ax4.table(cellText=degree_stats,
                         colLabels=['Statistic', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        # 5. 按标签的度分布
        ax5 = plt.subplot(3, 3, 5)
        train_mask = self.data['train_mask']
        train_labels = self.data['y'][train_mask]

        colors = ['#4CAF50', '#FF5722']

        for i, (label, color) in enumerate([(0, '#4CAF50'), (1, '#FF5722')]):
            label_mask = train_labels == label
            if np.any(label_mask):
                label_indices = train_mask[label_mask]
                label_degrees = degrees[label_indices]
                label_degrees_filtered = label_degrees[label_degrees > 0]
                if len(label_degrees_filtered) > 0:
                    ax5.hist(label_degrees_filtered, bins=30, alpha=0.7,
                            label=['Normal', 'Fraud'][i], color=color)

        ax5.set_yscale('log')
        ax5.set_title('Degree Distribution by Label', fontweight='bold')
        ax5.set_xlabel('Degree')
        ax5.set_ylabel('Frequency (log scale)')
        ax5.legend()
        ax5.grid(True, alpha=0.3)

        # 6. 高度数节点分析
        ax6 = plt.subplot(3, 3, 6)
        high_degree_threshold = np.percentile(degrees, 99)
        high_degree_mask = degrees >= high_degree_threshold

        ax6.hist([degrees[~high_degree_mask], degrees[high_degree_mask]],
                bins=30, label=['Regular Nodes', 'High-Degree Nodes'],
                color=['blue', 'red'], alpha=0.7)
        ax6.set_yscale('log')
        ax6.set_title(f'High-Degree Nodes (>{high_degree_threshold:.0f})', fontweight='bold')
        ax6.set_xlabel('Degree')
        ax6.set_ylabel('Frequency (log scale)')
        ax6.legend()
        ax6.grid(True, alpha=0.3)

        # 7. 边类型分布
        ax7 = plt.subplot(3, 3, 7)
        edge_types = self.data['edge_type']
        if len(edge_types.shape) > 1:
            edge_types = edge_types.flatten()

        unique_types, type_counts = np.unique(edge_types, return_counts=True)
        ax7.bar(unique_types, type_counts, color='lightcoral', alpha=0.8)
        ax7.set_title('Edge Type Distribution', fontweight='bold')
        ax7.set_xlabel('Edge Type')
        ax7.set_ylabel('Count')
        ax7.grid(True, alpha=0.3)

        # 8. 节点类型分布
        ax8 = plt.subplot(3, 3, 8)
        node_categories = [
            ['Isolated Nodes', np.sum(degrees == 0)],
            ['Low Degree (1-2)', np.sum((degrees >= 1) & (degrees <= 2))],
            ['Medium Degree (3-10)', np.sum((degrees >= 3) & (degrees <= 10))],
            ['High Degree (>10)', np.sum(degrees > 10)]
        ]

        categories, counts = zip(*node_categories)
        ax8.bar(categories, counts, color=['gray', 'blue', 'green', 'red'], alpha=0.7)
        ax8.set_title('Node Categories by Degree', fontweight='bold')
        ax8.set_ylabel('Number of Nodes')
        ax8.tick_params(axis='x', rotation=45)
        ax8.grid(True, alpha=0.3)

        # 9. 图统计总结
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('tight')
        ax9.axis('off')

        total_nodes = len(degrees)
        isolated_nodes = np.sum(degrees == 0)
        active_nodes = total_nodes - isolated_nodes
        num_edges = self.data['edge_index'].shape[0]

        if total_nodes > 1:
            graph_density = num_edges / (total_nodes * (total_nodes - 1))
        else:
            graph_density = 0

        graph_summary = [
            ['Total Nodes', f'{total_nodes:,}'],
            ['Active Nodes', f'{active_nodes:,}'],
            ['Isolated Nodes', f'{isolated_nodes:,}'],
            ['Activity Rate', f'{active_nodes/total_nodes*100:.2f}%'],
            ['Total Edges', f'{num_edges:,}'],
            ['Graph Density', f'{graph_density:.2e}'],
            ['Edge Types', f'{len(unique_types)}'],
            ['Avg Degree', f'{np.mean(degrees[degrees>0]):.2f}']
        ]

        table = ax9.table(cellText=graph_summary,
                         colLabels=['Graph Metric', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)

        plt.tight_layout()
        plt.savefig('analysis/graph_structure_analysis_fixed.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Fixed graph structure analysis saved to analysis/graph_structure_analysis_fixed.png")

    def analyze_fraud_patterns_fixed(self):
        """修复版欺诈模式分析"""
        print("Analyzing fraud patterns (fixed version)...")

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

        # 1. 度分布对比
        ax1 = plt.subplot(3, 3, 1)
        if len(fraud_indices) > 0 and len(normal_indices) > 0:
            fraud_degrees = self.graph_stats['total_degrees'][fraud_indices]
            normal_degrees = self.graph_stats['total_degrees'][normal_indices]

            # 采样正常用户
            sample_size = min(len(fraud_degrees) * 10, len(normal_degrees))
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

        # 2. 特征差异分析
        ax2 = plt.subplot(3, 3, 2)
        if len(fraud_indices) > 10 and len(normal_indices) > 10:
            fraud_features = features[fraud_indices]
            normal_features = features[normal_indices[:min(len(normal_indices), len(fraud_indices)*5)]]

            feature_means_fraud = np.mean(fraud_features, axis=0)
            feature_means_normal = np.mean(normal_features, axis=0)
            feature_diff = feature_means_fraud - feature_means_normal

            x_pos = np.arange(len(feature_diff))
            bars = ax2.bar(x_pos, feature_diff, alpha=0.7, color='red')
            ax2.set_title('Feature Difference (Fraud - Normal)', fontweight='bold')
            ax2.set_xlabel('Feature Index')
            ax2.set_ylabel('Mean Difference')
            ax2.grid(True, alpha=0.3)

            # 标记最显著的差异
            max_diff_idx = np.argmax(np.abs(feature_diff))
            ax2.axvline(max_diff_idx, color='blue', linestyle='--', alpha=0.8)
            ax2.text(max_diff_idx, max(0, feature_diff[max_diff_idx]),
                    f'Max: {feature_diff[max_diff_idx]:.3f}',
                    ha='center', va='bottom' if feature_diff[max_diff_idx] > 0 else 'top')

        # 3. 特征重要性（基于区分度）
        ax3 = plt.subplot(3, 3, 3)
        if len(fraud_indices) > 10 and len(normal_indices) > 10:
            importance_scores = []
            for i in range(min(10, features.shape[1])):
                fraud_feat = features[fraud_indices, i]
                normal_feat = features[normal_indices[:min(len(normal_indices), len(fraud_indices)*5)], i]

                # 使用Cohen's d作为效应量
                pooled_std = np.sqrt(((len(fraud_feat)-1)*np.var(fraud_feat) +
                                    (len(normal_feat)-1)*np.var(normal_feat)) /
                                   (len(fraud_feat) + len(normal_feat) - 2))
                if pooled_std > 0:
                    cohens_d = abs(np.mean(fraud_feat) - np.mean(normal_feat)) / pooled_std
                else:
                    cohens_d = 0
                importance_scores.append(cohens_d)

            x_pos = np.arange(len(importance_scores))
            ax3.bar(x_pos, importance_scores, color='orange', alpha=0.7)
            ax3.set_title('Feature Importance (Cohen\'s d)', fontweight='bold')
            ax3.set_xlabel('Feature Index')
            ax3.set_ylabel('Effect Size')
            ax3.grid(True, alpha=0.3)

        # 4. 时间模式对比
        ax4 = plt.subplot(3, 3, 4)
        if len(fraud_indices) > 0:
            # 安全地处理边索引
            try:
                # 采样边以减少内存使用
                edge_sample_size = min(100000, len(edge_index))
                edge_sample_indices = np.random.choice(len(edge_index), edge_sample_size, replace=False)
                edge_sample = edge_index[edge_sample_indices]
                timestamp_sample = edge_timestamp[edge_sample_indices]

                # 检查边是否涉及欺诈用户
                fraud_edge_mask = np.isin(edge_sample[:, 0], fraud_indices) | np.isin(edge_sample[:, 1], fraud_indices)
                normal_edge_mask = ~fraud_edge_mask

                fraud_times = timestamp_sample[fraud_edge_mask]
                normal_times = timestamp_sample[normal_edge_mask]

                if len(fraud_times) > 0 and len(normal_times) > 0:
                    # 采样正常时间以便可视化
                    normal_sample_times = np.random.choice(normal_times,
                                                         min(len(fraud_times) * 5, len(normal_times)),
                                                         replace=False)

                    ax4.hist([normal_sample_times, fraud_times], bins=50, alpha=0.7,
                            label=['Normal Edges', 'Fraud-related Edges'],
                            color=['#4CAF50', '#FF5722'])
                    ax4.set_title('Temporal Pattern: Fraud vs Normal', fontweight='bold')
                    ax4.set_xlabel('Time (days)')
                    ax4.set_ylabel('Frequency')
                    ax4.set_yscale('log')
                    ax4.legend()
                    ax4.grid(True, alpha=0.3)

            except Exception as e:
                ax4.text(0.5, 0.5, f'Temporal analysis error:\n{str(e)[:50]}...',
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Temporal Pattern Analysis', fontweight='bold')

        # 5. 边类型使用模式
        ax5 = plt.subplot(3, 3, 5)
        if len(fraud_indices) > 0:
            try:
                # 采样分析边类型
                edge_sample_size = min(50000, len(edge_index))
                edge_sample_indices = np.random.choice(len(edge_index), edge_sample_size, replace=False)
                edge_sample = edge_index[edge_sample_indices]
                edge_type_sample = edge_types[edge_sample_indices]
                if len(edge_type_sample.shape) > 1:
                    edge_type_sample = edge_type_sample.flatten()

                fraud_edge_mask = np.isin(edge_sample[:, 0], fraud_indices) | np.isin(edge_sample[:, 1], fraud_indices)
                normal_edge_mask = ~fraud_edge_mask

                fraud_edge_types = edge_type_sample[fraud_edge_mask]
                normal_edge_types = edge_type_sample[normal_edge_mask]

                unique_types = np.unique(edge_type_sample)
                fraud_type_counts = [np.sum(fraud_edge_types == t) for t in unique_types]
                normal_type_counts = [np.sum(normal_edge_types == t) for t in unique_types]

                width = 0.35
                x = np.arange(len(unique_types))
                ax5.bar(x - width/2, normal_type_counts, width, label='Normal', alpha=0.7, color='#4CAF50')
                ax5.bar(x + width/2, fraud_type_counts, width, label='Fraud', alpha=0.7, color='#FF5722')
                ax5.set_title('Edge Type Patterns', fontweight='bold')
                ax5.set_xlabel('Edge Type')
                ax5.set_ylabel('Count')
                ax5.set_yscale('log')
                ax5.set_xticks(x)
                ax5.legend()
                ax5.grid(True, alpha=0.3)

            except Exception as e:
                ax5.text(0.5, 0.5, f'Edge type analysis error:\n{str(e)[:50]}...',
                        ha='center', va='center', transform=ax5.transAxes)
                ax5.set_title('Edge Type Analysis', fontweight='bold')

        # 6. 欺诈用户度统计
        ax6 = plt.subplot(3, 3, 6)
        if len(fraud_indices) > 0:
            fraud_degrees = self.graph_stats['total_degrees'][fraud_indices]
            normal_degrees = self.graph_stats['total_degrees'][normal_indices]

            degree_stats = [
                ['Fraud Users', f'{len(fraud_indices):,}'],
                ['Normal Users', f'{len(normal_indices):,}'],
                ['Avg Fraud Degree', f'{np.mean(fraud_degrees):.2f}'],
                ['Avg Normal Degree', f'{np.mean(normal_degrees):.2f}'],
                ['Degree Ratio', f'{np.mean(fraud_degrees)/np.mean(normal_degrees):.2f}' if np.mean(normal_degrees) > 0 else 'N/A'],
                ['Max Fraud Degree', f'{np.max(fraud_degrees)}'],
                ['Max Normal Degree', f'{np.max(normal_degrees)}']
            ]

            ax6.axis('tight')
            ax6.axis('off')
            table = ax6.table(cellText=degree_stats,
                             colLabels=['Metric', 'Value'],
                             cellLoc='center',
                             loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.5)

        # 7. 欺诈网络连接分析
        ax7 = plt.subplot(3, 3, 7)
        if len(fraud_indices) > 0:
            try:
                # 采样分析连接模式
                edge_sample_size = min(20000, len(edge_index))
                edge_sample_indices = np.random.choice(len(edge_index), edge_sample_size, replace=False)
                edge_sample = edge_index[edge_sample_indices]

                fraud_to_fraud = 0
                fraud_to_normal = 0

                for edge in edge_sample:
                    is_fraud_a = edge[0] in fraud_indices
                    is_fraud_b = edge[1] in fraud_indices

                    if is_fraud_a and is_fraud_b:
                        fraud_to_fraud += 1
                    elif (is_fraud_a and not is_fraud_b) or (not is_fraud_a and is_fraud_b):
                        fraud_to_normal += 1

                if fraud_to_fraud + fraud_to_normal > 0:
                    connection_types = ['Fraud-Fraud', 'Fraud-Normal']
                    counts = [fraud_to_fraud, fraud_to_normal]
                    percentages = [c/sum(counts)*100 for c in counts]

                    bars = ax7.bar(connection_types, counts, color=['red', 'orange'], alpha=0.7)
                    ax7.set_title('Fraud Connection Types', fontweight='bold')
                    ax7.set_ylabel('Count (Sampled)')
                    ax7.set_yscale('log')
                    ax7.grid(True, alpha=0.3)

                    # 添加百分比标签
                    for bar, count, pct in zip(bars, counts, percentages):
                        ax7.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                                f'{pct:.1f}%', ha='center', va='bottom')

            except Exception as e:
                ax7.text(0.5, 0.5, f'Connection analysis error:\n{str(e)[:50]}...',
                        ha='center', va='center', transform=ax7.transAxes)
                ax7.set_title('Connection Analysis', fontweight='bold')

        # 8. 欺诈检测难度评估
        ax8 = plt.subplot(3, 3, 8)
        ax8.axis('tight')
        ax8.axis('off')

        # 计算各种难度指标
        total_samples = len(train_labels)
        fraud_ratio = len(fraud_indices) / total_samples * 100
        imbalance_ratio = len(normal_indices) / len(fraud_indices) if len(fraud_indices) > 0 else float('inf')

        difficulty_factors = []
        if fraud_ratio < 1:
            difficulty_factors.append("Very low fraud ratio (<1%)")
        if imbalance_ratio > 100:
            difficulty_factors.append("Severe class imbalance")
        if len(fraud_indices) < 1000:
            difficulty_factors.append("Limited fraud samples")

        difficulty_level = "High" if len(difficulty_factors) >= 2 else "Medium" if len(difficulty_factors) == 1 else "Low"

        difficulty_summary = [
            ['Fraud Ratio', f'{fraud_ratio:.3f}%'],
            ['Imbalance Ratio', f'{imbalance_ratio:.1f}:1'] if imbalance_ratio != float('inf') else ['Imbalance Ratio', '∞'],
            ['Fraud Samples', f'{len(fraud_indices):,}'],
            ['Normal Samples', f'{len(normal_indices):,}'],
            ['Difficulty Level', difficulty_level],
            ['Key Challenges', str(len(difficulty_factors))]
        ]

        if difficulty_factors:
            for i, factor in enumerate(difficulty_factors):
                if i < 3:  # 最多显示3个挑战
                    difficulty_summary.append([f'Challenge {i+1}', factor[:30]])

        table = ax8.table(cellText=difficulty_summary,
                         colLabels=['Detection Difficulty', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)

        # 9. 建议和策略
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('tight')
        ax9.axis('off')

        recommendations = []
        if fraud_ratio < 1:
            recommendations.append("Use anomaly detection techniques")
            recommendations.append("Apply focal loss or class weighting")
        if imbalance_ratio > 50:
            recommendations.append("Consider SMOTE or data augmentation")
        recommendations.append("Use ensemble methods")
        recommendations.append("Apply feature engineering based on analysis")

        rec_text = '\n'.join([f"• {rec}" for rec in recommendations])
        ax9.text(0.1, 0.5, 'Fraud Detection Recommendations:\n\n' + rec_text,
                transform=ax9.transAxes, fontsize=11, verticalalignment='center')
        ax9.set_title('Detection Strategy Recommendations', fontweight='bold')

        plt.tight_layout()
        plt.savefig('analysis/fraud_pattern_analysis_fixed.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Fixed fraud pattern analysis saved to analysis/fraud_pattern_analysis_fixed.png")

    def generate_final_report(self):
        """生成最终综合报告"""
        print("Generating final comprehensive report...")

        # 获取基本统计信息
        train_mask = self.data['train_mask']
        train_labels = self.data['y'][train_mask]
        unique_labels, counts = np.unique(train_labels, return_counts=True)
        fraud_indices = train_mask[train_labels == 1]

        # 计算数据质量评分
        features = self.data['x']
        degrees = self.graph_stats['total_degrees']

        completeness = (1 - np.mean(features == 0)) * 100
        connectivity = np.sum(degrees > 0) / len(degrees) * 100
        balance_score = min(counts) / max(counts) * 100 if len(counts) > 1 else 100

        overall_quality = np.mean([completeness, connectivity, balance_score])

        # 生成报告
        report_lines = [
            "="*80,
            "           FINAL COMPREHENSIVE DATASET ANALYSIS REPORT",
            "="*80,
            "",
            "="*40 + " DATASET OVERVIEW " + "="*40,
            f"• Total Nodes: {self.data['x'].shape[0]:,}",
            f"• Feature Dimensions: {self.data['x'].shape[1]}",
            f"• Total Edges: {self.data['edge_index'].shape[0]:,}",
            f"• Training Samples: {len(train_mask):,}",
            f"• Test Samples: {len(self.data['test_mask']):,}",
            f"• Edge Types: {len(np.unique(self.data['edge_type']))}",
            "",
            "="*40 + " LABEL DISTRIBUTION " + "="*40,
        ]

        label_names = ['Normal Users', 'Fraud Users', 'Background Users Type 1', 'Background Users Type 2']
        total_train = len(train_labels)

        for label, count in zip(unique_labels, counts):
            percentage = count / total_train * 100
            label_name = label_names[label] if label < len(label_names) else f'Class {label}'
            report_lines.append(f"• {label_name}: {count:,} ({percentage:.3f}%)")

        # 添加类别不平衡分析
        if len(counts) > 1:
            imbalance_ratio = max(counts) / min(counts[counts > 0])
            fraud_ratio = counts[1] / total_train * 100 if 1 in unique_labels else 0
            report_lines.extend([
                f"",
                f"• Class Imbalance Ratio: {imbalance_ratio:.1f}:1",
                f"• Fraud Detection Difficulty: {'High' if fraud_ratio < 2 else 'Medium' if fraud_ratio < 5 else 'Low'}",
                f"• Fraud Ratio: {fraud_ratio:.3f}%"
            ])

        # 图结构统计
        report_lines.extend([
            "",
            "="*40 + " GRAPH STRUCTURE " + "="*40,
            f"• Active Nodes: {np.sum(degrees > 0):,} ({np.sum(degrees > 0)/len(degrees)*100:.2f}%)",
            f"• Isolated Nodes: {np.sum(degrees == 0):,} ({np.sum(degrees == 0)/len(degrees)*100:.2f}%)",
            f"• Average Degree: {np.mean(degrees[degrees > 0]):.2f}",
            f"• Median Degree: {np.median(degrees):.2f}",
            f"• Maximum Degree: {np.max(degrees):,}",
        ])

        # 特征质量分析
        feature_variances = np.var(features, axis=0)
        low_variance_features = np.sum(feature_variances < 0.01)
        missing_rate = np.mean(features == 0) * 100

        report_lines.extend([
            "",
            "="*40 + " FEATURE QUALITY " + "="*40,
            f"• Missing Value Rate: {missing_rate:.2f}%",
            f"• Low Variance Features (<0.01): {low_variance_features}/{len(feature_variances)}",
            f"• Average Feature Variance: {np.mean(feature_variances):.4f}",
        ])

        # 数据质量评分
        report_lines.extend([
            "",
            "="*40 + " DATA QUALITY SCORE " + "="*40,
            f"• Completeness: {completeness:.1f}/100",
            f"• Connectivity: {connectivity:.1f}/100",
            f"• Label Balance: {balance_score:.1f}/100",
            f"• Overall Quality: {overall_quality:.1f}/100",
        ])

        # 时间分析
        edge_timestamp = self.data['edge_timestamp']
        unique_days, day_counts = np.unique(edge_timestamp, return_counts=True)

        report_lines.extend([
            "",
            "="*40 + " TEMPORAL ANALYSIS " + "="*40,
            f"• Time Span: {np.max(unique_days) - np.min(unique_days) + 1} days",
            f"• Active Days: {len(unique_days)}",
            f"• Average Daily Activity: {np.mean(day_counts):.0f} edges",
            f"• Peak Daily Activity: {np.max(day_counts):,} edges",
            f"• Activity Volatility: {np.std(day_counts):.0f}",
        ])

        # 欺诈模式总结
        if len(fraud_indices) > 0:
            fraud_degrees = degrees[fraud_indices]
            normal_degrees = degrees[train_mask[train_labels == 0]]

            report_lines.extend([
                "",
                "="*40 + " FRAUD PATTERN SUMMARY " + "="*40,
                f"• Total Fraud Users: {len(fraud_indices):,}",
                f"• Average Fraud User Degree: {np.mean(fraud_degrees):.2f}",
                f"• Average Normal User Degree: {np.mean(normal_degrees):.2f}",
                f"• Degree Ratio (Fraud/Normal): {np.mean(fraud_degrees)/np.mean(normal_degrees):.2f}",
            ])

        # 建议部分
        report_lines.extend([
            "",
            "="*40 + " KEY RECOMMENDATIONS " + "="*40,
        ])

        if imbalance_ratio > 100:
            report_lines.extend([
                "• HIGH PRIORITY: Address severe class imbalance",
                "  - Use oversampling (SMOTE) for fraud cases",
                "  - Apply class weighting in loss function",
                "  - Consider anomaly detection approaches",
            ])

        if missing_rate > 10:
            report_lines.extend([
                "• MEDIUM PRIORITY: High missing value rate detected",
                "  - Implement proper missing value imputation",
                "  - Consider missing value indicators as features",
            ])

        if np.sum(degrees == 0) / len(degrees) > 0.3:
            report_lines.extend([
                "• MEDIUM PRIORITY: Many isolated nodes detected",
                "  - Consider node feature-only models for isolated nodes",
            ])

        report_lines.extend([
            "• GENERAL RECOMMENDATIONS:",
            "  - Use ensemble methods (Random Forest, XGBoost)",
            "  - Apply feature engineering based on analysis insights",
            "  - Consider graph neural networks for connectivity patterns",
            "  - Use cross-validation with stratified sampling",
        ])

        # 生成分析文件列表
        report_lines.extend([
            "",
            "="*40 + " GENERATED ANALYSIS FILES " + "="*40,
            "• analysis/deep_feature_analysis.png - Comprehensive feature analysis",
            "• analysis/graph_structure_analysis_fixed.png - Fixed graph structure analysis",
            "• analysis/fraud_pattern_analysis_fixed.png - Fixed fraud pattern analysis",
            "• analysis/detailed_label_analysis.png - Detailed label distribution",
            "• analysis/temporal_pattern_analysis.png - Advanced temporal analysis",
            "• analysis/final_comprehensive_report.txt - This text report",
        ])

        # 结束语
        report_lines.extend([
            "",
            "="*80,
            "                    ANALYSIS COMPLETED SUCCESSFULLY",
            "     All visualizations and reports are available in the 'analysis/' directory",
            "="*80,
        ])

        # 保存报告
        report_text = '\n'.join(report_lines)

        with open('analysis/final_comprehensive_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)

        # 同时打印关键信息到控制台
        print("\n" + "="*60)
        print("               FINAL ANALYSIS SUMMARY")
        print("="*60)
        print(f"Dataset: {self.data['x'].shape[0]:,} nodes, {self.data['edge_index'].shape[0]:,} edges")
        print(f"Labels: {len(train_labels):,} samples, {len(fraud_indices):,} fraud cases")
        print(f"Fraud ratio: {len(fraud_indices)/len(train_labels)*100:.3f}%")
        print(f"Data quality: {overall_quality:.1f}/100")
        print(f"Class imbalance: {imbalance_ratio:.1f}:1" if 'imbalance_ratio' in locals() else "Class imbalance: N/A")
        print("\nGenerated files:")
        print("• analysis/deep_feature_analysis.png")
        print("• analysis/graph_structure_analysis_fixed.png")
        print("• analysis/fraud_pattern_analysis_fixed.png")
        print("• analysis/final_comprehensive_report.txt")
        print("="*60)

    def run_final_analysis(self):
        """运行最终完整分析"""
        print("Starting FINAL comprehensive data analysis...")

        # 确保目录存在
        if not os.path.exists('analysis'):
            os.makedirs('analysis')

        # 运行所有分析模块
        modules = [
            ("Deep Feature Analysis", self.analyze_features_deep),
            ("Graph Structure Analysis", self.analyze_graph_structure_fixed),
            ("Fraud Pattern Analysis", self.analyze_fraud_patterns_fixed),
            ("Final Report Generation", self.generate_final_report),
        ]

        for module_name, module_func in modules:
            try:
                print(f"\n{'='*20} {module_name} {'='*20}")
                module_func()
                print(f"✅ {module_name} completed successfully")
            except Exception as e:
                print(f"❌ Error in {module_name}: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "="*60)
        print("🎉 FINAL COMPREHENSIVE ANALYSIS COMPLETED!")
        print("📁 All files saved to 'analysis/' directory")
        print("📊 Check the generated PNG files for detailed visualizations")
        print("📋 Read 'final_comprehensive_report.txt' for complete analysis")
        print("="*60)

# 主程序
if __name__ == "__main__":
    analyzer = FinalDetailedAnalyzer()
    analyzer.run_final_analysis()