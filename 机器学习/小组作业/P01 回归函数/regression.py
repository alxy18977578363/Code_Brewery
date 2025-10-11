import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, explained_variance_score
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# 设置中文字体和样式
plt.rcParams['font.family'] = 'Kaiti'
plt.rcParams['axes.unicode_minus'] = False

# 梯度下降回归
class GradientDescentRegression:
    def __init__(self, learning_rate=0.01, max_iter=1000, tol=1e-4):
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.tol = tol
        self.weights = None
        self.bias = None
        self.loss_history = []
    
    def _compute_loss(self, X, y):
        """计算均方误差损失"""
        predictions = X @ self.weights + self.bias
        return np.mean((predictions - y) ** 2)
    
    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0
        
        for i in range(self.max_iter):
            # 前向传播
            predictions = X @ self.weights + self.bias
            
            # 计算梯度
            dw = (1 / n_samples) * X.T @ (predictions - y)
            db = (1 / n_samples) * np.sum(predictions - y)
            
            # 更新参数
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
            
            # 记录损失
            loss = self._compute_loss(X, y)
            self.loss_history.append(loss)
            
            # 收敛检查
            if i > 0 and abs(self.loss_history[-1] - self.loss_history[-2]) < self.tol:
                print(f"GD Regression converged after {i+1} iterations")
                break
    
    def predict(self, X):
        return X @ self.weights + self.bias

def calculate_additional_metrics(y_true, y_pred):
    """计算额外的评估指标"""
    metrics = {}
    
    # 基本指标
    metrics['r2'] = r2_score(y_true, y_pred)
    metrics['mse'] = mean_squared_error(y_true, y_pred)
    metrics['rmse'] = np.sqrt(metrics['mse'])
    metrics['mae'] = mean_absolute_error(y_true, y_pred)
    
    # 额外指标
    metrics['explained_variance'] = explained_variance_score(y_true, y_pred)
    
    # 平均绝对百分比误差
    epsilon = 1e-10  # 防止除零
    metrics['mape'] = np.mean(np.abs((y_true - y_pred) / (y_true + epsilon))) * 100
    
    # 均方根对数误差
    metrics['rmsle'] = np.sqrt(np.mean((np.log1p(y_true) - np.log1p(y_pred)) ** 2))
    
    # 中位数绝对误差
    metrics['medae'] = np.median(np.abs(y_true - y_pred))
    
    return metrics

