一、框架选择
Tensorflow
二、模型
（1）tf2.py（也就是基线）
TensorFlow 1.x (import tensorflow as tf)
TensorFlow MNIST 数据集工具 (tensorflow.examples.tutorials.mnist)

模型架构
-全连接神经网络 (Feedforward Neural Network)
输入层: 784 维 (28×28 图像展平)
隐藏层: 500 个神经元，使用 ReLU 激活函数
Dropout 层：保留率 0.9
输出层: 10 个神经元 (10 个数字类别)

环境搭建
conda create -n tf1 python=3.7
conda activate tf1
conda install -c conda-forge tensorflow-estimator==1.15.1

Data Prepare (数据准备)
python
# filepath: [mnist.py](http://_vscodecontentref_/1)
data_dir = './MNIST_DATA'   # 样本数据存储的路径
# 获取数据集，并采用one_hot热编码
mnist = input_data.read_data_sets(data_dir, one_hot=True)

Data Preprocess (数据预处理)
python
# 数据已在 input_data 中自动预处理:
# - 图像归一化到 [0, 1]
# - 标签转换为 one-hot 编码
# 输入占位符
x = tf.placeholder(tf.float32, [None, 784], name='x-input')
y_ = tf.placeholder(tf.float32, [None, 10], name='y-input')
# 用于可视化的图像重塑
image_shaped_input = tf.reshape(x, [-1, 28, 28, 1])
Model Construct (模型构建)
python
运行
# 第一层: 784 → 500 (ReLU)
hidden1 = nn_layer(x, 784, 500, 'layer1')
# Dropout 层 (防止过拟合)
keep_prob = tf.placeholder(tf.float32)
dropped = tf.nn.dropout(hidden1, keep_prob)
# 第二层: 500 → 10 (无激活函数,用于 softmax)
y = nn_layer(dropped, 500, 10, 'layer2', act=tf.identity)

Train & Test (训练与测试)
python
# 损失函数: 交叉熵
diff = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y)
cross_entropy = tf.reduce_mean(diff)
# 优化器: Adam
train_step = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy)
# 训练配置
max_steps = 1000          # 训练步数
learning_rate = 0.001     # 学习率
dropout = 0.9             # Dropout 保留率

Plot Result (结果展示)
python
log_dir = './MNIST_LOG'    # 输出日志保存的路径
# TensorBoard 可视化
tf.summary.scalar('loss', cross_entropy)
tf.summary.scalar('accuracy', accuracy)
tf.summary.histogram('weights', weights)
tf.summary.image('input', image_shaped_input, 10)
# 合并所有摘要
merged = tf.summary.merge_all()
train_writer = tf.summary.FileWriter(log_dir + '/train', sess.graph)
test_writer = tf.summary.FileWriter(log_dir + '/test')
可视化内容:
训练 / 测试损失曲线
训练 / 测试准确率曲线
权重和偏置的分布直方图
输入图像样本
计算图结构
查看方式
tensorboard --logdir=./MNIST_LOG

结果
Accuracy at step 850:0.9654
Accuracy at step 860:0.9646
Accuracy at step 870:0.9651
Accuracy at step 880:0.9666
Accuracy at step 890:0.9651
Accuracy at step 900:0.9641
Accuracy at step 910:0.9648
Accuracy at step 920:0.9653
Accuracy at step 930:0.9655
Accuracy at step 940:0.9667
Accuracy at step 950:0.9646
Accuracy at step 960:0.9678
Accuracy at step 970:0.9682
Accuracy at step 980:0.9679
Accuracy at step 990:0.9677

项目	内容
框架	TensorFlow 1.x
模型	2层全连接神经网络 (500 隐藏层)
数据集	MNIST 手写数字 (60k 训练 + 10k 测试)
优化器	Adam
正则化	Dropout (0.9)
可视化	TensorBoard
训练方式 Mini-batch (batch_size=100)

