import numpy as np
from typing import List, Tuple


def logsumexp(a, axis=None):
    a_max = np.max(a, axis=axis, keepdims=True)
    res = a_max + np.log(np.sum(np.exp(a - a_max), axis=axis, keepdims=True))
    if axis is None:
        return res.squeeze()
    return res.squeeze()


class LinearChainCRF:
    """最简单的线性链 CRF（NumPy 实现）。

    特征表示：每个特征 id 对应一个长度为 num_labels 的权重向量，emission 为这些向量之和。
    转移矩阵 shape=(num_labels, num_labels)，表示从 prev -> cur 的转移分数。
    标签顺序：B, M, E, S（固定为 4 类）。
    """

    LABELS = ['B', 'M', 'E', 'S']
    LAB2IDX = {l: i for i, l in enumerate(LABELS)}

    def __init__(self, num_features: int, num_labels: int = 4, seed: int = 1):
        rng = np.random.RandomState(seed)
        # 小的随机初始化有助于训练
        self.num_features = num_features
        self.num_labels = num_labels
        self.W = rng.normal(scale=0.1, size=(num_features, num_labels))
        self.T = rng.normal(scale=0.1, size=(num_labels, num_labels))

    def emissions(self, sent_feat_ids: List[List[int]]) -> np.ndarray:
        # sent_feat_ids: list length L, each is list of feature ids
        L = len(sent_feat_ids)
        emis = np.zeros((L, self.num_labels))
        for i, fids in enumerate(sent_feat_ids):
            if not fids:
                continue
            # sum W[fid] over features
            emis[i] = np.sum(self.W[fids, :], axis=0)
        return emis

    def score_path(self, labels: List[int], emis: np.ndarray) -> float:
        # emission scores + transition scores
        s = 0.0
        for i, y in enumerate(labels):
            s += emis[i, y]
            if i > 0:
                s += self.T[labels[i - 1], y]
        return s

    def _forward_logZ(self, emis: np.ndarray) -> Tuple[np.ndarray, float]:
        L = emis.shape[0]
        alpha = np.zeros((L, self.num_labels))
        alpha[0] = emis[0]
        for t in range(1, L):
            # alpha[t, b] = logsum_a alpha[t-1,a] + T[a,b] + emis[t,b]
            mat = alpha[t - 1][:, None] + self.T
            alpha[t] = logsumexp(mat, axis=0) + emis[t]
        logZ = logsumexp(alpha[-1])
        return alpha, float(logZ)

    def _backward(self, emis: np.ndarray) -> np.ndarray:
        L = emis.shape[0]
        beta = np.zeros((L, self.num_labels))
        beta[-1] = 0.0
        for t in range(L - 2, -1, -1):
            # beta[t,a] = logsum_b T[a,b] + emis[t+1,b] + beta[t+1,b]
            mat = self.T + (emis[t + 1] + beta[t + 1])[None, :]
            beta[t] = logsumexp(mat, axis=1)
        return beta

    def marginals(self, sent_feat_ids: List[List[int]]) -> Tuple[np.ndarray, np.ndarray, float]:
        emis = self.emissions(sent_feat_ids)
        alpha, logZ = self._forward_logZ(emis)
        beta = self._backward(emis)
        L = emis.shape[0]
        # unary marginals
        log_p_unary = alpha + beta - logZ
        p_unary = np.exp(log_p_unary)

        # pairwise marginals for positions 1..L-1
        p_pair = np.zeros((L - 1, self.num_labels, self.num_labels))
        for t in range(1, L):
            # log p(y_{t-1}=a, y_t=b) proportional to alpha[t-1,a] + T[a,b] + emis[t,b] + beta[t,b] - logZ
            log_pair = alpha[t - 1][:, None] + self.T + emis[t][None, :] + beta[t][None, :] - logZ
            p_pair[t - 1] = np.exp(log_pair)

        return p_unary, p_pair, logZ

    def neg_log_likelihood_and_grads(self, sent_feat_ids: List[List[int]], labels: List[int]) -> Tuple[float, np.ndarray, np.ndarray]:
        emis = self.emissions(sent_feat_ids)
        alpha, logZ = self._forward_logZ(emis)
        score = self.score_path(labels, emis)
        nll = logZ - score

        # empirical counts
        emp_W = np.zeros_like(self.W)
        emp_T = np.zeros_like(self.T)
        for i, y in enumerate(labels):
            for f in sent_feat_ids[i]:
                emp_W[f, y] += 1.0
            if i > 0:
                emp_T[labels[i - 1], y] += 1.0

        # expected counts from marginals
        p_unary, p_pair, _ = self.marginals(sent_feat_ids)
        exp_W = np.zeros_like(self.W)
        exp_T = np.zeros_like(self.T)
        L = len(sent_feat_ids)
        for i in range(L):
            for f in sent_feat_ids[i]:
                exp_W[f] += p_unary[i]
        for t in range(L - 1):
            exp_T += p_pair[t]

        # gradient of nll = expected - empirical
        grad_W = exp_W - emp_W
        grad_T = exp_T - emp_T
        return float(nll), grad_W, grad_T

    def viterbi(self, sent_feat_ids: List[List[int]]) -> List[int]:
        emis = self.emissions(sent_feat_ids)
        L = emis.shape[0]
        dp = np.zeros((L, self.num_labels))
        bp = np.zeros((L, self.num_labels), dtype=int)
        dp[0] = emis[0]
        for t in range(1, L):
            for b in range(self.num_labels):
                scores = dp[t - 1] + self.T[:, b]
                best_prev = np.argmax(scores)
                dp[t, b] = scores[best_prev] + emis[t, b]
                bp[t, b] = best_prev
        best_last = int(np.argmax(dp[-1]))
        path = [0] * L
        path[-1] = best_last
        for t in range(L - 1, 0, -1):
            path[t - 1] = int(bp[t, path[t]])
        return path

    def fit(self, dataset_feats: List[List[List[int]]], dataset_labels: List[List[int]], epochs: int = 10, lr: float = 0.1, l2: float = 0.0, verbose: bool = True):
        for epoch in range(1, epochs + 1):
            total_nll = 0.0
            for feats, labs in zip(dataset_feats, dataset_labels):
                nll, gW, gT = self.neg_log_likelihood_and_grads(feats, labs)
                # update (gradient descent on negative log-likelihood)
                self.W -= lr * (gW + l2 * self.W)
                self.T -= lr * (gT + l2 * self.T)
                total_nll += nll
            if verbose:
                print(f'Epoch {epoch}: NLL={total_nll:.4f}')