def plot_residual_analysis(results, X_test, y_test):
    """绘制残差分析图表"""
    print("\n正在绘制残差分析图表...")
    
    n_models = len(results)
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.ravel()
    
    colors = plt.cm.Set3(np.linspace(0, 1, n_models))
    
    # 1. 残差分布图
    for i, (name, result) in enumerate(results.items()):
        residuals = y_test - result['predictions']
        axes[0].hist(residuals, bins=20, alpha=0.6, label=name, color=colors[i])
    
    axes[0].axvline(0, color='red', linestyle='--', linewidth=2)
    axes[0].set_xlabel('残差')
    axes[0].set_ylabel('频数')
    axes[0].set_title('残差分布比较')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 2. 残差 vs 预测值
    for i, (name, result) in enumerate(results.items()):
        residuals = y_test - result['predictions']
        axes[1].scatter(result['predictions'], residuals, alpha=0.6, 
                       label=name, color=colors[i], s=50)
    
    axes[1].axhline(y=0, color='red', linestyle='--', linewidth=2)
    axes[1].set_xlabel('预测值')
    axes[1].set_ylabel('残差')
    axes[1].set_title('残差 vs 预测值')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # 3. 残差QQ图（正态性检验）
    axes[2].clear()
    for i, (name, result) in enumerate(results.items()):
        residuals = y_test - result['predictions']
        stats.probplot(residuals, dist="norm", plot=axes[2])
    
    axes[2].set_title('残差QQ图（正态性检验）')
    axes[2].grid(True, alpha=0.3)
    
    # 4. 残差自相关图
    for i, (name, result) in enumerate(results.items()):
        residuals = y_test - result['predictions']
        pd.plotting.autocorrelation_plot(residuals, ax=axes[3], label=name)
    
    axes[3].set_title('残差自相关图')
    axes[3].legend()
    axes[3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_learning_curves(X, y, models, cv=5):
    """绘制学习曲线"""
    print("\n正在绘制学习曲线...")
    
    n_models = len(models)
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.ravel()
    
    for idx, (name, model) in enumerate(models.items()):
        if idx >= 4:  # 只显示前4个模型
            break
            
        try:
            # 计算学习曲线
            train_sizes, train_scores, test_scores = learning_curve(
                model, X, y, cv=cv, scoring='r2',
                train_sizes=np.linspace(0.1, 1.0, 10), random_state=42
            )
            
            # 计算均值和标准差
            train_mean = np.mean(train_scores, axis=1)
            train_std = np.std(train_scores, axis=1)
            test_mean = np.mean(test_scores, axis=1)
            test_std = np.std(test_scores, axis=1)
            
            # 绘制学习曲线
            axes[idx].plot(train_sizes, train_mean, 'o-', color='blue', 
                          label='训练得分', linewidth=2)
            axes[idx].fill_between(train_sizes, train_mean - train_std, 
                                 train_mean + train_std, alpha=0.1, color='blue')
            
            axes[idx].plot(train_sizes, test_mean, 'o-', color='red', 
                          label='交叉验证得分', linewidth=2)
            axes[idx].fill_between(train_sizes, test_mean - test_std, 
                                 test_mean + test_std, alpha=0.1, color='red')
            
            axes[idx].set_xlabel('训练样本数')
            axes[idx].set_ylabel('R²得分')
            axes[idx].set_title(f'{name} - 学习曲线')
            axes[idx].legend()
            axes[idx].grid(True, alpha=0.3)
            
        except Exception as e:
            print(f"绘制 {name} 学习曲线时出错: {e}")
            continue
    
    plt.tight_layout()
    plt.show()

def plot_feature_importance_analysis(results, feature_names):
    """绘制特征重要性分析"""
    print("\n正在绘制特征重要性分析...")
    
    importance_plots = []
    
    for name, result in results.items():
        model = result['model']
        
        if name == "Random Forest" or name == "Decision Tree":
            # 树模型的特征重要性
            if hasattr(model, 'feature_importances_'):
                importance_plots.append((name, model.feature_importances_))
                
        elif name == "Lasso":
            # Lasso 系数绝对值作为重要性
            importance_plots.append((name, np.abs(model.coef_)))
            
        elif name == "Ridge":
            # Ridge 系数绝对值作为重要性
            if isinstance(model, dict) and 'weights' in model:
                importance_plots.append((name, np.abs(model['weights'])))
            elif hasattr(model, 'coef_'):
                importance_plots.append((name, np.abs(model.coef_)))
    
    if importance_plots:
        n_plots = len(importance_plots)
        fig, axes = plt.subplots(1, n_plots, figsize=(5*n_plots, 6))
        
        if n_plots == 1:
            axes = [axes]
        
        for idx, (name, importances) in enumerate(importance_plots):
            # 按重要性排序
            indices = np.argsort(importances)[::-1]
            sorted_importances = importances[indices]
            sorted_features = [feature_names[i] for i in indices]
            
            axes[idx].barh(range(len(sorted_importances)), sorted_importances, 
                          color=plt.cm.viridis(np.linspace(0, 1, len(sorted_importances))))
            axes[idx].set_yticks(range(len(sorted_importances)))
            axes[idx].set_yticklabels(sorted_features)
            axes[idx].set_xlabel('特征重要性')
            axes[idx].set_title(f'{name} - 特征重要性')
            axes[idx].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.show()

def plot_prediction_intervals(results, X_test, y_test, alpha=0.95):
    """绘制预测区间（使用自助法）"""
    print("\n正在绘制预测区间...")
    
    n_models = min(len(results), 4)  # 最多显示4个模型
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.ravel()
    
    for idx, (name, result) in enumerate(list(results.items())[:n_models]):
        predictions = result['predictions']
        residuals = y_test - predictions
        
        # 使用自助法计算预测区间
        n_bootstrap = 1000
        bootstrap_predictions = []
        
        for _ in range(n_bootstrap):
            # 重采样残差
            bootstrap_residuals = np.random.choice(residuals, size=len(residuals), replace=True)
            bootstrap_pred = predictions + bootstrap_residuals
            bootstrap_predictions.append(bootstrap_pred)
        
        bootstrap_predictions = np.array(bootstrap_predictions)
        
        # 计算分位数
        lower_bound = np.percentile(bootstrap_predictions, (1-alpha)*100/2, axis=0)
        upper_bound = np.percentile(bootstrap_predictions, 100 - (1-alpha)*100/2, axis=0)
        
        # 排序以便绘图
        sort_idx = np.argsort(predictions)
        sorted_pred = predictions[sort_idx]
        sorted_lower = lower_bound[sort_idx]
        sorted_upper = upper_bound[sort_idx]
        sorted_true = y_test.values[sort_idx] if hasattr(y_test, 'values') else y_test[sort_idx]
        
        # 绘制预测区间
        axes[idx].fill_between(range(len(sorted_pred)), sorted_lower, sorted_upper, 
                              alpha=0.3, color='lightblue', label=f'{int(alpha*100)}% 预测区间')
        axes[idx].plot(sorted_pred, 'r-', linewidth=2, label='预测值')
        axes[idx].plot(sorted_true, 'bo', alpha=0.6, markersize=3, label='真实值')
        
        axes[idx].set_xlabel('样本索引（排序后）')
        axes[idx].set_ylabel('目标值')
        axes[idx].set_title(f'{name} - 预测区间')
        axes[idx].legend()
        axes[idx].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_model_metrics_comparison(results):
    """绘制综合模型指标对比"""
    print("\n正在绘制综合模型指标对比...")
    
    metrics_list = ['r2', 'rmse', 'mae', 'mape']
    metric_names = ['R²得分', 'RMSE', 'MAE', 'MAPE (%)']
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.ravel()
    
    model_names = list(results.keys())
    colors = plt.cm.Set3(np.linspace(0, 1, len(model_names)))
    
    for idx, (metric, metric_name) in enumerate(zip(metrics_list, metric_names)):
        metric_values = []
        
        for name in model_names:
            if metric in results[name]:
                metric_values.append(results[name][metric])
            else:
                # 如果没有该指标，计算它
                y_true = results[name].get('y_true')
                y_pred = results[name].get('predictions')
                if y_true is not None and y_pred is not None:
                    additional_metrics = calculate_additional_metrics(y_true, y_pred)
                    metric_values.append(additional_metrics[metric])
                    results[name][metric] = additional_metrics[metric]
                else:
                    metric_values.append(np.nan)
        
        bars = axes[idx].bar(model_names, metric_values, color=colors)
        axes[idx].set_title(f'模型{metric_name}对比')
        axes[idx].set_ylabel(metric_name)
        axes[idx].tick_params(axis='x', rotation=45)
        axes[idx].grid(True, alpha=0.3, axis='y')
        
        # 在柱子上添加数值
        for bar, value in zip(bars, metric_values):
            height = bar.get_height()
            axes[idx].text(bar.get_x() + bar.get_width()/2., height,
                          f'{value:.4f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.show()

def plot_cross_validation_results(X, y, models, cv=5):
    """绘制交叉验证结果"""
    print("\n正在绘制交叉验证结果...")
    
    cv_results = {}
    
    for name, model in models.items():
        try:
            # 计算交叉验证得分
            cv_scores = cross_val_score(model, X, y, cv=cv, scoring='r2')
            cv_results[name] = cv_scores
        except Exception as e:
            print(f"计算 {name} 交叉验证时出错: {e}")
            continue
    
    if cv_results:
        plt.figure(figsize=(12, 6))
        
        # 箱线图显示交叉验证结果
        data_to_plot = [scores for scores in cv_results.values()]
        box_plot = plt.boxplot(data_to_plot, labels=cv_results.keys(), 
                              patch_artist=True)
        
        # 设置颜色
        colors = plt.cm.Set3(np.linspace(0, 1, len(cv_results)))
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
        
        plt.title('交叉验证R²得分分布 (5折)')
        plt.ylabel('R²得分')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, axis='y')
        
        # 添加均值点
        means = [np.mean(scores) for scores in cv_results.values()]
        for i, mean in enumerate(means):
            plt.plot(i+1, mean, 'ro', markersize=8, markeredgecolor='black')
        
        plt.tight_layout()
        plt.show()
        
        # 打印交叉验证统计
        print("\n交叉验证结果统计:")
        for name, scores in cv_results.items():
            print(f"{name:25} | 均值: {np.mean(scores):.4f} | 标准差: {np.std(scores):.4f}")

def compare_regression_models(X, y, test_size=0.2, random_state=42):
    """
    增强版的回归模型比较，包含更多验证指标和可视化
    """
    # 数据标准化
    scaler_X = StandardScaler()
    X_scaled = scaler_X.fit_transform(X)
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=test_size, random_state=random_state
    )
    
    # 定义所有模型
    models = {
        "OLS": "ols",
        "Ridge": "ridge",
        "Lasso": Lasso(alpha=0.1, random_state=random_state),
        "Gradient Descent": GradientDescentRegression(learning_rate=0.01, max_iter=2000),
        "Support Vector Regression": SVR(kernel='rbf', C=1.0),
        "Decision Tree": DecisionTreeRegressor(max_depth=5, random_state=random_state),
        "Random Forest": RandomForestRegressor(n_estimators=50, max_depth=5, random_state=random_state),
        "K-Nearest Neighbors": KNeighborsRegressor(n_neighbors=5)
    }
    
    results = {}
    
    print("=" * 60)
    print("增强版回归模型性能对比")
    print("=" * 60)
    
    for name, model in models.items():
        try:
            if name == "OLS":
                beta, y_pred_train, r2_train = OLS(X_train, y_train)
                X_test_with_bias = np.hstack((np.ones((X_test.shape[0], 1)), X_test))
                y_pred = X_test_with_bias.dot(beta)
                trained_model = beta
                
            elif name == "Ridge":
                alpha = 0.1
                weights, y_pred_train, r2_train = Ridge(X_train, y_train, alpha)
                X_train_mean = np.mean(X_train, axis=0)
                y_train_mean = np.mean(y_train)
                intercept = y_train_mean - np.dot(X_train_mean, weights)
                y_pred = np.dot(X_test, weights) + intercept
                trained_model = {'weights': weights, 'intercept': intercept}
                
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                trained_model = model
            
            # 计算所有评估指标
            metrics = calculate_additional_metrics(y_test, y_pred)
            
            results[name] = {
                'model': trained_model,
                'predictions': y_pred,
                'y_true': y_test,
                'scaler': scaler_X,
                **metrics  # 解包所有指标
            }
            
            # 打印详细指标
            print(f"{name:25} | R²: {metrics['r2']:.4f} | RMSE: {metrics['rmse']:.4f} | "
                  f"MAE: {metrics['mae']:.4f} | MAPE: {metrics['mape']:.2f}%")
            
        except Exception as e:
            print(f"{name:25} | 训练失败: {str(e)}")
            continue
    
    # 执行所有增强的可视化
    plot_residual_analysis(results, X_test, y_test)
    
    # 学习曲线（使用可用的模型）
    available_models = {name: results[name]['model'] for name in results 
                       if not isinstance(results[name]['model'], (str, dict, np.ndarray))}
    if available_models:
        plot_learning_curves(X_scaled, y, available_models)
    
    plot_feature_importance_analysis(results, X.columns.tolist())
    plot_prediction_intervals(results, X_test, y_test)
    plot_model_metrics_comparison(results)
    
    # 交叉验证
    plot_cross_validation_results(X_scaled, y, available_models)
    
    return results, X_test, y_test

