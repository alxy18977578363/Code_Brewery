import mindspore as ms
from mindspore import nn, ops
from mindspore.dataset import vision, transforms
from mindspore.dataset import MnistDataset

class LeNet5:
    def __init__(self, data_path='MNIST_Data', batch_size=64, learning_rate=1e-2, epochs=3):
        # 初始化参数
        self.data_path = data_path
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        
        # 初始化组件
        self._init_context()
        self._init_datasets()
        self._init_model()
        self._init_trainer()
    
    def _init_context(self):
        """设置MindSpore上下文"""
        ms.set_context(mode=ms.GRAPH_MODE, device_target="CPU")
    
    def datapipe(self, dataset):
        """数据预处理管道 (保持原始方法名)"""
        image_transforms = [
            vision.Resize(32),  # LeNet5需要32x32输入
            vision.Rescale(1.0 / 255.0, 0),
            vision.Normalize(mean=(0.1307,), std=(0.3081,)),
            vision.HWC2CHW()
        ]
        label_transform = transforms.TypeCast(ms.int32)
        
        dataset = dataset.map(image_transforms, 'image')
        dataset = dataset.map(label_transform, 'label')
        return dataset.batch(self.batch_size)
    
    def _init_datasets(self):
        """初始化数据集"""
        self.train_dataset = self.datapipe(MnistDataset(f'{self.data_path}/train'))
        self.test_dataset = self.datapipe(MnistDataset(f'{self.data_path}/test'))
    
    def _init_model(self):
        """初始化LeNet5模型"""
        self.model = nn.SequentialCell(
            # 特征提取
            nn.Conv2d(1, 6, kernel_size=5, pad_mode='valid'),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(6, 16, kernel_size=5, pad_mode='valid'),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # 分类
            nn.Flatten(),
            nn.Dense(16*5*5, 120),
            nn.ReLU(),
            nn.Dense(120, 84),
            nn.ReLU(),
            nn.Dense(84, 10)
        )
    
    def _init_trainer(self):
        """初始化训练组件"""
        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = nn.SGD(self.model.trainable_params(), self.learning_rate)
        self.grad_fn = ms.value_and_grad(self.forward_fn, None, self.optimizer.parameters, has_aux=True)
    
    def forward_fn(self, data, label):
        """前向计算 (保持原始方法名)"""
        logits = self.model(data)
        loss = self.loss_fn(logits, label)
        return loss, logits
    
    def train_step(self, data, label):
        """单步训练 (保持原始方法名)"""
        (loss, _), grads = self.grad_fn(data, label)
        self.optimizer(grads)
        return loss
    
    def save_model(self, path="model.ckpt"):
        """保存模型权重"""
        ms.save_checkpoint(self.model, path)
        print(f"Saved model to {path}")
    
    def load_model(self, path="model.ckpt"):
        """加载模型权重"""
        param_dict = ms.load_checkpoint(path)
        param_not_load, _ = ms.load_param_into_net(self.model, param_dict)
        if not param_not_load:
            print(f"Successfully loaded model from {path}")
        else:
            print(f"Failed to load parameters: {param_not_load}")
        return param_not_load
    
    def train(self):
        """训练模型 (保持原始方法名)"""
        size = self.train_dataset.get_dataset_size()
        
        for epoch in range(self.epochs):
            print(f"\nEpoch {epoch+1}/{self.epochs}")
            print("-" * 30)
            
            self.model.set_train()
            for batch, (data, label) in enumerate(self.train_dataset.create_tuple_iterator()):
                loss = self.train_step(data, label)
                
                if batch % 100 == 0:
                    print(f"loss: {loss.asnumpy():>7f}  [{batch:>3d}/{size:>3d}]")

        # 训练完成后自动保存模型
        self.save_model()
    
    def test(self):
        """测试模型 (保持原始方法名)"""
        num_batches = self.test_dataset.get_dataset_size()
        self.model.set_train(False)
        
        total = test_loss = correct = 0
        for data, label in self.test_dataset.create_tuple_iterator():
            pred = self.model(data)
            total += len(data)
            test_loss += self.loss_fn(pred, label).asnumpy()
            correct += (pred.argmax(1) == label).asnumpy().sum()
        
        test_loss /= num_batches
        correct /= total
        print(f"Test: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")
    
    def run(self):
        """运行完整流程"""
        print("Starting LeNet5 training on MNIST...")
        for t in range(self.epochs):
            print(f"Epoch {t+1}\n-------------------------------")
            self.train()
            self.test()
        print("Done!")

    def predict_sample(self, num_samples=10):
        """预测样本示例"""
        self.model.set_train(False)
        for data, label in self.test_dataset.create_tuple_iterator():
            pred = self.model(data)
            predicted = pred.argmax(1)
            print(f'Predicted: "{predicted[:num_samples].asnumpy()}", Actual: "{label[:num_samples].asnumpy()}"')
            break


if __name__ == "__main__":
    # 使用示例 (保持原始参数风格)
    lenet = LeNet5(
        data_path='MNIST_Data',
        batch_size=64,
        learning_rate=1e-2,
        epochs=3
    )
    lenet.run()

    # 单独测试模型加载和预测
    print("\nTesting model loading...")
    lenet2 = LeNet5()  # 新建一个模型实例
    lenet2.load_model()  # 加载之前保存的模型
    lenet2.test()  # 测试加载的模型
    lenet2.predict_sample()  # 进行预测