（2）tf2_cnn.py
模型架构
-卷积神经网络 (Convolutional Neural Network - CNN)
LeNet 风格架构
输入: 28×28 灰度图像
2 层卷积 + 池化
全连接层
Softmax 输出

环境搭建
同基线

Data Prepare (数据准备)
同基线

Data Preprocess (数据预处理)
python
# 输入占位符
x = tf.placeholder(tf.float32, [None, 784], name='x-input')
y_ = tf.placeholder(tf.float32, [None, 10], name='y-input')
# 将输入 reshape 为图像格式
with tf.name_scope('input_reshape'):
    x_image = tf.reshape(x, [-1, 28, 28, 1])
    tf.summary.image('input', x_image, 10)
Model Construct (模型构建)

第一层卷积
python
# 卷积: 28x28x1 -> 28x28x32
W_conv1 = weight_variable([5, 5, 1, 32])  # 5×5 卷积核, 32 个
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
# 池化: 28x28x32 -> 14x14x32
h_pool1 = max_pool_2x2(h_conv1)  # 2×2 最大池化

第二层卷积
python
# 卷积: 14x14x32 -> 14x14x64
W_conv2 = weight_variable([5, 5, 32, 64])  # 5×5 卷积核, 64 个
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
# 池化: 14x14x64 -> 7x7x64
h_pool2 = max_pool_2x2(h_conv2)

全连接层
python
# 展平: 7x7x64 -> 3136
h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
# 全连接: 3136 -> 1024
W_fc1 = weight_variable([7 * 7 * 64, 1024])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

Dropout 层
python
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)  # keep_prob = 0.9

输出层
python
# 全连接: 1024 -> 10
W_fc2 = weight_variable([1024, 10])
y = tf.matmul(h_fc1_drop, W_fc2) + b_fc2  # 无激活函数,用于 softmax

Train & Test (训练与测试)
python
# 损失函数: Softmax 交叉熵
diff = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y)
cross_entropy = tf.reduce_mean(diff)
# 优化器: Adam
train_step = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy)
# 训练参数
max_steps = 1000          # 训练步数
learning_rate = 0.001     # 学习率
dropout = 0.9             # Dropout 保留率

Plot Result (结果展示)
python
log_dir = './MNIST_LOG_CNN'
# TensorBoard 可视化
tf.summary.scalar('loss', cross_entropy)
tf.summary.scalar('accuracy', accuracy)
tf.summary.scalar('dropout_keep_probability', keep_prob)
tf.summary.histogram('activations', h_conv1)  # 卷积层激活值
tf.summary.histogram('outputs', y)            # 输出层
tf.summary.image('input', x_image, 10)        # 输入图像
# 写入日志
train_writer = tf.summary.FileWriter(log_dir + '/train', sess.graph)
test_writer = tf.summary.FileWriter(log_dir + '/test')

可视化内容:
标量 (Scalar):
训练 / 测试损失
训练 / 测试准确率
Dropout 保留率
直方图 (Histogram):
卷积层激活值分布
权重和偏置分布
输出层分布
图像 (Image):
输入图像样本 (10 张)
计算图 (Graph):
完整的 CNN 网络结构

查看方式
tensorboard --logdir=./MNIST_LOG_CNN --port=6006

结果
CNN 模型 - Accuracy at step 800:0.9856
CNN 模型 - Accuracy at step 810:0.9843
CNN 模型 - Accuracy at step 820:0.9848
CNN 模型 - Accuracy at step 830:0.9807
CNN 模型 - Accuracy at step 840:0.9807
CNN 模型 - Accuracy at step 850:0.9832
CNN 模型 - Accuracy at step 860:0.9828
CNN 模型 - Accuracy at step 870:0.9849
CNN 模型 - Accuracy at step 880:0.9837
CNN 模型 - Accuracy at step 890:0.986
CNN 模型 - Accuracy at step 900:0.9861
CNN 模型 - Accuracy at step 910:0.9845
CNN 模型 - Accuracy at step 920:0.9859
CNN 模型 - Accuracy at step 930:0.9865
CNN 模型 - Accuracy at step 940:0.9844
CNN 模型 - Accuracy at step 950:0.987
CNN 模型 - Accuracy at step 960:0.9833
CNN 模型 - Accuracy at step 970:0.9839
CNN 模型 - Accuracy at step 980:0.9844
CNN 模型 - Accuracy at step 990:0.986
CNN 模型训练完成！

