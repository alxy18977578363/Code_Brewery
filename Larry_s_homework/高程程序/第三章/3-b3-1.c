/*2351136 信03 李盛鹏*/
#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
int main()
{
	printf("请输入[0-100亿）之间的数字:\n");
	double a,b;
	int  c, d, e, f, g, h, i, j, k,l,m,n;
	scanf("%lf", &a);
	b= a / 10 - (int)(a / 10);
	c = ((int)(a / 1000000000) % 10);
	d = ((int)(a / 100000000) % 10);
	e = ((int)(a / 10000000) % 10);
	f = ((int)(a / 1000000) % 10);
	g = ((int)(a / 100000) % 10);
	h = ((int)(a / 10000) % 10);
	i = ((int)(a / 1000) % 10);
	j = ((int)(a / 100) % 10);
	k = ((int)(a / 10) % 10);
	l = ((int)(b * 10 + 0.001) % 10);
	m = ((int)(b * 100 + 0.001) % 10);
	n = ((int)(b * 1000 + 0.001) % 10);
	printf("十亿位 : %d\n", c);
	printf("亿位   : %d\n", d);
	printf("千万位 : %d\n", e);
	printf("百万位 : %d\n", f);
	printf("十万位 : %d\n", g);
	printf("万位   : %d\n", h);
	printf("千位   : %d\n", i);
	printf("百位   : %d\n", j);
	printf("十位   : %d\n", k);
	printf("圆     : %d\n", l);
	printf("角     : %d\n", m);
	printf("分     : %d\n", n);
	return 0;
}
