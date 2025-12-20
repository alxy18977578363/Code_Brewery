import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from torch_geometric.data import Data
from torch_geometric.utils import degree
import numpy as np
from torch_geometric.loader import NeighborLoader
from sklearn.metrics import roc_auc_score
from torch_scatter import scatter_mean, scatter_add, scatter_max
import time
import os


NUM_EDGE_TYPES = 11
NUM_NODE_FEATURES = 17
SPLIT_RATIO = 0.8
DATA_PATH = os.path.join('data', 'phase1_gdata.npz')


def load_data():
    data = np.load(DATA_PATH)

    #==================================
    # 处理数据
    # 节点特征中-1改为0
    data['x'][data['x']==-1] = 0
    #==================================

    num_nodes = data['x'].shape[0]
    x = torch.FloatTensor(data['x'])  # 节点特征 [num_nodes, feature_dim]
    y = torch.LongTensor(data['y'])  # 标签 [num_nodes]

    # 翻转边方向
    # edge_index = torch.LongTensor(np.fliplr(data['edge_index']).T)  # 边的连接关系 [2, num_edges]
    edge_index = torch.LongTensor(data['edge_index'].T)  # 边的连接关系 [2, num_edges]
    # 整数边类(离散)
    edge_type = torch.LongTensor(data['edge_type'].flatten() - 1)  # 边的类型 [num_edges]

    num_available = data['train_mask'].shape[0]
    indeks = np.random.permutation(num_available)
    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    train_mask[data['train_mask'][indeks[:int(num_available*SPLIT_RATIO)]]] = True
    test_mask = torch.zeros(num_nodes, dtype=torch.bool)
    test_mask[data['train_mask'][indeks[int(num_available*SPLIT_RATIO):]]] = True

    valid_index = data['test_mask']

    data = Data(
        x=x,
        y=y,
        edge_index=edge_index,
        edge_type=edge_type,
        train_mask=train_mask,
        test_mask=test_mask
    )

    loader_train = NeighborLoader(
        data=data,
        input_nodes=train_mask,  # 以训练节点为起点采样
        batch_size=128, 
        num_neighbors=[5, 5, 5, 5, 5],  
        shuffle=True,  # 训练时打乱
        num_workers=4,  # 多线程加载
        # directed=False
    )

    loader_test = NeighborLoader(
        data=data,
        input_nodes=test_mask,  # 以测试节点为起点采样
        batch_size=128,  
        num_neighbors=[5, 5, 5, 5, 5],  
        shuffle=True,
        # directed=False
    )

    print(f"dataset loaded")
    print(f"num_nodes: {num_nodes}")
    print(f"num_edges: {edge_index.shape[1]}")
    print(f"num_train: {train_mask.sum().item()}")
    print(f"num_test: {test_mask.sum().item()}")

    # Return original data and masks for prediction
    return loader_train, loader_test, data, valid_index


