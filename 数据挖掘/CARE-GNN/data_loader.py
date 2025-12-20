import numpy as np
import torch
from torch.utils.data import Dataset
import scipy.sparse as sp
from scipy.sparse import coo_matrix, csr_matrix
from scipy.stats import skew, kurtosis, entropy
from sklearn.preprocessing import StandardScaler


class DGraphDataset:
    """DGraph金融反欺诈数据集加载器 (增强版 - 参考baseline特征工程)"""

    def __init__(self, data_path='phase1_gdata.npz', use_enhanced_features=True):
        print("Loading DGraph dataset...")
        data = np.load(data_path)
        # 基本数据
        self.x_original = data['x']  # 原始节点特征 (N_node, 17)
        self.y = data['y']  # 节点标签 (N_node,)

        # ⚠️ 关键优化：边方向互换 [source, target] → [target, source]
        # 原因：原始数据可能是"受害者→欺诈者"方向，需要反转为"欺诈者→受害者"
        # 这样GNN能聚合到正确的邻居信息（欺诈者影响的大量受害者）
        self.edge_index = data['edge_index'][:, [1, 0]]  # 交换列！
        print("  ✓ Edge direction reversed: [source, target] → [target, source]")

        self.edge_type = data['edge_type']  # 边类型 (N_edge,)
        self.edge_timestamp = data['edge_timestamp']  # 边时间戳 (N_edge,)
        self.train_mask = data['train_mask']
        self.test_mask = data['test_mask']

        # 数据统计
        self.num_nodes = self.x_original.shape[0]
        self.num_features_original = self.x_original.shape[1]
        self.num_edges = self.edge_index.shape[0]
        self.num_edge_types = len(np.unique(self.edge_type))

        print(f"Nodes: {self.num_nodes}, Edges: {self.num_edges}")
        print(f"Original Features: {self.num_features_original}, Edge Types: {self.num_edge_types}")
        print(f"Train samples: {len(self.train_mask)}, Test samples: {len(self.test_mask)}")

        # 处理原始特征缺失值
        self.x = self.x_original.copy()
        self._handle_missing_values()

        # 生成增强特征（参考baseline）
        if use_enhanced_features:
            print("\n" + "="*60)
            print("Generating enhanced features (baseline-style)...")
            self._generate_enhanced_features()
            print("="*60 + "\n")

        # 标准化特征
        self._normalize_features()

        # 构建每种边类型的邻接表
        self._build_adjacency_lists()

        # 计算节点度数并分层
        self._compute_node_degrees()

        # 构建2-hop邻居（用于低度数节点扩展）
        self._build_2hop_neighbors()

        # 更新特征维度
        self.num_features = self.x.shape[1]
        print(f"Final feature dimension: {self.num_features}")

    def _handle_missing_values(self):
        """处理缺失值"""
        # 将-1替换为0或特征均值
        for i in range(self.num_features_original):
            col = self.x[:, i]
            mask = col != -1
            if mask.sum() > 0:
                # 用非缺失值的均值替换
                mean_val = col[mask].mean()
                col[~mask] = mean_val
            else:
                col[~mask] = 0

    def _generate_enhanced_features(self):
        """生成增强特征（参考baseline.ipynb）"""

        N = self.num_nodes
        E = self.num_edges
        edge_index = self.edge_index
        edge_timestamp = self.edge_timestamp
        edge_type = self.edge_type

        # 确保数组是一维的
        edge_timestamp = edge_timestamp.flatten()
        edge_type = edge_type.flatten()

        # ===== 1. 时间窗口特征 =====
        print("  [1/6] Computing time window features...")
        max_day = int(edge_timestamp.max())
        win_base = np.array([3, 7, 14, 30, 60, 90, 180], dtype=np.int32)
        win_days = np.concatenate([win_base, max_day - win_base])
        win_threshold = max_day - win_days
        W = len(win_threshold)

        edge_ts = edge_timestamp.reshape(-1, 1)
        mask = edge_ts >= win_threshold.reshape(1, -1)
        nodes_flat = np.concatenate([edge_index[:, 0], edge_index[:, 1]])
        mask_flat = np.concatenate([mask, mask], axis=0)

        recent_feats = np.zeros((N, W), dtype=np.float32)
        for w in range(W):
            recent_feats[:, w] = np.bincount(
                nodes_flat,
                weights=mask_flat[:, w].astype(np.float32),
                minlength=N
            )

        # ===== 2. 基础结构特征 =====
        print("  [2/6] Computing basic structural features...")
        out_deg = np.bincount(edge_index[:, 0], minlength=N).astype(np.float32)
        in_deg = np.bincount(edge_index[:, 1], minlength=N).astype(np.float32)
        deg = in_deg + out_deg
        deg_diff = out_deg - in_deg

        min_day = np.full(N, 1e9, dtype=np.float32)
        max_day_node = np.full(N, -1e9, dtype=np.float32)
        ts_flat = np.concatenate([edge_timestamp, edge_timestamp]).flatten()
        np.minimum.at(min_day, nodes_flat, ts_flat)
        np.maximum.at(max_day_node, nodes_flat, ts_flat)

        active_span = max_day_node - min_day
        active_span[active_span < 0] = 0

        day_sum = np.bincount(nodes_flat, weights=ts_flat, minlength=N)
        day_cnt = np.bincount(nodes_flat, minlength=N)
        day_mean = day_sum / np.maximum(day_cnt, 1)
        day_skew = (max_day_node - day_mean) / (active_span + 1e-6)
        deg_norm = deg / np.maximum(day_cnt, 1)

        Tmax = max_day_node.max() + 1e-6
        time_weight = ts_flat / Tmax
        w_out = np.zeros(N, dtype=np.float32)
        w_in = np.zeros(N, dtype=np.float32)
        np.add.at(w_out, edge_index[:, 0], time_weight[:E])
        np.add.at(w_in, edge_index[:, 1], time_weight[E:])
        time_weighted_deg = w_out + w_in

        mmin = min_day.min()
        mmax = min_day.max() + 1e-6
        last_active_norm = (max_day_node - mmin) / (mmax - mmin)

        X_recent = 30
        global_max = max_day_node.max()
        recent_active = (max_day_node > global_max - X_recent).astype(np.float32)

        median_span = np.median(active_span)
        active_long = (active_span > median_span).astype(np.float32)

        new_feats = np.stack([
            deg, deg_diff, active_span, day_mean, day_skew,
            deg_norm, time_weighted_deg, last_active_norm,
            active_long, recent_active
        ], axis=1).astype(np.float32)

        # ===== 3. 扩展特征 =====
        print("  [3/6] Computing extended features...")
        deg_ratio = out_deg / (in_deg + 1e-6)
        active_span_ratio = active_span / (active_span.max() + 1e-6)

        last_edge = np.zeros(N, dtype=np.float32)
        np.maximum.at(last_edge, nodes_flat, ts_flat)
        recent_gap = global_max - last_edge
        recent_gap_norm = recent_gap / (global_max + 1e-6)

        deg_squared = deg ** 2
        deg_diff_abs = np.abs(deg_diff)
        span_mean_ratio = active_span / (day_mean + 1e-6)

        # 邻居平均度
        rows = np.concatenate([edge_index[:, 0], edge_index[:, 1]])
        cols = np.concatenate([edge_index[:, 1], edge_index[:, 0]])
        adj = coo_matrix((np.ones_like(rows), (rows, cols)), shape=(N, N))
        mean_neighbor_deg = adj.dot(deg.reshape(-1, 1)).flatten() / np.maximum(adj.sum(axis=1).A1, 1)

        sum_ts = np.bincount(nodes_flat, weights=ts_flat, minlength=N)
        sum_ts2 = np.bincount(nodes_flat, weights=ts_flat**2, minlength=N)
        cnt_ts = np.bincount(nodes_flat, minlength=N)
        active_std = np.sqrt(np.maximum(0, sum_ts2/np.maximum(cnt_ts, 1) - (sum_ts/np.maximum(cnt_ts, 1))**2))
        active_std[cnt_ts == 0] = 0

        deg_rate = deg / np.maximum(active_span, 1e-6)

        deg_skew_val = skew(deg.astype(np.float64))
        deg_kurt_val = kurtosis(deg.astype(np.float64))
        deg_skew_feat = np.full(N, deg_skew_val, dtype=np.float32)
        deg_kurt_feat = np.full(N, deg_kurt_val, dtype=np.float32)

        more_feats = np.stack([
            deg_ratio, active_span_ratio, recent_gap_norm,
            deg_squared, deg_diff_abs, span_mean_ratio,
            mean_neighbor_deg, active_std, deg_rate,
            deg_skew_feat, deg_kurt_feat
        ], axis=1).astype(np.float32)

        # ===== 4. 邻居特征 =====
        print("  [4/6] Computing neighbor features...")
        A_in = coo_matrix((np.ones(E), (edge_index[:, 1], edge_index[:, 0])), shape=(N, N)).tocsr()
        A_out = coo_matrix((np.ones(E), (edge_index[:, 0], edge_index[:, 1])), shape=(N, N)).tocsr()

        num_in_neighbors = np.array(A_in.sum(axis=1)).flatten()
        num_out_neighbors = np.array(A_out.sum(axis=1)).flatten()
        num_all_neighbors = np.array((A_in + A_out).astype(bool).sum(axis=1)).flatten()
        ratio_in_out_neighbors = num_in_neighbors / np.maximum(num_out_neighbors, 1)

        mean_in_deg_neighbors = A_in.dot(in_deg) / np.maximum(num_in_neighbors, 1)
        mean_out_deg_neighbors = A_out.dot(out_deg) / np.maximum(num_out_neighbors, 1)

        mean_last_active_in_neighbors = A_in.dot(max_day_node) / np.maximum(num_in_neighbors, 1)
        mean_last_active_out_neighbors = A_out.dot(max_day_node) / np.maximum(num_out_neighbors, 1)

        recent_active_mask = (max_day_node > global_max - X_recent).astype(np.float32)
        recent_active_in_neighbors = A_in.dot(recent_active_mask) / np.maximum(num_in_neighbors, 1)
        recent_active_out_neighbors = A_out.dot(recent_active_mask) / np.maximum(num_out_neighbors, 1)

        # ===== 5. 边类型特征 =====
        print("  [5/6] Computing edge type features...")
        num_types = int(edge_type.max() + 1)
        in_type_count = np.zeros((N, num_types), dtype=np.float32)
        out_type_count = np.zeros((N, num_types), dtype=np.float32)
        np.add.at(out_type_count, (edge_index[:, 0], edge_type), 1)
        np.add.at(in_type_count, (edge_index[:, 1], edge_type), 1)

        in_type_ratio = in_type_count / np.maximum(in_type_count.sum(axis=1, keepdims=True), 1)
        out_type_ratio = out_type_count / np.maximum(out_type_count.sum(axis=1, keepdims=True), 1)

        # ===== 6. 边时间特征 =====
        print("  [6/6] Computing edge time features...")
        last_edge_out = np.zeros(N, dtype=np.float32)
        last_edge_in = np.zeros(N, dtype=np.float32)
        np.maximum.at(last_edge_out, edge_index[:, 0], edge_timestamp)
        np.maximum.at(last_edge_in, edge_index[:, 1], edge_timestamp)

        gap_last_edge_out = global_max - last_edge_out
        gap_last_edge_in = global_max - last_edge_in

        sum_ts_out = np.zeros(N, dtype=np.float32)
        cnt_out = np.zeros(N, dtype=np.float32)
        np.add.at(sum_ts_out, edge_index[:, 0], edge_timestamp)
        np.add.at(cnt_out, edge_index[:, 0], 1)
        avg_edge_time_out = sum_ts_out / np.maximum(cnt_out, 1)

        sum_ts_in = np.zeros(N, dtype=np.float32)
        cnt_in = np.zeros(N, dtype=np.float32)
        np.add.at(sum_ts_in, edge_index[:, 1], edge_timestamp)
        np.add.at(cnt_in, edge_index[:, 1], 1)
        avg_edge_time_in = sum_ts_in / np.maximum(cnt_in, 1)

        # ===== 合并所有特征 =====
        edge_feats = np.concatenate([
            num_in_neighbors.reshape(-1, 1),
            num_out_neighbors.reshape(-1, 1),
            num_all_neighbors.reshape(-1, 1),
            ratio_in_out_neighbors.reshape(-1, 1),
            mean_in_deg_neighbors.reshape(-1, 1),
            mean_out_deg_neighbors.reshape(-1, 1),
            mean_last_active_in_neighbors.reshape(-1, 1),
            mean_last_active_out_neighbors.reshape(-1, 1),
            recent_active_in_neighbors.reshape(-1, 1),
            recent_active_out_neighbors.reshape(-1, 1),
            gap_last_edge_in.reshape(-1, 1),
            gap_last_edge_out.reshape(-1, 1),
            avg_edge_time_in.reshape(-1, 1),
            avg_edge_time_out.reshape(-1, 1),
            in_type_ratio,
            out_type_ratio
        ], axis=1)

        struct_feats = np.concatenate([
            in_deg.reshape(-1, 1),
            out_deg.reshape(-1, 1),
            recent_feats,
            new_feats,
            more_feats,
            min_day.reshape(-1, 1),
            max_day_node.reshape(-1, 1),
            edge_feats
        ], axis=1).astype(np.float32)

        print(f"  Generated {struct_feats.shape[1]} structural features")

        # 拼接原始特征和结构特征
        self.x = np.concatenate([self.x, struct_feats], axis=1).astype(np.float32)
        print(f"  Total features: {self.x.shape[1]} ({self.num_features_original} original + {struct_feats.shape[1]} enhanced)")

    def _normalize_features(self):
        """标准化特征"""
        scaler = StandardScaler()
        self.x = scaler.fit_transform(self.x)
        
    def _build_adjacency_lists(self):
        """为每种边类型构建邻接表"""
        self.adj_lists = {}

        for edge_type in range(1, self.num_edge_types + 1):
            # 找到该类型的所有边
            type_mask = self.edge_type == edge_type
            type_indices = np.where(type_mask)[0]
            type_edges = self.edge_index[type_indices]
            
            # 构建邻接字典
            adj_dict = {}
            for src, dst in type_edges:
                if src not in adj_dict:
                    adj_dict[src] = []
                adj_dict[src].append(dst)
            
            # 转换为列表形式
            adj_list = [set(adj_dict.get(i, [])) for i in range(self.num_nodes)]
            self.adj_lists[edge_type] = adj_list
            
        print(f"Built adjacency lists for {len(self.adj_lists)} edge types")

    def _compute_node_degrees(self):
        """计算每个节点的度数并分层"""
        print("Computing node degrees...")

        # 初始化度数数组
        self.out_degrees = np.zeros(self.num_nodes, dtype=np.int32)
        self.in_degrees = np.zeros(self.num_nodes, dtype=np.int32)

        # 计算出度和入度
        for src, dst in self.edge_index:
            self.out_degrees[src] += 1
            self.in_degrees[dst] += 1

        self.total_degrees = self.out_degrees + self.in_degrees

        # 节点分层（基于总度数）
        self.degree_tiers = np.zeros(self.num_nodes, dtype=np.int8)
        # Tier 0: 极低度数 (0-2)
        self.degree_tiers[(self.total_degrees >= 0) & (self.total_degrees <= 2)] = 0
        # Tier 1: 低度数 (3-5)
        self.degree_tiers[(self.total_degrees >= 3) & (self.total_degrees <= 5)] = 1
        # Tier 2: 中度数 (6-10)
        self.degree_tiers[(self.total_degrees >= 6) & (self.total_degrees <= 10)] = 2
        # Tier 3: 高度数 (>10)
        self.degree_tiers[self.total_degrees > 10] = 3

        # 统计各层节点数
        for tier in range(4):
            count = np.sum(self.degree_tiers == tier)
            pct = 100.0 * count / self.num_nodes
            tier_names = ["Very Low (0-2)", "Low (3-5)", "Medium (6-10)", "High (>10)"]
            print(f"  Tier {tier} {tier_names[tier]}: {count:,} nodes ({pct:.2f}%)")

    def _build_2hop_neighbors(self):
        """为低度数节点构建2-hop邻居"""
        print("Building 2-hop neighbors for low-degree nodes...")

        # 合并所有边类型的邻接表（构建全局邻接表）
        global_adj = [set() for _ in range(self.num_nodes)]
        for edge_type, adj_list in self.adj_lists.items():
            for node_id, neighbors in enumerate(adj_list):
                global_adj[node_id].update(neighbors)

        # 为低度数节点（tier 0和1，即度数<=5）构建2-hop邻居
        self.adj_2hop = [set() for _ in range(self.num_nodes)]
        low_degree_mask = self.degree_tiers <= 1  # 度数 <=5

        low_degree_nodes = np.where(low_degree_mask)[0]
        print(f"  Building 2-hop for {len(low_degree_nodes):,} low-degree nodes...")

        for node_id in low_degree_nodes:
            # 1-hop邻居
            neighbors_1hop = global_adj[node_id]

            # 2-hop邻居（排除1-hop和自己）
            neighbors_2hop = set()
            for neighbor in neighbors_1hop:
                neighbors_2hop.update(global_adj[neighbor])

            neighbors_2hop -= neighbors_1hop  # 排除1-hop
            neighbors_2hop.discard(node_id)    # 排除自己

            self.adj_2hop[node_id] = neighbors_2hop

        # 统计2-hop扩展效果
        expanded_nodes = sum(1 for hop2 in self.adj_2hop if len(hop2) > 0)
        if expanded_nodes > 0:
            avg_2hop = sum(len(hop2) for hop2 in self.adj_2hop) / expanded_nodes
            print(f"  Expanded {expanded_nodes:,} nodes, avg 2-hop neighbors: {avg_2hop:.2f}")

    def get_2hop_neighbors(self, node_id):
        """获取节点的2-hop邻居"""
        return self.adj_2hop[node_id] if node_id < len(self.adj_2hop) else set()

    def get_node_degree_tier(self, node_id):
        """获取节点的度数层级"""
        return self.degree_tiers[node_id]

    def get_train_data(self):
        """获取训练数据"""
        train_idx = self.train_mask

        # 确保 train_idx 是一维数组
        if len(train_idx.shape) > 1:
            train_idx = train_idx.ravel()

        train_labels = self.y[train_idx]

        # 确保 train_labels 是一维数组
        if len(train_labels.shape) > 1:
            train_labels = train_labels.ravel()

        # 只保留前景节点 (Class 0 和 Class 1)
        foreground_mask = (train_labels == 0) | (train_labels == 1)
        train_idx = train_idx[foreground_mask]
        train_labels = train_labels[foreground_mask]
        
        print(f"Train set - Class 0: {(train_labels == 0).sum()}, Class 1: {(train_labels == 1).sum()}")
        
        return train_idx, train_labels
    
    def get_test_data(self):
        """获取测试数据"""
        test_idx = self.test_mask

        # 确保 test_idx 是一维数组
        if len(test_idx.shape) > 1:
            test_idx = test_idx.ravel()

        return test_idx
    
    def to_torch(self, device='cpu'):
        """转换为PyTorch张量"""
        self.features = torch.FloatTensor(self.x).to(device)
        self.labels = torch.LongTensor(self.y).to(device)
        return self


class BatchDataLoader:
    """批量数据加载器"""
    
    def __init__(self, dataset, batch_size=1024, shuffle=True):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        
    def get_batches(self, node_indices):
        """生成批次"""
        if self.shuffle:
            np.random.shuffle(node_indices)
        
        num_batches = (len(node_indices) + self.batch_size - 1) // self.batch_size
        
        for i in range(num_batches):
            start = i * self.batch_size
            end = min((i + 1) * self.batch_size, len(node_indices))
            batch_nodes = node_indices[start:end]
            yield batch_nodes, num_batches
