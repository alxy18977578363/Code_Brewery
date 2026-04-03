import argparse
from pathlib import Path
import sys
import numpy as np

from extract_features import load_feature_map, char_features
from crf_model import LinearChainCRF


def load_trained_model(model_dir: Path):
    w_path = model_dir / 'W.npy'
    t_path = model_dir / 'T.npy'
    feat_path = model_dir / 'feat2id.txt'
    if not (w_path.exists() and t_path.exists() and feat_path.exists()):
        raise FileNotFoundError(f'Model files not found in {model_dir}. 请先运行训练脚本保存模型。')
    W = np.load(w_path)
    T = np.load(t_path)
    feat2id = load_feature_map(str(feat_path))
    model = LinearChainCRF(num_features=W.shape[0])
    # safety: check shapes
    if model.W.shape != W.shape:
        model.W = W.copy()
    else:
        model.W[:] = W
    if model.T.shape != T.shape:
        model.T = T.copy()
    else:
        model.T[:] = T
    return model, feat2id


def sentence_to_feat_ids(sentence: str, feat2id: dict):
    chars = [c for c in sentence if not c.isspace()]
    sent_feats = []
    for i in range(len(chars)):
        fstrs = char_features(chars, i)
        fids = [feat2id[f] for f in fstrs if f in feat2id]
        sent_feats.append(fids)
    return chars, sent_feats


def labels_to_words(chars, labels):
    words = []
    buf = ''
    for ch, lab in zip(chars, labels):
        if lab == 'S':
            if buf:
                words.append(buf)
                buf = ''
            words.append(ch)
        elif lab == 'B':
            if buf:
                words.append(buf)
            buf = ch
        elif lab == 'M':
            buf += ch
        elif lab == 'E':
            buf += ch
            words.append(buf)
            buf = ''
        else:
            # 未知标签则当单字
            if buf:
                words.append(buf)
                buf = ''
            words.append(ch)
    if buf:
        words.append(buf)
    return words


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('text', nargs='?', help='要分词的句子，若省略则从标准输入读取')
    parser.add_argument('--model-dir', default='model', help='模型目录，包含 W.npy T.npy feat2id.txt')
    args = parser.parse_args()

    if args.text:
        text = args.text
    else:
        text = sys.stdin.read().strip()
    if not text:
        print('未提供输入句子。', file=sys.stderr)
        return

    model_dir = Path(args.model_dir)
    try:
        model, feat2id = load_trained_model(model_dir)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return

    chars, sent_feats = sentence_to_feat_ids(text, feat2id)
    if not chars:
        print('', end='')
        return

    pred_ids = model.viterbi(sent_feats)
    pred_labels = [LinearChainCRF.LABELS[i] for i in pred_ids]
    words = labels_to_words(chars, pred_labels)

    print(' '.join(words))


if __name__ == '__main__':
    main()
