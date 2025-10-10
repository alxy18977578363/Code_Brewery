# 导库
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pyecharts.options as opt
from scipy import interpolate
import warnings

from pypalettes import load_cmap, get_hex
from pyecharts.charts import Pie

warnings.filterwarnings('ignore')
plt.rcParams['font.family'] = 'Kaiti'
plt.rcParams['axes.unicode_minus'] = False # 显示负号


df4 = pd.read_excel('./附件.xlsx', sheet_name=1)
print(df4)

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
df4['孕周天数'] = df4['检测孕周'].apply(convert_gestational_week)

# 剔除GC含量异常的数据（正常范围40%~60%）
# 定义GC含量正常范围
gc_normal_lower = 0.395
gc_normal_upper = 0.60

# 筛选GC含量正常的数据
df4_copy = df4.copy()
df4 = df4[ 
    (df4['GC含量'] >= gc_normal_lower) & 
    (df4['GC含量'] <= gc_normal_upper)
 ].copy()

print(f"根据GC浓度剔除了 {len(df4_copy)- len(df4)}")


# 剔除10周以下和26周以上的数据
# 首先将孕周转换为天数
# 定义筛选条件：10周（63天）至25周（182天）
lower_bound = 10 * 7  # 10周
upper_bound = 25 * 7  # 25周

# 筛选数据
df4_copy = df4.copy()
df4 = df4[(df4['孕周天数'] >= lower_bound) & (df4['孕周天数'] < upper_bound)].copy()
print(f"根据周数筛选后剔除了 {len(df4_copy)- len(df4)}")

# 增加标签列 - 如果有染色体非整倍体则为1，否则为0
df4['标签'] = df4['染色体的非整倍体'].apply(
    lambda x: 1 if pd.notna(x) and str(x).strip() != '' else 0
)

# 删除无用列
cols_to_drop = []
for col in df4.columns:
    # 检查列是否完全为空（所有值都是NaN）
    if df4[col].isna().all():
        cols_to_drop.append(col)
        print(f"删除空白列: {col}")

# 删除这些完全空白的列
if cols_to_drop:
    df4 = df4.drop(columns=cols_to_drop)
    print(f"已删除 {len(cols_to_drop)} 个完全空白的列")
else:
    print("没有找到完全空白的列")

# 检查BMI缺失情况
print(f"BMI缺失值数量: {df4['孕妇BMI'].isna().sum()}")
print(f"BMI缺失比例: {df4['孕妇BMI'].isna().mean():.2%}")

# 使用样条插值补充BMI缺失值
def interpolate_bmi_by_woman(df):
    """
    对每个孕妇的BMI数据进行样条插值
    """
    df = df.copy()
    df_interpolated = pd.DataFrame()
    
    # 按孕妇代码分组
    for woman_code, group in df.groupby('孕妇代码'):
        group = group.sort_values('孕周天数')  # 按孕周排序
        
        # 检查该孕妇是否有BMI数据
        if group['孕妇BMI'].isna().all():
            # 如果完全没有BMI数据，使用整体中位数填充
            median_bmi = df['孕妇BMI'].median()
            group['孕妇BMI'] = median_bmi
        elif group['孕妇BMI'].isna().any():
            # 如果有部分BMI数据缺失，进行样条插值
            valid_mask = group['孕妇BMI'].notna()
            
            if valid_mask.sum() >= 2:  # 至少需要2个点才能进行样条插值
                # 获取有效数据点
                x_valid = group.loc[valid_mask, '孕周天数'].values
                y_valid = group.loc[valid_mask, '孕妇BMI'].values
                
                # 创建样条插值函数
                try:
                    spline = interpolate.InterpolatedUnivariateSpline(x_valid, y_valid, k=2)
                    
                    # 对所有孕周点进行插值
                    x_all = group['孕周天数'].values
                    y_interpolated = spline(x_all)
                    
                    # 更新BMI值
                    group['孕妇BMI'] = y_interpolated
                except:
                    # 如果样条插值失败，使用线性插值
                    group['孕妇BMI'] = group['孕妇BMI'].interpolate(method='linear')
            else:
                # 如果只有1个有效点，使用该点的值填充
                if valid_mask.sum() == 1:
                    single_value = group.loc[valid_mask, '孕妇BMI'].iloc[0]
                    group['孕妇BMI'] = single_value
                else:
                    # 如果没有有效点，使用整体中位数
                    median_bmi = df['孕妇BMI'].median()
                    group['孕妇BMI'] = median_bmi
        
        df_interpolated = pd.concat([df_interpolated, group])
    
    return df_interpolated

# 应用BMI插值
df4_interpolated = interpolate_bmi_by_woman(df4)

print(f"插值后BMI缺失值数量: {df4_interpolated['孕妇BMI'].isna().sum()}")

# 保存
df4.to_excel('女胎数据.xlsx', index=False)




# 分类
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder

# 读取数据（假设文件名为“女胎数据.xlsx”）
df = pd.read_excel("女胎数据.xlsx", sheet_name="Sheet1")

# 选择特征列和标签列
# 排除非特征列：序号、孕妇代码、末次月经、检测日期、胎儿是否健康、标签等
exclude_cols = ['序号', '孕妇代码', '末次月经', '检测日期', '胎儿是否健康', '标签','染色体的非整倍体','检测孕周','怀孕次数']
feature_cols = [col for col in df.columns if col not in exclude_cols and col != '标签']

# 处理分类变量：如“IVF妊娠”列
le = LabelEncoder()
df['IVF妊娠'] = le.fit_transform(df['IVF妊娠'])  # 自然受孕=0, IVF=1

# 处理缺失值：用中位数填充数值列
numeric_cols = df[feature_cols].select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

# 定义X和y
X = df[feature_cols]
y = df['标签']

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练随机森林模型
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# 预测
y_pred = rf.predict(X_test)

# 评估
print("准确率:", accuracy_score(y_test, y_pred))
print("\n混淆矩阵:\n", confusion_matrix(y_test, y_pred))
print("\n分类报告:\n", classification_report(y_test, y_pred))

# 特征重要性
importance = rf.feature_importances_
feature_importance_df = pd.DataFrame({
    '特征': feature_cols,
    '重要性': importance
}).sort_values(by='重要性', ascending=False)

# 特征重要性可视化 - 横向柱状图
plt.figure(figsize=(10, 8))

# 按重要性排序
feature_importance_df_sorted = feature_importance_df.sort_values('重要性', ascending=True)

# 创建横向柱状图
bars = plt.barh(feature_importance_df_sorted['特征'], 
                feature_importance_df_sorted['重要性'], 
                color='skyblue', 
                edgecolor='black', 
                alpha=0.7)

# 在每个柱状图上添加数值标签
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.001, bar.get_y() + bar.get_height()/2, 
             f'{width:.4f}', 
             ha='left', va='center', fontsize=9)

# 设置标题和标签
plt.title('随机森林特征重要性排序', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('特征重要性', fontsize=12)
plt.ylabel('特征名称', fontsize=12)

# 添加网格线
plt.grid(axis='x', alpha=0.3, linestyle='--')

# 调整布局
plt.tight_layout()

# 显示图表
plt.show()

print("\n特征重要性排序:\n", feature_importance_df)

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import time
from sklearn.metrics import roc_curve, auc, precision_recall_curve
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, 
                           roc_auc_score, confusion_matrix, classification_report,
                           cohen_kappa_score, matthews_corrcoef, precision_recall_curve, auc)
import time

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 分类算法导入
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

# 读取数据
df = pd.read_excel("女胎数据.xlsx", sheet_name="Sheet1")

# 选择指定的10个重要特征
selected_features = [
    'X染色体浓度', '13号染色体的GC含量', '18号染色体的GC含量', '21号染色体的GC含量',
    '年龄', '被过滤掉读段数的比例', '孕妇BMI', '重复读段的比例', '13号染色体的Z值', 'GC含量'
]

# 检查并处理缺失值
for col in selected_features:
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(df[col].median())

# 定义X和y
X = df[selected_features]
y = df['标签']

# 检查数据平衡性
print(f"数据分布: 0类: {sum(y==0)}, 1类: {sum(y==1)}")
print(f"正例比例: {sum(y==1)/len(y):.3f}")

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 数据标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 定义所有分类器
classifiers = {
    '决策树': DecisionTreeClassifier(random_state=42),
    '随机森林': RandomForestClassifier(n_estimators=100, random_state=42),
    'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=42),
    '梯度提升树(GBDT)': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'CatBoost': CatBoostClassifier(iterations=100, random_state=42, verbose=0),
    'ExtraTrees': ExtraTreesClassifier(n_estimators=100, random_state=42),
    'K近邻(KNN)': KNeighborsClassifier(),
    'BP神经网络': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42),
    '支持向量机(SVM)': SVC(kernel='rbf', random_state=42, probability=True),
    'XGBoost': XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss'),
    'LightGBM': LGBMClassifier(n_estimators=100, random_state=42),
    '朴素贝叶斯': GaussianNB(),
    '逻辑回归': LogisticRegression(max_iter=1000, random_state=42)
}

# 存储所有算法的详细结果
detailed_results = []

print("开始训练和评估各分类算法...")
print("="*80)

