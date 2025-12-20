import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from care_gnn_modules import (
    SimilarityModule, 
    RLNeighborSelector,
    IntraRelationAggregator,
    InterRelationAggregator,
    PredictionModule
)


class CAREGNN(nn.Module):
    """
    完整的CARE-GNN模型
    用于金融反欺诈图节点分类
    
    包含三个核心模块:
    1. 相似性计算模块 (SimilarityModule)
    2. 邻居选择器 (RLNeighborSelector) - 使用强化学习
    3. 预测模块 (PredictionModule)
    """
    
    def __init__(self,
                 feature_dim,
                 embed_dim=64,
                 num_relations=11,
                 num_classes=2,
                 max_neighbors=20,
                 agg_type='attention',
                 step_size=0.02,
                 dataset=None,
                 use_adaptive_sampling=False,
                 use_2hop=False):
        super(CAREGNN, self).__init__()

        self.feature_dim = feature_dim
        self.embed_dim = embed_dim
        self.num_relations = num_relations
        self.num_classes = num_classes
        self.max_neighbors = max_neighbors
        self.dataset = dataset
        self.use_adaptive_sampling = use_adaptive_sampling
        self.use_2hop = use_2hop

        # 自适应采样的max_neighbors配置（按度数层级）
        # Tier 0 (0-2): 5, Tier 1 (3-5): 10, Tier 2 (6-10): 15, Tier 3 (>10): 30
        self.adaptive_max_neighbors = {
            0: 5,   # Very low degree
            1: 10,  # Low degree
            2: 15,  # Medium degree
            3: 30   # High degree
        }
        
        # 三个核心模块
        
        # 1. 相似性计算模块
        self.similarity_module = SimilarityModule(feature_dim, embed_dim)
        
        # 2. 强化学习邻居选择器
        self.neighbor_selector = RLNeighborSelector(embed_dim, step_size)
        
        # 单关系内聚合器 (为每种关系类型创建)
        self.intra_aggregators = nn.ModuleList([
            IntraRelationAggregator(feature_dim, embed_dim)
            for _ in range(num_relations)
        ])
        
        # 跨关系聚合器
        self.inter_aggregator = InterRelationAggregator(embed_dim, num_relations, agg_type)
        
        # 3. 预测模块
        self.prediction_module = PredictionModule(embed_dim, num_classes)
        
        # 用于标签相似度的分类器 (辅助任务)
        self.label_classifier = nn.Linear(embed_dim, num_classes)
        
    def get_adaptive_max_neighbors(self, node):
        """根据节点度数层级获取自适应max_neighbors"""
        if not self.use_adaptive_sampling or self.dataset is None:
            return self.max_neighbors

        tier = self.dataset.get_node_degree_tier(node)
        return self.adaptive_max_neighbors.get(tier, self.max_neighbors)

    def sample_neighbors(self, nodes, adj_lists, relation_type, features):
        """
        采样邻居节点（支持自适应采样）

        Args:
            nodes: (batch_size,) 中心节点ID
            adj_lists: dict of adjacency lists for each relation
            relation_type: 关系类型
            features: 全局特征矩阵

        Returns:
            neighbor_features: (batch_size, max_neighbors, feature_dim)
            neighbor_mask: (batch_size, max_neighbors) 有效邻居掩码
        """
        batch_size = len(nodes)
        device = features.device

        # 如果使用自适应采样，需要找到batch中最大的max_neighbors
        if self.use_adaptive_sampling and self.dataset is not None:
            max_possible_neighbors = max(
                self.get_adaptive_max_neighbors(node) for node in nodes
            )
        else:
            max_possible_neighbors = self.max_neighbors

        neighbor_features = torch.zeros(
            batch_size, max_possible_neighbors, self.feature_dim
        ).to(device)

        neighbor_mask = torch.zeros(batch_size, max_possible_neighbors).to(device)

        for i, node in enumerate(nodes):
            neighbors = list(adj_lists[relation_type][node])

            # 获取该节点的自适应max_neighbors
            node_max_neighbors = self.get_adaptive_max_neighbors(node)

            if len(neighbors) > 0:
                # 随机采样或取全部
                if len(neighbors) > node_max_neighbors:
                    sampled_neighbors = np.random.choice(
                        neighbors,
                        node_max_neighbors,
                        replace=False
                    )
                else:
                    sampled_neighbors = neighbors

                # 填充特征
                num_sampled = len(sampled_neighbors)
                neighbor_features[i, :num_sampled] = features[sampled_neighbors]
                neighbor_mask[i, :num_sampled] = 1.0

        return neighbor_features, neighbor_mask

    def sample_2hop_neighbors(self, nodes, features, max_2hop=10):
        """
        为低度数节点采样2-hop邻居

        Args:
            nodes: (batch_size,) 中心节点ID
            features: 全局特征矩阵
            max_2hop: 最多采样的2-hop邻居数

        Returns:
            neighbor_2hop_features: (batch_size, max_2hop, feature_dim)
            neighbor_2hop_mask: (batch_size, max_2hop) 有效邻居掩码
        """
        batch_size = len(nodes)
        device = features.device

        neighbor_2hop_features = torch.zeros(
            batch_size, max_2hop, self.feature_dim
        ).to(device)

        neighbor_2hop_mask = torch.zeros(batch_size, max_2hop).to(device)

        for i, node in enumerate(nodes):
            # 只为低度数节点（tier 0和1）获取2-hop邻居
            if self.dataset is not None:
                tier = self.dataset.get_node_degree_tier(node)
                if tier <= 1:  # 度数 <= 5
                    neighbors_2hop = self.dataset.get_2hop_neighbors(node)

                    if len(neighbors_2hop) > 0:
                        neighbors_2hop_list = list(neighbors_2hop)

                        # 随机采样
                        if len(neighbors_2hop_list) > max_2hop:
                            sampled_2hop = np.random.choice(
                                neighbors_2hop_list,
                                max_2hop,
                                replace=False
                            )
                        else:
                            sampled_2hop = neighbors_2hop_list

                        # 填充特征
                        num_sampled = len(sampled_2hop)
                        neighbor_2hop_features[i, :num_sampled] = features[sampled_2hop]
                        neighbor_2hop_mask[i, :num_sampled] = 1.0

        return neighbor_2hop_features, neighbor_2hop_mask
    
    def forward(self, nodes, features, adj_lists, labels=None, training=True):
        """
        前向传播
        
        Args:
            nodes: (batch_size,) 节点ID
            features: (num_nodes, feature_dim) 全局特征矩阵
            adj_lists: dict of adjacency lists
            labels: (batch_size,) 标签 (训练时需要)
            training: 是否训练模式
        
        Returns:
            logits: (batch_size, num_classes) 分类logits
            label_logits: (batch_size, num_classes) 标签相似度logits
        """
        batch_size = len(nodes)
        device = features.device
        
        # 获取中心节点特征
        center_features = features[nodes]  # (batch_size, feature_dim)
        
        # 为每种关系类型聚合
        relation_embeddings = []
        
        for rel_type in range(1, self.num_relations + 1):
            # 采样邻居
            neighbor_features, neighbor_mask = self.sample_neighbors(
                nodes, adj_lists, rel_type, features
            )
            
            # 跳过没有邻居的关系
            if neighbor_mask.sum() == 0:
                continue
            
            # 计算相似度
            similarity_scores = self.similarity_module(
                center_features, 
                neighbor_features
            )  # (batch_size, max_neighbors)
            
            # 应用邻居掩码
            similarity_scores = similarity_scores * neighbor_mask + (1 - neighbor_mask) * (-1e9)
            
            # 初步聚合以获得中心节点嵌入 (用于RL决策)
            temp_center_emb = self.intra_aggregators[rel_type - 1].agg_layer(center_features)
            
            # 使用强化学习选择邻居
            selected_mask, threshold = self.neighbor_selector.select_neighbors(
                similarity_scores,
                temp_center_emb,
                training=training
            )
            
            # 应用邻居掩码确保不选择无效邻居
            selected_mask = selected_mask * neighbor_mask
            
            # 聚合被选中的邻居
            relation_emb = self.intra_aggregators[rel_type - 1](
                center_features,
                neighbor_features,
                selected_mask
            )
            
            relation_embeddings.append(relation_emb)
        
        # 跨关系聚合
        if len(relation_embeddings) > 0:
            final_emb_1hop = self.inter_aggregator(relation_embeddings)
        else:
            # 如果没有邻居,只使用中心节点特征
            final_emb_1hop = self.intra_aggregators[0].agg_layer(center_features)

        # 2-hop聚合（仅用于低度数节点）
        if self.use_2hop and self.dataset is not None:
            neighbor_2hop_features, neighbor_2hop_mask = self.sample_2hop_neighbors(
                nodes, features, max_2hop=10
            )

            # 如果有2-hop邻居
            if neighbor_2hop_mask.sum() > 0:
                # 计算2-hop相似度
                similarity_2hop = self.similarity_module(
                    center_features,
                    neighbor_2hop_features
                )
                similarity_2hop = similarity_2hop * neighbor_2hop_mask + (1 - neighbor_2hop_mask) * (-1e9)

                # 简化版聚合（不使用RL选择器）
                # 使用softmax加权平均
                attn_weights_2hop = F.softmax(similarity_2hop, dim=1).unsqueeze(2)  # (batch, max_2hop, 1)
                weighted_2hop = (neighbor_2hop_features * attn_weights_2hop).sum(dim=1)  # (batch, feature_dim)

                # 通过聚合层转换
                emb_2hop = self.intra_aggregators[0].agg_layer(weighted_2hop)

                # 结合1-hop和2-hop embedding（2-hop权重为0.5）
                final_emb = final_emb_1hop + 0.5 * emb_2hop
            else:
                final_emb = final_emb_1hop
        else:
            final_emb = final_emb_1hop

        # 预测
        logits = self.prediction_module(final_emb)
        
        # 标签相似度预测 (辅助任务)
        label_logits = self.label_classifier(final_emb)
        
        return logits, label_logits
    
    def loss(self, nodes, features, adj_lists, labels, lambda_1=2.0):
        """
        计算损失函数

        Args:
            nodes: 节点ID
            features: 特征矩阵
            adj_lists: 邻接表
            labels: 真实标签
            lambda_1: 标签相似度损失权重

        Returns:
            total_loss: 总损失
            gnn_loss: GNN分类损失
            label_loss: 标签相似度损失
        """
        logits, label_logits = self.forward(nodes, features, adj_lists, labels, training=True)

        # 确保标签是一维张量
        if len(labels.shape) > 1:
            labels = labels.squeeze()

        # GNN分类损失
        gnn_loss = F.cross_entropy(logits, labels)

        # 标签相似度损失
        label_loss = F.cross_entropy(label_logits, labels)

        # 总损失
        total_loss = gnn_loss + lambda_1 * label_loss

        return total_loss, gnn_loss, label_loss
    
    def predict_proba(self, nodes, features, adj_lists):
        """
        预测概率
        
        Returns:
            proba: (batch_size, num_classes) 概率分布
        """
        self.eval()
        with torch.no_grad():
            logits, _ = self.forward(nodes, features, adj_lists, training=False)
            proba = F.softmax(logits, dim=1)
        return proba


class FocalLoss(nn.Module):
    """
    Focal Loss用于处理类别不平衡
    """
    
    def __init__(self, alpha=0.25, gamma=2.0):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        
    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()


class CAREGNNWithFocalLoss(CAREGNN):
    """
    使用Focal Loss的CARE-GNN变体
    更好地处理极端类别不平衡问题
    """

    def __init__(self, *args, alpha=0.25, gamma=2.0, **kwargs):
        # 确保dataset, use_adaptive_sampling, use_2hop参数能正确传递
        super().__init__(*args, **kwargs)
        self.focal_loss = FocalLoss(alpha, gamma)
        
    def loss(self, nodes, features, adj_lists, labels, lambda_1=2.0):
        """使用Focal Loss的损失函数"""
        logits, label_logits = self.forward(nodes, features, adj_lists, labels, training=True)

        # 确保标签是一维张量
        if len(labels.shape) > 1:
            labels = labels.squeeze()

        # 使用Focal Loss
        gnn_loss = self.focal_loss(logits, labels)
        label_loss = self.focal_loss(label_logits, labels)

        total_loss = gnn_loss + lambda_1 * label_loss

        return total_loss, gnn_loss, label_loss
