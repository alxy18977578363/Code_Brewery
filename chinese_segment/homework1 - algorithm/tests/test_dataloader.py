from src import dataloader as dl
from pathlib import Path


def test_is_punct_char():
    assert dl.is_punct_char(',')
    assert dl.is_punct_char('。')
    assert not dl.is_punct_char('中')


def test_word_to_labelled_chars():
    assert dl.word_to_labelled_chars('') == []
    assert dl.word_to_labelled_chars('A') == [('A', 'S')]
    assert dl.word_to_labelled_chars('AB') == [('A', 'B'), ('B', 'E')]
    assert dl.word_to_labelled_chars('ABC') == [('A', 'B'), ('B', 'M'), ('C', 'E')]


def test_process_and_load_roundtrip(tmp_path):
    inp = tmp_path / 'raw.txt'
    out = tmp_path / 'proc.txt'
    # 包含引号、逗号与空格，验证分句与标签生成
    inp.write_text('"a bb ccc, d"\n', encoding='utf-8')
    dl.process_msr_training(inp, out)
    sents = dl.load_labelled_sentences(out)
    # 预期有两句：['a','b','b','c','c','c'] 与 ['d']
    assert len(sents) == 2
    chars1, labs1 = sents[0]
    assert ''.join(chars1) == 'abbccc'
    assert labs1 == ['S', 'B', 'E', 'B', 'M', 'E']
    chars2, labs2 = sents[1]
    assert ''.join(chars2) == 'd'
    assert labs2 == ['S']
