import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
import os
from multiobjective_optimizer import MultiObjectiveOptimizer
from enhanced_pregnancy_model import EnhancedPregnancyModel

class DetectionTimingOptimizer:
    """多目标优化检测时机求解器"""

    def __init__(self, risk_data_path, output_directory):
        self.risk_data_path = risk_data_path
        self.output_directory = output_directory
        self.risk_assessments = None
        self.risk_categories = None
        self.bmi_classifications = None
        self.optimization_outputs = None
        self.pregnancy_model = None
        self.optimization_engine = None
    
    def import_risk_assessments(self):
        """导入风险评估数据"""
        print("正在导入风险评估数据...")
        self.risk_assessments = pd.read_csv(self.risk_data_path)
        print(f"数据导入完成，共{len(self.risk_assessments)}位孕妇评估记录")
        return self.risk_assessments
    
    def execute_risk_categorization(self, num_categories=3):
        """执行风险评估分类（风险层级划分）"""
        print(f"正在进行风险评估分类（{num_categories}个类别）...")
        
        # 使用K-means对达标时间进行聚类
        kmeans_model = KMeans(n_clusters=num_categories, random_state=42)
        risk_categories = kmeans_model.fit_predict(self.risk_assessments[['achievement_time']].values)
        
        # 添加风险分类标签
        self.risk_assessments['risk_category'] = risk_categories
        
        # 按风险评分排序，确保标签含义一致
        category_means = self.risk_assessments.groupby('risk_category')['achievement_time'].mean().sort_values()
        category_mapping = {original_label: new_label for new_label, original_label in enumerate(category_means.index)}
        self.risk_assessments['risk_category'] = self.risk_assessments['risk_category'].map(category_mapping)
        
        print("风险评估分类完成")
        return self.risk_assessments
    
    def map_to_bmi_classifications(self):
        """将风险分类映射到BMI分类"""
        print("正在将风险分类映射到BMI分类...")
        
        # 使用决策树进行映射
        X_features = self.risk_assessments[['avg_bmi']].values
        y_labels = self.risk_assessments['risk_category'].values
        
        # 训练决策树模型
        tree_model = DecisionTreeClassifier(max_depth=2, random_state=42)
        tree_model.fit(X_features, y_labels)
        
        # 获取BMI分割阈值
        bmi_thresholds = tree_model.tree_.threshold[tree_model.tree_.threshold != -2]
        bmi_thresholds = sorted(bmi_thresholds)
        
        # 创建BMI分类函数
        def assign_bmi_classification(bmi_value):
            if bmi_value <= bmi_thresholds[0]:
                return 0
            elif bmi_value <= bmi_thresholds[1]:
                return 1
            else:
                return 2
        
        self.risk_assessments['bmi_class'] = self.risk_assessments['avg_bmi'].apply(assign_bmi_classification)
        self.risk_assessments['BMI分组ID'] = self.risk_assessments['bmi_class']  # 添加BMI分组标识
        
        print(f"BMI分割阈值: {bmi_thresholds}")
        print("BMI分类映射完成")
        return bmi_thresholds
    
    def initialize_pregnancy_model(self):
        """初始化孕期预测模型和优化引擎"""
        print("正在初始化孕期预测模型...")
        
        # 初始化增强版孕期模型
        self.pregnancy_model = EnhancedPregnancyModel('./男胎怀孕检测数据.xlsx', min_concentration=0.04)
        
        # 加载和处理数据
        processed_data = self.pregnancy_model.load_and_process_data()
        
        # 训练增强模型
        model_result, processed_df = self.pregnancy_model.train_enhanced_model()
        
        if model_result is not None:
            # 初始化多目标优化引擎
            self.optimization_engine = MultiObjectiveOptimizer(
                self.pregnancy_model,
                optimization_strategy='multiobj',  # 使用多目标优化
                scaling_mode='chebyshev',         # 使用Chebyshev标量化方法
                alpha_param=0.5,                 # Alpha方法的权重参数
                retest_interval=14,              # 重测间隔时间
                enforce_min_interval=True,
                min_interval_days=6.0,           # 最小时间间隔
                time_window=(70, 175),
            )
            print("孕期预测模型和优化引擎初始化完成")
            return True
        else:
            print("模型训练未成功！")
            return False
    
    def compute_optimal_detection_timings(self, use_multiobjective=True):
        """计算各类别的最佳检测时机（多目标优化方法）"""
        if use_multiobjective:
            print("正在使用多目标优化方法计算最佳检测时机...")
            
            if self.optimization_engine is None:
                if not self.initialize_pregnancy_model():
                    return None
            
            # 使用多目标优化引擎
            optimization_results = self.optimization_engine.optimize_all_categories(self.risk_assessments)
            
            # 转换为DataFrame格式
            timing_results = []
            for category_id, result in optimization_results.items():
                category_data = self.risk_assessments[self.risk_assessments['BMI分组ID'] == category_id]
                
                category_stats = {
                    'bmi_group': category_id,
                    'optimal_detection_time': result['optimal_t'] / 7,  # 转换为孕周
                    'optimal_detection_time_days': result['optimal_t'],  # 保持天数
                    'sample_count': result['group_size'],
                    'mean_bmi': result['avg_bmi'],
                    'bmi_range': f"{category_data['avg_bmi'].min():.1f}-{category_data['avg_bmi'].max():.1f}",
                    'strategy': result['strategy'],
                    'min_risk': result['min_risk'],
                    'p_target': result['p_target'],
                    'coverage_quantile': result['coverage_quantile'],
                    'min_gap_days': result['min_gap_days']
                }
                timing_results.append(category_stats)
            
            self.optimization_outputs = pd.DataFrame(timing_results)
            print("多目标优化检测时机计算完成")
            
        else:
            # 保留分位数方法作为备选方案
            print("正在使用分位数方法计算安全保障检测时机...")
            quantile_value = 0.75
            results_data = []
            
            for category_id in sorted(self.risk_assessments['BMI分组ID'].unique()):
                category_data = self.risk_assessments[self.risk_assessments['BMI分组ID'] == category_id]
                
                # 计算该类别的分位数作为安全保障检测时机
                optimal_timing = np.percentile(category_data['achievement_time'], quantile_value * 100)
                
                # 计算类别内统计信息
                category_stats = {
                    'bmi_group': category_id,
                    'optimal_detection_time': optimal_timing,
                    'sample_count': len(category_data),
                    'mean_achievement_time': category_data['achievement_time'].mean(),
                    'std_achievement_time': category_data['achievement_time'].std(),
                    'mean_bmi': category_data['avg_bmi'].mean(),
                    'bmi_range': f"{category_data['avg_bmi'].min():.1f}-{category_data['avg_bmi'].max():.1f}",
                    'mean_success_prob': category_data['current_success_prob'].mean()
                }
                
                results_data.append(category_stats)
            
            self.optimization_outputs = pd.DataFrame(results_data)
            print("分位数方法检测时机计算完成")
        
        return self.optimization_outputs
    
    def store_results(self):
        """保存所有分析结果"""
        print("正在保存分析结果...")
        
        # 保存风险驱动分类结果
        self.risk_assessments.to_csv(
            os.path.join(self.output_directory, 'q3_risk_driven_categories.csv'),
            index=False, encoding='utf-8-sig'
        )
        
        # 保存优化结果
        self.optimization_outputs.to_csv(
            os.path.join(self.output_directory, 'q3_optimization_results.csv'),
            index=False, encoding='utf-8-sig'
        )
        
        print("分析结果保存完成")
    
    def display_summary(self):
        """显示结果摘要信息"""
        print("\n=== 多目标优化检测时机分析结果 ===")
        
        for _, row in self.optimization_outputs.iterrows():
            print(f"\nBMI类别 {row['bmi_group']}:")
            print(f"  样本数量: {row['sample_count']}")
            print(f"  BMI数值范围: {row['bmi_range']}")
            print(f"  平均BMI: {row['mean_bmi']:.2f}")
            
            if 'optimal_detection_time_days' in row:
                print(f"  最佳检测时机: {row['optimal_detection_time']:.1f} 孕周 ({row['optimal_detection_time_days']:.1f} 天)")
                print(f"  优化策略: {row['strategy']}")
                if not pd.isna(row['min_risk']):
                    print(f"  最小风险值: {row['min_risk']:.4f}")
                if not pd.isna(row['p_target']):
                    print(f"  目标成功概率: {row['p_target']:.2f}")
                if not pd.isna(row['coverage_quantile']):
                    print(f"  覆盖分位数: {row['coverage_quantile']:.2f}")
                if not pd.isna(row['min_gap_days']):
                    print(f"  最小时间间隔: {row['min_gap_days']:.1f} 天")
            else:
                # 兼容分位数方法结果
                print(f"  平均达标时间: {row['mean_achievement_time']:.1f} 孕周")
                print(f"  安全保障检测时机: {row['optimal_detection_time']:.1f} 孕周")
                print(f"  平均成功概率: {row['mean_success_prob']:.4f}")

