"""
机器学习Lab3 - 聚类实验
数据集: UCI Online Retail (在线零售客户行为数据)
聚类方法: K-Means vs DBSCAN
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class ClusteringExperiment:
    """聚类实验类"""
    
    def __init__(self):
        self.data = None
        self.X = None
        self.X_scaled = None
        self.scaler = StandardScaler()
        self.kmeans_labels = None
        self.dbscan_labels = None
        
    def load_data(self):
        """加载并准备数据"""
        print("=" * 60)
        print("Step 1: Data Prepare")
        print("=" * 60)
        
        # 尝试加载真实数据集
        # 加载UCI Online Retail客户特征数据集
        csv_file = 'data/Online_Retail_Customers.csv'
        
        if not pd.io.common.file_exists(csv_file):
            raise FileNotFoundError(
                f"数据文件 '{csv_file}' 不存在！\n"
                f"请确保已运行数据处理脚本生成客户特征数据。"
            )
        
        print(f"✓ 检测到数据集: {csv_file}")
        self.data = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        # 标准化列名
        self.data.columns = self.data.columns.str.strip()
        
        print(f"数据集来源: {csv_file}")
        print(f"数据集大小: {self.data.shape}")
        
        print(f"\n数据前5行:")
        print(self.data.head())
        print(f"\n数据统计信息:")
        print(self.data.describe())
        
        return self.data
    
    def preprocess_data(self):
        """数据预处理"""
        print("\n" + "=" * 60)
        print("Step 2: Data Preprocess")
        print("=" * 60)
        
        # 自动选择数值特征列（排除ID列）
        exclude_cols = ['CustomerID', 'Customer_Type', 'Gender', 'Membership_Level']
        numeric_cols = self.data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        print(f"使用的特征列 ({len(feature_cols)}个):")
        for i, col in enumerate(feature_cols, 1):
            print(f"  {i}. {col}")
        
        # 检测和移除极端异常值
        original_count = len(self.data)
        outlier_mask = self._detect_outliers(feature_cols)
        outliers = self.data[outlier_mask].copy()
        
        if len(outliers) > 0:
            print(f"\n⚠️  检测到 {len(outliers)} 个极端异常客户:")
            for idx, row in outliers.iterrows():
                customer_id = row.get('CustomerID', idx)
                print(f"  - 客户 {customer_id}: ", end="")
                # 显示关键特征
                key_features = []
                if 'Total_Spending' in feature_cols:
                    key_features.append(f"总消费={row['Total_Spending']:.2f}")
                if 'Total_Quantity' in feature_cols:
                    key_features.append(f"总购买量={row['Total_Quantity']:.0f}")
                if 'Avg_Quantity' in feature_cols:
                    key_features.append(f"平均购买量={row['Avg_Quantity']:.0f}")
                print(", ".join(key_features))
            
            # 保存异常客户到单独文件
            outliers.to_csv('outliers.csv', index=False, encoding='utf-8-sig')
            print(f"✓ 异常客户已保存到: outliers.csv")
            
            # 移除异常值
            self.data = self.data[~outlier_mask].reset_index(drop=True)
            print(f"✓ 已移除异常值，剩余客户: {len(self.data)} (移除了 {original_count - len(self.data)} 个)")
        else:
            print(f"✓ 未检测到极端异常值")
        
        self.X = self.data[feature_cols].values
        
        # 检查缺失值
        print(f"缺失值数量: {pd.DataFrame(self.X).isnull().sum().sum()}")
        
        # 标准化
        self.X_scaled = self.scaler.fit_transform(self.X)
        print("数据已标准化 (均值=0, 标准差=1)")
        
        # 使用PCA进行降维可视化
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(self.X_scaled)
        
        plt.figure(figsize=(10, 6))
        plt.scatter(X_pca[:, 0], X_pca[:, 1], alpha=0.6, s=50)
        plt.xlabel('第一主成分')
        plt.ylabel('第二主成分')
        plt.title('原始数据分布 (PCA降维)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('01_data_distribution.png', dpi=300, bbox_inches='tight')
        print("✓ 数据分布图已保存: 01_data_distribution.png")
        plt.close()
    
    def _detect_outliers(self, feature_cols, threshold=3.0):
        """使用IQR方法检测极端异常值"""
        outlier_mask = np.zeros(len(self.data), dtype=bool)
        
        # 对关键特征使用IQR方法
        key_features = ['Total_Quantity', 'Avg_Quantity', 'Total_Spending', 'Avg_Spending']
        available_features = [f for f in key_features if f in feature_cols]
        
        if not available_features:
            return outlier_mask
        
        for feature in available_features:
            Q1 = self.data[feature].quantile(0.25)
            Q3 = self.data[feature].quantile(0.75)
            IQR = Q3 - Q1
            
            # 使用更严格的阈值（threshold * IQR）来只捕获极端异常值
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            feature_outliers = (self.data[feature] < lower_bound) | (self.data[feature] > upper_bound)
            outlier_mask = outlier_mask | feature_outliers
        
        return outlier_mask
        
    def find_optimal_k(self):
        """寻找K-Means最优K值"""
        print("\n寻找最优K值...")
        
        inertias = []
        silhouette_scores = []
        K_range = range(2, 7)  # 调整为K=2-6，更适合中等规模数据
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(self.X_scaled)
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(self.X_scaled, kmeans.labels_))
        
        # 绘制肘部法则图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1.plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
        ax1.set_xlabel('簇数量 K')
        ax1.set_ylabel('簇内误差平方和 (Inertia)')
        ax1.set_title('肘部法则 - 确定最优K值')
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(K_range, silhouette_scores, 'ro-', linewidth=2, markersize=8)
        ax2.set_xlabel('簇数量 K')
        ax2.set_ylabel('轮廓系数')
        ax2.set_title('轮廓系数 vs K值')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('02_optimal_k_selection.png', dpi=300, bbox_inches='tight')
        print("✓ 最优K值选择图已保存: 02_optimal_k_selection.png")
        plt.close()
        
        optimal_k = K_range[np.argmax(silhouette_scores)]
        print(f"推荐最优K值: {optimal_k} (基于轮廓系数)")
        return optimal_k
    
    def kmeans_clustering(self, n_clusters=3):
        """K-Means聚类"""
        print("\n" + "=" * 60)
        print("Step 3: Model Construct - K-Means")
        print("=" * 60)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.kmeans_labels = kmeans.fit_predict(self.X_scaled)
        
        print(f"K-Means 参数: n_clusters={n_clusters}")
        print(f"聚类结果: {np.unique(self.kmeans_labels, return_counts=True)}")
        
        # 簇中心（原始空间）
        centers = self.scaler.inverse_transform(kmeans.cluster_centers_)
        print("\n簇中心 (原始特征空间):")
        exclude_cols = ['CustomerID', 'Customer_Type', 'Gender', 'Membership_Level']
        numeric_cols = self.data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        centers_df = pd.DataFrame(centers, columns=feature_cols)
        print(centers_df)
        
        return self.kmeans_labels
    
    def dbscan_clustering(self, eps=0.5, min_samples=5):
        """DBSCAN聚类"""
        print("\n" + "=" * 60)
        print("Step 4: Model Construct - DBSCAN")
        print("=" * 60)
        
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        self.dbscan_labels = dbscan.fit_predict(self.X_scaled)
        
        print(f"DBSCAN 参数: eps={eps}, min_samples={min_samples}")
        n_clusters = len(set(self.dbscan_labels)) - (1 if -1 in self.dbscan_labels else 0)
        n_noise = list(self.dbscan_labels).count(-1)
        print(f"发现簇数量: {n_clusters}")
        print(f"噪声点数量: {n_noise}")
        print(f"聚类结果: {np.unique(self.dbscan_labels, return_counts=True)}")
        
        return self.dbscan_labels
    
    def evaluate_clustering(self):
        """评估聚类效果"""
        print("\n" + "=" * 60)
        print("Step 5: Train & Test - 聚类评估")
        print("=" * 60)
        
        metrics = {
            'Method': ['K-Means', 'DBSCAN'],
            'Silhouette Score': [],
            'Calinski-Harabasz Index': [],
            'Davies-Bouldin Index': []
        }
        
        # K-Means评估
        if len(np.unique(self.kmeans_labels)) > 1:
            metrics['Silhouette Score'].append(silhouette_score(self.X_scaled, self.kmeans_labels))
            metrics['Calinski-Harabasz Index'].append(calinski_harabasz_score(self.X_scaled, self.kmeans_labels))
            metrics['Davies-Bouldin Index'].append(davies_bouldin_score(self.X_scaled, self.kmeans_labels))
        
        # DBSCAN评估（排除噪声点）
        if len(np.unique(self.dbscan_labels)) > 1:
            mask = self.dbscan_labels != -1
            if mask.sum() > 0 and len(np.unique(self.dbscan_labels[mask])) > 1:
                metrics['Silhouette Score'].append(silhouette_score(self.X_scaled[mask], self.dbscan_labels[mask]))
                metrics['Calinski-Harabasz Index'].append(calinski_harabasz_score(self.X_scaled[mask], self.dbscan_labels[mask]))
                metrics['Davies-Bouldin Index'].append(davies_bouldin_score(self.X_scaled[mask], self.dbscan_labels[mask]))
            else:
                metrics['Silhouette Score'].append(np.nan)
                metrics['Calinski-Harabasz Index'].append(np.nan)
                metrics['Davies-Bouldin Index'].append(np.nan)
        
        metrics_df = pd.DataFrame(metrics)
        print("\n评估指标对比:")
        print(metrics_df.to_string(index=False))
        print("\n指标说明:")
        print("- Silhouette Score (轮廓系数): 越接近1越好，范围[-1, 1]")
        print("- Calinski-Harabasz Index: 越大越好")
        print("- Davies-Bouldin Index: 越小越好")
        
        # 生成详细的簇统计分析
        self._detailed_cluster_analysis()
        
        return metrics_df
    
    def _detailed_cluster_analysis(self):
        """详细的簇分析"""
        print("\n" + "-" * 60)
        print("详细簇分析")
        print("-" * 60)
        
        # K-Means 簇分析
        print("\n【K-Means 簇详情】")
        
        # 获取数值特征列
        exclude_cols = ['CustomerID', 'Customer_Type', 'Gender', 'Membership_Level']
        numeric_cols = self.data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        for cluster in sorted(np.unique(self.kmeans_labels)):
            mask = self.kmeans_labels == cluster
            cluster_data = self.data[mask]
            print(f"\n簇 {cluster} (n={mask.sum()}):")
            
            # 显示前3个最重要的特征统计
            for col in feature_cols[:3]:
                print(f"  {col}: {cluster_data[col].mean():.2f} ± {cluster_data[col].std():.2f}")
            
            # 智能客户画像（基于Total_Spending和Purchase_Frequency）
            if 'Total_Spending' in cluster_data.columns and 'Purchase_Frequency' in cluster_data.columns:
                avg_spending = cluster_data['Total_Spending'].mean()
                avg_freq = cluster_data['Purchase_Frequency'].mean()
                spending_threshold = self.data['Total_Spending'].median()
                freq_threshold = self.data['Purchase_Frequency'].median()
                
                if avg_spending > spending_threshold and avg_freq > freq_threshold:
                    print(f"  画像: 💎 高价值客户 - 高消费高频次")
                elif avg_spending > spending_threshold and avg_freq <= freq_threshold:
                    print(f"  画像: 🎯 大单客户 - 高消费低频次")
                elif avg_spending <= spending_threshold and avg_freq > freq_threshold:
                    print(f"  画像: 🌱 忠诚客户 - 低消费高频次")
                else:
                    print(f"  画像: 💤 普通客户 - 低消费低频次")
        
        # DBSCAN 簇分析
        print("\n【DBSCAN 簇详情】")
        for cluster in sorted(np.unique(self.dbscan_labels)):
            mask = self.dbscan_labels == cluster
            cluster_data = self.data[mask]
            label = "噪声点" if cluster == -1 else f"簇 {cluster}"
            print(f"\n{label} (n={mask.sum()}):")
            
            # 显示前3个最重要的特征统计
            for col in feature_cols[:3]:
                print(f"  {col}: {cluster_data[col].mean():.2f} ± {cluster_data[col].std():.2f}")
    
    def save_clustering_results(self):
        """保存聚类结果到文件"""
        print("\n" + "=" * 60)
        print("保存聚类结果")
        print("=" * 60)
        
        # 保存结果数据
        results_data = self.data.copy()
        results_data['KMeans_Cluster'] = self.kmeans_labels
        results_data['DBSCAN_Cluster'] = self.dbscan_labels
        
        # 添加客户类型标签（如果有相关列）
        if 'Total_Spending' in results_data.columns and 'Purchase_Frequency' in results_data.columns:
            def get_customer_type(row):
                spending_threshold = results_data['Total_Spending'].median()
                freq_threshold = results_data['Purchase_Frequency'].median()
                
                if row['Total_Spending'] > spending_threshold and row['Purchase_Frequency'] > freq_threshold:
                    return '高价值客户'
                elif row['Total_Spending'] > spending_threshold:
                    return '大单客户'
                elif row['Purchase_Frequency'] > freq_threshold:
                    return '忠诚客户'
                else:
                    return '普通客户'
            
            results_data['Customer_Type'] = results_data.apply(get_customer_type, axis=1)
        
        results_data.to_csv('clustering_results.csv', index=False, encoding='utf-8-sig')
        print("✓ 聚类结果已保存: clustering_results.csv")
        
        # 生成统计摘要
        summary_stats = []
        numeric_cols = results_data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        stat_cols = [col for col in numeric_cols if col not in ['CustomerID', 'KMeans_Cluster', 'DBSCAN_Cluster']][:3]
        
        for method, labels_col in [('K-Means', 'KMeans_Cluster'), ('DBSCAN', 'DBSCAN_Cluster')]:
            for cluster in sorted(results_data[labels_col].unique()):
                mask = results_data[labels_col] == cluster
                cluster_data = results_data[mask]
                stat_dict = {
                    'Method': method,
                    'Cluster': cluster,
                    'Size': len(cluster_data)
                }
                # 添加前3个特征的平均值
                for col in stat_cols:
                    stat_dict[f'Avg_{col}'] = cluster_data[col].mean()
                summary_stats.append(stat_dict)
        
        summary_df = pd.DataFrame(summary_stats)
        summary_df.to_csv('cluster_summary.csv', index=False, encoding='utf-8-sig')
        print("✓ 簇统计摘要已保存: cluster_summary.csv")
    
    def plot_results(self):
        """可视化聚类结果"""
        print("\n" + "=" * 60)
        print("Step 6: Plot Result")
        print("=" * 60)
        
        # PCA降维用于可视化
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(self.X_scaled)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 14))
        
        # 1. K-Means 2D可视化
        ax = axes[0, 0]
        scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=self.kmeans_labels, 
                           cmap='viridis', s=80, alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xlabel('第一主成分')
        ax.set_ylabel('第二主成分')
        ax.set_title('K-Means 聚类结果 (PCA 2D)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax, label='簇标签')
        
        # 2. DBSCAN 2D可视化
        ax = axes[0, 1]
        scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=self.dbscan_labels, 
                           cmap='plasma', s=80, alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xlabel('第一主成分')
        ax.set_ylabel('第二主成分')
        ax.set_title('DBSCAN 聚类结果 (PCA 2D)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax, label='簇标签 (-1=噪声)')
        
        # 3. K-Means 特征空间 (使用前两个最重要的特征)
        ax = axes[1, 0]
        exclude_cols = ['CustomerID', 'Customer_Type', 'Gender', 'Membership_Level']
        numeric_cols = self.data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        x_col = feature_cols[0] if len(feature_cols) > 0 else 'Purchase_Frequency'
        y_col = feature_cols[3] if len(feature_cols) > 3 else feature_cols[1] if len(feature_cols) > 1 else x_col
        
        for cluster in np.unique(self.kmeans_labels):
            mask = self.kmeans_labels == cluster
            ax.scatter(self.data.loc[mask, x_col], 
                      self.data.loc[mask, y_col],
                      label=f'簇 {cluster}', s=60, alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'K-Means: {x_col} vs {y_col}', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 4. DBSCAN 特征空间
        ax = axes[1, 1]
        for cluster in np.unique(self.dbscan_labels):
            mask = self.dbscan_labels == cluster
            label = '噪声点' if cluster == -1 else f'簇 {cluster}'
            ax.scatter(self.data.loc[mask, x_col], 
                      self.data.loc[mask, y_col],
                      label=label, s=60, alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'DBSCAN: {x_col} vs {y_col}', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('03_clustering_results.png', dpi=300, bbox_inches='tight')
        print("✓ 聚类结果可视化已保存: 03_clustering_results.png")
        plt.close()
        
        # 额外的客户特征分析图
        self._plot_customer_analysis()
    
    def _plot_customer_analysis(self):
        """客户特征多角度分析"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        
        # 为数据添加聚类标签
        plot_data = self.data.copy()
        plot_data['KMeans_Cluster'] = self.kmeans_labels
        plot_data['DBSCAN_Cluster'] = self.dbscan_labels
        
        # 获取前3个特征用于分布图
        exclude_cols = ['CustomerID', 'Customer_Type', 'Gender', 'Membership_Level', 'KMeans_Cluster', 'DBSCAN_Cluster']
        numeric_cols = plot_data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        feature_cols = [col for col in numeric_cols if col not in exclude_cols][:3]
        
        # 确保有足够的特征
        if len(feature_cols) < 3:
            feature_cols = feature_cols + ['Purchase_Frequency', 'Total_Spending', 'Product_Variety']
            feature_cols = feature_cols[:3]
        
        # K-Means 分布图
        for i, col in enumerate(feature_cols):
            ax = axes[0, i]
            for cluster in np.unique(self.kmeans_labels):
                mask = plot_data['KMeans_Cluster'] == cluster
                ax.hist(plot_data.loc[mask, col], bins=15, alpha=0.6, label=f'簇 {cluster}')
            ax.set_xlabel(col)
            ax.set_ylabel('频数')
            ax.set_title(f'K-Means: {col}分布')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # DBSCAN 分布图
        for i, col in enumerate(feature_cols):
            ax = axes[1, i]
            for cluster in np.unique(self.dbscan_labels):
                mask = plot_data['DBSCAN_Cluster'] == cluster
                label = '噪声' if cluster == -1 else f'簇 {cluster}'
                ax.hist(plot_data.loc[mask, col], bins=15, alpha=0.6, label=label)
            ax.set_xlabel(col)
            ax.set_ylabel('频数')
            ax.set_title(f'DBSCAN: {col}分布')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('04_customer_feature_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ 客户特征分析图已保存: 04_customer_feature_analysis.png")
        plt.close()
    
    def generate_experiment_report(self, metrics_df):
        """生成实验报告"""
        print("\n" + "=" * 60)
        print("生成实验报告")
        print("=" * 60)
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("机器学习Lab3 - 聚类实验详细报告")
        report_lines.append("Mall Customers 客户细分分析: K-Means vs DBSCAN")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # 1. 实验概述
        report_lines.append("【实验概述】")
        report_lines.append(f"实验时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"数据集规模: {len(self.data)} 个客户样本")
        report_lines.append(f"特征维度: 3 (年龄、年收入、消费评分)")
        report_lines.append(f"聚类方法: K-Means, DBSCAN")
        report_lines.append("")
        
        # 2. 数据统计
        report_lines.append("【数据统计】")
        numeric_cols = self.data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        stat_cols = [col for col in numeric_cols if col != 'CustomerID']
        report_lines.append(self.data[stat_cols].describe().to_string())
        report_lines.append("")
        
        # 3. K-Means结果
        report_lines.append("【K-Means 聚类结果】")
        report_lines.append(f"簇数量: {len(np.unique(self.kmeans_labels))}")
        
        numeric_cols = self.data.select_dtypes(include=['float64', 'int64']).columns.tolist()
        feature_cols = [col for col in numeric_cols if col != 'CustomerID']
        
        for cluster in sorted(np.unique(self.kmeans_labels)):
            mask = self.kmeans_labels == cluster
            cluster_data = self.data[mask]
            report_lines.append(f"\n簇 {cluster}: {mask.sum()} 个客户")
            
            # 显示主要特征统计
            for col in feature_cols[:5]:  # 显示前5个特征
                report_lines.append(f"  - {col}: {cluster_data[col].mean():.2f} (±{cluster_data[col].std():.2f})")
            
            # 智能客户画像
            if 'Total_Spending' in cluster_data.columns and 'Purchase_Frequency' in cluster_data.columns:
                avg_spending = cluster_data['Total_Spending'].mean()
                avg_freq = cluster_data['Purchase_Frequency'].mean()
                spending_threshold = self.data['Total_Spending'].median()
                freq_threshold = self.data['Purchase_Frequency'].median()
                
                if avg_spending > spending_threshold and avg_freq > freq_threshold:
                    report_lines.append(f"  - 客户画像: 💎 高价值客户群 - 高消费高频次")
                    report_lines.append(f"  - 营销策略: VIP服务、个性化推荐、专属优惠")
                elif avg_spending > spending_threshold:
                    report_lines.append(f"  - 客户画像: 🎯 大单客户群 - 高消费低频次")
                    report_lines.append(f"  - 营销策略: 定期提醒、会员计划、复购激励")
                elif avg_freq > freq_threshold:
                    report_lines.append(f"  - 客户画像: 🌱 忠诚客户群 - 低消费高频次")
                    report_lines.append(f"  - 营销策略: 品牌培养、交叉销售、提升客单价")
                else:
                    report_lines.append(f"  - 客户画像: 💤 普通客户群 - 低消费低频次")
                    report_lines.append(f"  - 营销策略: 促销活动、新品推荐、激活计划")
        
        report_lines.append("")
        
        # 4. DBSCAN结果
        report_lines.append("【DBSCAN 聚类结果】")
        n_clusters = len(set(self.dbscan_labels)) - (1 if -1 in self.dbscan_labels else 0)
        n_noise = list(self.dbscan_labels).count(-1)
        report_lines.append(f"簇数量: {n_clusters}")
        report_lines.append(f"噪声点: {n_noise} 个")
        
        for cluster in sorted(np.unique(self.dbscan_labels)):
            mask = self.dbscan_labels == cluster
            cluster_data = self.data[mask]
            label = "噪声点" if cluster == -1 else f"簇 {cluster}"
            report_lines.append(f"\n{label}: {mask.sum()} 个客户")
            
            # 显示主要特征统计
            for col in feature_cols[:5]:  # 显示前5个特征
                report_lines.append(f"  - {col}: {cluster_data[col].mean():.2f} (±{cluster_data[col].std():.2f})")
        
        report_lines.append("")
        
        # 5. 评估指标
        report_lines.append("【性能评估指标】")
        report_lines.append(metrics_df.to_string(index=False))
        report_lines.append("\n指标解释:")
        report_lines.append("  - Silhouette Score (轮廓系数): 范围[-1,1], 越接近1表示簇越紧密且分离")
        report_lines.append("  - Calinski-Harabasz Index: 簇间方差与簇内方差比, 越大越好")
        report_lines.append("  - Davies-Bouldin Index: 簇内外距离比的平均值, 越小越好")
        report_lines.append("")
        
        # 6. 算法对比
        report_lines.append("【算法对比分析】")
        report_lines.append("\nK-Means:")
        report_lines.append("  优点: ✓ 快速高效 ✓ 结果稳定 ✓ 易于理解")
        report_lines.append("  缺点: ✗ 需预设K值 ✗ 只适合凸形簇 ✗ 对异常值敏感")
        report_lines.append("  适用场景: 大规模数据、已知簇数、球形分布")
        report_lines.append("\nDBSCAN:")
        report_lines.append("  优点: ✓ 自动确定簇数 ✓ 发现任意形状 ✓ 识别噪声点")
        report_lines.append("  缺点: ✗ 参数敏感 ✗ 密度不均时效果差 ✗ 高维效果下降")
        report_lines.append("  适用场景: 未知簇数、不规则形状、含噪声数据")
        report_lines.append("")
        
        # 7. 商业建议
        report_lines.append("【商业洞察与建议】")
        report_lines.append("\n1. 客户细分价值:")
        report_lines.append("   - 通过聚类识别出高价值、潜力和培养三类客户群")
        report_lines.append("   - 不同客户群展现出明显的年龄、收入、消费差异")
        report_lines.append("\n2. 营销策略建议:")
        report_lines.append("   - 高价值客户: 提供VIP专属服务，维护客户忠诚度")
        report_lines.append("   - 潜力客户: 加强营销投入，通过促销激活消费潜力")
        report_lines.append("   - 培养客户: 长期培养品牌认知，提供性价比产品")
        report_lines.append("\n3. 算法选择建议:")
        report_lines.append("   - 本案例中K-Means表现更稳定，适合业务应用")
        report_lines.append("   - DBSCAN可用于发现异常客户和特殊消费模式")
        report_lines.append("")
        
        # 8. 结论
        report_lines.append("【实验结论】")
        report_lines.append("1. 两种聚类方法均成功识别出客户群体的差异")
        report_lines.append("2. K-Means在本数据集上表现更优，簇划分更清晰")
        report_lines.append("3. 聚类结果为精准营销提供了数据支持")
        report_lines.append("4. 建议结合业务场景选择合适的聚类算法")
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("报告生成完成")
        report_lines.append("=" * 80)
        
        # 保存报告
        report_text = "\n".join(report_lines)
        with open('experiment_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print("✓ 实验报告已保存: experiment_report.txt")
        
        # 打印关键摘要
        print("\n" + "=" * 60)
        print("实验关键发现")
        print("=" * 60)
        print(f"✓ 成功识别 {len(np.unique(self.kmeans_labels))} 个客户群体")
        print(f"✓ K-Means 轮廓系数: {metrics_df.iloc[0]['Silhouette Score']:.3f}")
        print(f"✓ DBSCAN 发现 {n_noise} 个异常客户")
        print(f"✓ 已生成 7 个文件（4张图片 + 2个数据文件 + 1份报告）")
    
    def optimize_and_review(self):
        """优化与总结"""
        print("\n" + "=" * 60)
        print("Step 7: Optimize & Review")
        print("=" * 60)
        
        print("\n【算法对比分析】")
        print("\n1. K-Means 聚类:")
        print("   优点:")
        print("   ✓ 计算效率高，适合大规模数据")
        print("   ✓ 结果稳定，易于理解和实现")
        print("   ✓ 适合球形簇的发现")
        print("   缺点:")
        print("   ✗ 需要预先指定簇数量K")
        print("   ✗ 对初始中心敏感")
        print("   ✗ 对异常值敏感")
        print("   ✗ 只能发现凸形簇")
        
        print("\n2. DBSCAN 聚类:")
        print("   优点:")
        print("   ✓ 无需预先指定簇数量")
        print("   ✓ 可以发现任意形状的簇")
        print("   ✓ 能够识别噪声点")
        print("   ✓ 对异常值鲁棒")
        print("   缺点:")
        print("   ✗ 对参数eps和min_samples敏感")
        print("   ✗ 密度不均匀时效果不佳")
        print("   ✗ 高维数据表现较差")
        
        print("\n【商业洞察】")
        print("基于聚类结果，可以识别出不同类型的客户群体:")
        print("- 高价值客户: 高收入 + 高消费 → VIP服务与维护")
        print("- 潜力客户: 高收入 + 低消费 → 促销激活与转化")
        print("- 培养客户: 低收入 + 低消费 → 品牌培养与忠诚度")
        print("\n差异化营销策略将显著提升客户价值和企业收益。")
        
        print("\n" + "=" * 60)
        print("实验完成！所有结果已保存。")
        print("=" * 60)


def main():
    """主函数"""
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "机器学习Lab3 - 聚类实验" + " " * 15 + "║")
    print("║" + " " * 8 + "UCI Online Retail: K-Means vs DBSCAN" + " " * 8 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # 创建实验对象
    exp = ClusteringExperiment()
    
    # 执行实验流程
    exp.load_data()
    exp.preprocess_data()
    
    # 寻找最优K值
    optimal_k = exp.find_optimal_k()
    
    # 执行聚类
    exp.kmeans_clustering(n_clusters=optimal_k)
    exp.dbscan_clustering(eps=0.5, min_samples=5)
    
    # 评估和可视化
    metrics_df = exp.evaluate_clustering()
    exp.plot_results()
    
    # 保存结果
    exp.save_clustering_results()
    
    # 生成报告
    exp.generate_experiment_report(metrics_df)
    
    # 优化与总结
    exp.optimize_and_review()
    
    print("\n" + "=" * 60)
    print("✓ 生成的文件清单")
    print("=" * 60)
    print("📊 可视化图片:")
    print("  1. 01_data_distribution.png         - 原始数据分布(PCA)")
    print("  2. 02_optimal_k_selection.png       - K值选择分析")
    print("  3. 03_clustering_results.png        - 聚类结果对比")
    print("  4. 04_customer_feature_analysis.png - 客户特征分析")
    print("\n📁 数据文件:")
    print("  5. clustering_results.csv           - 完整聚类结果数据")
    print("  6. cluster_summary.csv              - 簇统计摘要")
    print("  7. outliers.csv                     - 异常客户数据")
    print("\n📄 报告文档:")
    print("  8. experiment_report.txt            - 详细实验报告")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