def OLS(X, y):
    """普通最小二乘回归"""
    X = np.hstack((np.ones((X.shape[0], 1)), X))
    beta = np.linalg.pinv(X.T.dot(X)).dot(X.T).dot(y)
    y_pred = X.dot(beta)
    r_squared = 1 - (np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2))
    return beta, y_pred, r_squared

def Ridge(X, y, alpha):
    """岭回归"""
    n_samples, n_features = X.shape
    X_bias = np.hstack([np.ones((n_samples, 1)), X])
    
    I = np.eye(n_features + 1)
    I[0, 0] = 0
    
    X_T = X_bias.T
    X_T_X = np.dot(X_T, X_bias)
    X_T_X_reg = X_T_X + alpha * I
    X_T_y = np.dot(X_T, y)
    
    weights = np.dot(np.linalg.inv(X_T_X_reg), X_T_y)
    bias = weights[0]
    weights = weights[1:]
    
    y_pred = np.dot(X, weights) + bias
    r_squared = 1 - (np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2))
    
    return weights, y_pred, r_squared

def get_best_model(results):
    """获取最佳模型"""
    best_model_name = max(results.keys(), key=lambda x: results[x]['r2'])
    best_result = results[best_model_name]
    
    print(f"\n最佳模型: {best_model_name}")
    print(f"R² Score: {best_result['r2']:.4f}")
    print(f"RMSE: {best_result['rmse']:.4f}")
    
    return best_model_name, best_result