class LearnableEdgeSAGEConv(nn.Module):
    def __init__(self, in_channels, out_channels, num_edge_types, edge_dim=32, hidden_dim=64):
        """
        num_edge_types: 整数，离散边类型数
        edge_dim: 边嵌入维度
        """
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.edge_dim = edge_dim
        
        # 离散边类型嵌入
        self.edge_emb = nn.Embedding(num_edge_types, edge_dim)
        
        # 自节点与邻居节点的线性变换
        self.lin_self = nn.Linear(in_channels, out_channels, bias=False)
        self.lin_neigh = nn.Linear(in_channels + edge_dim, out_channels, bias=False)
        
        # 注意力 / 可学习聚合模块
        self.att_mlp = nn.Sequential(
            nn.Linear(2 * in_channels + edge_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, 1)
        )
        
        # 偏置项
        self.bias = nn.Parameter(torch.zeros(out_channels))
        
        self.reset_parameters()
    
    def reset_parameters(self):
        nn.init.xavier_uniform_(self.lin_self.weight)
        nn.init.xavier_uniform_(self.lin_neigh.weight)
        nn.init.xavier_uniform_(self.edge_emb.weight)
        for m in self.att_mlp:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
        nn.init.zeros_(self.bias)
    
    def forward(self, x, edge_index, edge_type):
        """
        x: [num_nodes, in_channels]
        edge_index: [2, num_edges] (LongTensor) or tuple(t_src, t_dst)
        edge_type: [num_edges]  LongTensor (每条边的离散类型编号)
        """
        # == 设备与类型安全 ==
        device = x.device
        if isinstance(edge_index, torch.Tensor):
            assert edge_index.dim() == 2 and edge_index.size(0) == 2, \
                "edge_index must be shape [2, num_edges]"
            dst, src = edge_index[0].to(device), edge_index[1].to(device)
        else:
            # 允许传入 (src, dst)
            dst = edge_index[0].to(device)
            src = edge_index[1].to(device)
        edge_type = edge_type.to(device).long()
        
        num_nodes = x.size(0)
        num_edges = src.size(0)
        # 简单越界/一致性检查（在CPU上快速触发友好错误）
        if src.min() < 0 or dst.min() < 0 or src.max() >= num_nodes or dst.max() >= num_nodes:
            raise IndexError(f"edge_index contains invalid node ids: "
                             f"src in [{int(src.min())}, {int(src.max())}], "
                             f"dst in [{int(dst.min())}, {int(dst.max())}], "
                             f"but num_nodes={num_nodes}")
        if edge_type.dim() != 1 or edge_type.size(0) != num_edges:
            raise ValueError(f"edge_type must be 1D tensor with length == num_edges ({num_edges}), got {edge_type.shape}")
        
        # 取出边嵌入
        edge_feat = self.edge_emb(edge_type)  # [num_edges, edge_dim]
        
        # 注意力计算输入 (src_feat, dst_feat, edge_feat)
        src_feat = x[src]     # [num_edges, in_channels]
        dst_feat = x[dst]     # [num_edges, in_channels]
        att_input = torch.cat([src_feat, dst_feat, edge_feat], dim=1)  # [num_edges, 2*in + edge_dim]
        
        # 计算注意力分数 (未归一化)
        att_score = self.att_mlp(att_input).squeeze(-1)  # [num_edges]
        
        # 为数值稳定性做中心化（可选）
        # 按目标节点做 softmax-like 归一化：exp(score - max_per_dst) / sum_exp
        # 先找每个 dst 的 max，避免 exp 溢出
        max_per_dst = torch.full((num_nodes,), -1e9, device=device)
        max_per_dst.index_put_((dst,), att_score, accumulate=False)  # initialize
        # 上面 index_put_ 不会做分组max，此处改为用 scatter:
        from torch_scatter import scatter_max
        max_vals = scatter_max(att_score, dst, dim=0, dim_size=num_nodes)[0]  # [num_nodes], 有些位置为 -inf
        # 替换 -inf 为 0 以避免 nan
        max_vals[~torch.isfinite(max_vals)] = 0.0
        att_score_centered = att_score - max_vals[dst]
        att_weight = torch.exp(att_score_centered)  # [num_edges]
        
        # denom per dst
        denom = torch.zeros(num_nodes, device=device)
        denom.index_add_(0, dst, att_weight)
        # avoid division by zero (if a node has no incoming edges)
        denom = denom + 1e-8
        att_weight = att_weight / denom[dst]  # normalized weights per dst
        
        # 聚合邻居特征
        neigh_input = torch.cat([src_feat, edge_feat], dim=1)
        neigh_msg = self.lin_neigh(neigh_input)  # [num_edges, out_channels]
        agg_neigh = torch.zeros((num_nodes, self.out_channels), device=device)
        agg_neigh.index_add_(0, dst, att_weight.unsqueeze(-1) * neigh_msg)
        
        # 自节点更新
        out = self.lin_self(x) + agg_neigh + self.bias
        return out


