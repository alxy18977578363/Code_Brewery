/*2351136 信03 李盛鹏*/ 
#define _CRT_SECURE_NO_WARNINGS
#include<math.h>
#include<stdio.h>
int main()
{
	const double pi = 3.14159;
	int a, b, c;
	float s;
	printf("请输入三角形的两边及其夹角（角度）\n");
	scanf("%d %d %d", &a, &b, &c);
	printf("三角形的面积为 : ");
	s = (float)(a * b / 2 * sin(pi * c / 180));
	printf("%.3f\n", s);
	return 0;
}