class SoftmaxRegression:
    def __init__(self, lr=0.1, max_iter=1000, tol=1e-6, reg=0.0):
        """
        Softmax 回归模型
        参数:
            lr: 学习率
            max_iter: 最大迭代次数
            tol: 收敛阈值
            reg: L2 正则化系数（防止过拟合）
        """
        self.lr = lr
        self.max_iter = max_iter
        self.tol = tol
        self.reg = reg
        self.W = None  # 权重矩阵 (n_features, n_classes)
        self.b = None  # 偏置向量 (n_classes,)

    def _softmax(self, z):
        """计算 softmax 概率"""
        z = z - np.max(z, axis=1, keepdims=True)  # 数值稳定性
        exp_z = np.exp(z)
        return exp_z / np.sum(exp_z, axis=1, keepdims=True)

    def _one_hot(self, y, n_classes):
        """将标签转为 one-hot 编码"""
        m = y.shape[0]
        one_hot = np.zeros((m, n_classes))
        one_hot[np.arange(m), y] = 1
        return one_hot

    def fit(self, X, y):
        """
        训练 softmax 回归模型
        参数:
            X: 输入数据 (n_samples, n_features)
            y: 标签 (n_samples,) 取值范围 [0, n_classes-1]
        """
        n_samples, n_features = X.shape
        n_classes = np.max(y) + 1

        # 初始化参数
        self.W = np.zeros((n_features, n_classes))
        self.b = np.zeros(n_classes)

        y_one_hot = self._one_hot(y, n_classes)

        for i in range(self.max_iter):
            # 线性部分
            logits = X @ self.W + self.b
            # 预测概率
            probs = self._softmax(logits)
            # 计算梯度
            grad_W = (X.T @ (probs - y_one_hot)) / n_samples + self.reg * self.W
            grad_b = np.mean(probs - y_one_hot, axis=0)
            # 参数更新
            W_old = self.W.copy()
            self.W -= self.lr * grad_W
            self.b -= self.lr * grad_b

            # 收敛判断
            if np.linalg.norm(self.W - W_old) < self.tol:
                print(f"Converged after {i+1} iterations.")
                break

    def predict_proba(self, X):
        """返回属于各类别的概率"""
        logits = X @ self.W + self.b
        return self._softmax(logits)

    def predict(self, X):
        """返回预测类别"""
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)
    