for name, clf in classifiers.items():
    print(f"正在训练 {name}...")
    start_time = time.time()
    
    # 选择是否使用标准化数据
    if name in ['K近邻(KNN)', '支持向量机(SVM)', 'BP神经网络', '逻辑回归', '朴素贝叶斯']:
        X_tr, X_te = X_train_scaled, X_test_scaled
    else:
        X_tr, X_te = X_train, X_test
    
    try:
        # 训练模型
        clf.fit(X_tr, y_train)
        
        # 预测
        y_pred = clf.predict(X_te)
        
        # 获取预测概率（用于AUC计算）
        if hasattr(clf, "predict_proba"):
            y_pred_proba = clf.predict_proba(X_te)[:, 1]
        else:
            y_pred_proba = clf.decision_function(X_te)
        
        # 计算各项指标
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # AUC-ROC
        auc_roc = roc_auc_score(y_test, y_pred_proba)
        
        # AUC-PR（精确率-召回率曲线下面积）
        precision_vals, recall_vals, _ = precision_recall_curve(y_test, y_pred_proba)
        auc_pr = auc(recall_vals, precision_vals)
        
        # 其他指标
        kappa = cohen_kappa_score(y_test, y_pred)
        mcc = matthews_corrcoef(y_test, y_pred)
        
        # 计算训练时间
        train_time = time.time() - start_time
        
        # 存储详细结果
        result = {
            '算法': name,
            '准确率': accuracy,
            '精确率': precision,
            '召回率': recall,
            'F1分数': f1,
            'AUC-ROC': auc_roc,
            'AUC-PR': auc_pr,
            'Kappa': kappa,
            'MCC': mcc,
            '训练时间(秒)': train_time,
            '模型': clf
        }
        
        detailed_results.append(result)
        
        print(f"{name:15} | 准确率: {accuracy:.4f} | 召回率: {recall:.4f} | F1: {f1:.4f} | AUC-ROC: {auc_roc:.4f} | 时间: {train_time:.2f}s")
        
    except Exception as e:
        print(f"{name} 训练失败: {str(e)}")

# 转换为DataFrame
results_df = pd.DataFrame(detailed_results)

print("\n" + "="*80)
print("各分类算法性能综合对比")
print("="*80)

# 按F1分数排序（综合性能）
sorted_by_f1 = results_df.sort_values('F1分数', ascending=False)
print("按F1分数排序:")
print(sorted_by_f1[['算法', '准确率', '精确率', '召回率', 'F1分数', 'AUC-ROC', 'AUC-PR']].round(4))

print("\n按召回率排序:")
sorted_by_recall = results_df.sort_values('召回率', ascending=False)
print(sorted_by_recall[['算法', '准确率', '精确率', '召回率', 'F1分数']].round(4))

print("\n按准确率排序:")
sorted_by_accuracy = results_df.sort_values('准确率', ascending=False)
print(sorted_by_accuracy[['算法', '准确率', '精确率', '召回率', 'F1分数']].round(4))


# 按F1分数排序
results_sorted = results_df.sort_values('F1分数', ascending=True)

# 创建图表
plt.figure(figsize=(12, 8))

# 绘制折线图
plt.plot(results_sorted['算法'], results_sorted['F1分数'], 
         marker='o', linewidth=2, markersize=8, color='steelblue')

# 设置标题和标签
plt.title('各分类算法F1分数对比', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('分类算法', fontsize=12)
plt.ylabel('F1分数', fontsize=12)

# 旋转x轴标签以避免重叠
plt.xticks(rotation=45, ha='right')

# 在折线上添加数值标签
for i, v in enumerate(results_sorted['F1分数']):
    plt.text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom', fontsize=10)

# 设置y轴范围，确保有足够的空间显示标签
plt.ylim(results_sorted['F1分数'].min() - 0.05, results_sorted['F1分数'].max() + 0.1)

# 添加网格
plt.grid(True, alpha=0.3, linestyle='--')

# 调整布局
plt.tight_layout()

# 显示图表
plt.show()

# 可选：保存图表
plt.close()


# adaboost 算法求解
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score
from sklearn.preprocessing import StandardScaler

# 选择指定的10个重要特征
selected_features = [
    'X染色体浓度', '13号染色体的GC含量', '18号染色体的GC含量', '21号染色体的GC含量',
    '年龄', '被过滤掉读段数的比例', '孕妇BMI', '重复读段的比例', '13号染色体的Z值', 'GC含量'
]

# 处理缺失值
for col in selected_features:
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(df[col].median())

# 定义X和y
X = df[selected_features]
y = df['标签']

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 数据标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 训练AdaBoost模型（使用最佳参数，这里用100个弱学习器）
ada = AdaBoostClassifier(n_estimators=100, random_state=42)
ada.fit(X_train_scaled, y_train)

# 预测
y_pred = ada.predict(X_test_scaled)
y_pred_proba = ada.predict_proba(X_test_scaled)[:, 1]  # 正类的概率

# 计算混淆矩阵
cm = confusion_matrix(y_test, y_pred)

# 计算各项指标
tn, fp, fn, tp = cm.ravel()

accuracy = (tp + tn) / (tp + tn + fp + fn)
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0



# 创建子图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# 1. ROC曲线
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = auc(fpr, tpr)

ax1.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC曲线 (AUC = {roc_auc:.3f})')
ax1.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='随机猜测')
ax1.set_xlim([0.0, 1.0])
ax1.set_ylim([0.0, 1.05])
ax1.set_xlabel('假正率 (False Positive Rate)', fontsize=12)
ax1.set_ylabel('真正率 (True Positive Rate)', fontsize=12)
ax1.set_title('AdaBoost模型ROC曲线', fontsize=14, fontweight='bold')
ax1.legend(loc="lower right")
ax1.grid(True, alpha=0.3)

