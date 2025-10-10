# 导库
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pyecharts.options as opt
import warnings

from pypalettes import load_cmap, get_hex
from pyecharts.charts import Pie

warnings.filterwarnings('ignore')
plt.rcParams['font.family'] = 'Kaiti'
plt.rcParams['axes.unicode_minus'] = False # 显示负号


df1 = pd.read_excel('./附件.xlsx', sheet_name=0)

# 先得到孕周的天数
def convert_gestational_week(week_str):
    """
    将孕周字符串转换为天数
    格式示例: '12w+3d', '15w', '20+4' 等
    """
    if pd.isna(week_str):
        return float('nan')
    
    week_str = str(week_str).lower().strip()
    
    try:
        if '+' in week_str:
            parts = week_str.split('+')
            weeks = int(parts[0].replace('w', '').replace('周', ''))
            days = int(parts[1].replace('d', '').replace('天', ''))
            return weeks * 7 + days
        elif 'w' in week_str or '周' in week_str:
            weeks = int(week_str.replace('w', '').replace('周', ''))
            return weeks * 7
        else:
            # 尝试直接转换为数字（可能是纯周数）
            try:
                weeks = float(week_str)
                return weeks * 7
            except:
                return float('nan')
    except:
        return float('nan')

# 应用转换函数
df1['孕周天数'] = df1['检测孕周'].apply(convert_gestational_week)

# 数据预处理

# 按孕妇代码和检测抽血次数排序
# df1 = df1.sort_values(['孕妇代码', '检测抽血次数', '序号'])
    
# 找出需要删除的重复行
# rows_to_remove = []
    
#for i in range(len(df1) - 1):
#    current_row = df1.iloc[i]
#    next_row = df1.iloc[i + 1]
        
    # 检查是否是同一孕妇且检测抽血次数相同
#    if (current_row['孕妇代码'] == next_row['孕妇代码'] and 
#        current_row['检测抽血次数'] == next_row['检测抽血次数']):
        # 标记当前行为需要删除（保留最后一行）
#        rows_to_remove.append(i)
    
# 删除重复行
#df1_copy = df1.copy()
#df1 = df1.drop(df1.index[rows_to_remove])
#print(f"根据孕妇重复数据后剔除了 {len(df1_copy)- len(df1)}")

# 重新排序
#df1 = df1.sort_values('序号').reset_index(drop=True)


# bmi
# lower_bmi = 36
# upper_bmi = 40

# df1_copy = df1.copy()
# df1 = df1[(df1['孕妇BMI'] >= lower_bmi) & (df1['孕妇BMI'] < upper_bmi)].copy()
# print(f"根据bmi筛选后剔除了 {len(df1_copy)- len(df1)}")

# 剔除10周以下和26周以上的数据
# 首先将孕周转换为天数
# 定义筛选条件：10周（63天）至25周（182天）
lower_bound = 18 * 7  # 10周
upper_bound = 26 * 7  # 25周

# 筛选数据
df1_copy = df1.copy()
df1 = df1[(df1['孕周天数'] >= lower_bound) & (df1['孕周天数'] < upper_bound)].copy()
print(f"根据周数筛选后剔除了 {len(df1_copy)- len(df1)}")

# 剔除Y染色体浓度低的
# y_lower_bound = 0.04

# df1_copy = df1.copy()
# df1 = df1[df1['Y染色体浓度'] >= y_lower_bound].copy()
# print(f"根据Y染色体浓度筛选后剔除了 {len(df1_copy)- len(df1)}")

# 剔除GC含量异常的数据（正常范围40%~60%）
# 定义GC含量正常范围
#gc_normal_lower = 0.398
#gc_normal_upper = 0.60

# 筛选GC含量正常的数据
#df1_copy = df1.copy()
#df1 = df1[
#    (df1['GC含量'] >= gc_normal_lower) & 
#    (df1['GC含量'] <= gc_normal_upper)
# ].copy()

#print(f"根据GC浓度剔除了 {len(df1_copy)- len(df1)}")