def plot_comparison_results(results, X_test, y_test, X_columns):
    """
    绘制模型比较结果的可视化图表
    
    参数:
        results: 模型结果字典
        X_test: 测试集特征
        y_test: 测试集真实值
        X_columns: 特征列名
    """
    plt.figure(figsize=(15, 10))
    
    # 1. 损失曲线（仅对梯度下降）
    plt.subplot(2, 3, 1)
    if "Gradient Descent" in results and hasattr(results["Gradient Descent"]['model'], 'loss_history'):
        plt.plot(results["Gradient Descent"]['model'].loss_history)
        plt.title('Gradient Descent Loss Curve')
        plt.xlabel('Iteration')
        plt.ylabel('MSE Loss')
        plt.grid(True)
    
    # 2. 预测 vs 真实值对比
    plt.subplot(2, 3, 2)
    for name, result in results.items():
        plt.scatter(y_test, result['predictions'], alpha=0.6, label=name)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2)
    plt.xlabel('True Values')
    plt.ylabel('Predictions')
    plt.title('Predictions vs True Values')
    plt.legend()
    
    # 3. 模型性能对比（R²）
    plt.subplot(2, 3, 3)
    model_names = list(results.keys())
    r2_scores = [results[name]['r2'] for name in model_names]
    plt.bar(model_names, r2_scores, color='skyblue')
    plt.title('Model Comparison (R方 Score)')
    plt.xticks(rotation=45)
    plt.ylabel('R方 Score')
    plt.grid(True, axis='y')
    
    # 4. 模型性能对比（RMSE）
    plt.subplot(2, 3, 4)
    rmse_scores = [results[name]['rmse'] for name in model_names]
    plt.bar(model_names, rmse_scores, color='lightcoral')
    plt.title('Model Comparison (RMSE)')
    plt.xticks(rotation=45)
    plt.ylabel('RMSE')
    plt.grid(True, axis='y')
    
    # 5. 残差图
    plt.subplot(2, 3, 5)
    for name, result in results.items():
        residuals = y_test - result['predictions']
        plt.scatter(result['predictions'], residuals, alpha=0.6, label=name)
    plt.axhline(y=0, color='black', linestyle='--')
    plt.xlabel('Predictions')
    plt.ylabel('Residuals')
    plt.title('Residual Plot')
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
    # 特征重要性分析（对于随机森林）
    if "Random Forest" in results:
        plt.figure(figsize=(10, 6))
        feature_importance = results["Random Forest"]['model'].feature_importances_
        features = X_columns
        indices = np.argsort(feature_importance)[::-1]
        
        plt.bar(range(len(features)), feature_importance[indices], color='lightgreen')
        plt.xticks(range(len(features)), [features[i] for i in indices], rotation=45)
        plt.title('Random Forest Feature Importance')
        plt.ylabel('Importance Score')
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    # example data
    X = np.zeros((2500,2))
    y = np.zeros(2500)
    for i in range(50):
        for j in range(50):
            X[i*50+j,0] = i
            X[i*50+j,1] = j
            y[i*50+j] = i + j + 10 + np.random.normal(0, 0.1)

    # OLS regression
    beta, y_pred, r_squared = OLS(X, y)
    print("OLS")
    print(f"beta: {beta}")
    print(f"R-squared: {r_squared}")

    # Ridge regression
    alpha = 0.1
    beta, y_pred, r_squared = Ridge(X, y, alpha)
    print("Ridge")
    print(f"beta: {beta}")
    print(f"R-squared: {r_squared}")

    # Lasso regression
    lasso = Lasso(alpha=0.1)
    lasso.fit(X, y)
    print("Lasso")
    print(f"beta: {lasso.coef_}")
    print(f"R-squared: {lasso.score(X, y)}")