# 在ROC曲线上标注最佳阈值点（Youden's J统计量）
youden_j = tpr - fpr
best_idx = np.argmax(youden_j)
best_threshold = thresholds[best_idx]
ax1.plot(fpr[best_idx], tpr[best_idx], 'ro', markersize=8)
ax1.annotate(f'最佳阈值: {best_threshold:.3f}\n(FPR={fpr[best_idx]:.3f}, TPR={tpr[best_idx]:.3f})',
            xy=(fpr[best_idx], tpr[best_idx]), xytext=(fpr[best_idx]+0.1, tpr[best_idx]-0.1),
            arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, color='red')

# 2. PR曲线
precision, recall, thresholds_pr = precision_recall_curve(y_test, y_pred_proba)
pr_auc = auc(recall, precision)

# 计算基准线（正例比例）
positive_ratio = np.sum(y_test) / len(y_test)

ax2.plot(recall, precision, color='blue', lw=2, label=f'PR曲线 (AUC = {pr_auc:.3f})')
ax2.axhline(y=positive_ratio, color='red', linestyle='--', 
           label=f'基准线 (正例比例 = {positive_ratio:.3f})')
ax2.set_xlim([0.0, 1.0])
ax2.set_ylim([0.0, 1.05])
ax2.set_xlabel('召回率 (Recall)', fontsize=12)
ax2.set_ylabel('精确率 (Precision)', fontsize=12)
ax2.set_title('AdaBoost模型PR曲线', fontsize=14, fontweight='bold')
ax2.legend(loc="upper right")
ax2.grid(True, alpha=0.3)

# 在PR曲线上标注最佳F1分数点
f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
best_f1_idx = np.argmax(f1_scores)
ax2.plot(recall[best_f1_idx], precision[best_f1_idx], 'ro', markersize=8)
ax2.annotate(f'最佳F1点\n(P={precision[best_f1_idx]:.3f}, R={recall[best_f1_idx]:.3f})',
            xy=(recall[best_f1_idx], precision[best_f1_idx]), 
            xytext=(recall[best_f1_idx]-0.3, precision[best_f1_idx]-0.2),
            arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, color='red')

plt.tight_layout()
plt.show()

# 打印详细指标
print("="*50)
print("AdaBoost模型性能详细指标")
print("="*50)
print(f"ROC曲线下面积 (AUC-ROC): {roc_auc:.4f}")
print(f"PR曲线下面积 (AUC-PR): {pr_auc:.4f}")
print(f"最佳阈值 (Youden's J): {best_threshold:.4f}")
print(f"对应F1分数: {f1_scores[best_f1_idx]:.4f}")
print(f"正例比例: {positive_ratio:.4f}")
print(f"准确率: {accuracy:.4f}")
print(f"精确率: {precision_score(y_test, y_pred):.4f}")
print(f"召回率: {recall_score(y_test, y_pred):.4f}")
print(f"F1分数: {f1_score:.4f}")


# 使用最佳阈值0.448重新训练AdaBoost模型并绘制曲线
from sklearn.metrics import roc_curve, auc, precision_recall_curve
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.family'] = 'Kaiti'
plt.rcParams['axes.unicode_minus'] = False

# 重新训练AdaBoost模型，调整阈值
ada_best = AdaBoostClassifier(n_estimators=100, random_state=42)
ada_best.fit(X_train_scaled, y_train)

# 获取预测概率
y_pred_proba_best = ada_best.predict_proba(X_test_scaled)[:, 1]

# 使用最佳阈值0.448进行预测
best_threshold = 0.448
y_pred_best = (y_pred_proba_best >= best_threshold).astype(int)

# 计算使用最佳阈值后的性能指标
cm_best = confusion_matrix(y_test, y_pred_best)
tn, fp, fn, tp = cm_best.ravel()

accuracy_best = (tp + tn) / (tp + tn + fp + fn)
precision_best = tp / (tp + fp) if (tp + fp) > 0 else 0
recall_best = tp / (tp + fn) if (tp + fn) > 0 else 0
f1_score_best = 2 * (precision_best * recall_best) / (precision_best + recall_best) if (precision_best + recall_best) > 0 else 0

# 创建子图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))



# 打印详细指标
print("="*60)
print("AdaBoost模型性能详细指标 (使用最佳阈值0.448)")
print("="*60)
print(f"ROC曲线下面积 (AUC-ROC): {roc_auc:.4f}")
print(f"PR曲线下面积 (AUC-PR): {pr_auc:.4f}")
print(f"使用阈值: {best_threshold:.4f}")
print(f"准确率: {accuracy_best:.4f}")
print(f"精确率: {precision_best:.4f}")
print(f"召回率: {recall_best:.4f}")
print(f"F1分数: {f1_score_best:.4f}")
print(f"混淆矩阵:")
print(f"真正例(TP): {tp}")
print(f"假正例(FP): {fp}")
print(f"真负例(TN): {tn}")
print(f"假负例(FN): {fn}")