# 筛选男胎数据（Y染色体浓度非空）
df1_copy = df1.copy()
df1 = df1[df1['Y染色体浓度'].notna()].copy()
print(f"根据Y浓度非空剔除了 {len(df1_copy)- len(df1)}")


# 第二步：异常值处理（IQR法则）
def remove_outliers(df, col):
    """使用IQR方法剔除异常值"""
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    before_count = len(df)
    df_clean = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    after_count = len(df_clean)
    
    print(f"{col}: 剔除 {before_count - after_count} 个异常值 "
          f"(范围: {lower_bound:.2f} - {upper_bound:.2f})")
    
    return df_clean

# 对关键变量进行异常值处理
variables_to_clean = ["孕周", "BMI指标", "Y染色体浓度"]
for col in variables_to_clean:
    if col in df1.columns:
        df1 = remove_outliers(df1, col)

print(f"异常值处理后剩余样本量: {len(df1)}")

# 输出到xlsx文件
df1.to_excel("男胎怀孕检测数据.xlsx", index=False)

# 根据题目BMI分组
labels = [
    '[20,28]',
    '[28,32]', 
    '[32,36]',
    '[36,40]',
    '≥40'
]

# 归类
bins = [20,28,32,36,40,float("inf")]
df1['BMI分级']= pd.cut(df1['孕妇BMI'],bins=bins,labels=labels,right=False)

# 计算每个分组的数量
bmi_counts = df1['BMI分级'].value_counts().sort_index()

# 计算百分比
total_count = len(df1)
percentages = (bmi_counts / total_count * 100).round(1).tolist()

# 绘制BMI展示图
colors = ["#356BA5", "#CE7B29", "#AE585A", '#76B7B2', "#4E8B46"]
fig, ax = plt.subplots(figsize=(10, 8))

# 绘制饼图
wedges, texts, autotexts = ax.pie(
    percentages, 
    labels=labels, 
    colors=colors,
    autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize': 11, 'fontweight': 'bold'}
)

# 美化标签
plt.setp(autotexts, size=11, weight="bold", color="white")
plt.setp(texts, size=11)

# 标题
ax.set_title('孕妇BMI分组分布（基于NIPT数据）', 
             fontsize=16, fontweight='bold', pad=20)

# 添加图例
ax.legend(wedges, [f'{label}: {size}%' for label, size in zip(labels, percentages)],
          title="BMI分组",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1),
          fontsize=10)

# 确保饼图是圆形
ax.axis('equal')

# 调整布局
plt.tight_layout()

# 显示图表
plt.show()

# 打印统计信息
print("BMI分组统计：")
for i, (label, size) in enumerate(zip(labels, percentages)):
    print(f"{label}: {size}%")

# 孕周可视化


# 孕周天数分箱统计（基于临床分期）
bins_weeks = [0, 84, 189, float('inf')]  # 0-12周, 13-27周, 28周以上（以天为单位）
labels_weeks = ['早期(0-12周)', '中期(13-27周)', '晚期(28周以上)']

# 进行孕周分箱
df1['孕周分期'] = pd.cut(df1['孕周天数'], bins=bins_weeks, labels=labels_weeks, right=False)

# 计算每个分期的数量
week_counts = df1['孕周分期'].value_counts().sort_index()
week_percentages = (week_counts / len(df1.dropna(subset=['孕周天数'])) * 100).round(1)

# 输出分箱统计
print("=" * 50)
print("孕周天数分箱统计（临床分期）")
print("=" * 50)
for label in labels_weeks:
    count = week_counts.get(label, 0)
    percentage = week_percentages.get(label, 0)
    print(f"{label}: {count}例 ({percentage}%)")

print("=" * 50)
print(f"有效样本数: {len(df1.dropna(subset=['孕周天数']))}")
print(f"缺失值数: {df1['孕周天数'].isna().sum()}")

# 可视化
plt.figure(figsize=(10, 6))
plt.hist(df1['孕周天数'].dropna(), bins=10, density=True, alpha=0.6, edgecolor="black")
df1['孕周天数'].dropna().plot(kind="density", color="red")
plt.title("男胎怀孕检测天数分布")
plt.xlabel("天")
plt.ylabel("密度")
plt.savefig("image/男胎怀孕检测天数分布.png", dpi=500)
plt.show()


