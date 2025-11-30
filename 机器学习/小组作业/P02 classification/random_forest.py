import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from tensorflow.examples.tutorials.mnist import input_data
import pickle
import time

'''
随机森林模型: 集成学习方法
预期效果: 准确率约 96-97%
优点: 抗过拟合,特征重要性分析
缺点: 模型较大,推理速度慢
'''

print("="*80)
print("随机森林 (Random Forest) - MNIST 手写数字识别")
print("="*80)

# 加载数据
data_dir = './MNIST_DATA'
mnist = input_data.read_data_sets(data_dir, one_hot=False)

X_train = mnist.train.images
y_train = mnist.train.labels
X_test = mnist.test.images
y_test = mnist.test.labels

print(f"\n训练集大小: {X_train.shape}")
print(f"测试集大小: {X_test.shape}")

# 创建随机森林模型
print("\n开始训练随机森林模型...")
start_time = time.time()

model = RandomForestClassifier(
    n_estimators=100,      # 树的数量
    max_depth=20,          # 树的最大深度
    min_samples_split=5,   # 分裂所需最小样本数
    min_samples_leaf=2,    # 叶子节点最小样本数
    n_jobs=-1,             # 并行训练
    verbose=2,             # 显示进度
    random_state=42
)

model.fit(X_train, y_train)

train_time = time.time() - start_time
print(f"训练完成! 耗时: {train_time:.2f} 秒")

# 预测
print("\n在测试集上评估...")
y_pred = model.predict(X_test)

# 计算准确率
accuracy = accuracy_score(y_test, y_pred)
print(f"\n测试集准确率: {accuracy:.4f} ({accuracy*100:.2f}%)")

# 详细分类报告
print("\n分类报告:")
print(classification_report(y_test, y_pred, digits=4))

# 特征重要性分析 (前10个最重要的像素)
feature_importance = model.feature_importances_
top_10_features = np.argsort(feature_importance)[-10:][::-1]
print("\n前10个最重要的特征 (像素位置):")
for i, idx in enumerate(top_10_features):
    row = idx // 28
    col = idx % 28
    print(f"  {i+1}. 像素 ({row}, {col}), 重要性: {feature_importance[idx]:.6f}")

# 保存模型
model_path = './models/random_forest.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"\n模型已保存到: {model_path}")

print("\n" + "="*80)
print("随机森林模型训练完成!")
print("="*80)