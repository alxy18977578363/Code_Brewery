import matplotlib.pyplot as plt

def calculate_growth_rate(current, previous):
    return (current - previous) / previous * 100

# 销售额数据
sales = [10000, 12000, 15000, 11000, 9000, 13000]

# 计算每个月的销售额变化百分比
growth_rates = []
for i in range(1, len(sales)):
    growth_rate = calculate_growth_rate(sales[i], sales[i-1])
    growth_rates.append(growth_rate)

# 可视化展示
months = [f"Month {i+1}" for i in range(len(growth_rates))]

plt.bar(months, growth_rates)
plt.xlabel("Month")
plt.ylabel("Growth Rate (%)")
plt.title("Sales Growth Rate")
plt.ylim(min(growth_rates) - 10, max(growth_rates) + 10)
plt.axhline(0, color='black', linestyle='--')  # 添加水平参考线
plt.show()