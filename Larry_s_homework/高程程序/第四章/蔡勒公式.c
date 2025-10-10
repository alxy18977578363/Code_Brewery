/* 2351136 李盛鹏 信03 */
#define _CRT_SECURE_NO_WARNINGS
#include<stdbool.h>
#include<stdio.h>

int zeller(int y, int m, int d)
{
	int c;
	if (m >= 3) {
		m = m;
		c = y / 100;
		y = y % 100;
	}
	else {
		m += 12;
		c = (y - 1) / 100;
		y = (y - 1) % 100;
	}//参数处理

	int w = y + (int)(y / 4) + (int)(c / 4) - (2 * c) + (int)(26 * (m + 1) / 10) + d - 1;
	if (w < 0) {
		while (w < 0) {
			w += 7;
		}
		w = w % 7;
	}
	if (w >= 0) {
		w = w % 7;
	}
	return w;
}
//zeller公式

bool relation(int y, int m, int d)
{
	bool isLeapYear = (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
	int allday = 0;
	switch (m) {
		case 1:
		case 3:
		case 5:
		case 7:
		case 8:
		case 10:
		case 12:
			allday = 31;
			break;

		case 2:
			(isLeapYear == 1) ? (allday = 29) : (allday = 28);
			break;

		case 4:
		case 6:
		case 9:
		case 11:
			allday = 30;
			break;
	}//为每个月赋值

	if (d > allday) {
		return 1;
	}
	else {
		return 0;
	}
}


int main()
{
	int y, m, d;
	while (1) {
		printf("请输入年[1900-2100]、月、日：\n");
		int ret = scanf("%d %d %d", &y, &m, &d);

		if (ret < 3) {
			printf("输入错误，请重新输入\n");
			while ((getchar()) != '\n')
				;
			continue;
		}

		if (y > 2100 || y < 1900) {
			printf("年份不正确，请重新输入\n");
			while ((getchar()) != '\n')
				;
			continue;
		}

		if (m < 1 || m>12) {
			printf("月份不正确，请重新输入\n");
			while ((getchar()) != '\n')
				;
			continue;
		}

		bool connection = relation(y, m, d);
		if (d < 1 || connection) {
			printf("日不正确，请重新输入\n");
			while ((getchar()) != '\n')
				;
			continue;
		}
		break;
	}//判断错误

	int w = zeller(y, m, d);
	switch (w) {
		case 0:
			printf("星期日\n");
			break;
		case 1:
			printf("星期一\n");
			break;
		case 2:
			printf("星期二\n");
			break;
		case 3:
			printf("星期三\n");
			break;
		case 4:
			printf("星期四\n");
			break;
		case 5:
			printf("星期五\n");
			break;
		case 6:
			printf("星期六\n");
			break;
		default:
			printf("error\n");
			break;
	}//输出星期几

	return 0;
}