class SensitivityAnalyzer:
    """敏感性分析类"""
    
    def __init__(self, optimizer):
        """
        初始化敏感性分析器
        
        参数:
            optimizer: DetectionTimingOptimizer实例
        """
        self.optimizer = optimizer
        self.sensitivity_results = {}
    
    def analyze_parameter_sensitivity(self, parameters_to_test):
        """
        分析参数敏感性
        
        参数:
            parameters_to_test: 要测试的参数字典
                {参数名: [参数值列表]}
        
        返回:
            敏感性分析结果DataFrame
        """
        print("开始敏感性分析...")
        
        # 保存原始优化器设置
        original_engine = self.optimizer.optimization_engine
        original_params = {
            'alpha_param': original_engine.alpha_param,
            'retest_interval': original_engine.retest_interval,
            'min_interval_days': original_engine.min_interval_days
        }
        
        results = []
        
        # 测试每个参数
        for param_name, param_values in parameters_to_test.items():
            print(f"\n分析参数 {param_name} 的敏感性...")
            
            for param_value in param_values:
                print(f"  测试值: {param_value}")
                
                # 更新参数
                if param_name == 'alpha_param':
                    original_engine.alpha_param = param_value
                elif param_name == 'retest_interval':
                    original_engine.retest_interval = param_value
                elif param_name == 'min_interval_days':
                    original_engine.min_interval_days = param_value
                
                # 重新计算最优检测时机
                optimization_results = original_engine.optimize_all_categories(
                    self.optimizer.risk_assessments
                )
                
                # 记录结果
                for category_id, result in optimization_results.items():
                    results.append({
                        'parameter': param_name,
                        'parameter_value': param_value,
                        'bmi_group': category_id,
                        'optimal_detection_time_days': result['optimal_t'],
                        'optimal_detection_time_weeks': result['optimal_t'] / 7,
                        'min_risk': result['min_risk'],
                        'strategy': result['strategy'],
                        'group_size': result['group_size']
                    })
        
        # 恢复原始参数
        original_engine.alpha_param = original_params['alpha_param']
        original_engine.retest_interval = original_params['retest_interval']
        original_engine.min_interval_days = original_params['min_interval_days']
        
        # 转换为DataFrame
        sensitivity_df = pd.DataFrame(results)
        self.sensitivity_results = sensitivity_df
        
        print("敏感性分析完成!")
        return sensitivity_df
    
    def analyze_bmi_threshold_sensitivity(self, threshold_variations=(-1.0, -0.5, 0.5, 1.0)):
        """
        分析BMI阈值分割的敏感性
        
        参数:
            threshold_variations: 阈值变化量列表（kg/m²）
        
        返回:
            BMI阈值敏感性分析结果
        """
        print("分析BMI阈值分割的敏感性...")
        
        # 获取原始BMI阈值
        original_bmi_thresholds = self.optimizer.map_to_bmi_classifications()
        
        results = []
        
        # 测试每个阈值变化
        for variation in threshold_variations:
            print(f"\n测试阈值变化: {variation} kg/m²")
            
            # 创建修改后的阈值
            modified_thresholds = [t + variation for t in original_bmi_thresholds]
            
            # 重新分配BMI分类
            def assign_modified_bmi_classification(bmi_value):
                if bmi_value <= modified_thresholds[0]:
                    return 0
                elif bmi_value <= modified_thresholds[1]:
                    return 1
                else:
                    return 2
            
            # 应用修改后的分类
            modified_assessments = self.optimizer.risk_assessments.copy()
            modified_assessments['bmi_class'] = modified_assessments['avg_bmi'].apply(
                assign_modified_bmi_classification
            )
            modified_assessments['BMI分组ID'] = modified_assessments['bmi_class']
            
            # 重新计算最优检测时机
            optimization_results = self.optimizer.optimization_engine.optimize_all_categories(
                modified_assessments
            )
            
            # 记录结果
            for category_id, result in optimization_results.items():
                category_data = modified_assessments[modified_assessments['BMI分组ID'] == category_id]
                
                results.append({
                    'threshold_variation': variation,
                    'bmi_group': category_id,
                    'optimal_detection_time_days': result['optimal_t'],
                    'optimal_detection_time_weeks': result['optimal_t'] / 7,
                    'group_size': result['group_size'],
                    'mean_bmi': result['avg_bmi'],
                    'bmi_range': f"{category_data['avg_bmi'].min():.1f}-{category_data['avg_bmi'].max():.1f}",
                    'strategy': result['strategy']
                })
        
        # 恢复原始BMI分类
        self.optimizer.map_to_bmi_classifications()
        
        bmi_sensitivity_df = pd.DataFrame(results)
        return bmi_sensitivity_df
    
    def save_sensitivity_results(self, output_path='./Q3/sensitivity_analysis_results.csv'):
        """保存敏感性分析结果"""
        if not self.sensitivity_results.empty:
            self.sensitivity_results.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"敏感性分析结果已保存至: {output_path}")
    
    def display_sensitivity_summary(self):
        """显示敏感性分析摘要"""
        if not self.sensitivity_results.empty:
            print("\n=== 敏感性分析结果摘要 ===")
            
            for param_name in self.sensitivity_results['parameter'].unique():
                param_data = self.sensitivity_results[self.sensitivity_results['parameter'] == param_name]
                
                print(f"\n参数 {param_name}:")
                for bmi_group in sorted(param_data['bmi_group'].unique()):
                    group_data = param_data[param_data['bmi_group'] == bmi_group]
                    
                    time_range = group_data['optimal_detection_time_weeks']
                    risk_range = group_data['min_risk']
                    
                    print(f"  BMI类别 {bmi_group}:")
                    print(f"    检测时机范围: {time_range.min():.1f}-{time_range.max():.1f} 孕周")
                    print(f"    风险值范围: {risk_range.min():.4f}-{risk_range.max():.4f}")
                    print(f"    变化幅度: {(time_range.max() - time_range.min()):.1f} 孕周")

