from kanren import var,run,lall,membero
from kanren.constraints import neq

# 创建八皇后
def eight_queens(n):
	Queens = [var() for i in range(n)]
	value_range = lall(*(membero(q,range(n)) for q in Queens))  # 每个皇后的列表在0-7之间
	
	# 限制皇后不能在同一列
	no_a_column = lall(*(neq(q1,q2) for i,q1 in enumerate(Queens) for j,q2 in enumerate(Queens) if i < j ))  # 不同列

	# 合并所有约束为单一目标
	all_constraints = lall(value_range,no_a_column)

	# 只获取第一个解（参数0表示无限制数量，取第一个结果）
	return run(0, Queens, all_constraints)

if __name__ == '__main__':
	n = 6
	result = list(eight_queens(n))
	valid_result = []
	for i in range(len(result)):
		is_valid = True
		for j in range(0,n-1):
			for k in range(j+1,n):
				if abs(result[i][j] - result[i][k]) == abs(j-k):
					is_valid = False
					break
				if not is_valid:
					break
		if is_valid:
			valid_result.append(result[i])
print(valid_result)