# 年龄，孕妇BMI，原始读段数，孕妇天数，基因组上比对的比例，重复读段的比例，13号染色体的z值，18号染色体的z值，Y染色体的z值，X染色体的浓度，过滤掉读段数的比例
# 读取数据
df = pd.read_excel('./男胎怀孕检测数据.xlsx', sheet_name=0)

# 选择特征列
features = [
    '年龄', '孕妇BMI', '孕周天数','原始读段数',
    '在参考基因组上比对的比例', '重复读段的比例',
    'Y染色体的Z值',
    'X染色体浓度', '被过滤掉读段数的比例'
]
target = 'Y染色体浓度'

# 检查所选列是否有空值
print("每列空值数量：")
print(df[features + [target]].isnull().sum())
df_clean = df[features + [target]].dropna()

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np
from sklearn.preprocessing import StandardScaler

# 线性回归
X = df_clean[features]
y = df_clean[target]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 训练模型
model = LinearRegression()
model.fit(X_train, y_train)

# 预测
y_pred = model.predict(X_test)

# 评估
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\n 线性回归模型效果")
print(f"R²: {r2:.4f}")
print(f"RMSE: {rmse:.4f}")


# ridge回归
X = df_clean[features]
y = df_clean[target]

# 数据标准化（对Ridge回归很重要）
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 使用交叉验证寻找最佳alpha值
from sklearn.linear_model import RidgeCV
from sklearn.linear_model import Ridge, RidgeCV

# 尝试不同的alpha值
alphas = np.logspace(-3, 3, 50)
ridge_cv = RidgeCV(alphas=alphas, cv=5, scoring='neg_mean_squared_error')
ridge_cv.fit(X_train, y_train)

best_alpha = ridge_cv.alpha_
print(f"\n最佳alpha值: {best_alpha:.4f}")

# 使用最佳alpha训练Ridge模型
ridge_model = Ridge(alpha=best_alpha)
ridge_model.fit(X_train, y_train)

# 预测
y_pred = ridge_model.predict(X_test)

# 评估模型
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_squared_error(y_test, y_pred)

