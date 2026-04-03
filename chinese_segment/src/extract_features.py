from typing import List, Tuple, Dict
from pathlib import Path


def char_features(chars: List[str], i: int) -> List[str]:
    """返回位置 i 的特征字符串列表。

    特征包括：前一个字符、当前字符、下一个字符。句子边界使用特殊标记。
    """
    prev = chars[i - 1] if i - 1 >= 0 else '<BOS>'
    curr = chars[i]
    nex = chars[i + 1] if i + 1 < len(chars) else '<EOS>'
    return [f'P={prev}', f'C={curr}', f'N={nex}']


def build_feature_map(sentences: List[Tuple[List[str], List[str]]]) -> Dict[str, int]:
    """从带标注的句子集合构建特征到 id 的映射。

    输入：sentences 为 (chars_list, labels_list) 的列表。
    返回：一个字典，将特征字符串映射为整数 id（从 0 开始）。
    """
    feat_set = {}
    for chars, _ in sentences:
        for i in range(len(chars)):
            for f in char_features(chars, i):
                if f not in feat_set:
                    feat_set[f] = None
    # 分配 id
    feature2id = {f: idx for idx, f in enumerate(sorted(feat_set.keys()))}
    return feature2id


def sentences_to_feature_ids(sentences: List[Tuple[List[str], List[str]]], feature2id: Dict[str, int]) -> List[List[List[int]]]:
    """将句子转换为特征 id 列表。

    返回结构：句子列表 -> 每个位置的特征 id 列表。
    """
    out = []
    for chars, _ in sentences:
        sentence_feats = []
        for i in range(len(chars)):
            feats = []
            for f in char_features(chars, i):
                if f in feature2id:
                    feats.append(feature2id[f])
            sentence_feats.append(feats)
        out.append(sentence_feats)
    return out


def save_feature_map(feature2id: Dict[str, int], path: str):
    """将 feature->id 映射保存到文件，每行 `feature<TAB>id`。"""
    p = Path(path)
    with p.open('w', encoding='utf-8') as f:
        for feat, idx in sorted(feature2id.items(), key=lambda x: x[1]):
            f.write(f"{feat}\t{idx}\n")


def load_feature_map(path: str) -> Dict[str, int]:
    """从文件加载 feature->id 映射（与 save_feature_map 对应）。"""
    p = Path(path)
    m = {}
    with p.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            feat, idx = line.split('\t')
            m[feat] = int(idx)
    return m


if __name__ == '__main__':
    # 测试示例：使用指定的两条句子构建特征映射并展示前几项
    sentences = [
        (['人', '们', '常', '说', '生', '活', '是', '一', '部', '教', '科', '书'], ['B', 'E', 'S', 'S', 'B', 'E', 'S', 'S', 'S', 'B', 'M', 'E']),
        (['而', '血', '与', '火', '的', '战', '争', '更', '是', '不', '可', '多', '得', '的', '教', '科', '书'], ['S', 'S', 'S', 'S', 'S', 'B', 'E', 'S', 'S', 'B', 'M', 'M', 'E', 'S', 'B', 'M', 'E'])
    ]

    feat2id = build_feature_map(sentences)
    print(f'构建特征数: {len(feat2id)}')

    feat_ids = sentences_to_feature_ids(sentences, feat2id)

    # 打印第一条句子前六个位置的详细信息
    print('\n第一条句子示例（字符 / 标签 / 特征字符串 -> 特征 id）:')
    chars, labs = sentences[0]
    for i in range(min(6, len(chars))):
        fstrs = char_features(chars, i)
        fids = [feat2id[f] for f in fstrs]
        print(f"{i}: {chars[i]} / {labs[i]} / {fstrs} -> {fids}")

    # 打印第二条句子末尾几个位置作为额外检查
    print('\n第二条句子末尾示例:')
    chars2, labs2 = sentences[1]
    for i in range(max(0, len(chars2)-4), len(chars2)):
        fstrs = char_features(chars2, i)
        fids = [feat2id[f] for f in fstrs]
        print(f"{i}: {chars2[i]} / {labs2[i]} / {fstrs} -> {fids}")