/* 信03 2351136 李盛鹏*/
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdbool.h>

int main()
{
	int allday = 0, month, year, week, day = 0, weekday;
	int ret;
	while (1) {
		printf("请输入年份(2000-2030)和月份(1-12) : ");
		ret=scanf("%d %d", &year, &month);
		if (year <= 2030 && year >= 2000 && ret==2 && month <= 12 && month >= 1) {//里面的小数咋办
			break;
		}

		if (year > 2030 || year < 2000)  {
			printf("输出非法，请重新输入\n");
			continue;
		}
		if (ret<2) {
			printf("输出非法，请重新输入\n");
			scanf("%*[^\n]%*c");
			continue;
		}
		// 年的不正确处理

		if (month > 12 || month < 1) {
			printf("输出非法，请重新输入\n");
			continue;
		}
		
		if ((month <= 12 || month >= 1) && ret==2) {
			break;
		}
		// 月的不正确处理
		break;
	}


	bool isLeapYear = (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
	//判断闰年

	while (1) {
		printf("请输入%d年%d月1日的星期(0-6表示星期日-星期六) : ", year, month);
		int ret2=scanf("%d", &week);
		if (week <= 6 && week >= 0 && ret2==1) {
			break;
		}

		if ((week < 0 || week>6) && ret2==1) {
			printf("输出非法，请重新输入\n");
			continue;
		}
		if (ret2==0) {
			printf("输出非法，请重新输入\n");
			scanf("%*[^\n]%*c");
			continue;
		}
		break;
	}
	//判断第一天是星期几
	weekday = week;

	switch (month) {
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
			if (isLeapYear == 1) {
				allday = 29;
			}
			else {
				allday = 28;
			}
			break;

		case 4:
		case 6:
		case 9:
		case 11:
			allday = 30;
			break;
	}//为每个月赋值

	printf("\n");
	printf("%d年%d月的月历为:\n",year,month);
	printf("星期日  星期一  星期二  星期三  星期四  星期五  星期六\n");
	for (weekday; weekday > 0; weekday--) {
		printf("        ");
	}//解决前面的空格问题

	while (day < allday) {
		day++;
		printf("%4d    ", day);

		if ((day + week) % 7 == 0) {
			printf("\n");
		}
	}
	if (day == allday) {
		printf("\n");
	}
	return 0;
}