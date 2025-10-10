/* 2351136 李盛鹏 大数据 */
#include <iostream>
using namespace std;

#include "16-b2-1.h" //16-b2-1.h在编译时会被替换，不需要提交，自己测试时可以任意改动

class matrix
{
private:
	int value[ROW][COL];
	//除此之外不允许再添加数据成员
public:
	matrix(const int(*p)[COL]);	//构造函数，用数组初始化矩阵

#if OPERATOR_IS_MENBER_FUNCTION
	//给出+的成员函数实现方式的声明
	matrix operator+(const matrix& other);
#else
	//给出+的友元函数实现方式的声明
	friend matrix operator+(const matrix& m1, const matrix& m2);
#endif

	/* ----根据需要添加其它成员函数的定义和友元函数的声明，数量不限---- */
	matrix();
	matrix(const matrix& m);
	friend ostream& operator<<(ostream& out, const matrix& m);		 // 重载输入输出运算符
	friend istream& operator>>(istream& in, matrix& m);
};

/* ---- 给出成员函数的体外实现/友元函数的实现，其中+的实现有成员和友元两种形式，要求放在下面的预编译中 ---- */
matrix::matrix(const int(*p)[COL])
{
	for (int row = 0; row < ROW; ++row)
	{
		for (int col = 0; col < COL; ++col)
		{
			value[row][col] = p[row][col];
		}
	}
}

matrix::matrix()
{
	for (int row = 0; row < ROW; row++)
	{
		for (int col = 0; col < COL; col++)
		{
			value[row][col] = 0;
		}
	}
}

matrix:: matrix(const matrix& m)
{
	for (int row = 0; row < ROW; row++)
	{
		for (int col = 0; col < COL; col++)
		{
			value[row][col] = m.value[row][col];
		}
	}
}

#if OPERATOR_IS_MENBER_FUNCTION
//给出+的成员函数方式的体外实现
matrix matrix::operator+(const matrix& other)
{
	matrix result;		// 初始化一个二维数组
	for (int row = 0; row < ROW; row++)
	{
		for (int col = 0; col < COL; col++)
		{
			result.value[row][col] = value[row][col] + other.value[row][col];
		}
	}

	return result;
}
#else
//给出+的友元函数方式的体外实现
matrix operator+(const matrix& m1, const matrix& m2)
{
	matrix result; // 初始化为全0
	for (int i = 0; i < ROW; ++i)
	{
		for (int j = 0; j < COL; ++j)
		{
			result.value[i][j] = m1.value[i][j] + m2.value[i][j];
		}
	}
	return result;
}
#endif

// 重载输出运算符
ostream& operator<<(ostream& out, const matrix& m)
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

istream& operator>>(istream &in,matrix&m)
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

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：main函数不准动
***************************************************************************/
int main()
{
	//	int a[ROW][COL] = { { 1,2,3 },{ 4,5,6 } };
	//	int b[ROW][COL] = { { 2,4,6 },{ 3,6,9 } };
	//   a/b两个二维数组具体见16-b2-1.h，作业检查时会被替换

	matrix m1(a), m2(b), m3; //m3的初值为全0

	/* 下面为定值测试 */
	cout << "初始矩阵m1的值" << endl;
	cout << m1 << endl;
	cout << "初始矩阵m2的值" << endl;
	cout << m2 << endl;

	m3 = m1 + m2;
	cout << "相加后矩阵m3的值" << endl;
	cout << m3 << endl;

	cout << "------------------" << endl;

	/* 下面为键盘输入测试 */
	cout << "请输入初始矩阵m1" << endl;
	cin >> m1;
	cout << "请输入初始矩阵m2" << endl;
	cin >> m2;

	cout << "初始矩阵m1的值" << endl;
	cout << m1 << endl;
	cout << "初始矩阵m2的值" << endl;
	cout << m2 << endl;
	cout << "相加后矩阵m3的值" << endl;
	cout << (m3 = m1 + m2) << endl;

	return 0;
}
