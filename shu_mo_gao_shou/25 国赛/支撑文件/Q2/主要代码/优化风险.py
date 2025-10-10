import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import CubicSpline
from scipy import optimize
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import shutil
from tqdm import tqdm
import seaborn as sns

#NIPT检测时点优化分析类
class NIPTOptimizer:

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.results_df = None
        self.earliest_compliance_time_df = None
        self.original_data = None

    def load_and_preprocess_data(self):
        """加载并预处理数据"""
        if not os.path.exists(self.file_path):
            print(f"文件不存在: {self.file_path}")
            return False

        try:
            self.data = pd.read_excel(self.file_path)
            self.original_data = self.data.copy()
        except Exception as e:
            print(f"读取文件失败: {e}")
            return False

        required_columns = ['孕妇BMI', '孕周天数', 'Y染色体浓度', '是否误检', '孕妇代码']
        if any(col not in self.data.columns for col in required_columns):
            print("缺少必要列")
            return False

        self.data['孕期阶段'] = self.data['孕周天数'].apply(
            lambda days: "早期" if days <= 84 else ("中期" if days <= 189 else "晚期"))
        return True

    #添加测量误差
    def add_measurement_error(self, y_concentration_error_std=0.01, bmi_error_std=0.5, gestational_error_std=2):

        if self.original_data is None:
            return False

        self.data = self.original_data.copy()

        # 添加Y染色体浓度误差
        y_concentration_error = np.random.lognormal(mean=0, sigma=y_concentration_error_std, size=len(self.data)) - 1
        self.data['Y染色体浓度'] = np.clip(self.data['Y染色体浓度'] * (1 + y_concentration_error), 0, 1)

        # 添加BMI误差
        bmi_error = np.random.normal(0, bmi_error_std, len(self.data))
        self.data['孕妇BMI'] = np.clip(self.data['孕妇BMI'] + bmi_error, 15, 50)

        # 添加孕周误差
        gestational_error = np.random.normal(0, gestational_error_std, len(self.data))
        self.data['孕周天数'] = np.clip(self.data['孕周天数'] + gestational_error, 7 * 6, 7 * 40)

        self.data['孕期阶段'] = self.data['孕周天数'].apply(
            lambda days: "早期" if days <= 84 else ("中期" if days <= 189 else "晚期"))
        return True

    #添加模型不确定性
    def add_model_uncertainty(self, risk_factor_std=0.1):

        alpha_perturb = np.random.normal(0.3, risk_factor_std)
        beta_perturb = np.random.normal(0.6, risk_factor_std)
        gamma_perturb = np.random.normal(0.1, risk_factor_std)

        total = alpha_perturb + beta_perturb + gamma_perturb
        return alpha_perturb / total, beta_perturb / total, gamma_perturb / total

    #运行敏感性分析（蒙特卡洛模拟）
    def run_sensitivity_analysis(self, n_simulations=100, y_concentration_error_std=0.01,
                                 bmi_error_std=0.5, gestational_error_std=2, risk_factor_std=0.1):


        all_bmi_groups = []
        all_optimal_times = []
        all_risks = []

        for _ in tqdm(range(n_simulations)):
            self.add_measurement_error(y_concentration_error_std, bmi_error_std, gestational_error_std)
            alpha, beta, gamma = self.add_model_uncertainty(risk_factor_std)
            self.calculate_earliest_compliance_time()
            bmi_groups = self.optimize_bmi_groups_clustering(n_groups=4)
            results_df = self.joint_optimization_with_params(alpha=alpha, beta=beta, gamma=gamma)

            all_bmi_groups.append(bmi_groups)
            if not results_df.empty:
                all_optimal_times.append(results_df['最佳检测时点(周)'].tolist())
                all_risks.append(results_df['最小风险'].tolist())
            else:
                all_optimal_times.append([np.nan] * 4)
                all_risks.append([np.nan] * 4)

        return self.analyze_stability(all_bmi_groups, all_optimal_times, all_risks)

    #联合优化
    def joint_optimization_with_params(self, alpha=0.3, beta=0.6, gamma=0.1):

        bmi_groups = self.optimize_bmi_groups_clustering(n_groups=4)
        results = []

        for i, (bmi_min, bmi_max) in enumerate(bmi_groups):
            group_data = self.data[(self.data['孕妇BMI'] >= bmi_min) & (self.data['孕妇BMI'] < bmi_max)]
            if len(group_data) == 0:
                continue

            optimal_time, min_risk = self.optimize_detection_time_with_params(group_data, alpha, beta, gamma)
            if optimal_time is None:
                continue

            min_weeks = group_data['孕周天数'].min() / 7
            max_weeks = group_data['孕周天数'].max() / 7

            results.append({
                '组ID': i+1,
                'BMI范围': (round(bmi_min, 2), round(bmi_max, 2)),
                '最佳检测时点(周)': optimal_time,
                '最小风险': min_risk,
                '样本数量': len(group_data),
                '数据孕周范围': (round(min_weeks, 2), round(max_weeks, 2))
            })

        return pd.DataFrame(results)

    #优化单个分组的最佳检测时点
    def optimize_detection_time_with_params(self, group_data, alpha, beta, gamma):

        min_days = group_data['孕周天数'].min()
        max_days = group_data['孕周天数'].max()

        def objective_function(gestational_days):
            return self.calculate_composite_risk_three_factors_with_params(
                group_data, gestational_days, alpha, beta, gamma)

        constraints = [{'type': 'ineq', 'fun': lambda x: x - min_days},
                       {'type': 'ineq', 'fun': lambda x: max_days - x}]

        result = minimize(objective_function, [(min_days + max_days) / 2],
                          constraints=constraints, method='SLSQP')

        if not result.success:
            return None, None

        return round(result.x[0] / 7, 2), result.fun

    #计算三因素综合风险
    def calculate_composite_risk_three_factors_with_params(self, group_data, gestational_days,
                                                           alpha, beta, gamma):

        non_compliance = self.calculate_non_compliance_rate_by_period(group_data, gestational_days)
        misdiagnosis = self.calculate_misdiagnosis_risk(group_data, gestational_days)
        late_risk = self.calculate_late_detection_risk_regression(gestational_days)
        return (alpha * non_compliance + beta * misdiagnosis + gamma * late_risk)

    #分析分组和时点推荐的稳定性
    def analyze_stability(self, all_bmi_groups, all_optimal_times, all_risks):


        # 创建结果DataFrame
        optimal_times_df = pd.DataFrame(all_optimal_times, columns=[f'组{i}' for i in range(4)])
        risks_df = pd.DataFrame(all_risks, columns=[f'组{i}' for i in range(4)])

        # 提取BMI边界
        bmi_boundaries = []
        for bmi_groups in all_bmi_groups:
            boundaries = [group[0] for group in bmi_groups] + [bmi_groups[-1][1]]
            bmi_boundaries.append(boundaries)

        bmi_boundaries_df = pd.DataFrame(bmi_boundaries, columns=[f'边界{i}' for i in range(5)])

        # 计算统计指标
        stability_results = {
            'optimal_times_mean': optimal_times_df.mean().to_dict(),
            'optimal_times_std': optimal_times_df.std().to_dict(),
            'optimal_times_cv': (optimal_times_df.std() / optimal_times_df.mean()).to_dict(),
            'risks_mean': risks_df.mean().to_dict(),
            'risks_std': risks_df.std().to_dict(),
            'bmi_boundaries_mean': bmi_boundaries_df.mean().to_dict(),
            'bmi_boundaries_std': bmi_boundaries_df.std().to_dict()
        }

        # 稳定性结果
        print("\n=== 敏感性分析结果 ===")
        print("\n最佳检测时点稳定性:")
        for group in range(4):
            mean = stability_results['optimal_times_mean'][f'组{group}']
            std = stability_results['optimal_times_std'][f'组{group}']
            cv = stability_results['optimal_times_cv'][f'组{group}']
            print(f"组{group + 1}: {mean:.2f} ± {std:.2f} 周 (变异系数: {cv:.3f})")

        print("\nBMI分组边界稳定性:")
        for boundary in range(5):
            mean = stability_results['bmi_boundaries_mean'][f'边界{boundary}']
            std = stability_results['bmi_boundaries_std'][f'边界{boundary}']
            print(f"边界{boundary + 1}: {mean:.2f} ± {std:.2f}")

        print("\n风险值稳定性:")
        for group in range(4):
            mean = stability_results['risks_mean'][f'组{group}']
            std = stability_results['risks_std'][f'组{group}']
            print(f"组{group + 1}: {mean:.4f} ± {std:.4f}")

        # 可视化稳定性结果
        self.visualize_stability(optimal_times_df, bmi_boundaries_df)

        return stability_results

    #可视化稳定性分析结果
    def visualize_stability(self, optimal_times_df, bmi_boundaries_df):

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # 最佳检测时点的分布
        for i in range(4):
            sns.histplot(optimal_times_df[f'组{i}'], ax=axes[0, 0], kde=True, label=f'组{i + 1}')
        axes[0, 0].set_title('最佳检测时点分布')
        axes[0, 0].legend()

        # 最佳检测时点的箱线图
        boxplot_data = optimal_times_df.rename(columns={f'组{i}': f'组{i + 1}' for i in range(4)})
        boxplot_data.boxplot(ax=axes[0, 1])
        axes[0, 1].set_title('最佳检测时点变异性')

        # BMI边界的变化
        for i in range(5):
            sns.histplot(bmi_boundaries_df[f'边界{i}'], ax=axes[1, 0], kde=True, label=f'边界{i + 1}')
        axes[1, 0].set_title('BMI分组边界分布')
        axes[1, 0].legend()

        # BMI边界的箱线图
        bmi_boxplot_data = bmi_boundaries_df.rename(columns={f'边界{i}': f'边界{i + 1}' for i in range(5)})
        bmi_boxplot_data.boxplot(ax=axes[1, 1])
        axes[1, 1].set_title('BMI分组边界变异性')

        plt.tight_layout()
        plt.savefig('敏感性分析结果.png', dpi=300)
        plt.show()

    #为每位孕妇计算Y染色体浓度达到4%的最早时间
    def calculate_earliest_compliance_time(self):

        results = []
        grouped = self.data.groupby('孕妇代码')

        for woman_id, group in grouped:
            group_sorted = group.sort_values('孕周天数')
            gestational_days = group_sorted['孕周天数'].values
            y_concentration = group_sorted['Y染色体浓度'].values

            if len(gestational_days) < 3:
                above_threshold = group_sorted[group_sorted['Y染色体浓度'] >= 0.04]
                earliest_time = above_threshold['孕周天数'].min() if len(above_threshold) > 0 else np.inf
            else:
                try:
                    cs = CubicSpline(gestational_days, y_concentration, extrapolate=False)

                    def func(days):
                        return cs(days) - 0.04

                    day_min, day_max = gestational_days.min(), gestational_days.max()
                    if func(day_min) >= 0:
                        earliest_time = day_min
                    else:
                        try:
                            earliest_time = optimize.brentq(func, day_min, day_max)
                        except ValueError:
                            earliest_time = day_max if func(day_max) >= 0 else np.inf
                except Exception:
                    above_threshold = group_sorted[group_sorted['Y染色体浓度'] >= 0.04]
                    earliest_time = above_threshold['孕周天数'].min() if len(above_threshold) > 0 else np.inf

            results.append({
                '孕妇代码': woman_id,
                '最早达标时间': earliest_time,
                'BMI': group_sorted['孕妇BMI'].iloc[0]
            })

        self.earliest_compliance_time_df = pd.DataFrame(results)
        return self.earliest_compliance_time_df

    #基于最早达标时间进行聚类分析
    def optimize_bmi_groups_clustering(self, n_groups=4):

        if self.earliest_compliance_time_df is None:
            self.calculate_earliest_compliance_time()

        valid_data = self.earliest_compliance_time_df[self.earliest_compliance_time_df['最早达标时间'] < np.inf].copy()
        if len(valid_data) == 0:
            return self._fallback_bmi_groups()

        full_bmi_min = self.data['孕妇BMI'].min()
        full_bmi_max = self.data['孕妇BMI'].max()

        X = valid_data[['BMI', '最早达标时间']].values
        X_scaled = StandardScaler().fit_transform(X)

        kmeans = KMeans(n_clusters=n_groups, random_state=42, n_init=10)
        valid_data['cluster'] = kmeans.fit_predict(X_scaled)

        cluster_bmi_ranges = []
        for cluster_id in range(n_groups):
            cluster_data = valid_data[valid_data['cluster'] == cluster_id]
            if len(cluster_data) > 0:
                bmi_min, bmi_max = cluster_data['BMI'].min(), cluster_data['BMI'].max()
                cluster_bmi_ranges.append({
                    'bmi_range': (bmi_min, bmi_max),
                    'avg_compliance_time': cluster_data['最早达标时间'].mean()
                })

        cluster_bmi_ranges.sort(key=lambda x: x['bmi_range'][0])
        bmi_groups = []
        current_max = full_bmi_min

        for i, cluster_info in enumerate(cluster_bmi_ranges):
            bmi_min, bmi_max = cluster_info['bmi_range']
            group_min = max(current_max, bmi_min)
            group_max = full_bmi_max if i == len(cluster_bmi_ranges) - 1 else (bmi_max +
                                                                               cluster_bmi_ranges[i + 1]['bmi_range'][
                                                                                   0]) / 2
            group_max = group_min + 0.1 if group_min >= group_max else group_max

            bmi_groups.append((group_min, group_max))
            current_max = group_max

        return bmi_groups

    #当没有有效数据时的BMI分组方案
    def _fallback_bmi_groups(self):

        bmi_min = self.data['孕妇BMI'].min()
        bmi_max = self.data['孕妇BMI'].max()
        return [(bmi_min + i * (bmi_max - bmi_min) / 4, bmi_min + (i + 1) * (bmi_max - bmi_min) / 4) for i in range(4)]

    #不达标率风险函数
    def calculate_non_compliance_rate_by_period(self, group_data, gestational_days):

        gestational_weeks = gestational_days / 7
        if gestational_weeks < 10 or gestational_weeks > 25:
            return 1.0

        period = "早期" if gestational_days <= 84 else ("中期" if gestational_days <= 189 else "晚期")
        period_data = group_data[group_data['孕期阶段'] == period]
        if len(period_data) == 0:
            period_data = group_data

        weights = np.exp(-0.5 * ((period_data['孕周天数'] - gestational_days) / 14) ** 2)
        low_concentration = (period_data['Y染色体浓度'] < 0.04).astype(float)
        return np.sum(low_concentration * weights) / np.sum(weights)

    #误检风险函数
    def calculate_misdiagnosis_risk(self, group_data, gestational_days):

        min_days = group_data['孕周天数'].min()
        max_days = group_data['孕周天数'].max()
        gestational_days = np.clip(gestational_days, min_days, max_days)

        period = "早期" if gestational_days <= 84 else ("中期" if gestational_days <= 189 else "晚期")
        period_data = group_data[group_data['孕期阶段'] == period]
        if len(period_data) == 0:
            period_data = group_data

        weights = np.exp(-0.5 * ((period_data['孕周天数'] - gestational_days) / 14) ** 2)
        return np.sum(period_data['是否误检'] * weights) / np.sum(weights)

    @staticmethod

    #晚检风险函数
    def calculate_late_detection_risk_regression(gestational_days):

        gestational_weeks = gestational_days / 7
        if gestational_weeks <= 10:
            return 0.0
        if gestational_weeks >= 27:
            return 1.0

        normalized_weeks = (gestational_weeks - 10) / 17
        return min(max(normalized_weeks ** 1.5, 0), 1)

    #联合优化BMI分组和最佳NIPT时点
    def joint_optimization(self):

        bmi_groups = self.optimize_bmi_groups_clustering(4)
        results = []

        for i, (bmi_min, bmi_max) in enumerate(bmi_groups):
            group_data = self.data[(self.data['孕妇BMI'] >= bmi_min) & (self.data['孕妇BMI'] < bmi_max)]
            if len(group_data) == 0:
                continue

            optimal_time, min_risk = self.optimize_detection_time(group_data)
            if optimal_time is None:
                continue

            min_weeks = group_data['孕周天数'].min() / 7
            max_weeks = group_data['孕周天数'].max() / 7

            # 计算各孕期误检率
            early_mis_rate = self.calculate_misdiagnosis_risk(group_data, 70)
            mid_mis_rate = self.calculate_misdiagnosis_risk(group_data, 120)
            late_mis_rate = self.calculate_misdiagnosis_risk(group_data, 200)

            # 计算各孕期不达标率
            early_non_compliance = self.calculate_non_compliance_rate_by_period_static(group_data, "早期")
            mid_non_compliance = self.calculate_non_compliance_rate_by_period_static(group_data, "中期")
            late_non_compliance = self.calculate_non_compliance_rate_by_period_static(group_data, "晚期")

            results.append({
                '组ID': i,
                'BMI范围': (round(bmi_min, 2), round(bmi_max, 2)),
                '最佳检测时点(周)': optimal_time,
                '最小风险': min_risk,
                '样本数量': len(group_data),
                '数据孕周范围': (round(min_weeks, 2), round(max_weeks, 2)),
                '早期误检率': early_mis_rate,
                '中期误检率': mid_mis_rate,
                '晚期误检率': late_mis_rate,
                '早期不达标率': early_non_compliance,
                '中期不达标率': mid_non_compliance,
                '晚期不达标率': late_non_compliance
            })

        self.results_df = pd.DataFrame(results)
        return self.results_df

    #计算特定孕期阶段的不达标率
    def calculate_non_compliance_rate_by_period_static(self, group_data, period):

        period_data = group_data[group_data['孕期阶段'] == period]
        if len(period_data) == 0:
            return np.nan
        return (period_data['Y染色体浓度'] < 0.04).mean()

    #优化单个分组的最佳检测时点
    def optimize_detection_time(self, group_data):

        min_days = group_data['孕周天数'].min()
        max_days = group_data['孕周天数'].max()

        def objective_function(gestational_days):
            return self.calculate_composite_risk_three_factors(group_data, gestational_days)

        constraints = [{'type': 'ineq', 'fun': lambda x: x - min_days},
                       {'type': 'ineq', 'fun': lambda x: max_days - x}]

        result = minimize(objective_function, [(min_days + max_days) / 2],
                          constraints=constraints, method='SLSQP')

        if not result.success:
            return None, None

        return round(result.x[0] / 7, 2), result.fun

    #计算三因素综合风险
    def calculate_composite_risk_three_factors(self, group_data, gestational_days):

        non_compliance = self.calculate_non_compliance_rate_by_period(group_data, gestational_days)
        misdiagnosis = self.calculate_misdiagnosis_risk(group_data, gestational_days)
        late_risk = self.calculate_late_detection_risk_regression(gestational_days)
        return 0.3 * non_compliance + 0.6 * misdiagnosis + 0.1 * late_risk

    #可视化分析结果
    def visualize_results(self):

        if self.results_df is None or self.results_df.empty:
            return

        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))

        # 误检率可视化
        for i, row in self.results_df.iterrows():
            axes[0, 0].bar(i - 0.25, row['早期误检率'], 0.25, color='skyblue')
            axes[0, 0].bar(i, row['中期误检率'], 0.25, color='lightgreen')
            axes[0, 0].bar(i + 0.25, row['晚期误检率'], 0.25, color='lightcoral')

        axes[0, 0].legend(['早期误检率', '中期误检率', '晚期误检率'])
        axes[0, 0].set_title('各BMI分组在不同孕期的误检率')
        axes[0, 0].set_xticks(range(len(self.results_df)))
        axes[0, 0].set_xticklabels([f"组 {i + 1}" for i in self.results_df['组ID']])

        # 不达标率可视化
        for i, row in self.results_df.iterrows():
            axes[0, 1].bar(i - 0.25, row['早期不达标率'], 0.25, color='lightblue')
            axes[0, 1].bar(i, row['中期不达标率'], 0.25, color='lightgreen')
            axes[0, 1].bar(i + 0.25, row['晚期不达标率'], 0.25, color='lightpink')

        axes[0, 1].legend(['早期不达标率', '中期不达标率', '晚期不达标率'])
        axes[0, 1].set_title('各BMI分组在不同孕期的Y染色体不达标率')
        axes[0, 1].set_xticks(range(len(self.results_df)))
        axes[0, 1].set_xticklabels([f"组 {i + 1}" for i in self.results_df['组ID']])

        # 最佳检测时点可视化
        min_weeks = self.results_df['数据孕周范围'].apply(lambda x: x[0])
        max_weeks = self.results_df['数据孕周范围'].apply(lambda x: x[1])
        optimal_times = self.results_df['最佳检测时点(周)']

        axes[1, 0].errorbar(range(len(self.results_df)), min_weeks, fmt='_', capsize=5, color='gray',
                            label='数据孕周下限')
        axes[1, 0].errorbar(range(len(self.results_df)), max_weeks, fmt='_', capsize=5, color='gray',
                            label='数据孕周上限')
        axes[1, 0].scatter(range(len(self.results_df)), optimal_times, s=100, color='red', label='最佳检测时点')

        for i, row in self.results_df.iterrows():
            min_w, max_w = row['数据孕周范围']
            optimal = row['最佳检测时点(周)']
            axes[1, 0].text(i, max_w + 0.5, f"数据范围: [{min_w}, {max_w}]", ha='center', fontsize=8)
            axes[1, 0].text(i, optimal + 0.5, f"最佳时点: {optimal}", ha='center', fontsize=8)

        axes[1, 0].set_title('各BMI分组的最佳检测时点与数据范围')
        axes[1, 0].set_xticks(range(len(self.results_df)))
        axes[1, 0].set_xticklabels([f"组 {i + 1}" for i in self.results_df['组ID']])
        axes[1, 0].legend()

        axes[1, 1].set_visible(False)
        plt.tight_layout()
        plt.savefig('NIPT检测时点优化分析.png', dpi=300)
        plt.show()

    #保存分析结果
    def save_results(self, filename="D:\\国赛\\CUMCM2025Problems\\C题\\BMI分组与最佳NIPT时点分析结果.xlsx"):

        if self.results_df is None:
            return False

        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.results_df.to_excel(filename, index=False)
            print(f"结果已保存到: {filename}")
            return True
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False


def main():
    optimizer = NIPTOptimizer("D:\\国赛\\CUMCM2025Problems\\C题\\问题二\\男胎怀孕检测数据(3).xlsx")

    if not optimizer.load_and_preprocess_data():
        return

    optimizer.calculate_earliest_compliance_time()

    # BMI与最早达标时间关系图
    valid_data = optimizer.earliest_compliance_time_df[optimizer.earliest_compliance_time_df['最早达标时间'] < np.inf]
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'SimSun']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(10, 6))
    plt.scatter(valid_data['BMI'], valid_data['最早达标时间'] / 7, alpha=0.5)
    plt.xlabel('BMI')
    plt.ylabel('最早达标时间 (周)')
    plt.title('BMI与最早达标时间的关系')
    plt.grid(True)
    plt.savefig('BMI_vs_compliance_time.png', dpi=300)
    plt.show()

    # 联合优化
    results_df = optimizer.joint_optimization()
    print("\n优化结果:")
    print(results_df)
    optimizer.save_results()
    optimizer.visualize_results()

    # 敏感性分析
    stability_results = optimizer.run_sensitivity_analysis(n_simulations=50)



if __name__ == "__main__":
    main()