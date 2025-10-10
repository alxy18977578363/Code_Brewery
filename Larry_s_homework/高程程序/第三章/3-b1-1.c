/*2351136 信03 李盛鹏*/
#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
int main()
{
	const double pi = 3.14159;
	double a, b, c, d, e, f, g;
	a = 0, b = 0;
	printf("请输入半径和高度\n");
	scanf("%lf %lf", &a, &b);
	c = a * 2 * pi;
	d = a * a * pi;
	e = a * a * 4 * pi;
	f = a * a * a * 4 / 3 * pi;
	g = a * a * pi * b;
	printf("圆周长     : %.2lf\n", c);
	printf("圆面积     : %.2lf\n", d);
	printf("圆球表面积 : %.2lf\n", e);
	printf("圆球体积   : %.2lf\n", f);
	printf("圆柱体积   : %.2lf\n", g);
	return 0;
}
