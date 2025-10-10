/* 2351136 李盛鹏 大数据 */
#include <iostream>
#include <string>
using namespace std;

template<typename T, int ROW, int COL>
class matrix
{
private:
    T value[ROW][COL];

public:
    // 默认构造函数
    matrix()
    {

        for (int i = 0; i < ROW; ++i)
        {
            for (int j = 0; j < COL; ++j)
            {
                value[i][j] = T(); // 初始化为类型T的默认值
            }
        }
    }

    // 输入运算符重载
    friend istream& operator>>(istream& in, matrix& m)
    {
        for (int i = 0; i < ROW; ++i)
        {
            for (int j = 0; j < COL; ++j)
            {
                in >> m.value[i][j];
            }
        }
        return in;
    }

    // 输出运算符重载
    friend ostream& operator<<(ostream& out, const matrix& m)
    {
        for (int i = 0; i < ROW; ++i)
        {
            for (int j = 0; j < COL; ++j)
            {
                out << m.value[i][j] << " ";
            }
            out << endl;
        }
        return out;
    }

    // 加法运算符重载
    friend matrix operator+(const matrix& m1, const matrix& m2)
    {
        matrix<T, ROW, COL> result; // 创建一个结果矩阵

        for (int i = 0; i < ROW; ++i)
        {
            for (int j = 0; j < COL; ++j)
            {
                result.value[i][j] = m1.value[i][j] + m2.value[i][j]; // 对应元素相加
            }
        }

        return result; // 返回结果矩阵
    }
};



