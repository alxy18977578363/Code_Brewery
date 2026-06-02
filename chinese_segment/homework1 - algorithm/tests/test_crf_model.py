import math
import numpy as np
import pytest
from src.crf_model import LinearChainCRF


def test_emissions_viterbi_and_nll_zero_weights():
    num_features = 4
    model = LinearChainCRF(num_features=num_features, seed=0)
    model.W = np.zeros_like(model.W)
    model.T = np.zeros_like(model.T)

    sent_feats = [[0], [1, 2], []]
    emis = model.emissions(sent_feats)
    assert emis.shape == (3, model.num_labels)
    assert np.allclose(emis, 0.0)

    path = model.viterbi(sent_feats)
    assert path == [0, 0, 0]

    nll, gW, gT = model.neg_log_likelihood_and_grads(sent_feats, [0, 0, 0])
    assert pytest.approx(nll, rel=1e-6) == math.log(model.num_labels)
    assert gW.shape == model.W.shape
    assert gT.shape == model.T.shape


def test_marginals_probability_sums():
    model = LinearChainCRF(num_features=3, seed=1)
    # 简单句子，每个位置有一个特征 id
    sent_feats = [[0], [1], [2]]
    p_unary, p_pair, logZ = model.marginals(sent_feats)
    # 每个位置的 unary 概率和为 1
    sums = p_unary.sum(axis=1)
    assert np.allclose(sums, np.ones_like(sums))
    # 每个时刻的 pair 概率和为 1
    for t in range(p_pair.shape[0]):
        assert np.isclose(p_pair[t].sum(), 1.0)


def test_neg_log_likelihood_gradients_finite():
    model = LinearChainCRF(num_features=5, seed=2)
    sent_feats = [[0, 1], [2], [3, 4]]
    labels = [0, 1, 2]
    nll, gW, gT = model.neg_log_likelihood_and_grads(sent_feats, labels)
    assert np.isfinite(nll)
    assert np.all(np.isfinite(gW))
    assert np.all(np.isfinite(gT))
