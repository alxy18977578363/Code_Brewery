import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import os

'''
CNN模型: 使用卷积层提取图像特征
预期效果: 准确率应该达到 99%+
模型结构: Conv1(32) -> Pool -> Conv2(64) -> Pool -> FC(1024) -> Output(10)
'''

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
config = tf.ConfigProto(allow_soft_placement = True)
gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction = 0.33)
config.gpu_options.allow_growth = True

max_steps = 1000
learning_rate = 0.001
dropout = 0.9
data_dir = './MNIST_DATA'
log_dir = './MNIST_LOG_CNN'

# 获取数据集
mnist = input_data.read_data_sets(data_dir, one_hot=True)

sess = tf.InteractiveSession(config=config)

# 输入层
with tf.name_scope('input'):
    x = tf.placeholder(tf.float32, [None, 784], name='x-input')
    y_ = tf.placeholder(tf.float32, [None, 10], name='y-input')

# 将输入reshape为图像格式
with tf.name_scope('input_reshape'):
    x_image = tf.reshape(x, [-1, 28, 28, 1])
    tf.summary.image('input', x_image, 10)

# 初始化权重
def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

# 初始化偏置
def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

# 参数统计
def variable_summaries(var):
    with tf.name_scope('summaries'):
        mean = tf.reduce_mean(var)
        tf.summary.scalar('mean', mean)
        with tf.name_scope('stddev'):
            stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
        tf.summary.scalar('stddev', stddev)
        tf.summary.scalar('max', tf.reduce_max(var))
        tf.summary.scalar('min', tf.reduce_min(var))
        tf.summary.histogram('histogram', var)

# 卷积操作
def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

# 池化操作
def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# 第一层卷积: 28x28x1 -> 28x28x32 -> 14x14x32
with tf.name_scope('conv1'):
    with tf.name_scope('weights'):
        W_conv1 = weight_variable([5, 5, 1, 32])
        variable_summaries(W_conv1)
    with tf.name_scope('biases'):
        b_conv1 = bias_variable([32])
        variable_summaries(b_conv1)
    with tf.name_scope('conv'):
        h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
        tf.summary.histogram('activations', h_conv1)
    with tf.name_scope('pool'):
        h_pool1 = max_pool_2x2(h_conv1)

# 第二层卷积: 14x14x32 -> 14x14x64 -> 7x7x64
with tf.name_scope('conv2'):
    with tf.name_scope('weights'):
        W_conv2 = weight_variable([5, 5, 32, 64])
        variable_summaries(W_conv2)
    with tf.name_scope('biases'):
        b_conv2 = bias_variable([64])
        variable_summaries(b_conv2)
    with tf.name_scope('conv'):
        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
        tf.summary.histogram('activations', h_conv2)
    with tf.name_scope('pool'):
        h_pool2 = max_pool_2x2(h_conv2)

# 全连接层1: 7x7x64 -> 1024
with tf.name_scope('fc1'):
    with tf.name_scope('weights'):
        W_fc1 = weight_variable([7 * 7 * 64, 1024])
        variable_summaries(W_fc1)
    with tf.name_scope('biases'):
        b_fc1 = bias_variable([1024])
        variable_summaries(b_fc1)
    with tf.name_scope('flat'):
        h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
    with tf.name_scope('activation'):
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
        tf.summary.histogram('activations', h_fc1)

# Dropout层
with tf.name_scope('dropout'):
    keep_prob = tf.placeholder(tf.float32)
    tf.summary.scalar('dropout_keep_probability', keep_prob)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

# 输出层: 1024 -> 10
with tf.name_scope('fc2'):
    with tf.name_scope('weights'):
        W_fc2 = weight_variable([1024, 10])
        variable_summaries(W_fc2)
    with tf.name_scope('biases'):
        b_fc2 = bias_variable([10])
        variable_summaries(b_fc2)
    with tf.name_scope('output'):
        y = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
        tf.summary.histogram('outputs', y)

# 损失函数
with tf.name_scope('loss'):
    diff = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y)
    with tf.name_scope('total'):
        cross_entropy = tf.reduce_mean(diff)
    tf.summary.scalar('loss', cross_entropy)

# 优化器
with tf.name_scope('train'):
    train_step = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy)

# 准确率
with tf.name_scope('accuracy'):
    with tf.name_scope('correct_prediction'):
        correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
    with tf.name_scope('accuracy'):
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

tf.summary.scalar('accuracy', accuracy)

# 合并所有summaries
merged = tf.summary.merge_all()
train_writer = tf.summary.FileWriter(log_dir + '/train', sess.graph)
test_writer = tf.summary.FileWriter(log_dir + '/test')

# 初始化变量
tf.global_variables_initializer().run()

def feed_dict(train):
    if train:
        xs, ys = mnist.train.next_batch(100)
        k = dropout
    else:
        xs, ys = mnist.test.images, mnist.test.labels
        k = 1.0
    return {x: xs, y_: ys, keep_prob: k}

# 训练
for i in range(max_steps):
    if i % 10 == 0:
        summary, acc = sess.run([merged, accuracy], feed_dict=feed_dict(False))
        test_writer.add_summary(summary, i)
        print('CNN模型 - Accuracy at step %s: %s' % (i, acc))
    else:
        summary, _ = sess.run([merged, train_step], feed_dict=feed_dict(True))
        train_writer.add_summary(summary, i)

train_writer.close()
test_writer.close()
print("CNN模型训练完成!")