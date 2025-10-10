import pandas as pd
import numpy as np
from enhanced_pregnancy_model import EnhancedPregnancyModel
import os

class MultiObjectiveOptimizer:
    """
    基于多维特征的混合效应模型的多目标优化求解器
    """
    
    def __init__(self, pregnancy_model, retest_interval=14, alpha_param=0.5, scaling_mode='chebyshev',
                 optimization_strategy='multiobj', target_prob=0.95, coverage_quant=0.95,
                 # 增强功能：组特异性阈值与最小时间间隔
                 use_group_specific_threshold=True,
                 base_target_prob=0.75, target_prob_slope=0.0005, reference_bmi=30.0,
                 min_target_prob=0.73, max_target_prob=0.87,
                 enforce_min_interval=True, min_interval_days=6.0,
                 time_window=(70, 175)):
        """
        初始化多目标优化求解器
        
        参数:
        pregnancy_model: 增强版孕期模型实例
        retest_interval: 重测间隔时间（天）
        alpha_param: Alpha方法的权重系数
        scaling_mode: 标量化方法 ('alpha', 'chebyshev', 'knee')
        optimization_strategy: 优化策略 ('coverage', 'multiobj')
        target_prob: 个体达标的目标成功概率
        coverage_quant: 覆盖分位数
        use_group_specific_threshold: 是否使用组特异性阈值
        base_target_prob: 基础目标成功概率
        target_prob_slope: 目标概率随BMI的变化斜率
        reference_bmi: 参考BMI值
        min_target_prob/max_target_prob: 目标概率的最小/最大值
        enforce_min_interval: 是否强制最小时间间隔
        min_interval_days: 最小时间间隔（天）
        time_window: 时间窗口范围（天）
        """
        self.pregnancy_model = pregnancy_model
        self.retest_interval = retest_interval
        self.alpha_param = alpha_param
        self.scaling_mode = scaling_mode
        self.optimization_strategy = optimization_strategy
        self.target_prob = target_prob
        self.coverage_quant = coverage_quant
        self.use_group_specific_threshold = use_group_specific_threshold
        self.base_target_prob = base_target_prob
        self.target_prob_slope = target_prob_slope
        self.reference_bmi = reference_bmi
        self.min_target_prob = min_target_prob
        self.max_target_prob = max_target_prob
        self.enforce_min_interval = enforce_min_interval
        self.min_interval_days = min_interval_days
        self.default_time_window = time_window
    
    def risk_function(self, time_days, feature_dict=None):
        """
        平滑化的风险函数 R(t) - 基于临床风险的时间依赖模型
        """
        # 将天数转换为周数
        weeks = time_days / 7
        
        # 早期风险：使用sigmoid函数实现平滑递减
        early_risk = 0.08 * (1 - 1 / (1 + np.exp(-0.05 * (time_days - 100))))
        
        # 中期风险：稳定期，使用平滑的波动函数
        mid_risk = 0.06 * (1 + 0.05 * np.sin(2 * np.pi * (time_days - 110) / 40))
        
        # 晚期风险：使用sigmoid函数实现平滑指数增长，加入BMI依赖
        if feature_dict is not None and 'bmi' in feature_dict:
            bmi_val = feature_dict['bmi']
            # 增强的非线性BMI依赖
            bmi_normalized = (bmi_val - 25.0) / 20.0  # 归一化到[0,1]范围
            bmi_normalized = max(0.0, min(1.0, bmi_normalized))
            # 使用适度的sigmoid函数，平衡BMI差异的影响
            bmi_factor = 1.0 + 1.0 * (1 / (1 + np.exp(-3.5 * (bmi_normalized - 0.25))))
            bmi_factor = max(0.5, min(2.0, bmi_factor))
            late_risk = 0.15 * bmi_factor * (1 / (1 + np.exp(-0.12 * (time_days - 100))))
        else:
            late_risk = 0.15 * (1 / (1 + np.exp(-0.12 * (time_days - 100))))
        
        # 时间窗边界风险：使用平滑的边界惩罚
        boundary_penalty = 0.0
        if time_days > 140:  # 极端前移边界惩罚
            boundary_penalty = 0.25 * (1 / (1 + np.exp(-0.15 * (time_days - 140))))
        elif time_days < 80:  # 接近下界时平滑增加惩罚
            boundary_penalty = 0.10 * (1 / (1 + np.exp(0.1 * (time_days - 80))))
        
        # 组合所有风险分量
        total_risk = early_risk + mid_risk + late_risk + boundary_penalty
        
        # 确保风险值在合理范围内 [0.05, 0.6]
        return max(0.05, min(0.6, total_risk))
    
    def expected_risk_components(self, feature_dict, detection_time):
        """
        计算平衡目标分量：
        - 期望风险 = p_s * R(t_g) + (1 - p_s) * R(t_g + Δt_retest)
        - 不确定性 = 1 - p_s
        """
        # 将天数转换为孕周
        gestation_weeks = detection_time / 7
        
        # 计算成功概率
        success_prob = self.pregnancy_model.compute_detection_probability(feature_dict, gestation_weeks, method='normal')
        
        # 计算期望风险和不确定性
        expected_risk_val = success_prob * self.risk_function(detection_time, feature_dict) + \
                          (1 - success_prob) * self.risk_function(detection_time + self.retest_interval, feature_dict)
        uncertainty = 1.0 - success_prob
        
        return expected_risk_val, uncertainty
    
    def group_objective_function(self, detection_time, group_features, normalization_params=None):
        """
        组目标函数（按模式）：
        - alpha:       α*E[R] + (1-α)*(1-p_s)
        - chebyshev:   max( z(E[R]), z(1-p_s) )  其中 z(x) 为基于组内时间范围的线性归一化
        - knee:        仅用于网格搜索，返回与端点连线的垂距，供选拐点
        """
        component_values = np.array([self.expected_risk_components(feature_dict, detection_time) for feature_dict in group_features])
        exp_risk = float(np.mean(component_values[:, 0]))
        uncertainty = float(np.mean(component_values[:, 1]))

        if self.scaling_mode == 'alpha':
            return self.alpha_param * exp_risk + (1.0 - self.alpha_param) * uncertainty
        elif self.scaling_mode == 'chebyshev':
            # 归一化处理
            (er_min, er_max, unc_min, unc_max) = normalization_params
            epsilon = 1e-9
            z_er = (exp_risk - er_min) / max(epsilon, (er_max - er_min))
            z_unc = (uncertainty - unc_min) / max(epsilon, (unc_max - unc_min))
            return max(z_er, z_unc)
        else:
            # knee模式不直接用于优化
            return self.alpha_param * exp_risk + (1.0 - self.alpha_param) * uncertainty
    
    def optimize_group_detection(self, group_features, time_range=(84, 175)):
        """优化组的最佳检测时机（支持多种标量化策略）"""
        # 使用细网格近似计算
        time_grid = np.linspace(time_range[0], time_range[1], 400)

        # 预计算两个分量曲线
        expected_risks = []
        uncertainties = []
        for t in time_grid:
            er, unc = np.mean([self.expected_risk_components(feature_dict, t) for feature_dict in group_features], axis=0)
            expected_risks.append(er)
            uncertainties.append(unc)
        expected_risks = np.array(expected_risks)
        uncertainties = np.array(uncertainties)

        if self.scaling_mode == 'alpha':
            objectives = self.alpha_param * expected_risks + (1.0 - self.alpha_param) * uncertainties
            best_idx = int(np.argmin(objectives))
            return float(time_grid[best_idx]), float(objectives[best_idx])

        if self.scaling_mode == 'chebyshev':
            er_min, er_max = float(expected_risks.min()), float(expected_risks.max())
            unc_min, unc_max = float(uncertainties.min()), float(uncertainties.max())
            epsilon = 1e-9
            z_er = (expected_risks - er_min) / max(epsilon, (er_max - er_min))
            z_unc = (uncertainties - unc_min) / max(epsilon, (unc_max - unc_min))
            
            # 时间正则化：偏好更早的时间点
            t_min, t_max = float(time_grid.min()), float(time_grid.max())
            z_t = (time_grid - t_min) / max(epsilon, (t_max - t_min))
            
            # 计算组内平均BMI
            avg_bmi = np.mean([feature_dict.get('bmi', 30.0) for feature_dict in group_features])
            mean_bmi = float(avg_bmi)
            
            # BMI归一化处理
            bmi_norm = (mean_bmi - 25.0) / 20.0
            bmi_norm = max(0.0, min(1.0, bmi_norm))
            
            # BMI差异的时间偏好调整
            bmi_effect = 1 / (1 + np.exp(-4 * (bmi_norm - 0.2)))
            time_weight = 0.95 + 1.2 * (0.5 - bmi_effect)

            # 组特异性时间偏好调整
            base_time_pref = 95.0
            
            # 分段BMI效应处理
            if bmi_norm <= 0.25:
                bmi_effect = 0.15 * bmi_norm
            elif bmi_norm <= 0.5:
                bmi_effect = 0.0375 + 0.3 * (bmi_norm - 0.25)
            elif bmi_norm <= 0.75:
                bmi_effect = 0.1125 + 0.4 * (bmi_norm - 0.5)
            else:
                bmi_effect = 0.2125 + 0.3 * (bmi_norm - 0.75)
            
            time_pref_slope = 180.0
            time_preference = base_time_pref + time_pref_slope * bmi_effect
            z_time_pref = (time_preference - t_min) / max(epsilon, (t_max - t_min))
            pref_weight = 4.0
            preference_penalty = pref_weight * (z_t - z_time_pref) ** 2

            objectives = np.maximum(np.maximum(z_er, z_unc), time_weight * z_t) + preference_penalty
            best_idx = int(np.argmin(objectives))
            return float(time_grid[best_idx]), float(objectives[best_idx])

        if self.scaling_mode == 'knee':
            # 自动拐点选择算法
            x_vals = uncertainties
            y_vals = expected_risks
            x0, y0 = x_vals[0], y_vals[0]
            x1, y1 = x_vals[-1], y_vals[-1]
            A_coef = y0 - y1
            B_coef = x1 - x0
            C_coef = x0*y1 - x1*y0
            denominator = (A_coef*A_coef + B_coef*B_coef) ** 0.5 + 1e-12
            distances = np.abs(A_coef * x_vals + B_coef * y_vals + C_coef) / denominator
            best_idx = int(np.argmax(distances))
            return float(time_grid[best_idx]), float(distances[best_idx])

        # 默认使用alpha方法
        objectives = self.alpha_param * expected_risks + (1.0 - self.alpha_param) * uncertainties
        best_idx = int(np.argmin(objectives))
        return float(time_grid[best_idx]), float(objectives[best_idx])
    
    def optimize_all_categories(self, risk_based_categories):
        """为所有类别求解最佳检测时机"""
        optimization_results = {}
        
        # 计算每个类别的平均BMI并排序
        category_stats = []
        for category_id in risk_based_categories['BMI分组ID'].unique():
            category_data = risk_based_categories[risk_based_categories['BMI分组ID'] == category_id]
            
            # 构建个体特征字典
            category_features = []
            for _, row in category_data.iterrows():
                feature_dict = {
                    'bmi': row['avg_bmi'],
                    'age': row.get('avg_age', 28.0),
                    'pregnancy_count': row.get('avg_pregnancy_count', 1.0),
                    'delivery_count': row.get('avg_delivery_count', 0.0),
                    'gc_content': row.get('avg_gc_content', 0.5)
                }
                category_features.append(feature_dict)
            
            avg_bmi = np.mean([f['bmi'] for f in category_features])
            category_stats.append((category_id, avg_bmi, category_features))
        
        # 按平均BMI升序排序
        category_stats.sort(key=lambda x: x[1])
        
        # 重新分配类别标签
        new_category_mapping = {}
        raw_times = []
        category_metadata = []
        for new_id, (old_id, avg_bmi, category_features) in enumerate(category_stats):
            new_category_mapping[old_id] = new_id
            if self.optimization_strategy == 'coverage':
                # 类别特异性阈值调整
                if self.use_group_specific_threshold:
                    adjusted_prob = self.base_target_prob + self.target_prob_slope * (float(avg_bmi) - self.reference_bmi)
                    adjusted_prob = max(self.min_target_prob, min(self.max_target_prob, adjusted_prob))
                else:
                    adjusted_prob = self.target_prob
                optimal_time = self._coverage_based_safe_time(
                    category_features,
                    target_prob=adjusted_prob,
                    quantile=self.coverage_quant,
                    time_range=self.default_time_window,
                )
                raw_times.append(float(optimal_time))
                category_metadata.append((new_id, old_id, avg_bmi, len(category_features), adjusted_prob))
                print(f"类别 {new_id} (原类别{old_id}, BMI均值{avg_bmi:.2f}): 覆盖法 t_raw = {optimal_time:.1f}天 (p_target={adjusted_prob:.2f}, q={self.coverage_quant:.2f})")
            else:
                optimal_time, min_risk_val = self.optimize_group_detection(category_features)
                raw_times.append(float(optimal_time))
                category_metadata.append((new_id, old_id, avg_bmi, len(category_features), float('nan')))
                print(f"类别 {new_id} (原类别{old_id}, BMI均值{avg_bmi:.2f}): 多目标 t_raw = {optimal_time:.1f}天, 最小风险 = {min_risk_val:.4f}")
        
        # 最小时间间隔处理
        recommended_times = list(raw_times)
        if self.enforce_min_interval and len(recommended_times) >= 2:
            recommended_times[0] = raw_times[0]
            for i in range(1, len(recommended_times)):
                if recommended_times[i] < recommended_times[i-1] + self.min_interval_days:
                    recommended_times[i] = recommended_times[i-1] + self.min_interval_days

        # 汇总优化结果
        for idx, (new_id, old_id, avg_bmi, size, adj_prob) in enumerate(category_metadata):
            optimization_results[new_id] = {
                'optimal_t': float(raw_times[idx]),
                'recommended_t': float(recommended_times[idx]),
                'min_risk': float('nan') if self.optimization_strategy == 'coverage' else float('nan'),
                'group_size': int(size),
                'avg_bmi': float(avg_bmi),
                'strategy': 'coverage' if self.optimization_strategy == 'coverage' else 'multiobj',
                'p_target': float(adj_prob) if not np.isnan(adj_prob) else float('nan'),
                'coverage_quantile': float(self.coverage_quant) if self.optimization_strategy == 'coverage' else float('nan'),
                'min_gap_days': float(self.min_interval_days) if self.enforce_min_interval else float(0.0),
            }
            if self.optimization_strategy == 'coverage':
                print(f"类别 {new_id}: 建议 t_rec = {recommended_times[idx]:.1f}天 (raw={raw_times[idx]:.1f})")

        return optimization_results

    # ================ 覆盖率法：基于达标时间分布的安全时点计算 ==================
    def _threshold_time_for_features(self, feature_dict, target_prob=None, time_range=(84, 175), tolerance=0.1, max_iterations=60):
        """对单个特征组合，求使 p_s(t, features) ≥ target_prob 的最小 t"""
        if target_prob is None:
            target_prob = self.target_prob
        t_low, t_high = float(time_range[0]), float(time_range[1])
        
        # 将天数转换为孕周
        gestation_weeks_low = t_low / 7
        gestation_weeks_high = t_high / 7
        
        # 边界条件检查
        if self.pregnancy_model.compute_detection_probability(feature_dict, gestation_weeks_low, method='normal') >= target_prob:
            return t_low
        if self.pregnancy_model.compute_detection_probability(feature_dict, gestation_weeks_high, method='normal') < target_prob:
            return t_high
        
        # 二分搜索算法
        iteration = 0
        while t_high - t_low > tolerance and iteration < max_iterations:
            t_mid = 0.5 * (t_low + t_high)
            gestation_weeks_mid = t_mid / 7
            success_prob = self.pregnancy_model.compute_detection_probability(feature_dict, gestation_weeks_mid, method='normal')
            if success_prob >= target_prob:
                t_high = t_mid
            else:
                t_low = t_mid
            iteration += 1
        return 0.5 * (t_low + t_high)

    def _coverage_based_safe_time(self, category_features, target_prob=None, quantile=None, time_range=(84, 175)):
        """对一组特征组合，计算各自达标时间，取分位数作为安全时点"""
        if target_prob is None:
            target_prob = self.target_prob
        if quantile is None:
            quantile = self.coverage_quant
        threshold_times = [self._threshold_time_for_features(feature_dict, target_prob=target_prob, time_range=time_range) for feature_dict in category_features]
        return float(np.quantile(threshold_times, quantile))


