import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from matplotlib.gridspec import GridSpec

# 设置学术风格
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

# 加载数据
print("Loading dataset...")
data = np.load('phase1_gdata.npz')
x = data['x']
y = data['y'].flatten()
edge_index = data['edge_index']
edge_type = data['edge_type'].flatten()
edge_timestamp = data['edge_timestamp'].flatten()
train_mask = data['train_mask']
test_mask = data['test_mask']

print(f"Dataset loaded: {x.shape[0]} nodes, {x.shape[1]} features, {edge_index.shape[0]} edges")


def plot_node_features():
    """生成节点特征的学术化统计图表"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 1. 特征分布的箱线图
    ax1 = axes[0]
    positions = range(x.shape[1])
    bp = ax1.boxplot([x[:, i] for i in range(x.shape[1])], 
                      positions=positions, 
                      patch_artist=True,
                      showfliers=False,
                      widths=0.6)
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_alpha(0.7)
    ax1.set_xlabel('Feature Dimension', fontsize=11)
    ax1.set_ylabel('Feature Value', fontsize=11)
    ax1.set_title('(a) Distribution of Node Features Across Dimensions', fontweight='bold', loc='left', fontsize=12)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(positions)
    
    # 2. 特征相关性矩阵
    ax2 = axes[1]
    corr_matrix = np.corrcoef(x.T)
    im = ax2.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
    ax2.set_xticks(range(x.shape[1]))
    ax2.set_yticks(range(x.shape[1]))
    ax2.set_xlabel('Feature Dimension', fontsize=11)
    ax2.set_ylabel('Feature Dimension', fontsize=11)
    ax2.set_title('(b) Feature Correlation Matrix', fontweight='bold', loc='left', fontsize=12)
    cbar = plt.colorbar(im, ax=ax2)
    cbar.set_label('Pearson Correlation', rotation=270, labelpad=15)
    
    plt.suptitle('Node Feature Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('figure1_node_features.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('figure1_node_features.png', dpi=300, bbox_inches='tight')
    print("Figure 1 saved: Node Features Analysis")
    plt.close()


def plot_label_distribution():
    """生成标签分布的学术化统计图表"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 分离训练集和测试集标签
    train_labels = y[train_mask]
    train_labels_clean = train_labels[train_labels != -100]
    
    # 统计标签分布
    unique_labels, counts = np.unique(train_labels_clean, return_counts=True)
    
    # 1. 标签分布条形图（带百分比）
    ax1 = axes[0]
    colors = sns.color_palette("Set2", len(unique_labels))
    bars = ax1.bar(unique_labels, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # 添加数值标签
    for i, (bar, count) in enumerate(zip(bars, counts)):
        height = bar.get_height()
        percentage = count / len(train_labels_clean) * 100
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax1.set_xlabel('Class Label', fontsize=11)
    ax1.set_ylabel('Number of Samples', fontsize=11)
    ax1.set_title('(a) Class Distribution in Training Set', fontweight='bold', loc='left', fontsize=12)
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax1.set_xticks(unique_labels)
    
    # 2. 训练集/测试集分布对比
    ax2 = axes[1]
    train_size = len(train_mask)
    test_size = len(test_mask)
    labeled_size = len(train_labels_clean)
    unlabeled_size = train_size - labeled_size
    
    categories = ['Labeled\nTrain', 'Unlabeled\nTrain', 'Test']
    sizes = [labeled_size, unlabeled_size, test_size]
    colors_split = ['#2ecc71', '#f39c12', '#3498db']
    bars = ax2.bar(categories, sizes, color=colors_split, alpha=0.8, edgecolor='black', linewidth=1.2)
    
    for bar, size in zip(bars, sizes):
        height = bar.get_height()
        percentage = size / x.shape[0] * 100
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{size}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax2.set_ylabel('Number of Nodes', fontsize=11)
    ax2.set_title('(b) Train-Test Split Overview', fontweight='bold', loc='left', fontsize=12)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    plt.suptitle('Label Distribution Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('figure2_label_distribution.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('figure2_label_distribution.png', dpi=300, bbox_inches='tight')
    print("Figure 2 saved: Label Distribution Analysis")
    plt.close()


def plot_graph_structure():
    """生成图结构的学术化统计图表"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 计算度数统计
    in_degrees = np.bincount(edge_index[:, 1], minlength=x.shape[0])
    out_degrees = np.bincount(edge_index[:, 0], minlength=x.shape[0])
    total_degrees = in_degrees + out_degrees
    
    # 1. 度数分布（对数尺度）
    ax1 = axes[0]
    degree_counts = np.bincount(total_degrees)
    non_zero_degrees = np.where(degree_counts > 0)[0]
    ax1.loglog(non_zero_degrees, degree_counts[non_zero_degrees], 
               'o-', color='steelblue', markersize=5, linewidth=2, alpha=0.7, label='Observed')
    
    # 拟合幂律分布
    if len(non_zero_degrees) > 1:
        valid_idx = degree_counts[non_zero_degrees] > 0
        if valid_idx.sum() > 1:
            z = np.polyfit(np.log(non_zero_degrees[valid_idx]), 
                          np.log(degree_counts[non_zero_degrees][valid_idx]), 1)
            p = np.poly1d(z)
            ax1.loglog(non_zero_degrees[valid_idx], 
                      np.exp(p(np.log(non_zero_degrees[valid_idx]))), 
                      '--', color='red', linewidth=2, alpha=0.7, 
                      label=f'Power-law fit: γ≈{-z[0]:.2f}')
    
    ax1.set_xlabel('Degree (k)', fontsize=11)
    ax1.set_ylabel('Frequency P(k)', fontsize=11)
    ax1.set_title('(a) Degree Distribution (Log-Log Scale)', fontweight='bold', loc='left', fontsize=12)
    ax1.grid(True, alpha=0.3, linestyle='--', which='both')
    ax1.legend()
    
    # 2. 边类型分布
    ax2 = axes[1]
    edge_type_counts = np.bincount(edge_type)
    edge_type_ids = np.where(edge_type_counts > 0)[0]
    colors_edge = sns.color_palette("Set3", len(edge_type_ids))
    bars = ax2.bar(edge_type_ids, edge_type_counts[edge_type_ids], 
                   color=colors_edge, alpha=0.8, edgecolor='black', linewidth=1.2)
    
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax2.set_xlabel('Edge Type', fontsize=11)
    ax2.set_ylabel('Number of Edges', fontsize=11)
    ax2.set_title('(b) Edge Type Distribution', fontweight='bold', loc='left', fontsize=12)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.set_xticks(edge_type_ids)
    
    plt.suptitle('Graph Structure Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('figure3_graph_structure.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('figure3_graph_structure.png', dpi=300, bbox_inches='tight')
    print("Figure 3 saved: Graph Structure Analysis")
    plt.close()


# 生成所有图表
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Academic Statistical Analysis of Graph Dataset")
    print("="*60 + "\n")
    
    print("Generating Figure 1: Node Features Analysis...")
    plot_node_features()
    
    print("Generating Figure 2: Label Distribution Analysis...")
    plot_label_distribution()
    
    print("Generating Figure 3: Graph Structure Analysis...")
    plot_graph_structure()
    
    print("\n" + "="*60)
    print("All figures generated successfully!")
    print("Output files:")
    print("  - figure1_node_features.pdf/png")
    print("  - figure2_label_distribution.pdf/png")
    print("  - figure3_graph_structure.pdf/png")
    print("="*60 + "\n")
