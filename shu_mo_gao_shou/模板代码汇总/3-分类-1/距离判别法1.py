import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 加载鸢尾花数据集
iris = datasets.load_iris()
X = iris.data
y = iris.target

# 将数据集分为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# 定义距离判别法分类器
class DistanceClassifier:
    def fit(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train

    def predict(self, X_test):
        predictions = []
        for sample in X_test:
            distances = []
            for train_sample in self.X_train:
                distance = np.sqrt(np.sum((sample - train_sample) ** 2))
                distances.append(distance)

            closest_index = np.argmin(distances)
            predicted_label = self.y_train[closest_index]
            predictions.append(predicted_label)

        return predictions

    # 创建并训练分类器


classifier = DistanceClassifier()
classifier.fit(X_train, y_train)

# 使用分类器进行预测
y_pred = classifier.predict(X_test)

# 计算准确率
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# 可视化输出
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis')  # 绘制原始数据点
plt.scatter(X_test[:, 0], X_test[:, 1], c=y_pred, cmap='viridis', alpha=0.5)  # 绘制预测数据点及类别颜色
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('Distance Discriminant Analysis on Iris Dataset')
plt.show()