（3）logistic_regression.py
模型架构
scikit-learn (from sklearn.linear_model import LogisticRegression)
TensorFlow MNIST 数据集工具 (tensorflow.examples.tutorials.mnist)
NumPy - 数值计算
Pickle - 模型保存

模型类型
逻辑回归 (Logistic Regression)
实际是 Softmax 回归 (多分类逻辑回归)
线性分类器
基于最大似然估计

环境搭建
同基线

Data Prepare (数据准备)
同基线

Data Preprocess (数据预处理)
无需手动预处理：MNIST 数据已经归一化到 [0, 1]，图像已展平为 784 维向量特征工程：无特征提取：直接使用原始像素值，每个像素是一个特征 (784 个特征)标准化：逻辑回归对特征尺度不太敏感，MNIST 像素值已归一化，无需额外处理

Model Construct (模型构建)
python
model = LogisticRegression(
    max_iter=100,                  # 最大迭代次数
    solver='lbfgs',                # 优化算法
    multi_class='multinomial',     # 多分类策略 (Softmax)
    verbose=1,                     # 显示训练过程
    n_jobs=-1                      # 使用所有CPU核心并行
)

Train & Test (训练与测试)
python
# 训练
start_time = time.time()
model.fit(X_train, y_train)
train_time = time.time() - start_time
# 预测
y_pred = model.predict(X_test)
# 计算准确率
accuracy = accuracy_score(y_test, y_pred)

Plot Result (结果展示)
测试集准确率: 0.9260 (92.60%)
分类报告:
    precision    recall  f1-score   support

0     0.9513    0.9776    0.9643     980
1     0.9611    0.9789    0.9699    1135
2     0.9302    0.9041    0.9170    1032
3     0.9025    0.9069    0.9047    1010
4     0.9394    0.9318    0.9356     982
5     0.9045    0.8711    0.8875     892
6     0.9355    0.9530    0.9442     958
7     0.9387    0.9241    0.9314    1028
8     0.8802    0.8830    0.8816     974
9     0.9079    0.9187    0.9133    1009
accuracy                  0.9260    10000
macro 
  avg 0.9251    0.9249    0.9249    10000
weighted
  avg 0.9259    0.9260    0.9258    10000
混淆矩阵:
plaintext
[[ 958    0    0    3    1    8    5    4    1    0]
 [   0 1111    5    1    0    2    3    2   11    0]
 [   5    7  933   13    8    3   15    8   36    4]
 [   4    1   21  916    1   23    4   11   21    8]
 [   1    2    6    3  915    0   11    3    8   33]
 [  10    3    3   38    7  777   13    6   29    6]
 [   8    3    6    3    6   16  913    2    1    0]
 [   1    9   22    5    6    1    0  950    3   31]
 [   9   12    7   24    7   24   12    7  860   12]
 [  11    8    0    9   23    5    0   19    7  927]]

（4）svm.py
模型架构
核心库
scikit-learn (from sklearn.svm import SVC)
TensorFlow MNIST 数据集工具 (tensorflow.examples.tutorials.mnist)
NumPy - 数值计算
Pickle - 模型保存

模型类型
支持向量机 (Support Vector Machine - SVM)
使用 SVC (Support Vector Classification)
基于核函数的非线性分类器
径向基核函数 (RBF Kernel)

环境搭建
同基线

Data Prepare (数据准备)
同基线

