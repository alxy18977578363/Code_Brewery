/* 2351136 李盛鹏 信03 */
#define _CRT_SECURE_NO_WARNINGS
#include<stdbool.h>
#include<stdio.h>

//判断闰年函数
bool LeapYear(int year)
{
	bool isLeapYear = (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
	return isLeapYear;
}


//计算天数函数
int calculate(int year, int month, int day, int dayofmonth[])
{
	int tamp = 0, allday = day;
	for (tamp = 0; tamp < month - 1; tamp++) {
		allday = dayofmonth[tamp] + allday;
	}

	return allday;
}


//main函数
int main()
{
	printf("请输入年，月，日\n");
	int dayofmonth[12] = { 31,28,31,30,31,30,31,31,30,31,30,31 };
	int year = 0, month, day;
	scanf("%d %d %d", &year, &month, &day);

	if (month > 12 || month < 1) {
		printf("输入错误-月份不正确\n");
	}
	else if (day<1 || day>dayofmonth[month - 1]) {
		printf("输入错误-日与月的关系非法\n");
	}
	else {
		//分别引用两个函数
		bool ifLeapYear = LeapYear(year);
		if (ifLeapYear) {
			dayofmonth[1]++;
		}


		int allday = calculate(year, month, day, dayofmonth);
		printf("%d-%d-%d是%d年的第%d天\n",year,month,day,year,allday);
	}

	return 0;
}