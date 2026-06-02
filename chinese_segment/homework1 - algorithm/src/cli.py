import subprocess
import sys
import shlex


def run(cmd):
    print('> ' + cmd)
    proc = subprocess.run(cmd, shell=True)
    return proc.returncode


def menu():
    prompt = '''
CRF 中文分词演示 CLI
请选择操作：
1) 预处理训练数据（生成 data/train/msr_training_processed.utf8）
2) 训练模型（保存到 model/）
3) 用已训练模型分词（预测）
4) 运行全部示例（预处理 -> 训练（小规模） -> 预测示例句）
0) 退出
请输入编号：'''
    while True:
        choice = input(prompt).strip()
        if choice == '1':
            run('python src/dataloader.py')
        elif choice == '2':
            epochs = input('训练轮数（默认 10）：').strip() or '10'
            max_sents = input('最大句数（用于快速演示，0 表示全部，默认 2000）：').strip() or '2000'
            cmd = f'python src/train.py --epochs {shlex.quote(epochs)} --max-sents {shlex.quote(max_sents)} --model-dir model'
            run(cmd)
        elif choice == '3':
            sent = input('请输入要分词的句子：').strip()
            if not sent:
                print('输入为空，返回菜单')
                continue
            cmd = f'python src/predict.py {shlex.quote(sent)}'
            run(cmd)
        elif choice == '4':
            # 预处理
            if run('python src/dataloader.py') != 0:
                print('预处理失败，终止')
                continue
            # 训练（小规模示例）
            if run('python src/train.py --epochs 5 --lr 0.5 --max-sents 200 --model-dir model') != 0:
                print('训练失败，终止')
                continue
            # 预测示例句
            example = '我爱自然语言处理'
            run(f'python src/predict.py {shlex.quote(example)}')
        elif choice == '0':
            print('退出')
            break
        else:
            print('无效选择，请重试')


if __name__ == '__main__':
    try:
        menu()
    except KeyboardInterrupt:
        sys.exit(0)