class SAGE(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, num_layers,
                 num_edge_types, edge_dim=32, use_residual=False):
        """
        num_edge_types: 必需，图中边类别数（离散）
        edge_dim: 边嵌入维度
        """
        super(SAGE, self).__init__()
        assert num_layers >= 2, "num_layers must be >= 2"
        self.num_layers = num_layers
        self.use_residual = use_residual

        self.convs = nn.ModuleList()
        self.bns = nn.ModuleList()
        self.res_proj = nn.ModuleList()

        # 第一层: in -> hidden
        self.convs.append(LearnableEdgeSAGEConv(in_channels, hidden_channels,
                                                num_edge_types, edge_dim=edge_dim, hidden_dim=hidden_channels))
        # 中间层: hidden -> hidden
        for _ in range(num_layers - 2):
            self.convs.append(LearnableEdgeSAGEConv(hidden_channels, hidden_channels,
                                                    num_edge_types, edge_dim=edge_dim, hidden_dim=hidden_channels))
        # 最后一层: hidden -> out
        self.convs.append(LearnableEdgeSAGEConv(hidden_channels, out_channels,
                                                num_edge_types, edge_dim=edge_dim, hidden_dim=hidden_channels))

        # BatchNorm for hidden layers (num_layers-1 places)
        for _ in range(num_layers - 1):
            self.bns.append(nn.BatchNorm1d(hidden_channels))

        # projection layers for residual when dims mismatch
        dims = [in_channels] + [hidden_channels] * (num_layers - 1) + [out_channels]
        for i in range(num_layers - 1):
            if dims[i] != dims[i + 1]:
                self.res_proj.append(nn.Linear(dims[i], dims[i + 1], bias=False))
            else:
                self.res_proj.append(nn.Identity())

    def forward(self, x, edge_index, edge_type):
        """
        edge_type: [num_edges] LongTensor of edge labels. (not one-hot)
        """
        # ensure device
        # (convs check and move internally, but here we just move edge_index/edge_type to x.device)
        if isinstance(edge_index, torch.Tensor):
            edge_index = edge_index.to(x.device)
        else:
            edge_index = (edge_index[0].to(x.device), edge_index[1].to(x.device))
        edge_type = edge_type.to(x.device).long()

        for i, conv in enumerate(self.convs[:-1]):
            residual = x
            x = conv(x, edge_index, edge_type)

            if self.use_residual:
                res = self.res_proj[i](residual)
                x = x + res

            x = self.bns[i](x)
            x = F.relu(x)
            x = F.dropout(x, p=0.2, training=self.training)

        # final layer (no BN/activation here)
        x = self.convs[-1](x, edge_index, edge_type)
        return x


def focalLoss(output, target, gamma=2, alpha=0.25):
    ce_loss = F.cross_entropy(output, target, reduction='none')
    pt = torch.exp(-ce_loss)
    focal_loss = alpha * (1-pt)**gamma * ce_loss
    return focal_loss.mean()
    

