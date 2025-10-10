/* 2351136 李盛鹏 大数据 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include<math.h>

double definite_integration(double (*fun)(double), double low, double high, int n)
{
	if (n <= 0)
		return 0;
	double sum = 0.0;
	double dx = (high - low) / n;
	for (int i = 1; i <= n; i++)
	{
		sum += fun(low + i * dx) * dx; 
	}
	return sum;
}

int main()
{
	int n;
	double low, high, value;
	// 计算 sin(x) 的积分
	printf("请输入sinxdx的下限、上限及区间划分数量\n");
	scanf("%lg %lg %d", &low, &high, &n);
	value = definite_integration(sin, low, high, n);
	printf("sinxdx[%g~%g/n=%d] : %g\n", low, high, n, value);

	printf("请输入cosxdx的下限、上限及区间划分数量\n");
	scanf("%lg %lg %d", &low, &high, &n);
	value = definite_integration(cos, low, high, n);
	printf("cosxdx[%g~%g/n=%d] : %g\n", low, high, n, value);
	
	printf("请输入e^xdx的下限、上限及区间划分数量\n");
	scanf("%lg %lg %d", &low, &high, &n);
	value = definite_integration(exp, low, high, n);
	printf("e^xdx[%g~%g/n=%d] : %g\n", low, high, n, value);
	

}