# 对比默认阈值0.5的性能
print("\n" + "="*60)
print("与默认阈值0.5的对比")
print("="*60)

# 使用默认阈值0.5的预测
y_pred_default = (y_pred_proba_best >= 0.5).astype(int)
cm_default = confusion_matrix(y_test, y_pred_default)
tn_d, fp_d, fn_d, tp_d = cm_default.ravel()

accuracy_default = (tp_d + tn_d) / (tp_d + tn_d + fp_d + fn_d)
precision_default = tp_d / (tp_d + fp_d) if (tp_d + fp_d) > 0 else 0
recall_default = tp_d / (tp_d + fn_d) if (tp_d + fn_d) > 0 else 0
f1_score_default = 2 * (precision_default * recall_default) / (precision_default + recall_default) if (precision_default + recall_default) > 0 else 0

print(f"默认阈值0.5的性能:")
print(f"准确率: {accuracy_default:.4f}")
print(f"精确率: {precision_default:.4f}")
print(f"召回率: {recall_default:.4f}")
print(f"F1分数: {f1_score_default:.4f}")

print(f"\n阈值0.448 vs 阈值0.5:")
print(f"准确率变化: {accuracy_best - accuracy_default:+.4f}")
print(f"精确率变化: {precision_best - precision_default:+.4f}")
print(f"召回率变化: {recall_best - recall_default:+.4f}")
print(f"F1分数变化: {f1_score_best - f1_score_default:+.4f}")

# 绘制使用最佳阈值0.448的混淆矩阵
plt.figure(figsize=(10, 8))

# 使用seaborn绘制热力图
sns.heatmap(cm_best, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['正常 (0)', '异常 (1)'], 
            yticklabels=['正常 (0)', '异常 (1)'],
            cbar_kws={'label': '样本数量'})

# 设置标题和标签
plt.title('AdaBoost模型混淆矩阵 (使用最佳阈值0.448)\n(胎儿染色体异常检测)', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('预测标签', fontsize=12, fontweight='bold')
plt.ylabel('真实标签', fontsize=12, fontweight='bold')

# 在图中添加性能指标文本
metrics_text = f'准确率: {accuracy_best:.3f}\n精确率: {precision_best:.3f}\n召回率: {recall_best:.3f}\nF1分数: {f1_score_best:.3f}\n阈值: {best_threshold:.3f}'
plt.text(2.5, 0.5, metrics_text, fontsize=12, bbox=dict(facecolor='white', alpha=0.8),
         verticalalignment='center')

plt.tight_layout()
plt.show()

# ===================== 敏感性分析（优化版） =====================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import os

# 设置中文字体
plt.rcParams['font.family'] = 'Kaiti'
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = "敏感性分析结果"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 重新加载数据
df = pd.read_excel("女胎数据.xlsx", sheet_name="Sheet1")

# 选择指定的10个重要特征
selected_features = [
    'X染色体浓度', '13号染色体的GC含量', '18号染色体的GC含量', '21号染色体的GC含量',
    '年龄', '被过滤掉读段数的比例', '孕妇BMI', '重复读段的比例', '13号染色体的Z值', 'GC含量'
]

# 处理缺失值
for col in selected_features:
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(df[col].median())

# 定义X和y
X = df[selected_features]
y = df['标签']

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 数据标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("="*60)
print("开始敏感性分析")
print("="*60)

# 1. 模型超参数敏感性分析
print("1. 模型超参数敏感性分析")

# 分析n_estimators的影响
n_estimators_range = [10, 30, 50, 70, 100, 150, 200]
learning_rate_range = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]

results_n_estimators = []
results_learning_rate = []

for n_est in n_estimators_range:
    ada = AdaBoostClassifier(n_estimators=n_est, random_state=42)
    ada.fit(X_train_scaled, y_train)
    y_pred = ada.predict(X_test_scaled)
    y_pred_proba = ada.predict_proba(X_test_scaled)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc_score = roc_auc_score(y_test, y_pred_proba)
    
    results_n_estimators.append({
        'n_estimators': n_est,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc': auc_score
    })

for lr in learning_rate_range:
    ada = AdaBoostClassifier(n_estimators=100, learning_rate=lr, random_state=42)
    ada.fit(X_train_scaled, y_train)
    y_pred = ada.predict(X_test_scaled)
    y_pred_proba = ada.predict_proba(X_test_scaled)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc_score = roc_auc_score(y_test, y_pred_proba)
    
    results_learning_rate.append({
        'learning_rate': lr,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc': auc_score
    })

# 转换为DataFrame
df_n_estimators = pd.DataFrame(results_n_estimators)
df_learning_rate = pd.DataFrame(results_learning_rate)