class Trainer:
    def __init__(self, model, loader_train, loader_test, data, valid_index):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = model.to(self.device)
        self.loader_train = loader_train
        self.loader_test = loader_test
        self.data = data
        self.valid_index = valid_index

        self.train_loss = []
        self.test_loss = []

        self.best_auc = 0.0
        self.best_model_path = None
        self.final_model_path = None

        self.weight = torch.FloatTensor([0.24, 20.31]).to(self.device)

    
    def loss(self, output, target):
        # return focalLoss(output, target, gamma=2, alpha=0.25)
        return F.cross_entropy(output, target, weight=self.weight)


    def train(self, epochs=10, lr=0.01, weight_decay=5e-4):
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        print('start_training')
        for epoch in range(1, epochs+1):
            self.model.train()
            total_loss = 0
            for data in self.loader_train:
                x = data.x.to(self.device)
                y = data.y.to(self.device).squeeze(dim=1)
                edge_index = data.edge_index.to(self.device)
                edge_attr = data.edge_type.to(self.device)  # 使用边类型作为边特征
                optimizer.zero_grad()
                out = self.model(x, edge_index, edge_attr)
                loss = self.loss(out[:data.batch_size], y[:data.batch_size])
                loss.backward()
                optimizer.step()
                total_loss += loss.item() * data.y.shape[0]

                # print(f"Loss: {loss.item():.4f}")
            self.train_loss.append(total_loss / len(self.loader_train.dataset))

            self.model.eval()
            total_loss = 0
            all_preds = []
            all_labels = []
            for data in self.loader_test:
                x = data.x.to(self.device)
                y = data.y.to(self.device).squeeze(dim=1)
                edge_index = data.edge_index.to(self.device)
                edge_attr = data.edge_type.to(self.device)  # 使用边类型作为边特征
                with torch.no_grad():
                    out = self.model(x, edge_index, edge_attr)
                    loss = self.loss(out[:data.batch_size], y[:data.batch_size])
                total_loss += loss.item() * data.y.shape[0]

                preds = F.softmax(out, dim=1)
                all_preds.append(preds.cpu().numpy())
                all_labels.append(y.cpu().numpy())

            self.test_loss.append(total_loss / len(self.loader_test.dataset))

            # Calculate AUC for first two labels
            all_preds = np.concatenate(all_preds, axis=0)
            all_labels = np.concatenate(all_labels, axis=0)

            # Calculate AUC for label 1 with error handling
            auc_label1 = 0.0

            # Check if label 1 exists in test set
            if np.any(all_labels == 1):
                auc_label1 = roc_auc_score((all_labels == 1).astype(int), all_preds[:, 1])
            else:
                auc_label1 = float('nan')

            if auc_label1 > self.best_auc:
                self.best_auc = auc_label1
                self.save_model(os.path.join('data', f'model_auc{self.best_auc:.4f}.pth'))
                if self.best_model_path is not None:
                    os.remove(self.best_model_path) 
                self.best_model_path = os.path.join('data', f'model_auc{self.best_auc:.4f}.pth')
                self.final_model_path = os.path.join('data', f'model_auc{self.best_auc:.4f}.pth')

            print(f'Epoch: {epoch:03d}, Train Loss: {self.train_loss[-1]:.4f}, Test Loss: {self.test_loss[-1]:.4f}, AUC Label1: {auc_label1:.4f}')

            c = input('是否继续训练？(y: 继续训练, n: 停止训练, s: 停止训练并保存当前模型)')
            if c == 'n':
                break
            elif c == 's':
                self.save_model(os.path.join('data', f'model_auc{self.best_auc:.4f}.pth'))
                self.final_model_path = os.path.join('data', f'model_auc{self.best_auc:.4f}.pth')
                break

    def save_model(self, path='model.pth'):
        torch.save(self.model.state_dict(), path)
        print(f"模型已保存到 {path}")

    def predict_test_nodes(self, output_path=None):
        """
        对test_mask标记的节点进行预测，并保存为npy文件
        shape: (N, 2)，其中N为测试样本数目
        """
        if output_path is None:
            output_path = os.path.join('data', f'result_auc{self.best_auc:.4f}.npy')
        # 加载模型参数
        self.model.load_state_dict(torch.load(self.final_model_path))
        self.model.eval()

        # 获取所有节点的预测结果
        with torch.no_grad():
            x = self.data.x.to(self.device)
            edge_index = self.data.edge_index.to(self.device)
            edge_attr = self.data.edge_type.to(self.device)  # 使用边类型作为边特征
            out = self.model(x, edge_index, edge_attr)
            preds = F.softmax(out, dim=1)

        # 提取test_mask对应的预测结果
        test_preds = preds[self.valid_index].cpu().numpy()

        # # 只取前两个label的概率，shape为(N, 2)
        test_preds_first_two = test_preds[:, :2]

        # 保存为npy文件
        np.save(output_path, test_preds_first_two)

        print(f"预测结果已保存到 {output_path}")
        print(f"预测结果shape: {test_preds_first_two.shape}")
        print(f"测试样本数量: {test_preds_first_two.shape[0]}")

        return test_preds_first_two


if __name__ == '__main__':
    loader_train, loader_test, data, test_mask = load_data()
    # 创建使用边特征的新模型
    model = SAGE(
        in_channels=17,
        hidden_channels=32,
        out_channels=2,
        num_layers=5,
        num_edge_types=11,
        edge_dim=4,
        use_residual=True,
    )
    # 模型参数量
    print(f"模型参数量: {sum(p.numel() for p in model.parameters())}")
    trainer = Trainer(model, loader_train, loader_test, data, test_mask)
    trainer.train(epochs=50, lr=0.01, weight_decay=5e-4)

    # 训练完成后进行预测并保存结果
    trainer.predict_test_nodes()


