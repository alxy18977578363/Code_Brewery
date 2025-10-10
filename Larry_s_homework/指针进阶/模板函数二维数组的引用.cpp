/* 大数据 2351136 李盛鹏 */
#include <iostream>
#include <iomanip>
using namespace std;

const char* sp = "=====================================";

/***************************************************************************
  函数名称：matrix_print
  功    能：
  输入参数：
  返 回 值：
  说    明：每个数字宽度为8，右对齐
***************************************************************************/
template<typename T,size_t row,size_t column>
void matrix_print(const char*p,T (&matrix)[row][column])	//将...替换为相应内容
{
	if (p != NULL)
	{
		cout << p << endl;
	}

	for (size_t i = 0; i < row; i++)
	{
		for (size_t j = 0; j < column; j++)
		{
			cout << setw(8) << matrix[i][j];
		}
		cout << endl;
	}
	return;
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
template<typename T1,typename T2,typename TResult, size_t row, size_t column>
void matrix_addition(TResult(&add_matrix)[row][column], T1(&a_matrix)[row][column], T2(&b_matrix)[row][column])	//将...替换为相应内容
{
	/* 按需增加内容 */
	cout << "源矩阵1 : 行=" << row << " 列=" << column << " 占用空间=" << sizeof(T1) * column * row << "字节" << endl;
	cout << "源矩阵2 : 行=" << row << " 列=" << column << " 占用空间=" << sizeof(T2) * column * row << "字节" << endl;
	cout << "和矩阵  : 行=" << row << " 列=" << column << " 占用空间=" << sizeof(TResult) * column * row << "字节" << endl;

	for (size_t i = 0; i < row; i++)
	{
		for (size_t j = 0; j < column; j++)
		{
			add_matrix[i][j] = static_cast<TResult>(a_matrix[i][j] + b_matrix[i][j]);
		}
	}

	return;
}


/***************************************************************************
  函数名称：matrix_multiplication
  功    能：将两个矩阵相乘
  输入参数：T (& mu_matrix)[row1][column], T (& a_matrix)[column][row2], T (& b_matrix)[row1][row2]
  返 回 值：
  说    明：
***************************************************************************/
// 矩阵乘法模板，允许不同数据类型
template<typename T1, typename T2, typename TResult, size_t row1, size_t column, size_t row2>
void matrix_multiplication(TResult(&mu_matrix)[row1][row2], const T1(&a_matrix)[row1][column], const T2(&b_matrix)[column][row2])
{
	cout << "源矩阵1 : 行=" << row1 << " 列=" << column << " 占用空间=" << sizeof(T1) * column * row1 << "字节" << endl;
	cout << "源矩阵2 : 行=" << column << " 列=" << row2 << " 占用空间=" << sizeof(T2) * column * row2 << "字节" << endl;
	cout << "积矩阵  : 行=" << row1 << " 列=" << row2 << " 占用空间=" << sizeof(TResult) * row1 * row2 << "字节" << endl;

	for (size_t i = 0; i < row1; ++i)
	{
		for (size_t j = 0; j < row2; ++j)
		{
			mu_matrix[i][j] = 0;
			for (size_t k = 0; k < column; ++k)
			{
				mu_matrix[i][j] += static_cast<TResult>((a_matrix[i][k]) * (b_matrix[k][j]));
			}
		}
	}
}
/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：main函数不准更改
***************************************************************************/
int main()
{
	int t1[3][4] = {
		{1,2,3,4},
		{5,6,7,8},
		{9,10,11,12}
	};
	int t2[3][4] = {
		{12,11,10,9},
		{8,7,6,5},
		{4,3,2,1}
	};
	int t3[4][2] = {
		{1, 2},
		{3, 4},
		{5, 6},
		{7, 8}
	};
	int t_add[3][4], t_mul[3][2];

	cout << sp << endl;
	matrix_print("加法运算，源矩阵1：", t1);
	matrix_print("加法运算，源矩阵2：", t2);
	matrix_addition(t_add, t1, t2);	//将t1和t2的和放入t_add中，人工保证三个矩阵行列一致
	matrix_print("加法运算，和矩阵 ：", t_add);
	cout << sp << endl;
	matrix_print("乘法运算，源矩阵1：", t1);
	matrix_print("乘法运算，源矩阵2：", t3);
	matrix_multiplication(t_mul, t1, t3);	//将t1和t2的和放入t_add中，人工保证三个矩阵行列一致
	matrix_print("乘法运算，积矩阵 ：", t_mul);
	cout << sp << endl;

	double d1[2][4] = {
		{1.1, 2.2, 3.3, 4.4},
		{5.5 ,6.6, 7.7, 8.8}
	};
	double d2[2][4] = {
		{8.8, 7.7, 6.6, 5.5},
		{4.4, 3.3, 2.2, 1.1}
	};
	double d_add[2][4];
	/* 不要问为什么矩阵乘法数据类型不同，故意的 */
	float f3[4][3] = {
		{12.12f, 11.11f, 10.10f},
		{9.9f, 8.8f, 7.7f},
		{6.6f, 5.5f, 4.4f},
		{3.3f, 2.2f, 1.1f}
	};
	int i_mul[2][3];

	matrix_print("加法运算，源矩阵1：", d1);
	matrix_print("加法运算，源矩阵2：", d2);
	matrix_addition(d_add, d1, d2);	//将d1和d2的和放入d_add中，人工保证三个矩阵行列一致
	matrix_print("加法运算，和矩阵 ：", d_add);
	cout << sp << endl;
	matrix_print("乘法运算，源矩阵1：", d1);
	matrix_print("乘法运算，源矩阵2：", f3);
	matrix_multiplication(i_mul, d1, f3);	//将t1和t2的和放入t_add中，人工保证三个矩阵行列一致
	matrix_print("乘法运算，积矩阵 ：", i_mul);
	cout << sp << endl;

	return 0;
}