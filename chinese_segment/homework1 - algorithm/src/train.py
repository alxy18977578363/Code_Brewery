import argparse
from pathlib import Path
import numpy as np

from dataloader import prepare_dataset
from extract_features import build_feature_map, sentences_to_feature_ids, save_feature_map
from crf_model import LinearChainCRF


def save_model(model: LinearChainCRF, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / 'W.npy', model.W)
    np.save(out_dir / 'T.npy', model.T)


def load_small_dataset(max_sentences=None):
    sentences = prepare_dataset()
    if max_sentences is not None:
        sentences = sentences[:max_sentences]
    return sentences


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--lr', type=float, default=0.1)
    parser.add_argument('--max-sents', type=int, default=2000)
    parser.add_argument('--model-dir', type=str, default='model')
    args = parser.parse_args()

    print('加载并准备数据...')
    sentences = load_small_dataset(max_sentences=args.max_sents)
    print(f'句子数: {len(sentences)}')

    print('构建特征字典...')
    feat2id = build_feature_map(sentences)
    print(f'特征数量: {len(feat2id)}')

    print('转换为特征 id...')
    feats_ids = sentences_to_feature_ids(sentences, feat2id)
    labels_ids = [[LinearChainCRF.LAB2IDX[l] for l in labs] for _, labs in sentences]

    print('初始化模型并训练...')
    model = LinearChainCRF(num_features=len(feat2id))
    model.fit(feats_ids, labels_ids, epochs=args.epochs, lr=args.lr, l2=1e-4)

    out_dir = Path(args.model_dir)
    print(f'保存模型到 {out_dir} ...')
    save_model(model, out_dir)
    save_feature_map(feat2id, str(out_dir / 'feat2id.txt'))

    print('训练完成。样例预测（前5句）:')
    for feats, (chars, labs) in zip(feats_ids[:5], sentences[:5]):
        pred = model.viterbi(feats)
        pred_labels = [LinearChainCRF.LABELS[p] for p in pred]
        print(''.join(chars))
        print('gold :', ''.join(labs))
        print('pred :', ''.join(pred_labels))
        print()


if __name__ == '__main__':
    main()
