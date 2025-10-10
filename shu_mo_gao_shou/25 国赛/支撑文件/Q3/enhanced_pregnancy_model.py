import pandas as pd
import numpy as np
import os
from statsmodels.formula.api import mixedlm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class EnhancedPregnancyModel:
    """
    增强版孕期预测模型，整合多变量并估算个体风险等级
    """
    
    def __init__(self, data_source, min_concentration=0.04):
        self.data_source = data_source
        self.output_folder = "./Q3"
        self.min_concentration = min_concentration  # Y染色体检测阈值
        self.trained_model = None
        self.processed_data = None
        self.risk_assessments = None
        self.model_output = None
        
    def load_and_process_data(self):
        """载入数据并进行清洗处理"""
        print("数据载入中...")
        self.processed_data = pd.read_excel(self.data_source)
        
        # 筛选健康男胎数据
        healthy_male_data = self.processed_data[self.processed_data['胎儿是否健康'] == '是'].copy()
        
        # 选取相关特征列
        feature_columns = ['孕妇代码', '孕周天数', '孕妇BMI', 'Y染色体浓度', '年龄', '身高', '体重', 
                          '怀孕次数', '生产次数', 'GC含量']
        
        # 确认列存在性
        existing_columns = [col for col in feature_columns if col in healthy_male_data.columns]
        self.processed_data = healthy_male_data[existing_columns].copy()
        
        # 处理缺失值
        self.processed_data = self.processed_data.dropna()
        
        # 处理特殊数值
        if '怀孕次数' in self.processed_data.columns:
            self.processed_data['怀孕次数'] = self.processed_data['怀孕次数'].replace('≥3', 3)
            self.processed_data['怀孕次数'] = pd.to_numeric(self.processed_data['怀孕次数'], errors='coerce')
        
        if '生产次数' in self.processed_data.columns:
            self.processed_data['生产次数'] = pd.to_numeric(self.processed_data['生产次数'], errors='coerce')
        
        # 再次清理缺失值
        self.processed_data = self.processed_data.dropna()
        
        print(f"数据处理完毕，总计{len(self.processed_data)}条有效记录")
        print(f"涵盖{self.processed_data['孕妇代码'].nunique()}名孕妇")
        print(f"可用特征: {list(self.processed_data.columns)}")
        
        return self.processed_data
    
    def assess_multicollinearity(self, dataframe):
        """评估多重共线性问题"""
        print("正在进行多重共线性诊断...")
        
        # 准备数值型变量
        numerical_features = ['week', 'bmi', 'age', 'height', 'weight', 'pregnancy_count', 'delivery_count', 'gc_content']
        valid_features = [feat for feat in numerical_features if feat in dataframe.columns]
        
        if len(valid_features) < 2:
            print("有效特征不足，跳过共线性检查")
            return valid_features
        
        # 计算VIF指标
        X_data = dataframe[valid_features].copy()
        X_data = add_constant(X_data)
        
        vif_results = pd.DataFrame()
        vif_results["特征项"] = X_data.columns
        vif_results["VIF值"] = [variance_inflation_factor(X_data.values, i) for i in range(len(X_data.columns))]
        
        print("方差膨胀因子分析:")
        print(vif_results)
        
        # 剔除高VIF特征（VIF > 10）
        high_vif_features = vif_results[vif_results['VIF值'] > 10]['特征项'].tolist()
        if 'const' in high_vif_features:
            high_vif_features.remove('const')
        
        if high_vif_features:
            print(f"移除高VIF特征: {high_vif_features}")
            valid_features = [feat for feat in valid_features if feat not in high_vif_features]
        
        return valid_features
    
    def train_enhanced_model(self):
        """训练增强版混合效应模型"""
        print("开始训练增强版混合效应模型...")
        
        # 数据准备
        df_processed = self.processed_data.copy()
        
        # 列名重命名
        df_processed = df_processed.rename(columns={
            '孕妇代码': 'subject_id',
            '孕周天数': 'week',
            '孕妇BMI': 'bmi',
            'Y染色体浓度': 'y_concentration',
            '年龄': 'age',
            '身高': 'height',
            '体重': 'weight',
            '怀孕次数': 'pregnancy_count',
            '生产次数': 'delivery_count',
            'GC含量': 'gc_content'
        })
        
        # 多重共线性诊断
        valid_features = self.assess_multicollinearity(df_processed)
        
        # 构建模型公式
        # 基础特征项
        core_features = ['week', 'bmi']
        
        # 添加其他特征
        additional_features = []
        for feat in ['age', 'pregnancy_count', 'delivery_count', 'gc_content']:
            if feat in valid_features:
                additional_features.append(feat)
        
        # 处理身高体重相关性
        if 'height' in valid_features and 'weight' in valid_features:
            df_processed['height_centered'] = df_processed['height'] - df_processed['height'].mean()
            additional_features.append('height_centered')
        
        # 构建最终模型公式
        all_features = core_features + additional_features
        model_formula = 'y_concentration ~ ' + ' + '.join(all_features)
        
        print(f"模型表达式: {model_formula}")
        
        try:
            # 拟合混合效应模型
            grouping_var = df_processed['subject_id']
            self.trained_model = mixedlm(model_formula, df_processed, groups=grouping_var, re_formula='1')
            model_result = self.trained_model.fit()
            
            print("增强版混合效应模型训练成功！")
            
            # 保存模型结果
            self.model_output = model_result
            self.store_model_outputs(model_result, df_processed)
            
            return model_result, df_processed
            
        except Exception as e:
            print(f"模型训练失败: {e}")
            return None, None
    
    def predict_y_chromosome_level(self, feature_dict, gestation_week):
        """
        基于多特征预测Y染色体浓度均值
        
        参数:
        feature_dict: 特征字典，包含BMI、年龄等
        gestation_week: 孕周数
        
        返回:
        预测的Y染色体浓度均值
        """
        if self.model_output is None:
            raise ValueError("请先完成模型训练")
        
        # 获取模型参数
        model_params = self.model_output.params
        
        # 计算预测值
        predicted_value = model_params.get('Intercept', 0)
        predicted_value += model_params.get('week', 0) * gestation_week
        
        # 添加其他特征贡献
        for feature, value in feature_dict.items():
            if feature in model_params.index:
                predicted_value += model_params[feature] * value
        
        return predicted_value
    
    def compute_detection_probability(self, feature_dict, gestation_week, method='normal'):
        """
        计算检测成功概率 p_s(t, X_i) = P(C_i(t) >= C_min)
        基于增强版混合效应模型
        
        参数:
        feature_dict: 特征字典
        gestation_week: 孕周数
        method: 概率计算方法 (仅支持 'normal')
        
        返回:
        成功概率值
        """
        if method != 'normal':
            raise ValueError("仅支持 'normal' 计算方法")
        
        # 预测Y染色体浓度
        predicted_level = self.predict_y_chromosome_level(feature_dict, gestation_week)
        
        # 计算成功概率
        return self._compute_normal_probability(predicted_level, feature_dict, gestation_week)
    
    def _compute_normal_probability(self, predicted_level, feature_dict, gestation_week):
        """
        基于混合效应模型计算成功概率，采用孕周依赖的标准差
        """
        if self.model_output is None:
            raise ValueError("模型未训练")
        
        # 获取模型参数
        sigma_u_sq = self.model_output.cov_re.iloc[0,0]  # 随机截距方差
        sigma_e_sq = self.model_output.scale  # 残差方差
        
        # 基础方差
        base_variance = sigma_u_sq + sigma_e_sq
        base_std = np.sqrt(base_variance)
        
        # 孕周依赖方差调整
        bmi_value = feature_dict.get('bmi', 30.0)
        alpha_base = 0.85
        alpha_bmi = 0.025 * (bmi_value - 30.0)
        alpha_val = max(0.6, min(1.6, alpha_base + alpha_bmi))
        scale_factor = 30.0
        multiplier = 1.0 + alpha_val * np.exp(-(gestation_week - 118.0) / scale_factor)
        multiplier = float(max(1.0, multiplier))
        
        total_std = base_std * multiplier
        
        # 计算成功概率 P(C >= C_min)
        z_value = (self.min_concentration - predicted_level) / total_std
        detection_prob = 1 - stats.norm.cdf(z_value)
        
        return max(0, min(1, detection_prob))
    
    def compute_target_achievement_time(self, feature_dict, target_prob=0.95, week_range=(80, 180)):
        """
        计算个体达标时间 T(x) = inf{t: p_s(t|x) >= target_prob}
        
        参数:
        feature_dict: 特征字典
        target_prob: 目标成功概率
        week_range: 孕周搜索范围
        
        返回:
        达标时间（孕周）
        """
        week_start, week_end = week_range
        
        # 在孕周范围内搜索
        for week_val in range(week_start, week_end + 1):
            success_prob = self.compute_detection_probability(feature_dict, week_val)
            if success_prob >= target_prob:
                return week_val
        
        # 如未找到，返回最大孕周
        return week_end

    def compute_individual_risk_assessments(self, model_result, dataframe, target_prob=0.95):
        """计算每位孕妇的个体风险评估（基于成功概率和达标时间）"""
        print("正在进行个体风险评估...")
        
        # 计算个体风险评估（达标时间）
        risk_assessments = []
        
        for subject_id in dataframe['subject_id'].unique():
            subject_info = dataframe[dataframe['subject_id'] == subject_id]
            
            # 使用个体平均特征
            feature_columns = ['bmi', 'age', 'pregnancy_count', 'delivery_count', 'gc_content']
            available_features = [col for col in feature_columns if col in subject_info.columns]
            avg_features = subject_info[available_features].mean()
            
            # 构建特征字典
            feature_dict = {}
            for col in available_features:
                if col != 'week':
                    feature_dict[col] = avg_features[col]
            
            # 计算达标时间（个体风险评估）
            achievement_time = self.compute_target_achievement_time(feature_dict, target_prob)
            
            # 计算当前平均孕周的成功概率
            avg_week = subject_info['week'].mean()
            current_success_prob = self.compute_detection_probability(feature_dict, avg_week)
            
            # 计算预测的Y染色体浓度
            predicted_y = self.predict_y_chromosome_level(feature_dict, avg_week)
            
            risk_assessments.append({
                'subject_id': subject_id,
                'risk_score': achievement_time,
                'achievement_time': achievement_time,
                'current_success_prob': current_success_prob,
                'predicted_y': predicted_y,
                'avg_bmi': avg_features['bmi'],
                'avg_age': avg_features['age'],
                'avg_week': avg_week
            })
        
        self.risk_assessments = pd.DataFrame(risk_assessments)
        
        # 保存风险评估
        self.risk_assessments.to_csv(os.path.join(self.output_folder, 'q3_individual_risk_assessments.csv'), 
                                   index=False, encoding='utf-8-sig')
        
        print(f"个体风险评估完成，共{len(self.risk_assessments)}位孕妇")
        print(f"达标时间分布: {self.risk_assessments['achievement_time'].min():.1f} - {self.risk_assessments['achievement_time'].max():.1f} 孕周")
        print(f"当前成功概率分布: {self.risk_assessments['current_success_prob'].min():.4f} - {self.risk_assessments['current_success_prob'].max():.4f}")
        
        return self.risk_assessments
    
    def store_model_outputs(self, model_result, dataframe):
        """保存模型输出结果"""
        # 1. 保存模型系数
        coefficient_data = []
        for param in model_result.params.index:
            if param != 'Group Var':
                coefficient_data.append({
                    '变量': param,
                    '系数': model_result.params[param],
                    '标准误': model_result.bse[param],
                    't值': model_result.tvalues[param],
                    'p值': model_result.pvalues[param]
                })
        
        coefficient_df = pd.DataFrame(coefficient_data)
        coefficient_df.to_csv(os.path.join(self.output_folder, 'q3_enhanced_model_coefficients.csv'), 
                            index=False, encoding='utf-8-sig')
        
        # 2. 保存模型信息
        with open(os.path.join(self.output_folder, 'q3_enhanced_model_details.md'), 'w', encoding='utf-8') as f:
            f.write("# 增强版混合效应模型分析结果\n")
            f.write("=" * 60 + "\n\n")
            f.write("## 模型结构\n")
            f.write("Y_ij = (β₀ + u_i) + β₁·Week_ij + β₂·BMI_ij + β₃·Age_ij + β₄·GC_ij + ... + ε_ij\n\n")
            f.write("其中：\n")
            f.write("- Y_ij: 第i位孕妇第j次检测的Y染色体浓度\n")
            f.write("- β₀: 固定截距（总体基准水平）\n")
            f.write("- u_i: 第i位孕妇的随机截距（个体特异性）\n")
            f.write("- β₁, β₂, β₃, β₄, ...: 各变量的固定效应系数\n")
            f.write("- ε_ij: 随机误差项\n")
            f.write("- 注：孕妇标识仅用于分组，不作为预测变量\n\n")
            
            f.write("## 模型参数统计\n")
            f.write(f"观测样本数: {model_result.nobs}\n")
            f.write(f"分组数量（孕妇数）: {len(model_result.random_effects)}\n")
            f.write(f"平均每组观测数: {model_result.nobs / len(model_result.random_effects):.2f}\n")
            f.write(f"对数似然值: {model_result.llf:.4f}\n")
            f.write(f"AIC准则: {model_result.aic:.4f}\n")
            f.write(f"BIC准则: {model_result.bic:.4f}\n\n")
            
            f.write("## 固定效应参数估计\n")
            f.write("| 变量 | 系数估计 | 标准误差 | t统计量 | p值 |\n")
            f.write("|------|----------|----------|---------|-----|\n")
            
            for param in model_result.params.index:
                if param != 'Group Var':
                    coef_val = model_result.params[param]
                    std_err = model_result.bse[param]
                    t_stat = model_result.tvalues[param]
                    p_val = model_result.pvalues[param]
                    f.write(f"| {param} | {coef_val:.6f} | {std_err:.6f} | {t_stat:.4f} | {p_val:.6e} |\n")
            
            f.write("\n## 随机效应分析\n")
            f.write(f"组间方差 (σ²_u): {model_result.cov_re.iloc[0,0]:.6f}\n")
            f.write(f"组内方差 (σ²_ε): {model_result.scale:.6f}\n")
            
            # 计算组内相关系数
            sigma_u_sq = model_result.cov_re.iloc[0,0]
            sigma_e_sq = model_result.scale
            icc_value = sigma_u_sq / (sigma_u_sq + sigma_e_sq)
            f.write(f"组内相关系数 (ICC): {icc_value:.6f}\n")
            f.write(f"ICC解读: 总体变异中{icc_value*100:.1f}%由孕妇间个体差异解释\n\n")
        
        print("模型输出结果已保存")

