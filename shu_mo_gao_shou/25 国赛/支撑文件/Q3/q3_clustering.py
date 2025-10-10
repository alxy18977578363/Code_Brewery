import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 设置学术风格的绘图参数
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial', 'DejaVu Sans']  # 添加中文字体
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.dpi'] = 300

class AcademicRiskGroupingAnalysis:
    """
    学术风格的风险评估分组分析
    """
    
    def __init__(self, output_directory):
        self.output_directory = output_directory
        self.risk_assessments = None
        self.grouping_output = None
        self.bmi_categories = None
        
    def import_risk_data(self, risk_data_path):
        """导入风险评估数据"""
        print("正在导入风险评估数据...")
        self.risk_assessments = pd.read_csv(risk_data_path)
        print(f"数据导入完成：共 {len(self.risk_assessments)} 条孕产妇记录")
        return self.risk_assessments
    
    def find_optimal_clusters(self, max_clusters=8):
        """使用肘部准则确定最佳聚类数量"""
        print("正在确定最佳聚类数量...")
        
        risk_values = self.risk_assessments[['risk_score']].values
        
        # 计算不同聚类数的惯性值
        inertia_values = []
        cluster_range = range(2, max_clusters + 1)
        
        for k_val in cluster_range:
            kmeans_model = KMeans(n_clusters=k_val, random_state=42, n_init=10)
            kmeans_model.fit(risk_values)
            inertia_values.append(kmeans_model.inertia_)
        
        # 计算肘部点（二阶导数最大值）
        if len(inertia_values) >= 3:
            second_derivs = []
            for i in range(1, len(inertia_values) - 1):
                second_deriv = inertia_values[i-1] - 2*inertia_values[i] + inertia_values[i+1]
                second_derivs.append(second_deriv)
            
            best_k = cluster_range[np.argmax(second_derivs) + 1]
        else:
            best_k = 5  # 默认值
        
        print(f"最佳聚类数量：{best_k}")
        return best_k
    
    def execute_risk_grouping(self, k_value=None):
        """执行风险评估分组聚类"""
        print("正在进行风险评估分组...")
        
        if k_value is None:
            k_value = self.find_optimal_clusters()
        
        # 准备数据
        risk_values = self.risk_assessments[['risk_score']].values
        
        # 执行K-means聚类
        kmeans_model = KMeans(n_clusters=k_value, random_state=42, n_init=10)
        cluster_assignments = kmeans_model.fit_predict(risk_values)
        
        # 创建分组结果
        self.grouping_output = self.risk_assessments.copy()
        self.grouping_output['风险层级标识'] = cluster_assignments
        
        # 按风险评分排序分组
        risk_order = self.grouping_output.groupby('风险层级标识')['risk_score'].mean().sort_values().index
        id_mapping = {original_id: new_id for new_id, original_id in enumerate(risk_order)}
        self.grouping_output['风险层级标识'] = self.grouping_output['风险层级标识'].map(id_mapping)
        
        print(f"风险评估分组完成：共 {k_value} 个风险层级")
        return self.grouping_output
    
    def map_to_bmi_categories(self):
        """应用数据驱动的BMI分类规则"""
        print("正在应用数据驱动的BMI分类...")
        
        # 分析BMI分布特征
        bmi_values = self.grouping_output['avg_bmi']
        
        # 使用分位数方法确定切割点
        quartile_25 = np.percentile(bmi_values, 25)
        quartile_50 = np.percentile(bmi_values, 50) 
        quartile_75 = np.percentile(bmi_values, 75)
        
        # 调整切割点为更合理的数值
        natural_thresholds = [
            round(quartile_25, 1),  # 25分位点
            round(quartile_50, 1),  # 50分位点  
            round(quartile_75, 1)   # 75分位点
        ]
        
        # 确保切割点间有足够间隔
        final_thresholds = []
        for i, threshold in enumerate(natural_thresholds):
            if i == 0 or threshold - final_thresholds[-1] >= 1.5:
                final_thresholds.append(threshold)
        
        print(f"数据驱动的BMI阈值：{final_thresholds}")
        
        # 创建BMI分类
        self.bmi_categories = self.generate_bmi_categories(final_thresholds)
        
        print(f"BMI分类完成，使用阈值：{final_thresholds}")
        return self.bmi_categories, final_thresholds
    
    def generate_bmi_categories(self, threshold_values):
        """根据阈值创建BMI分类"""
        bmi_categories_df = self.grouping_output.copy()
        
        # 创建BMI分类标签
        bmi_categories_df['BMI分组'] = pd.cut(
            bmi_categories_df['avg_bmi'], 
            bins=[-np.inf] + threshold_values + [np.inf],
            labels=[f'类别{i}' for i in range(len(threshold_values) + 1)]
        )
        
        # 重新编号分类
        category_mapping = {f'类别{i}': i for i in range(len(threshold_values) + 1)}
        bmi_categories_df['BMI分组ID'] = bmi_categories_df['BMI分组'].map(category_mapping)
        
        return bmi_categories_df
    
    def generate_elbow_analysis_plot(self, max_clusters=8):
        """生成肘部法则分析图 - 学术风格"""
        print("正在生成肘部分析图...")
        
        risk_values = self.risk_assessments[['risk_score']].values
        
        inertia_values = []
        cluster_range = range(2, max_clusters + 1)
        
        for k_val in cluster_range:
            kmeans_model = KMeans(n_clusters=k_val, random_state=42, n_init=10)
            kmeans_model.fit(risk_values)
            inertia_values.append(kmeans_model.inertia_)
        
        # 计算最佳K值
        if len(inertia_values) >= 3:
            second_derivs = []
            for i in range(1, len(inertia_values) - 1):
                second_deriv = inertia_values[i-1] - 2*inertia_values[i] + inertia_values[i+1]
                second_derivs.append(second_deriv)
            best_k = cluster_range[np.argmax(second_derivs) + 1]
        else:
            best_k = 5
        
        # 创建学术风格图表
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 使用学术配色
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        
        ax.plot(cluster_range, inertia_values, 'o-', color=colors[0], 
                linewidth=2, markersize=8, markerfacecolor='white', markeredgewidth=2)
        ax.axvline(x=best_k, color=colors[2], linestyle='--', linewidth=2, 
                  label=f'最佳K值 = {best_k}')
        
        ax.set_xlabel('聚类数量 (K)', fontweight='bold')
        ax.set_ylabel('聚类内平方和', fontweight='bold')
        ax.set_title('孕产妇风险分层中的肘部法则分析\n确定最佳聚类数量', 
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(frameon=True, fancybox=True, shadow=True)
        
        # 设置边框样式
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'fig1_elbow_analysis.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("图1：肘部分析图已保存")
        return best_k
    
    def generate_risk_distribution_plot(self):
        """生成风险评分分布直方图 - 学术风格"""
        print("正在生成风险评分分布图...")
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 学术配色
        colors = ['#264653', '#2A9D8F', '#E9C46A', '#F4A261']
        
        n, bins, patches = ax.hist(self.grouping_output['risk_score'], bins=30, 
                                  alpha=0.8, edgecolor='black', linewidth=0.5,
                                  color=colors[0], density=True)
        
        # 添加分布曲线
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(self.grouping_output['risk_score'])
        x_range = np.linspace(self.grouping_output['risk_score'].min(), 
                            self.grouping_output['risk_score'].max(), 100)
        ax.plot(x_range, kde(x_range), color=colors[2], linewidth=2, 
               label='密度估计')
        
        ax.set_xlabel('风险评分', fontweight='bold')
        ax.set_ylabel('概率密度', fontweight='bold')
        ax.set_title('孕产妇队列中风险评分的分布\n', 
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(frameon=True, fancybox=True, shadow=True)
        
        # 设置边框样式
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'fig2_risk_distribution.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("图2：风险分布图已保存")
    
    def generate_bmi_risk_scatterplot(self):
        """生成BMI与风险评分散点图 - 学术风格"""
        print("正在生成BMI-风险散点图...")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 学术配色方案
        colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD']
        
        for i, stratum_id in enumerate(sorted(self.grouping_output['风险层级标识'].unique())):
            stratum_data = self.grouping_output[self.grouping_output['风险层级标识'] == stratum_id]
            ax.scatter(stratum_data['avg_bmi'], stratum_data['risk_score'], 
                     alpha=0.7, s=50, edgecolors='black', linewidth=0.5,
                     color=colors[i % len(colors)], 
                     label=f'风险层级 {stratum_id}')
        
        # 添加趋势线
        z = np.polyfit(self.grouping_output['avg_bmi'], self.grouping_output['risk_score'], 1)
        p = np.poly1d(z)
        ax.plot(self.grouping_output['avg_bmi'], p(self.grouping_output['avg_bmi']), 
               "r--", alpha=0.8, linewidth=2, label='线性趋势')
        
        ax.set_xlabel('身体质量指数 (BMI)', fontweight='bold')
        ax.set_ylabel('风险评分', fontweight='bold')
        ax.set_title('孕产妇BMI与风险评分的关联分析\n', 
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.legend(frameon=True, fancybox=True, shadow=True, ncol=2)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # 设置边框样式
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'fig3_bmi_risk_association.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("图3：BMI-风险关联图已保存")
    
    def generate_bmi_category_distribution(self):
        """生成BMI分类分布条形图 - 学术风格"""
        print("正在生成BMI分类分布图...")
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 学术配色
        colors = ['#4E79A7', '#F28E2B', '#59A14F', '#E15759', '#76B7B2']
        
        bmi_category_counts = self.bmi_categories['BMI分组ID'].value_counts().sort_index()
        
        bars = ax.bar(bmi_category_counts.index, bmi_category_counts.values, 
                     alpha=0.8, edgecolor='black', linewidth=1,
                     color=colors[:len(bmi_category_counts)])
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('BMI分类标识', fontweight='bold')
        ax.set_ylabel('样本数量', fontweight='bold')
        ax.set_title('基于BMI的风险分类中孕产妇样本分布\n', 
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 设置边框样式
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'fig4_bmi_category_distribution.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("图4：BMI分类分布图已保存")
    
    def generate_risk_category_heatmap(self):
        """生成风险层级与BMI分类热力图 - 学术风格"""
        print("正在生成风险分类热力图...")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 创建交叉表
        cross_table = pd.crosstab(self.bmi_categories['风险层级标识'], 
                                self.bmi_categories['BMI分组ID'])
        
        # 使用学术配色方案
        cmap = sns.color_palette("Blues", as_cmap=True)
        
        # 创建热力图
        sns.heatmap(cross_table, annot=True, fmt='d', cmap=cmap, 
                   cbar_kws={'label': '样本数量'}, ax=ax,
                   linewidths=0.5, linecolor='gray')
        
        ax.set_xlabel('BMI分类', fontweight='bold')
        ax.set_ylabel('风险层级', fontweight='bold')
        ax.set_title('风险层级与BMI分类的交叉分析\n孕产妇人群分布', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'fig5_risk_bmi_heatmap.png'), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("图5：风险-BMI热力图已保存")
    
    def execute_analysis(self):
        """执行完整的学术分析流程"""
        print("开始学术分析...")
        
        # 导入数据
        self.import_risk_data('./Q3/q3_individual_risk_assessments.csv')
        
        # 执行风险评估分组
        k_value = self.find_optimal_clusters()
        self.execute_risk_grouping(k_value)
        
        # 映射到BMI分类
        self.map_to_bmi_categories()
        
        # 生成所有学术图表
        self.generate_elbow_analysis_plot()
        self.generate_risk_distribution_plot()
        self.generate_bmi_risk_scatterplot()
        self.generate_bmi_category_distribution()
        self.generate_risk_category_heatmap()
        
        print("\n学术分析完成！")
        print("所有图表已以学术风格保存到 ./Q3 目录")

def execute_academic_analysis():
    """执行学术分析"""
    analyzer = AcademicRiskGroupingAnalysis('./Q3')
    analyzer.execute_analysis()

if __name__ == "__main__":
    execute_academic_analysis()