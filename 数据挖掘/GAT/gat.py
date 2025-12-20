import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score, average_precision_score
import time

class FastGNNSubmission:
    """快速生成提交文件 - 使用预计算特征的MLP"""

    def __init__(self):
        print("=== 快速GNN提交生成器 ===")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name()}")
            print(f"显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
        torch.manual_seed(42)
        np.random.seed(42)
        print("=== 初始化完成 ===\n")

    def load_data(self):
        """加载数据"""
        print("=== 加载数据 ===")
        try:
            # 加载数据
            data = np.load('phase1_gdata.npz', allow_pickle=True)
            y = torch.LongTensor(data['y'].flatten())
            train_mask = torch.BoolTensor(data['train_mask'])
            test_indices = torch.LongTensor(data['test_mask'])  # 354578个测试节点索引
            features = torch.FloatTensor(np.load('gpu_features.npy'))

            print(f"数据: 节点{len(y)}, 特征{features.shape}")
            print(f"训练样本: {train_mask.sum()}")
            print(f"测试样本: {len(test_indices)}")

            # 获取有效标签节点
            valid_mask = (y >= 0) & (y <= 1)
            valid_indices = torch.where(valid_mask)[0]

            # 准备训练数据
            train_features = features[valid_indices[train_mask]]
            train_labels = y[valid_indices[train_mask]]

            # 准备测试数据
            test_features = features[test_indices]

            print(f"\n训练数据: {train_features.shape}")
            print(f"  正样本: {(train_labels==1).sum()}, 负样本: {(train_labels==0).sum()}")
            print(f"测试数据: {test_features.shape}")

            # 保存数据
            self.train_features = train_features.to(self.device)
            self.train_labels = train_labels.to(self.device)
            self.test_features = test_features.to(self.device)
            self.test_indices = test_indices

            return True

        except Exception as e:
            print(f"数据加载失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def train_model(self):
        """训练强大的MLP模型"""
        print("\n=== 训练模型 ===")
        try:
            # 创建强大的MLP模型
            class PowerfulMLP(nn.Module):
                def __init__(self, input_dim):
                    super().__init__()
                    self.layers = nn.Sequential(
                        # 第一层
                        nn.Linear(input_dim, 1024),
                        nn.ReLU(),
                        nn.BatchNorm1d(1024),
                        nn.Dropout(0.3),

                        # 第二层
                        nn.Linear(1024, 512),
                        nn.ReLU(),
                        nn.BatchNorm1d(512),
                        nn.Dropout(0.3),

                        # 第三层
                        nn.Linear(512, 256),
                        nn.ReLU(),
                        nn.BatchNorm1d(256),
                        nn.Dropout(0.3),

                        # 第四层
                        nn.Linear(256, 128),
                        nn.ReLU(),
                        nn.BatchNorm1d(128),
                        nn.Dropout(0.3),

                        # 第五层
                        nn.Linear(128, 64),
                        nn.ReLU(),
                        nn.Dropout(0.3),

                        # 输出层
                        nn.Linear(64, 2)
                    )

                def forward(self, x):
                    return self.layers(x)

            # 创建模型
            model = PowerfulMLP(self.train_features.shape[1]).to(self.device)
            print(f"模型参数: {sum(p.numel() for p in model.parameters()):,}")

            # 处理类别不平衡
            pos_count = (self.train_labels == 1).sum().float()
            neg_count = (self.train_labels == 0).sum().float()
            pos_weight = neg_count / pos_count
            print(f"正样本权重: {pos_weight:.2f}")

            # 优化器和损失函数
            optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, mode='max', factor=0.5, patience=10
            )

            # 使用加权损失
            class_weights = torch.tensor([1.0, pos_weight]).to(self.device)
            criterion = nn.CrossEntropyLoss(weight=class_weights)

            # 分割训练和验证集
            n_train = int(0.9 * len(self.train_features))
            train_idx = torch.randperm(len(self.train_features))[:n_train]
            val_idx = torch.randperm(len(self.train_features))[n_train:]

            train_X = self.train_features[train_idx]
            train_y = self.train_labels[train_idx]
            val_X = self.train_features[val_idx]
            val_y = self.train_labels[val_idx]

            print(f"训练集: {len(train_X)}, 验证集: {len(val_X)}")

            # 训练循环
            print("\n开始训练...")
            best_auc = 0
            best_ap = 0
            patience = 0

            start_time = time.time()
            for epoch in range(1500):
                # 训练
                model.train()
                optimizer.zero_grad()

                out = model(train_X)
                loss = criterion(out, train_y)

                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

                # 验证
                if epoch % 10 == 0:
                    model.eval()
                    with torch.no_grad():
                        val_out = model(val_X)
                        val_probs = torch.softmax(val_out, dim=1)[:, 1]

                        if len(torch.unique(val_y)) > 1:
                            val_auc = roc_auc_score(val_y.cpu(), val_probs.cpu())
                            val_ap = average_precision_score(val_y.cpu(), val_probs.cpu())
                        else:
                            val_auc = 0.5
                            val_ap = 0.0

                        print(f"Epoch {epoch:3d}: Loss={loss:.4f}, Val AUC={val_auc:.4f}, Val AP={val_ap:.4f}")

                        if val_auc > best_auc:
                            best_auc = val_auc
                            best_ap = val_ap
                            patience = 0
                            torch.save(model.state_dict(), 'best_fast_model.pt')
                            print(f"  * 最佳AUC: {best_auc:.4f}")
                        else:
                            patience += 1

                        scheduler.step(val_auc)

                        if patience >= 30:
                            print(f"早停于第{epoch}轮")
                            break

            print(f"\n训练完成! 用时: {time.time()-start_time:.2f}秒")
            print(f"最佳验证AUC: {best_auc:.4f}, AP: {best_ap:.4f}")

            # 加载最佳模型
            model.load_state_dict(torch.load('best_fast_model.pt'))

            return True, model, best_auc, best_ap

        except Exception as e:
            print(f"训练失败: {e}")
            import traceback
            traceback.print_exc()
            return False, None, 0, 0

    def generate_submission(self, model, best_auc, best_ap):
        """生成提交文件"""
        print("\n=== 生成提交文件 ===")
        try:
            model.eval()
            print("1. 检查格式...")
            demo = np.load('submit_demo.npy')
            print(f"   demo形状: {demo.shape}")

            print("2. 生成预测...")
            # 批量预测
            batch_size = 10000
            all_probs = []

            with torch.no_grad():
                for i in range(0, len(self.test_features), batch_size):
                    batch = self.test_features[i:i+batch_size]
                    out = model(batch)
                    probs = torch.softmax(out, dim=1)
                    all_probs.append(probs.cpu())

                    if i % 100000 == 0:
                        print(f"   处理进度: {i}/{len(self.test_features)}")

            final_probs = torch.cat(all_probs, dim=0).numpy()
            print(f"   预测形状: {final_probs.shape}")

            print("3. 保存提交文件...")
            # 确保格式正确
            if final_probs.shape != demo.shape:
                print(f"   错误: 形状不匹配!")
                return False

            # 确保概率和为1
            final_probs = final_probs / np.sum(final_probs, axis=1, keepdims=True)

            # 保存
            np.save('fast_gnn_submission.npy', final_probs)
            print(f"   成功: 提交文件已保存 - {final_probs.shape}")

            # 验证
            print("\n验证信息:")
            print(f"  形状: {final_probs.shape}")
            print(f"  概率范围: [{final_probs.min():.4f}, {final_probs.max():.4f}]")
            print(f"  格式匹配: {'是' if final_probs.shape == demo.shape else '否'}")
            print(f"  概率和正确: {'是' if np.allclose(np.sum(final_probs, axis=1), 1.0) else '否'}")

            # 性能报告
            print(f"\n性能报告:")
            print(f"  验证AUC: {best_auc:.4f}")
            print(f"  验证AP: {best_ap:.4f}")
            print(f"  相比simple_debug提升: {best_auc - 0.6213:.4f}")
            if best_auc >= 0.85:
                print(f"  ✓ 达到目标AUC > 0.85")
            else:
                print(f"  ✗ 未达到目标AUC (需要继续优化)")

            # 预测统计
            print(f"\n预测统计:")
            print(f"  正样本概率均值: {np.mean(final_probs[:, 1]):.4f}")
            print(f"  正样本概率标准差: {np.std(final_probs[:, 1]):.4f}")
            print(f"  预测为正样本比例: {np.mean(final_probs[:, 1] > 0.5):.4f}")

            return True

        except Exception as e:
            print(f"生成失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self):
        """运行完整流程"""
        start_time = time.time()
        print("开始快速GNN提交生成...\n")

        # 加载数据
        if not self.load_data():
            return False

        # 训练模型
        success, model, best_auc, best_ap = self.train_model()
        if not success:
            return False

        # 生成提交
        if not self.generate_submission(model, best_auc, best_ap):
            return False

        print(f"\n总用时: {time.time()-start_time:.2f}秒")
        print("\n快速GNN提交生成完成!")
        return True

if __name__ == "__main__":
    trainer = FastGNNSubmission()
    success = trainer.run()
    if not success:
        print("\n生成失败!")