def execute_main_process():
    """主流程执行函数"""
    # 初始化优化求解器
    timing_optimizer = DetectionTimingOptimizer('./Q3/q3_individual_risk_assessments.csv', './Q3')
    
    # 执行优化流程
    timing_optimizer.import_risk_assessments()
    timing_optimizer.execute_risk_categorization(num_categories=3)
    timing_optimizer.map_to_bmi_classifications()
    
    # 使用多目标优化方法（默认）
    timing_optimizer.compute_optimal_detection_timings(use_multiobjective=True)
    
    # 进行敏感性分析
    sensitivity_analyzer = SensitivityAnalyzer(timing_optimizer)
    
    # 测试关键参数的敏感性
    parameters_to_test = {
        'alpha_param': [0.3, 0.5, 0.7],
        'retest_interval': [7, 14, 21],
        'min_interval_days': [3.0, 6.0, 9.0]
    }
    
    sensitivity_results = sensitivity_analyzer.analyze_parameter_sensitivity(parameters_to_test)
    sensitivity_analyzer.save_sensitivity_results()
    sensitivity_analyzer.display_sensitivity_summary()
    
    timing_optimizer.store_results()
    timing_optimizer.display_summary()
    
    print("\n多目标优化检测时机分析和敏感性分析完成！")

if __name__ == "__main__":
    execute_main_process()