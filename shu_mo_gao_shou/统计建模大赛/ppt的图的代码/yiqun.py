import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'SimHei'  # 替换为你选择的字体
# 迭代次数
iterations = np.arange(1, 301)

# 每条曲线的配置参数
curve_configs = [
    {"final": 3300, "power": 0.6, "early_noise": 40, "mid_noise": 20, "late_noise": 8, "slowdown": 150},
    {"final": 4700, "power": 0.4, "early_noise": 50, "mid_noise": 25, "late_noise": 12, "slowdown": 190},
    {"final": 3900, "power": 0.5, "early_noise": 60, "mid_noise": 15, "late_noise": 10, "slowdown": 180},
    {"final": 4400, "power": 0.7, "early_noise": 30, "mid_noise": 18, "late_noise": 6, "slowdown": 170},
]

# 生成每条路径曲线
curves = []

for config in curve_configs:
    final_value = config["final"]
    slowdown = config["slowdown"]
    curve = []
    for i in iterations:
        if i < slowdown:
            value = final_value + 3000 / (i ** config["power"]) + np.random.normal(0, config["early_noise"])
        elif i < slowdown + 30:
            value = final_value + 500 / (i - slowdown + 1) + np.random.normal(0, config["mid_noise"])
        else:
            value = final_value + np.random.normal(0, config["late_noise"])
        curve.append(value)
    curves.append(curve)

# 绘图
plt.figure(figsize=(12, 6))
colors = ['blue', 'green', 'orange', 'red']
labels = [f'周期 {i+1}' for i in range(4)]

for i in range(4):
    plt.plot(iterations, curves[i], label=labels[i], color=colors[i])

plt.xlabel('迭代次数')
plt.ylabel('路径长度')
plt.title('蚁群算法路径长度变化趋势（多阶段非平行曲线）')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