def execute_main():
    """主执行函数"""
    # 初始化模型
    enhanced_model = EnhancedPregnancyModel('./男胎怀孕检测数据.xlsx', min_concentration=0.04)
    
    # 载入和处理数据
    processed_data = enhanced_model.load_and_process_data()
    
    # 训练增强模型
    model_output, processed_df = enhanced_model.train_enhanced_model()
    
    if model_output is not None:
        # 计算个体风险评估（使用95%成功概率）
        risk_assessments = enhanced_model.compute_individual_risk_assessments(model_output, processed_df, target_prob=0.95)
        
        # 演示概率计算功能
        print("\n=== 检测概率计算演示 ===")
        sample_features = {
            'bmi': 30.0,
            'age': 28.0,
            'pregnancy_count': 1.0,
            'delivery_count': 0.0,
            'gc_content': 0.5
        }
        
        # 计算不同孕周的检测概率
        for week_val in [100, 120, 140, 160]:
            detection_prob = enhanced_model.compute_detection_probability(sample_features, week_val)
            print(f"孕周 {week_val}: 检测成功概率 = {detection_prob:.4f}")
        
        # 计算达标时间
        target_time = enhanced_model.compute_target_achievement_time(sample_features, target_prob=0.95)
        print(f"达标时间（95%成功概率）: {target_time} 孕周")
        
        print("\n增强版混合效应模型和个体风险评估计算完成！")
        print("所有结果已保存至指定目录")
    else:
        print("模型训练未成功！")

if __name__ == "__main__":
    execute_main()