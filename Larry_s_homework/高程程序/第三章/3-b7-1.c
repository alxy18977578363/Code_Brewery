/*2351136 信03 李盛鹏*/
#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
int main()
{
	printf("请输入找零值：\n");
	double a=0;
	scanf("%lf",&a);
	int b = (int)(a * 100 + 0.001);

	int c = b / 5000;
	int d = (b % 5000) / 2000;
	int e = (b % 5000 % 2000) / 1000;
	int f = (b % 5000 % 2000 % 1000) / 500;
	int g = (b % 5000 % 2000 % 1000 % 500) / 100;
	int h = (b % 5000 % 2000 % 1000 % 500 % 100) / 50;
	int i = (b % 5000 % 2000 % 1000 % 500 % 100 % 50) / 10;
	int j = (b % 5000 % 2000 % 1000 % 500 % 100 % 50 % 10) / 5;
	int k = (b % 5000 % 2000 % 1000 % 500 % 100 % 50 % 10 % 5) / 2;
	int l = (b % 5000 % 2000 % 1000 % 500 % 100 % 50 % 10 % 5 % 2) / 1;//算出每个有多少张

	int m = c + d + e + f + g + h + i + j + k + l;
	printf("共%d张找零，具体如下：\n", m);//算出一共有多少张

	if (a >= 50) {
		printf("50元 : %d张\n", c);
		a -= c * 50;
	}
	if (a >= 20) {
		printf("20元 : %d张\n", d);
		a -= d * 20;
	}
	if (a >= 10) {
		printf("10元 : %d张\n", e);
		a -= e * 10;
	}
	if (a >= 5) {
		printf("5元  : %d张\n", f);
		a -= f * 5;
	}
	if (a >= 1) {
		printf("1元  : %d张\n", g);
		a -= g * 1;
	}
	if (a >= 0.5) {
		printf("5角  : %d张\n", h);
		a -= h * 0.5;
	}
	if (a >= 0.1) {
		printf("1角  : %d张\n", i);
		a -= i * 0.1;
	}
	if (a >= 0.05) {
		printf("5分  : %d张\n", j);
		a -= j * 0.05;
	}
	if (a >= 0.02) {
		printf("2分  : %d张\n", k);
		a -= k * 0.02;
	}
	if (a >= 0.01) {
		printf("1分  : %d张\n", l);
		a -= l * 0.01;
	}//表示最后的输出的张数
	return 0;
}