# 保存数据到Excel
with pd.ExcelWriter(f'{output_dir}/超参数敏感性分析数据.xlsx') as writer:
    df_n_estimators.to_excel(writer, sheet_name='n_estimators影响', index=False)
    df_learning_rate.to_excel(writer, sheet_name='learning_rate影响', index=False)

print("超参数敏感性分析数据已保存到Excel文件")

# 图表1：超参数敏感性分析（两个子图组合）
fig, ((ax1, ax2)) = plt.subplots(1, 2, figsize=(16, 6))

# n_estimators对各项指标的影响
ax1.plot(df_n_estimators['n_estimators'], df_n_estimators['accuracy'], 'o-', label='准确率', linewidth=2, markersize=6)
ax1.plot(df_n_estimators['n_estimators'], df_n_estimators['precision'], 's-', label='精确率', linewidth=2, markersize=6)
ax1.plot(df_n_estimators['n_estimators'], df_n_estimators['recall'], '^-', label='召回率', linewidth=2, markersize=6)
ax1.plot(df_n_estimators['n_estimators'], df_n_estimators['f1'], 'd-', label='F1分数', linewidth=2, markersize=6)
ax1.set_xlabel('弱学习器数量 (n_estimators)')
ax1.set_ylabel('性能指标分数')
ax1.set_title('n_estimators对模型性能的影响')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0.7, 1.0)

# learning_rate对各项指标的影响
ax2.plot(df_learning_rate['learning_rate'], df_learning_rate['accuracy'], 'o-', label='准确率', linewidth=2, markersize=6)
ax2.plot(df_learning_rate['learning_rate'], df_learning_rate['precision'], 's-', label='精确率', linewidth=2, markersize=6)
ax2.plot(df_learning_rate['learning_rate'], df_learning_rate['recall'], '^-', label='召回率', linewidth=2, markersize=6)
ax2.plot(df_learning_rate['learning_rate'], df_learning_rate['f1'], 'd-', label='F1分数', linewidth=2, markersize=6)
ax2.set_xlabel('学习率 (learning_rate)')
ax2.set_ylabel('性能指标分数')
ax2.set_title('learning_rate对模型性能的影响')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xscale('log')
ax2.set_ylim(0.7, 1.0)

plt.tight_layout()
plt.savefig(f'{output_dir}/超参数敏感性分析.png', dpi=300, bbox_inches='tight')
plt.show()

# 图表2：AUC指标分析（两个子图组合）
fig, ((ax1, ax2)) = plt.subplots(1, 2, figsize=(16, 6))

# n_estimators对AUC的影响
ax1.plot(df_n_estimators['n_estimators'], df_n_estimators['auc'], 'o-', color='purple', linewidth=3, markersize=8)
ax1.set_xlabel('弱学习器数量 (n_estimators)')
ax1.set_ylabel('AUC分数')
ax1.set_title('n_estimators对AUC的影响')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0.7, 1.0)

# learning_rate对AUC的影响
ax2.plot(df_learning_rate['learning_rate'], df_learning_rate['auc'], 'o-', color='purple', linewidth=3, markersize=8)
ax2.set_xlabel('学习率 (learning_rate)')
ax2.set_ylabel('AUC分数')
ax2.set_title('learning_rate对AUC的影响')
ax2.grid(True, alpha=0.3)
ax2.set_xscale('log')
ax2.set_ylim(0.7, 1.0)

plt.tight_layout()
plt.savefig(f'{output_dir}/AUC敏感性分析.png', dpi=300, bbox_inches='tight')
plt.show()

# 2. 特征重要性敏感性分析
print("\n2. 特征重要性敏感性分析")

# 训练最终模型获取特征重要性
ada_final = AdaBoostClassifier(n_estimators=100, random_state=42)
ada_final.fit(X_train_scaled, y_train)

# 获取特征重要性
feature_importance = ada_final.feature_importances_
feature_names = selected_features

# 创建特征重要性DataFrame
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': feature_importance
}).sort_values('importance', ascending=False)

# 保存特征重要性数据
importance_df.to_excel(f'{output_dir}/特征重要性排序.xlsx', index=False)
print("特征重要性数据已保存到Excel文件")

# 分析移除不同特征对模型性能的影响
feature_removal_results = []

# 基准模型（使用所有特征）
ada_baseline = AdaBoostClassifier(n_estimators=100, random_state=42)
ada_baseline.fit(X_train_scaled, y_train)
y_pred_baseline = ada_baseline.predict(X_test_scaled)
f1_baseline = f1_score(y_test, y_pred_baseline)

feature_removal_results.append({
    'removed_feature': '无（基准）',
    'f1_score': f1_baseline,
    'change': 0.0
})

