import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class SimilarityModule(nn.Module):
    """
    3.1 相似性计算模块 (Label-aware Similarity Measure)
    计算节点之间的标签感知相似度分数
    """
    
    def __init__(self, feature_dim, hidden_dim=64):
        super(SimilarityModule, self).__init__()
        
        # 特征转换层
        self.feature_transform = nn.Sequential(
            nn.Linear(feature_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # 相似度打分层
        self.score_layer = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
    def forward(self, center_features, neighbor_features):
        """
        计算中心节点与邻居节点的相似度
        
        Args:
            center_features: (batch_size, feature_dim) 中心节点特征
            neighbor_features: (batch_size, num_neighbors, feature_dim) 邻居特征
        
        Returns:
            similarity_scores: (batch_size, num_neighbors) 相似度分数
        """
        batch_size, num_neighbors, feature_dim = neighbor_features.shape
        
        # 特征转换
        center_emb = self.feature_transform(center_features)  # (batch_size, hidden_dim)
        neighbor_emb = self.feature_transform(
            neighbor_features.view(-1, feature_dim)
        ).view(batch_size, num_neighbors, -1)  # (batch_size, num_neighbors, hidden_dim)
        
        # 扩展中心节点特征以匹配邻居数量
        center_emb_expanded = center_emb.unsqueeze(1).expand(-1, num_neighbors, -1)
        
        # 拼接中心节点和邻居特征
        combined = torch.cat([center_emb_expanded, neighbor_emb], dim=-1)  # (batch_size, num_neighbors, hidden_dim*2)
        
        # 计算相似度分数
        similarity_scores = self.score_layer(combined).squeeze(-1)  # (batch_size, num_neighbors)
        
        return similarity_scores


class RLNeighborSelector(nn.Module):
    """
    3.2 邻居选择器 (Reinforcement Learning-based Neighbor Selector)
    使用强化学习动态选择最优邻居数量
    """
    
    def __init__(self, embed_dim, step_size=0.02):
        super(RLNeighborSelector, self).__init__()
        
        self.embed_dim = embed_dim
        self.step_size = step_size
        
        # 用于决策的神经网络
        self.decision_net = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()  # 输出0-1之间的阈值
        )
        
        # 保存训练过程中的奖励
        self.saved_log_probs = []
        self.rewards = []
        
        # 初始化阈值参数
        self.init_threshold = 0.5
        
    def select_neighbors(self, similarity_scores, center_emb, training=True):
        """
        基于相似度分数和强化学习策略选择邻居
        
        Args:
            similarity_scores: (batch_size, num_neighbors) 相似度分数
            center_emb: (batch_size, embed_dim) 中心节点嵌入
            training: 是否在训练模式
        
        Returns:
            selected_mask: (batch_size, num_neighbors) 选择的邻居掩码
            threshold: (batch_size,) 选择阈值
        """
        batch_size, num_neighbors = similarity_scores.shape
        
        # 使用决策网络预测阈值
        threshold = self.decision_net(center_emb).squeeze(-1)  # (batch_size,)
        
        if training:
            # 训练时添加探索噪声
            noise = torch.randn_like(threshold) * self.step_size
            threshold = torch.clamp(threshold + noise, 0, 1)
        
        # 归一化相似度分数到0-1
        sim_normalized = torch.sigmoid(similarity_scores)
        
        # 选择相似度大于阈值的邻居
        threshold_expanded = threshold.unsqueeze(1).expand(-1, num_neighbors)
        selected_mask = (sim_normalized > threshold_expanded).float()
        
        # 确保至少选择一个邻居
        max_sim_idx = torch.argmax(sim_normalized, dim=1)
        for i in range(batch_size):
            selected_mask[i, max_sim_idx[i]] = 1.0
        
        return selected_mask, threshold
    
    def compute_reward(self, predictions, labels):
        """
        计算强化学习的奖励
        基于分类准确率和召回率
        
        Args:
            predictions: (batch_size, num_classes) 预测概率
            labels: (batch_size,) 真实标签
        
        Returns:
            reward: 标量奖励
        """
        pred_labels = torch.argmax(predictions, dim=1)
        
        # 准确率
        accuracy = (pred_labels == labels).float().mean()
        
        # 召回率 (针对Class 1)
        class1_mask = (labels == 1)
        if class1_mask.sum() > 0:
            recall = (pred_labels[class1_mask] == 1).float().mean()
        else:
            recall = 0.0
        
        # 综合奖励 (更重视召回率以应对类别不平衡)
        reward = 0.3 * accuracy + 0.7 * recall
        
        return reward.item()


class IntraRelationAggregator(nn.Module):
    """
    单关系内的聚合器 - 改进版，添加BatchNorm和更深的网络
    """

    def __init__(self, feature_dim, embed_dim):
        super(IntraRelationAggregator, self).__init__()

        self.feature_dim = feature_dim
        self.embed_dim = embed_dim

        # 聚合层 - 添加BatchNorm
        self.agg_layer = nn.Sequential(
            nn.Linear(feature_dim, embed_dim),
            nn.BatchNorm1d(embed_dim),
            nn.ReLU(),
            nn.Dropout(0.3)
        )

        # 组合层 - 更深的网络
        self.combine_layer = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.BatchNorm1d(embed_dim),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
    def forward(self, center_features, neighbor_features, selected_mask):
        """
        聚合邻居信息
        
        Args:
            center_features: (batch_size, feature_dim)
            neighbor_features: (batch_size, num_neighbors, feature_dim)
            selected_mask: (batch_size, num_neighbors)
        
        Returns:
            aggregated_emb: (batch_size, embed_dim)
        """
        batch_size, num_neighbors, feature_dim = neighbor_features.shape
        
        # 转换特征
        center_emb = self.agg_layer(center_features)  # (batch_size, embed_dim)
        neighbor_emb = self.agg_layer(
            neighbor_features.view(-1, feature_dim)
        ).view(batch_size, num_neighbors, -1)  # (batch_size, num_neighbors, embed_dim)
        
        # 应用选择掩码
        selected_mask_expanded = selected_mask.unsqueeze(-1).expand_as(neighbor_emb)
        masked_neighbor_emb = neighbor_emb * selected_mask_expanded
        
        # 聚合邻居嵌入 (加权平均)
        num_selected = selected_mask.sum(dim=1, keepdim=True).clamp(min=1)
        neighbor_agg = masked_neighbor_emb.sum(dim=1) / num_selected  # (batch_size, embed_dim)
        
        # 组合中心节点和邻居聚合
        combined = torch.cat([center_emb, neighbor_agg], dim=-1)
        aggregated_emb = self.combine_layer(combined)
        
        return aggregated_emb


class InterRelationAggregator(nn.Module):
    """
    跨关系聚合器
    聚合来自不同边类型的信息
    """
    
    def __init__(self, embed_dim, num_relations, agg_type='attention'):
        super(InterRelationAggregator, self).__init__()
        
        self.embed_dim = embed_dim
        self.num_relations = num_relations
        self.agg_type = agg_type
        
        if agg_type == 'attention':
            # 注意力机制聚合
            self.attention = nn.Sequential(
                nn.Linear(embed_dim, 64),
                nn.Tanh(),
                nn.Linear(64, 1)
            )
        elif agg_type == 'weight':
            # 可学习权重聚合
            self.relation_weights = nn.Parameter(torch.ones(num_relations) / num_relations)
        
    def forward(self, relation_embeddings):
        """
        聚合多个关系的嵌入
        
        Args:
            relation_embeddings: list of (batch_size, embed_dim), 每个关系的嵌入
        
        Returns:
            final_emb: (batch_size, embed_dim)
        """
        if len(relation_embeddings) == 0:
            return None
        
        # 堆叠所有关系的嵌入
        stacked_emb = torch.stack(relation_embeddings, dim=1)  # (batch_size, num_relations, embed_dim)
        
        if self.agg_type == 'mean':
            # 简单平均
            final_emb = stacked_emb.mean(dim=1)
            
        elif self.agg_type == 'attention':
            # 注意力加权
            attention_scores = self.attention(stacked_emb).squeeze(-1)  # (batch_size, num_relations)
            attention_weights = F.softmax(attention_scores, dim=1).unsqueeze(-1)  # (batch_size, num_relations, 1)
            final_emb = (stacked_emb * attention_weights).sum(dim=1)  # (batch_size, embed_dim)
            
        elif self.agg_type == 'weight':
            # 可学习权重
            weights = F.softmax(self.relation_weights, dim=0).view(1, -1, 1)  # (1, num_relations, 1)
            final_emb = (stacked_emb * weights).sum(dim=1)
        
        return final_emb


class PredictionModule(nn.Module):
    """
    3.3 预测模块 - 改进版，更深的网络和BatchNorm
    基于聚合的节点嵌入进行分类
    """

    def __init__(self, embed_dim, num_classes=2):
        super(PredictionModule, self).__init__()

        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes)
        )
        
    def forward(self, embeddings):
        """
        预测节点标签
        
        Args:
            embeddings: (batch_size, embed_dim)
        
        Returns:
            logits: (batch_size, num_classes)
        """
        logits = self.classifier(embeddings)
        return logits
