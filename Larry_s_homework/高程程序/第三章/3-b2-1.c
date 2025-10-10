/*2351136 信03 李盛鹏*/ 
#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
int main()
{
	printf("请输入一个【1..30000】间的整数；\n");
	int a, b, c, d, e, f;
	scanf("%d",&a); 
	b =( (a - a % 10000) / 10000) % 10;
	c = ((a - a % 1000) / 1000) % 10;
	d = ((a - a % 100) / 100) % 10;
	e=((a - a % 10) / 10) % 10;
	f = a % 10;
	printf("万位 : %d\n", b);
	printf("千位 : %d\n", c);
	printf("百位 : %d\n", d);
	printf("十位 : %d\n", e);
	printf("个位 : %d\n", f);
	return 0;
}
