def diamond(n,m):
    for j in range(1,n+1):
        for i in range(1,m+1):
            space=m-i    #space表示有几个空格
            star=2*i-1   #star表示*的数量

            line = ' ' * space + '*' * star  # 构建每行的字符串
            print(line)
            #倒三角
        for i in range(m-1,0,-1):
            space = m - i  # space表示有几个空格
            star = 2 * i - 1  # star表示*的数量

            line2 = ' ' * space + '*' * star  # 构建每行的字符串
            print(line2)

# 测试函数

if __name__=='__main__':
    n=int(input('n='))
    m=int(input('m='))
    diamond(n,m)