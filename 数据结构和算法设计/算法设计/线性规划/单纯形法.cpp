#include<iostream>
#include<algorithm>
#include<cstring>
#include<cstdio>
#include<cmath>
#include <vector>
using namespace std;

const double eps = 1e-10;
enum
{
    mxn = 50, mxm = 50
}; // 适当调整大小

class Simplex
{
public:
    int n, m, t;
    double c[mxn];
    double a[mxm][mxn];
    int idx[mxn], idy[mxn];
    int st[mxn], top = 0;

    Simplex(int _m, int _n)
    {
        this->m = _m;
        this->n = _n;
        for (int i = 1; i <= n; i++) idx[i] = i; // 基变量
        for (int i = 1; i <= m; i++) idy[i] = i + n; // 非基变量
    }

    void set_objective(double ci[mxn])
    {
        for (int i = 1; i <= n; i++)
        {
            a[0][i] = -ci[i - 1]; // 第0行作为目标函数
        }
    }

    void set_co_matrix(double co_matrix[mxm][mxn])
    {
        for (int i = 1; i <= m; i++)
        {
            for (int j = 1; j <= n; j++)
            {
                a[i][j] = co_matrix[i - 1][j - 1];
            }
        }
    }

    void set_bi_matrix(double b_matrix[mxm])
    {
        for (int i = 1; i <= m; i++)
        {
            a[i][0] = b_matrix[i - 1]; // 第0列作为b矩阵
        }
        a[0][0] = 0;
    }

    int init_simplex()
    {
        while (1)
        {
            int i, x = 0, y = 0;
            for (i = 1; i <= m; i++)
            {
                if (a[i][0] < -eps && ((!x) || (rand() & 1)))
                {
                    x = i;
                }
            }
            if (!x) break;

            for (i = 1; i <= n; i++)
            {
                if (a[x][i] < -eps && ((!y) || (rand() & 1)))
                {
                    y = i;
                }
            }

            if (!y)
            {
                printf("Infeasible\n");
                return 0;
            }
            Pivot(x, y);
        }
        return 1;
    }

    void Pivot(int x, int y)
    {
        swap(idy[x], idx[y]);
        double tmp = a[x][y];
        a[x][y] = 1 / a[x][y];
        top = 0;

        for (int i = 0; i <= n; i++)
        {
            if (y != i) a[x][i] /= tmp;
        }

        for (int i = 0; i <= n; i++)
        {
            if ((y != i) && fabs(a[x][i]) > eps)
            {
                st[++top] = i;
            }
        }

        for (int i = 0; i <= m; i++)
        {
            if ((i == x) || (fabs(a[i][y]) < eps)) continue;

            for (int j = 1; j <= top; j++)
            {
                a[i][st[j]] -= a[x][st[j]] * a[i][y];
            }
            a[i][y] = -a[i][y] / tmp;
        }
    }

    int run()
    {
        int init = init_simplex();
        if (init == 0) return init;

        while (1)
        {
            int x = 0, y = 0;
            double mn = 1e15;

            for (int i = 1; i <= n; i++)
            {
                if (a[0][i] > eps)
                {
                    y = i;
                    break;
                }
            }
            if (!y) break;

            for (int i = 1; i <= m; i++)
            {
                if (a[i][y] > eps && (a[i][0] / a[i][y] < mn))
                {
                    mn = a[i][0] / a[i][y];
                    x = i;
                }
            }

            if (!x)
            {
                printf("Unbounded\n");
                return -1;
            }
            Pivot(x, y);
        }
        return 1;
    }

    pair<vector<double>, double> getans()
    {
        vector<double> x;
        double z = a[0][0];

        for (int i = 1; i <= n; i++) a[0][i] = 0;
        for (int i = 1; i <= m; i++)
        {
            if (idy[i] <= n) a[0][idy[i]] = a[i][0];
        }
        for (int i = 1; i <= n; i++)
        {
            x.push_back(a[0][i]);
        }
        return make_pair(x, z);
    }
};

int main()
{
    // 问题数据
    double b_matrix[mxm] = { -10000, -30000 }; // 注意这里是负号，因为原约束是≥
    double co_matrix[mxm][mxn] = {
        { -2, -7.5, -3 },    // 2x1 + 7.5x2 + 3x3 ≥ 10000 → -2x1 -7.5x2 -3x3 ≤ -10000
        { -20, -5, -10 }      // 20x1 + 5x2 + 10x3 ≥ 30000 → -20x1 -5x2 -10x3 ≤ -30000
    };
    double c_matrix[mxn] = { 1, 1, 1 }; // min z = x1 + x2 + x3

    Simplex simplex(2, 3); // 2个约束，3个变量
    simplex.set_objective(c_matrix);
    simplex.set_co_matrix(co_matrix);
    simplex.set_bi_matrix(b_matrix);

    int result = simplex.run();

    if (result == 1)
    {
        pair<vector<double>, double> rst = simplex.getans();
        cout << "最优解: z = " << rst.second << endl;
        cout << "x1 = " << rst.first[0] << endl;
        cout << "x2 = " << rst.first[1] << endl;
        cout << "x3 = " << rst.first[2] << endl;
    }
    else if (result == 0)
    {
        cout << "问题无可行解" << endl;
    }
    else
    {
        cout << "问题无界" << endl;
    }

    return 0;
}