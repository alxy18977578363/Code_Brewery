#include <iostream>
using namespace std;

template<typename Tlist, typename T, size_t ROW, size_t COLUMN>
void make_list(Tlist(&my_list)[ROW][COLUMN], T X, int N)
{
    // 将X放入矩阵中
    my_list[1][COLUMN - 1] = X % 10;
    my_list[1][COLUMN - 2] = X / 10;  // 只考虑1-15的情况

    for (size_t i = 2; i <= (size_t)N; i++)
    {
        for (size_t j = 1; j <= COLUMN - 1; j++)
        {
            my_list[i][COLUMN - j] = my_list[i - 1][COLUMN - j] * X;  // 每一个都等于上面一个 * X
        }

        // 处理进位
        for (size_t j = COLUMN - 1; j > 0; j--)
        {
            if (my_list[i][j] >= 10)
            {
                my_list[i][j - 1] += my_list[i][j] / 10;  // 进位
                my_list[i][j] %= 10;  // 保持当前位的值
            }
        }
    }
}

int main()
{
    unsigned short cal[152][200] = { 0 };
    int N, X;
    cin >> N >> X;

    make_list(cal, X, N);

    // 计算结果并存入最后一行
    for (int j = 1; j < 200; j++)
    {
        for (int num = 1; num <= N; num++)
        {
            cal[151][j] += num * cal[num][j];  // 把数据加到最后一行
        }
    }

    // 处理最后一行的进位
    for (int j = 200 - 1; j > 0; j--)
    {
        if (cal[151][j] >= 10)
        {
            cal[151][j - 1] += cal[151][j] / 10;  // 进位
            cal[151][j] %= 10;  // 保持当前位的值
        }
    }

    // 输出结果，跳过前导0
    bool first_0 = true;
    for (int j = 1; j < 200; j++)
    {
        if (cal[151][j] != 0)
        {
            first_0 = false;
        }
        if (!first_0)
        {
            cout << (int)cal[151][j];
        }
    }

    // 如果输出的都是0
    if (first_0)
    {
        cout << 0;
    }
    cout << endl;

    return 0;
}
