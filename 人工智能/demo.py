from kanren import var,run,eq,lall,membero
from kanren.constraints import neq

# 创建八皇后
def eight_queens():
    Queens = [var() for i in range(8)]
    value_range = lall(membero(q,range(8)) for q in Queens)     # 每个皇后的列表在0-7之间
    no_a_column = lall(neq(q1,q2) for i,q1 in enumerate(Queens) for j,q2 in enumerate(Queens) if i < j )  # 不同列

    # 不在一个斜线上
    no_a_diagonal = lall(neq(abs(q1-q2), abs(i-j)) for i,q1 in enumerate(Queens) for j,q2 in enumerate(Queens) if i < j )

    # 合并所有约束为单一目标
    all_constraints = lall(value_range, no_a_column)
    all_constraints = lall(all_constraints, no_a_diagonal)

    # 只获取第一个解（参数0表示无限制数量，取第一个结果）
    return run(1, Queens, all_constraints)


if __name__ == '__main__':
    result = eight_queens()
    print(result)