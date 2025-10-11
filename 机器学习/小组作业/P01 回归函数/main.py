from regression import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def get_df(filename, selected_cols, target_col):
    """
    filename: 数据集名（不带后缀）
    selected_cols: 选择的特征列名
    target_col: 目标列名
    """
    df = pd.read_csv(f'archive/{filename}.csv')
    print("数据列名:", df.columns.tolist())
    print("\n数据前5行:")
    print(df.head())
    print(f"\n数据形状: {df.shape}")
    
    # 检查缺失值
    print(f"\n缺失值统计:")
    print(df.isnull().sum())
    
    X = df[selected_cols]
    y = df[target_col]
    
    # 处理缺失值
    y = y.fillna(y.mean())
    for col in X.columns:
        X.loc[:,col] = X[col].fillna(X[col].mean())
    
    # 数据基本信息
    print(f"\n特征统计信息:")
    print(X.describe())
    print(f"\n目标变量统计信息:")
    print(f"均值: {y.mean():.2f}, 标准差: {y.std():.2f}")
    print(f"最小值: {y.min():.2f}, 最大值: {y.max():.2f}")
    
    return X, y

def run_basic_linear_models(X, y):
    """运行基础线性回归模型（在整个数据集上）"""
    print("\n" + "="*50)
    print("基础线性回归模型（全数据集）")
    print("="*50)
    
    # OLS
    beta, y_pred, r_squared = OLS(X, y)
    print("OLS:")
    print("系数 (包含截距项):", beta)
    print("R²:", r_squared)
    
    # Ridge
    alpha = 0.1
    weights, y_pred, r_squared = Ridge(X, y, alpha)
    print("\nRidge:")
    print("系数:", weights)
    print("R²:", r_squared)
    
    # Lasso
    alpha = 0.1
    lasso = Lasso(alpha=alpha, random_state=42)
    lasso.fit(X, y)
    beta = lasso.coef_
    y_pred = lasso.predict(X)
    r_squared = lasso.score(X, y)
    print("\nLasso:")
    print("系数:", beta)
    print("R²:", r_squared)

def run_ml_comparison(X, y):
    """运行机器学习回归模型比较（训练集/测试集划分）"""
    print("\n" + "="*50)
    print("机器学习回归模型比较（训练集/测试集）")
    print("="*50)
    
    # 比较多种回归模型
    results, X_test, y_test = compare_regression_models(X, y)
    
    # 绘制比较结果
    plot_comparison_results(results, X_test, y_test, X.columns)
    
    # 获取最佳模型
    best_model_name, best_result = get_best_model(results)
    
    return results, best_model_name, best_result

def plot_feature_relationships(X, y):
    """绘制特征与目标变量的关系图"""
    plt.figure(figsize=(15, 10))
    
    for i, col in enumerate(X.columns, 1):
        plt.subplot(2, 2, i)
        plt.scatter(X[col], y, alpha=0.6)
        plt.xlabel(col)
        plt.ylabel('Exam Score')
        plt.title(f'{col} vs Exam Score')
        
        # 添加趋势线
        z = np.polyfit(X[col], y, 1)
        p = np.poly1d(z)
        plt.plot(X[col], p(X[col]), "r--", alpha=0.8)
        
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def analyze_best_model(results, best_model_name, X_columns):
    """分析最佳模型的详细信息"""
    print("\n" + "="*50)
    print(f"最佳模型分析: {best_model_name}")
    print("="*50)
    
    best_result = results[best_model_name]
    
    if best_model_name == "OLS":
        coefficients = best_result['model']
        print("系数 (包含截距项):")
        print(f"  截距: {coefficients[0]:.4f}")
        for i, col in enumerate(X_columns, 1):
            print(f"  {col}: {coefficients[i]:.4f}")
            
    elif best_model_name == "Ridge":
        model_info = best_result['model']
        print("系数:")
        print(f"  截距: {model_info['intercept']:.4f}")
        for i, col in enumerate(X_columns):
            print(f"  {col}: {model_info['weights'][i]:.4f}")
            
    elif best_model_name == "Lasso":
        model = best_result['model']
        print("系数:")
        for i, col in enumerate(X_columns):
            print(f"  {col}: {model.coef_[i]:.4f}")
        print(f"  截距: {model.intercept_:.4f}")
        
    elif best_model_name == "Random Forest":
        model = best_result['model']
        print("特征重要性:")
        importances = model.feature_importances_
        for i, col in enumerate(X_columns):
            print(f"  {col}: {importances[i]:.4f}")

def run_custom_model_test(X, y):
    """运行自定义模型测试"""
    print("\n" + "="*50)
    print("自定义模型参数测试")
    print("="*50)
    
    # 测试不同的正则化参数
    alphas = [0.01, 0.1, 1.0, 10.0]
    
    print("Ridge回归不同alpha值测试:")
    for alpha in alphas:
        weights, y_pred, r_squared = Ridge(X, y, alpha)
        print(f"  alpha={alpha}: R方 = {r_squared:.4f}")
    
    print("\nLasso回归不同alpha值测试:")
    for alpha in alphas:
        lasso = Lasso(alpha=alpha, random_state=42)
        lasso.fit(X, y)
        r_squared = lasso.score(X, y)
        non_zero_coef = np.sum(lasso.coef_ != 0)
        print(f"  alpha={alpha}: R方 = {r_squared:.4f}, 非零系数: {non_zero_coef}")

def plot_model_predictions(results, y_test):
    """绘制模型预测结果对比"""
    plt.figure(figsize=(12, 8))
    
    # 选择前4个模型进行详细对比
    top_models = list(results.keys())[:4]
    
    for i, model_name in enumerate(top_models, 1):
        plt.subplot(2, 2, i)
        predictions = results[model_name]['predictions']
        r2 = results[model_name]['r2']
        
        plt.scatter(y_test, predictions, alpha=0.6)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        plt.xlabel('True Values')
        plt.ylabel('Predictions')
        plt.title(f'{model_name}\nR方 = {r2:.4f}')
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # 设置中文字体（如果需要）
    plt.rcParams['font.family'] = 'Kaiti'
    plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
    
    # 加载数据
    print("正在加载数据...")
    X, y = get_df('student_exam_scores', 
                  ['hours_studied', 'sleep_hours', 'attendance_percent', 'previous_scores'], 
                  'exam_score')
    
    # 绘制特征关系图
    print("\n绘制特征与目标变量关系图...")
    plot_feature_relationships(X, y)
    
    # 运行基础线性回归
    run_basic_linear_models(X, y)
    
    # 运行机器学习回归比较
    results, best_model_name, best_result = run_ml_comparison(X, y)
    
    # 分析最佳模型
    analyze_best_model(results, best_model_name, X.columns)
    
    # 运行自定义测试
    run_custom_model_test(X, y)
    
    # 绘制模型预测对比
    plot_model_predictions(results, best_result['predictions'])
    
    print("\n" + "="*50)
    print("分析完成!")
    print("="*50)
    print(f"推荐使用模型: {best_model_name}")
    print(f"最佳模型 R²: {best_result['r2']:.4f}")
    print(f"最佳模型 RMSE: {best_result['rmse']:.4f}")