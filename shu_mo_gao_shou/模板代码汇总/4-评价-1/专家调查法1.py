import matplotlib.pyplot as plt

# 专家评分数据
expert_ratings = [8, 9, 7, 6, 8, 9, 8, 7, 9, 8]

# 计算平均评分
average_rating = sum(expert_ratings) / len(expert_ratings)

# 可视化展示
plt.bar(range(len(expert_ratings)), expert_ratings)
plt.axhline(average_rating, color='red', linestyle='--')  # 添加平均评分的水平线
plt.xlabel("Expert")
plt.ylabel("Rating")
plt.title("Expert Ratings for Product Quality")
plt.xticks(range(len(expert_ratings)))
plt.ylim(min(expert_ratings) - 1, max(expert_ratings) + 1)
plt.show()