Data Preprocess (数据预处理)
1.无额外预处理:
MNIST 数据已归一化到 [0, 1]
图像已展平为 784 维向量
2.SVM 对特征尺度敏感:
幸运的是，MNIST 像素值范围统一
通常需要标准化: StandardScaler ()
但这里可以省略
3.特征工程:
直接使用原始像素值作为特征
SVM 通过核函数自动进行非线性变换

Model Construct (模型构建)
python
model = SVC(
    kernel='rbf',      # 径向基核函数
    C=5.0,             # 正则化参数
    gamma='scale',     # 核函数系数
    verbose=True       # 显示训练过程
)

Train & Test (训练与测试)
python
# 训练
start_time = time.time()
model.fit(X_train, y_train)
train_time = time.time() - start_time
# 预测
y_pred = model.predict(X_test)
# 计算准确率
accuracy = accuracy_score(y_test, y_pred)

Plot Result (结果展示)
测试集准确率: 0.9690 (96.90%)
分类报告:
              precision    recall  f1-score   support

           9     0.9647    0.9485    0.9565    1009
    accuracy                         0.9690    10000
   macro avg     0.9690    0.9686    0.9688    10000
weighted avg     0.9690    0.9690    0.9690    10000

（5）random_forest.py
模型架构
核心库
scikit-learn (from sklearn.ensemble import RandomForestClassifier)
TensorFlow MNIST 数据集工具 (tensorflow.examples.tutorials.mnist)
NumPy - 数值计算
Pickle - 模型保存

模型类型
随机森林 (Random Forest)
集成学习 (Ensemble Learning)
基于决策树的 Bagging 方法
多棵决策树投票决策

环境搭建
同基线

Data Prepare (数据准备)
同基线

Data Preprocess (数据预处理)
1.无额外预处理:
MNIST 数据已归一化到 [0, 1]
图像已展平为 784 维向量
2.决策树对特征尺度不敏感:
不需要标准化
基于阈值分裂，不依赖距离度量
3.特征工程:
直接使用原始像素值
随机森林自动进行特征选择

Model Construct (模型构建)
python
model = RandomForestClassifier(
    n_estimators=100,      # 树的数量
    max_depth=20,          # 树的最大深度
    min_samples_split=5,   # 分裂所需最小样本数
    min_samples_leaf=2,    # 叶子节点最小样本数
    n_jobs=-1,             # 并行训练
    verbose=2,             # 显示进度
    random_state=42        # 随机种子
)

Train & Test (训练与测试)
python
# 训练
start_time = time.time()
model.fit(X_train, y_train)
train_time = time.time() - start_time
# 预测
y_pred = model.predict(X_test)
# 计算准确率
accuracy = accuracy_score(y_test, y_pred)

Plot Result (结果展示)
测试集准确率: 0.9660 (96.60%)
分类报告:
              precision    recall  f1-score   support

           0     0.9699    0.9878    0.9788     980
           1     0.9885    0.9868    0.9877    1135
           2     0.9523    0.9671    0.9596    1032
           3     0.9536    0.9574    0.9555    1010
           4     0.9724    0.9674    0.9699     982
           5     0.9694    0.9596    0.9645     892
           6     0.9770    0.9760    0.9765     958
           7     0.9695    0.9601    0.9648    1028
           8     0.9556    0.9497    0.9526     974
           9     0.9502    0.9455    0.9478    1009
    accuracy                         0.9660    10000
2.像素 (15, 13), 重要性: 0.008757
3.像素 (14, 13), 重要性: 0.008368
4.像素 (13, 13), 重要性: 0.008093
5.像素 (12, 11), 重要性: 0.008021
6.像素 (5, 15), 重要性: 0.007963
7.像素 (19, 10), 重要性: 0.007847
8.像素 (16, 13), 重要性: 0.007586
9.像素 (12, 14), 重要性: 0.007424
10.像素 (20, 9), 重要性: 0.007316