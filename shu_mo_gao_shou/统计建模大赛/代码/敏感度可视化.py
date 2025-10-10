import matplotlib.pyplot as plt

# ALPHA 敏感性分析结果
alpha_values = [0.5, 1.0, 1.5, 2.0]
alpha_results = [5493.8,3323.6,3368.0,3431.6]

# BETA 敏感性分析结果
beta_values = [0.5, 1.0, 1.5, 2.0]
beta_results = [3751.2, 3394.0, 3380.8, 3387.8]

# RHO 敏感性分析结果
rho_values = [0.3, 0.5, 0.7, 1.0]
rho_results = [3412.6, 3394.6, 3391.2, 3303.0]


# 绘制 ALPHA 敏感性分析图
plt.figure(figsize=(10, 6))

# ALPHA 图
plt.subplot(2, 2, 1)
plt.plot(alpha_values, alpha_results, marker='o', label='ALPHA')
plt.xlabel('ALPHA')
plt.ylabel('Average Path Length')
plt.title('Sensitivity Analysis of ALPHA')
plt.grid(True)

# BETA 图
plt.subplot(2, 2, 2)
plt.plot(beta_values, beta_results, marker='o', label='BETA')
plt.xlabel('BETA')
plt.ylabel('Average Path Length')
plt.title('Sensitivity Analysis of BETA')
plt.grid(True)

# RHO 图
plt.subplot(2, 2, 3)
plt.plot(rho_values, rho_results, marker='o', label='RHO')
plt.xlabel('RHO')
plt.ylabel('Average Path Length')
plt.title('Sensitivity Analysis of RHO')
plt.grid(True)



# 显示图形
plt.tight_layout()
plt.show()
