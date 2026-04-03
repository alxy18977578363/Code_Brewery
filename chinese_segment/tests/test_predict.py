import sys
from pathlib import Path
import numpy as np


def _import_predict_from_src():
    # 将 src 目录加入 path，然后以顶级模块方式导入 predict
    root = Path(__file__).resolve().parents[1]
    src_dir = root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    import predict
    return predict


def test_labels_to_words():
    predict = _import_predict_from_src()
    chars = ['你', '好', '世']
    labs = ['B', 'E', 'S']
    words = predict.labels_to_words(chars, labs)
    assert words == ['你好', '世']


def test_sentence_to_feat_ids_and_load_trained_model(tmp_path):
    predict = _import_predict_from_src()
    # 使用 src.extract_features 构建 feat2id
    from extract_features import build_feature_map, save_feature_map
    sentences = [(['我', '是'], ['B', 'E'])]
    feat2id = build_feature_map(sentences)

    model_dir = tmp_path / 'model'
    model_dir.mkdir()
    # 保存简单的 W 和 T
    W = np.zeros((len(feat2id), 4))
    T = np.zeros((4, 4))
    np.save(model_dir / 'W.npy', W)
    np.save(model_dir / 'T.npy', T)
    save_feature_map(feat2id, str(model_dir / 'feat2id.txt'))

    model, loaded_map = predict.load_trained_model(model_dir)
    assert np.array_equal(model.W, W)
    assert loaded_map == feat2id

    # sentence_to_feat_ids 返回字符与特征 id 列表
    chars, sent_feats = predict.sentence_to_feat_ids('我是', feat2id)
    assert chars == ['我', '是']
    assert isinstance(sent_feats, list)