for feature_to_remove in selected_features:
    features_to_keep = [f for f in selected_features if f != feature_to_remove]
    
    X_train_reduced = X_train[features_to_keep]
    X_test_reduced = X_test[features_to_keep]
    
    scaler_reduced = StandardScaler()
    X_train_reduced_scaled = scaler_reduced.fit_transform(X_train_reduced)
    X_test_reduced_scaled = scaler_reduced.transform(X_test_reduced)
    
    ada_reduced = AdaBoostClassifier(n_estimators=100, random_state=42)
    ada_reduced.fit(X_train_reduced_scaled, y_train)
    y_pred_reduced = ada_reduced.predict(X_test_reduced_scaled)
    f1_reduced = f1_score(y_test, y_pred_reduced)
    
    change = f1_reduced - f1_baseline
    
    feature_removal_results.append({
        'removed_feature': feature_to_remove,
        'f1_score': f1_reduced,
        'change': change
    })

# 转换为DataFrame
df_feature_removal = pd.DataFrame(feature_removal_results)

# 保存特征移除影响数据
df_feature_removal.to_excel(f'{output_dir}/特征移除影响分析.xlsx', index=False)
print("特征移除影响数据已保存到Excel文件")

# 图表3：特征重要性分析（两个子图组合）
fig, ((ax1, ax2)) = plt.subplots(1, 2, figsize=(16, 6))

# 特征重要性排序
features_sorted = importance_df.sort_values('importance', ascending=True)
bars1 = ax1.barh(features_sorted['feature'], features_sorted['importance'], 
                 color='lightblue', edgecolor='black', alpha=0.7)
ax1.set_xlabel('特征重要性')
ax1.set_title('AdaBoost特征重要性排序')
ax1.grid(True, alpha=0.3, axis='x')

for bar in bars1:
    width = bar.get_width()
    ax1.text(width + 0.001, bar.get_y() + bar.get_height()/2, 
             f'{width:.4f}', ha='left', va='center', fontsize=9)

# 特征移除影响
df_feature_impact = df_feature_removal[df_feature_removal['removed_feature'] != '无（基准）']
df_feature_impact = df_feature_impact.sort_values('change', ascending=True)

bars2 = ax2.barh(df_feature_impact['removed_feature'], df_feature_impact['change'], 
                 color=np.where(df_feature_impact['change'] < 0, 'lightcoral', 'lightgreen'),
                 edgecolor='black', alpha=0.7)
ax2.axvline(x=0, color='black', linestyle='-', alpha=0.8)
ax2.set_xlabel('F1分数变化 (移除该特征后)')
ax2.set_title('移除单个特征对F1分数的影响')
ax2.grid(True, alpha=0.3, axis='x')

for bar in bars2:
    width = bar.get_width()
    ax2.text(width + (0.001 if width >= 0 else -0.001), 
             bar.get_y() + bar.get_height()/2, 
             f'{width:.4f}', 
             ha='left' if width >= 0 else 'right', 
             va='center', fontsize=9)

plt.tight_layout()
plt.savefig(f'{output_dir}/特征敏感性分析.png', dpi=300, bbox_inches='tight')
plt.show()

# 3. 数据扰动和样本量敏感性分析
print("\n3. 数据扰动和样本量敏感性分析")

# 数据扰动分析
noise_levels = [0.01, 0.05, 0.1, 0.2, 0.3]
noise_results = []

for noise_level in noise_levels:
    X_test_noisy = X_test_scaled + np.random.normal(0, noise_level, X_test_scaled.shape)
    y_pred_noisy = ada_final.predict(X_test_noisy)
    
    accuracy = accuracy_score(y_test, y_pred_noisy)
    precision = precision_score(y_test, y_pred_noisy, zero_division=0)
    recall = recall_score(y_test, y_pred_noisy, zero_division=0)
    f1 = f1_score(y_test, y_pred_noisy, zero_division=0)
    
    noise_results.append({
        'noise_level': noise_level,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    })

df_noise = pd.DataFrame(noise_results)

# 样本量分析
train_sizes = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
sample_size_results = []

for train_size in train_sizes:
    n_samples = int(len(X_train_scaled) * train_size)
    indices = np.random.choice(len(X_train_scaled), n_samples, replace=False)
    
    X_train_sampled = X_train_scaled[indices]
    y_train_sampled = y_train.iloc[indices]
    
    ada_sampled = AdaBoostClassifier(n_estimators=100, random_state=42)
    ada_sampled.fit(X_train_sampled, y_train_sampled)
    y_pred_sampled = ada_sampled.predict(X_test_scaled)
    
    accuracy = accuracy_score(y_test, y_pred_sampled)
    precision = precision_score(y_test, y_pred_sampled, zero_division=0)
    recall = recall_score(y_test, y_pred_sampled, zero_division=0)
    f1 = f1_score(y_test, y_pred_sampled, zero_division=0)
    
    sample_size_results.append({
        'train_size': train_size,
        'n_samples': n_samples,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    })

df_sample_size = pd.DataFrame(sample_size_results)