def execute_optimization():
    """主优化执行函数"""
    # 初始化增强版孕期模型
    pregnancy_model = EnhancedPregnancyModel('./男胎怀孕检测数据.xlsx', min_concentration=0.04)
    
    # 加载和处理数据
    processed_data = pregnancy_model.load_and_process_data()
    
    # 训练增强模型
    model_result, processed_df = pregnancy_model.train_enhanced_model()
    
    if model_result is not None:
        # 计算个体风险评估
        risk_assessments = pregnancy_model.compute_individual_risk_assessments(model_result, processed_df, target_prob=0.95)
        
        # 加载风险驱动分类结果
        risk_categories = pd.read_csv('./Q3/q3_risk_grouping_results.csv')
        
        # 初始化多目标优化器
        optimizer = MultiObjectiveOptimizer(
            pregnancy_model,
            optimization_strategy='multiobj',  # 使用多目标优化
            scaling_mode='chebyshev',         # 使用Chebyshev标量化方法
            alpha_param=0.5,                 # Alpha方法的权重参数
            retest_interval=14,              # 重测间隔时间
            enforce_min_interval=True,
            min_interval_days=6.0,           # 最小时间间隔
            time_window=(70, 175),
        )
        
        # 优化所有类别
        optimization_results = optimizer.optimize_all_categories(risk_categories)
        
        # 保存优化结果
        results_df = pd.DataFrame([
            {
                '组ID': category_id,
                '最佳检测时点raw': result['optimal_t'],
                '建议检测时点': result['optimal_t'],  # 使用原始预测数据
                '最小风险': result['min_risk'],
                '组大小': result['group_size'],
                '平均BMI': result.get('avg_bmi', float('nan')),
                '策略': result.get('strategy', ''),
                '个体目标成功率p_target': result.get('p_target', float('nan')),
                '覆盖分位数q': result.get('coverage_quantile', float('nan')),
                '最小组间间隔(天)': result.get('min_gap_days', float('nan')),
            }
            for category_id, result in optimization_results.items()
        ])
        results_df.to_csv('./Q3/q3_optimization_results.csv', index=False, encoding='utf-8-sig')
        print(f"\n优化结果已保存至: ./Q3/q3_optimization_results.csv")
        
        print("\n第三问多目标优化求解完成！")
    else:
        print("模型训练未成功！")


if __name__ == "__main__":
    execute_optimization()