print(f"\nRidge回归模型评估结果：")
print(f"R²: {r2:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"MSE: {mae:.4f}")



# 输出模型性能摘要
print("\n=== 模型性能摘要 ===")
print(f"最佳正则化参数(alpha): {best_alpha:.4f}")
print(f"决定系数(R²): {r2:.4f}")
print(f"均方根误差(RMSE): {rmse:.4f}")
print(f"平均绝对误差(MAE): {mae:.4f}")
print(f"使用的样本数: {len(df_clean)}")
print(f"特征数量: {len(features)}")


# 导库
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import statsmodels.api as sm
import statsmodels.formula.api as smf
from patsy import dmatrix, cr
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')
plt.rcParams['font.family'] = 'Kaiti'
plt.rcParams['axes.unicode_minus'] = False # 显示负号

# 读取数据
df = pd.read_excel('./男胎怀孕检测数据.xlsx', sheet_name=0)


# 选择特征列
features = [
    '年龄', '孕妇BMI', '孕周天数','原始读段数',
    '在参考基因组上比对的比例', '重复读段的比例',
    'Y染色体的Z值',
    'X染色体浓度', '被过滤掉读段数的比例'
]
target = 'Y染色体浓度'

# 检查所选列是否有空值
print("每列空值数量：")
print(df[features + [target]].isnull().sum())
df_clean = df[features + [target]].dropna()

print("\n" + "="*60)
print("开始构建广义加性模型(GAM)")
print("="*60)

# 确保有BMI分级列
if 'BMI分级' not in df_clean.columns:
    # 重新创建BMI分级
    labels = ['[20,28]', '[28,32]', '[32,36]', '[36,40]', '≥40']
    bins = [20, 28, 32, 36, 40, float("inf")]
    df_clean['BMI分级'] = pd.cut(df_clean['孕妇BMI'], bins=bins, labels=labels, right=False)

# 选择GAM的特征
gam_features = [
    '孕妇BMI', '孕周天数', '年龄', '原始读段数',
    '在参考基因组上比对的比例', '重复读段的比例',
    'Y染色体的Z值', 'X染色体浓度'
]

target = 'Y染色体浓度'

# 确保所有特征都存在
available_features = [f for f in gam_features if f in df_clean.columns]
print(f"可用于GAM的特征: {available_features}")

# 准备数据
gam_data = df_clean[available_features + [target]].dropna()
print(f"GAM可用样本数: {len(gam_data)}")

# 为连续变量构建样条基
important_vars = ['孕妇BMI', '孕周天数', '年龄']  # 选择最重要的3个变量

df_spline = gam_data.copy()
spline_terms = []

for var in important_vars:
    if var in df_spline.columns:
        try:
            # 选择节点位置（基于分位数）
            knots = np.quantile(df_spline[var].dropna(), [0.25, 0.5, 0.75])
            
            # 创建三次样条基
            spline_basis = dmatrix(f"cr({var}, knots=knots)", 
                                  {var: df_spline[var]}, 
                                  return_type='dataframe')
            
            # 重命名列
            spline_cols = [f'{var}_sp{i}' for i in range(spline_basis.shape[1])]
            spline_basis.columns = spline_cols
            
            # 添加到数据集
            df_spline = pd.concat([df_spline, spline_basis], axis=1)
            spline_terms.extend(spline_cols)
            print(f"为变量 {var} 创建了 {len(spline_cols)} 个样条基")
            
        except Exception as e:
            print(f"为变量 {var} 创建样条基时出错: {e}")

# 添加其他变量的线性项
linear_terms = [var for var in available_features if var not in important_vars]

# 构建GAM公式
if spline_terms:
    if linear_terms:
        formula = f"{target} ~ {' + '.join(spline_terms)} + {' + '.join(linear_terms)}"
    else:
        formula = f"{target} ~ {' + '.join(spline_terms)}"
    
    print(f"\nGAM模型公式: {formula}")
    
    # 拟合广义加性模型
    try:
        print("正在拟合GAM模型...")
        
        # 使用普通最小二乘法
        X = df_spline[spline_terms + linear_terms]
        X = sm.add_constant(X)  # 添加截距项
        y = df_spline[target]
        
        model_gam = sm.OLS(y, X).fit()
        
        # 输出模型结果
        print("\n" + "="*80)
        print("广义加性模型(GAM)拟合结果")
        print("="*80)
        print(model_gam.summary())
        
        # 模型评估
        y_pred = model_gam.predict(X)
        residuals = y - y_pred
        
        # 计算性能指标
        r_squared = model_gam.rsquared
        adj_r_squared = model_gam.rsquared_adj
        rmse = np.sqrt(np.mean(residuals**2))
        
        print("\n" + "="*80)
        print("模型评估指标")
        print("="*80)
        print(f"决定系数(R²): {r_squared:.4f}")
        print(f"调整R²: {adj_r_squared:.4f}")
        print(f"均方根误差(RMSE): {rmse:.4f}")
        print(f"对数似然值: {model_gam.llf:.4f}")
        print(f"AIC: {model_gam.aic:.4f}")
        print(f"BIC: {model_gam.bic:.4f}")
        
        # ============ 显著性分析 ============
        print("\n" + "="*80)
        print("变量显著性分析")
        print("="*80)
        
        # 提取p值并分类
        p_values = model_gam.pvalues
        significant_vars = []
        marginal_vars = []
        non_significant_vars = []
        
        for var, p_val in p_values.items():
            if var == 'const':
                continue
            if p_val < 0.01:
                significant_vars.append((var, p_val))
            elif p_val < 0.05:
                marginal_vars.append((var, p_val))
            else:
                non_significant_vars.append((var, p_val))
        
        # 输出显著性结果
        print("\n高度显著变量 (p < 0.01):")
        for var, p_val in significant_vars:
            print(f"  {var}: p = {p_val:.4f}")
        
        print("\n边缘显著变量 (0.01 ≤ p < 0.05):")
        for var, p_val in marginal_vars:
            print(f"  {var}: p = {p_val:.4f}")
        
        print("\n不显著变量 (p ≥ 0.05):")
        for var, p_val in non_significant_vars:
            print(f"  {var}: p = {p_val:.4f}")
        
        # 按变量类型分组分析
        print("\n" + "="*80)
        print("按变量类型分组分析")
        print("="*80)
        
        # 分析样条变量的整体显著性
        spline_groups = {}
        for var in important_vars:
            var_spline_terms = [term for term in spline_terms if term.startswith(var)]
            # 检查这些项中是否有显著的
            significant_spline = any(p_values[term] < 0.05 for term in var_spline_terms if term in p_values)
            spline_groups[var] = {
                'terms': var_spline_terms,
                'has_significant': significant_spline,
                'min_p': min([p_values.get(term, 1) for term in var_spline_terms])
            }
        
        print("\n样条变量显著性分析:")
        for var, info in spline_groups.items():
            status = "显著" if info['has_significant'] else "不显著"
            print(f"  {var}: {status} (最小p值: {info['min_p']:.4f})")
        
        # 线性变量的显著性
        print("\n线性变量显著性分析:")
        for var in linear_terms:
            p_val = p_values.get(var, 1)
            status = "高度显著" if p_val < 0.01 else ("边缘显著" if p_val < 0.05 else "不显著")
            print(f"  {var}: {status} (p = {p_val:.4f})")
        
        # 绘制诊断图
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 预测值 vs 真实值
        axes[0,0].scatter(y_pred, df_spline[target], alpha=0.6)
        axes[0,0].plot([df_spline[target].min(), df_spline[target].max()], 
                      [df_spline[target].min(), df_spline[target].max()], 
                      'r--', lw=2)
        axes[0,0].set_xlabel('预测值')
        axes[0,0].set_ylabel('真实值')
        axes[0,0].set_title('GAM: 预测值 vs 真实值')
        axes[0,0].grid(True, alpha=0.3)
        
        # 2. 残差图
        axes[0,1].scatter(y_pred, residuals, alpha=0.6)
        axes[0,1].axhline(y=0, color='red', linestyle='--')
        axes[0,1].set_xlabel('预测值')
        axes[0,1].set_ylabel('残差')
        axes[0,1].set_title('GAM: 残差图')
        axes[0,1].grid(True, alpha=0.3)
        
        # 3. 残差直方图
        axes[1,0].hist(residuals, bins=30, alpha=0.7, edgecolor='black')
        axes[1,0].set_xlabel('残差')
        axes[1,0].set_ylabel('频数')
        axes[1,0].set_title('GAM: 残差分布')
        axes[1,0].grid(True, alpha=0.3)
        
        # 4. QQ图
        sm.qqplot(residuals, line='45', ax=axes[1,1])
        axes[1,1].set_title('GAM: 残差QQ图')
        
        plt.tight_layout()
        plt.savefig('image/GAM模型诊断图.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 保存模型结果和显著性分析
        results_summary = {
            'model_type': 'GAM',
            'n_observations': len(df_spline),
            'r_squared': r_squared,
            'adj_r_squared': adj_r_squared,
            'rmse': rmse,
            'log_likelihood': model_gam.llf,
            'aic': model_gam.aic,
            'bic': model_gam.bic,
            'formula': formula,
            'significant_variables': {var: float(p_val) for var, p_val in significant_vars},
            'marginal_variables': {var: float(p_val) for var, p_val in marginal_vars},
            'non_significant_variables': {var: float(p_val) for var, p_val in non_significant_vars},
            'spline_analysis': spline_groups
        }
        
        # 保存到文件
        import json
        with open('gam_model_results.json', 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, indent=4, ensure_ascii=False)
        
        print("\nGAM模型结果和显著性分析已保存到 'gam_model_results.json'")
        
    except Exception as e:
        print(f"GAM模型拟合失败: {e}")
        
else:
    print("无法创建样条基，跳过GAM建模")

print("\nGAM建模和显著性分析完成！")