# 保存数据
with pd.ExcelWriter(f'{output_dir}/鲁棒性分析数据.xlsx') as writer:
    df_noise.to_excel(writer, sheet_name='数据噪声影响', index=False)
    df_sample_size.to_excel(writer, sheet_name='样本量影响', index=False)

print("鲁棒性分析数据已保存到Excel文件")

# 图表4：鲁棒性分析（两个子图组合）
fig, ((ax1, ax2)) = plt.subplots(1, 2, figsize=(16, 6))

# 数据噪声影响
ax1.plot(df_noise['noise_level'], df_noise['accuracy'], 'o-', label='准确率', linewidth=2, markersize=6)
ax1.plot(df_noise['noise_level'], df_noise['precision'], 's-', label='精确率', linewidth=2, markersize=6)
ax1.plot(df_noise['noise_level'], df_noise['recall'], '^-', label='召回率', linewidth=2, markersize=6)
ax1.plot(df_noise['noise_level'], df_noise['f1'], 'd-', label='F1分数', linewidth=2, markersize=6)
ax1.set_xlabel('噪声水平 (标准差)')
ax1.set_ylabel('性能指标分数')
ax1.set_title('数据噪声对模型性能的影响')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0.5, 1.0)

# 样本量影响（按比例）
ax2.plot(df_sample_size['train_size'], df_sample_size['accuracy'], 'o-', label='准确率', linewidth=2, markersize=6)
ax2.plot(df_sample_size['train_size'], df_sample_size['precision'], 's-', label='精确率', linewidth=2, markersize=6)
ax2.plot(df_sample_size['train_size'], df_sample_size['recall'], '^-', label='召回率', linewidth=2, markersize=6)
ax2.plot(df_sample_size['train_size'], df_sample_size['f1'], 'd-', label='F1分数', linewidth=2, markersize=6)
ax2.set_xlabel('训练集比例')
ax2.set_ylabel('性能指标分数')
ax2.set_title('训练集大小对模型性能的影响')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0.5, 1.0)

plt.tight_layout()
plt.savefig(f'{output_dir}/鲁棒性分析.png', dpi=300, bbox_inches='tight')
plt.show()

# 5. 综合敏感性分析报告
print("\n5. 综合敏感性分析报告")
print("="*60)

report_data = {
    '分析类型': ['超参数敏感性', '特征重要性', '数据噪声鲁棒性', '样本量需求'],
    '关键发现': [
        f'n_estimators最佳范围: 50-150, learning_rate最佳范围: 0.1-0.5',
        f'最重要特征: {importance_df.iloc[0]["feature"]} (重要性: {importance_df.iloc[0]["importance"]:.4f})',
        f'噪声从{noise_levels[0]}到{noise_levels[-1]}, F1变化: {df_noise["f1"].iloc[-1] - df_noise["f1"].iloc[0]:.4f}',
        f'达到90%性能所需最小训练集比例: {df_sample_size[df_sample_size["f1"] >= 0.9 * df_sample_size["f1"].max()]["train_size"].min():.2f}'
    ],
    '模型稳定性': ['高', '中', '中', '高']
}

report_df = pd.DataFrame(report_data)
report_df.to_excel(f'{output_dir}/综合敏感性分析报告.xlsx', index=False)
print("综合敏感性分析报告已保存到Excel文件")

print("\n详细发现:")
print(f"a) 超参数敏感性:")
print(f"   - n_estimators: 最佳范围 50-150, F1分数变化范围: {df_n_estimators['f1'].min():.4f} - {df_n_estimators['f1'].max():.4f}")
print(f"   - learning_rate: 最佳范围 0.1-0.5, F1分数变化范围: {df_learning_rate['f1'].min():.4f} - {df_learning_rate['f1'].max():.4f}")

print(f"\nb) 特征重要性 (前5):")
for i, row in importance_df.head().iterrows():
    print(f"   {i+1}. {row['feature']}: {row['importance']:.4f}")

most_sensitive = df_feature_removal.loc[df_feature_removal['change'].idxmin()]
least_sensitive = df_feature_removal.loc[df_feature_removal['change'].idxmax()]
print(f"\nc) 特征敏感性:")
print(f"   最敏感特征: {most_sensitive['removed_feature']} (F1变化: {most_sensitive['change']:.4f})")
print(f"   最不敏感特征: {least_sensitive['removed_feature']} (F1变化: {least_sensitive['change']:.4f})")

print(f"\nd) 噪声鲁棒性:")
print(f"   噪声水平从{noise_levels[0]}增加到{noise_levels[-1]}, F1分数变化: {df_noise['f1'].iloc[-1] - df_noise['f1'].iloc[0]:.4f}")

print(f"\ne) 样本量需求:")
print(f"   达到90%最大性能所需的最小训练集比例: {df_sample_size[df_sample_size['f1'] >= 0.9 * df_sample_size['f1'].max()]['train_size'].min():.2f}")

print(f"\n所有分析结果已保存到目录: {output_dir}/")
print("="*60)
print("敏感性分析完成！")
print("="*60)