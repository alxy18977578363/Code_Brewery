
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
        self.classes = np.unique(y_train)
        self.mean_centers = [X_train[y_train == class_].mean(axis=0) for class_ in self.classes]

    def predict(self, X_test):
        predictions = []
        for sample in X_test:
            distances = [np.sqrt(np.sum((sample - mean_center) ** 2)) for mean_center in self.mean_centers]
            closest_index = np.argmin(distances)
            predictions.append(self.classes[closest_index])
        return predictions

    # 创建并训练分类器


classifier = DistanceClassifier()
classifier.fit(X_train, y_train)

# 使用分类器进行预测
y_pred = classifier.predict(X_test)

# 计算准确率
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