if __name__ == '__main__':
    # 简单演示：使用两条小句子训练几轮并解码
    import extract_features as ef

    sentences = [
        (['人', '们', '常', '说', '生', '活', '是', '一', '部', '教', '科', '书'], ['B', 'E', 'S', 'S', 'B', 'E', 'S', 'S', 'S', 'B', 'M', 'E']),
        (['而', '血', '与', '火', '的', '战', '争', '更', '是', '不', '可', '多', '得', '的', '教', '科', '书'], ['S', 'S', 'S', 'S', 'S', 'B', 'E', 'S', 'S', 'B', 'M', 'M', 'E', 'S', 'B', 'M', 'E'])
    ]

    feat2id = ef.build_feature_map(sentences)
    feats_ids = ef.sentences_to_feature_ids(sentences, feat2id)
    labs_ids = [[LinearChainCRF.LAB2IDX[l] for l in lab_seq] for _, lab_seq in sentences]

    model = LinearChainCRF(num_features=len(feat2id))
    model.fit(feats_ids, labs_ids, epochs=30, lr=0.5, l2=1e-4)

    print('\n训练后解码结果:')
    for feats, (chars, labs) in zip(feats_ids, sentences):
        pred = model.viterbi(feats)
        pred_labels = [LinearChainCRF.LABELS[p] for p in pred]
        print('chars:', ''.join(chars))
        print('gold :', ''.join(labs))
        print('pred :', ''.join(pred_labels))
        print()
