import random
import numpy as np

# 计算纳什均衡策略
def calculate_nash_equilibrium():
    # Jack和Rose最佳出正面的概率
    return 3 / 8, 3 / 8

# 获取最佳策略
jack_probability_heads, rose_probability_heads = calculate_nash_equilibrium()
print(f"Jack最佳出正面的概率: {jack_probability_heads:.2f}")
print(f"Rose最佳出正面的概率: {rose_probability_heads:.2f}")

# 定义收益计算函数
def game_result(jack_choices, rose_choices):
    # 预先初始化收益数组
    results = np.zeros(jack_choices.shape[0], dtype=int)

    # 计算结果
    results[(jack_choices == 'H') & (rose_choices == 'H')] += 3  # Jack赢得3元
    results[(jack_choices == 'T') & (rose_choices == 'T')] += 1  # Jack赢得1元
    results[(jack_choices == 'H') & (rose_choices == 'T')] -= 2  # Jack输掉2元
    results[(jack_choices == 'T') & (rose_choices == 'H')] -= 2  # Jack输掉2元

    return results

# 模拟100万次PK
n_rounds = 1000000
jack_choices = np.random.choice(['H', 'T'], size=n_rounds, p=[jack_probability_heads, 1 - jack_probability_heads])
rose_choices = np.random.choice(['H', 'T'], size=n_rounds, p=[rose_probability_heads, 1 - rose_probability_heads])

# 计算每个结果
results = game_result(jack_choices, rose_choices)

# 统计结果
jack_wins = np.sum(results > 0)
rose_wins = np.sum(results < 0)
jack_balance = np.sum(results)

# 输出最终结果
print(f"Jack的胜利次数: {jack_wins}")
print(f"Rose的胜利次数: {rose_wins}")
print(f"Jack的最终余额: {jack_balance}元")