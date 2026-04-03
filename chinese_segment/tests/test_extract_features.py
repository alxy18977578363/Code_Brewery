from src import extract_features as ef


def test_char_features_basic():
    chars = ['a', 'b', 'c']
    assert ef.char_features(chars, 0) == ['P=<BOS>', 'C=a', 'N=b']
    assert ef.char_features(chars, 1) == ['P=a', 'C=b', 'N=c']
    assert ef.char_features(chars, 2) == ['P=b', 'C=c', 'N=<EOS>']


def test_char_features_single():
    chars = ['x']
    assert ef.char_features(chars, 0) == ['P=<BOS>', 'C=x', 'N=<EOS>']


def test_build_feature_map_and_sentences_to_ids_consistency():
    sentences = [(['你', '好'], ['B', 'E'])]
    feat2id = ef.build_feature_map(sentences)
    # 每个位置至少有三个特征
    feats_ids = ef.sentences_to_feature_ids(sentences, feat2id)
    assert isinstance(feats_ids, list)
    assert len(feats_ids) == 1
    assert len(feats_ids[0]) == 2
    for pos in feats_ids[0]:
        assert isinstance(pos, list)
        assert len(pos) >= 1


def test_save_and_load_feature_map(tmp_path):
    sentences = [(['中', '国'], ['B', 'E'])]
    feat2id = ef.build_feature_map(sentences)
    p = tmp_path / 'feat_map.txt'
    ef.save_feature_map(feat2id, str(p))
    loaded = ef.load_feature_map(str(p))
    assert loaded == feat2id
