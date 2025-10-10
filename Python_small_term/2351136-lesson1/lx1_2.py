def tablem(n):
    for i in range(1, n + 1):
        for j in range(1, i + 1):
            # 打印乘积，使用格式化字符串使输出整齐
            print(f"{j * i:4}", end=" ")  # 每个乘积占4个字符宽度
        print()  # 每行结束后换行

# 测试程序
if __name__ == '__main__':
    n = int(input('n='))
    tablem(n)