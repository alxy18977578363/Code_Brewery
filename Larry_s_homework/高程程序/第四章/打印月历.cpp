/* 2351136 李盛鹏 信03 */
#include <iostream>
#include<iomanip>
using namespace std;


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

	int w = y + int(y / 4) + int(c / 4) - (2 * c) + int(26 * (m + 1) / 10) + d - 1;
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

int relation(int y,int m)
{
	bool isLeapYear = (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
	int allday=0;
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
			isLeapYear == 1 ? allday = 29 : allday = 28;
			break;

		case 4:
		case 6:
		case 9:
		case 11:
			allday = 30;
			break;
	}//为每个月赋值

	return allday;
}

void calender(int year, int month)
{
	/* 按需添加代码 */

	cout << year << "年" << month << "月" << endl;
	/* 头部分隔线，不算打表 */
	cout << "======================================================" << endl;
	cout << "星期日  星期一  星期二  星期三  星期四  星期五  星期六" << endl;
	cout << "======================================================" << endl;

	/* 按需添加代码 */
	int week = zeller(year, month, 1), weekday = week;
	int allday = relation(year, month);
	int day = 0;
	for (weekday; weekday > 0; weekday--) {
		cout << "        ";
	}//解决前面的空格问题

	while (day < allday) {
		day++;
		cout << setw(4) << day << "    ";

		if ((day + week) % 7 == 0) {
			cout << endl;
		}
	}
	if (day == allday) {
		cout << endl;
	}
	/* 尾部分隔线，不算打表 */
	cout << "======================================================" << endl;
}


int main()
{
	int y, m;
	while (1) {
		cout << "请输入年[1900-2100]、月" << endl;
		cin >> y >> m ;

		if (cin.fail()) {
			cout << "输入错误，请重新输入" << endl;
			cin.clear();
			cin.ignore(1024,'\n');
			continue;
		}

		if (y > 2100 || y < 1900) {
			cout << "年份不正确，请重新输入" << endl;
			cin.ignore(1024,'\n');
			continue;
		}

		if (m < 1 || m>12) {
			cout << "月份不正确，请重新输入" << endl;
			cin.ignore(1024,'\n');
			continue;
		}

		
		break;
	}//判断错误

	int w = zeller(y, m, 1);
	int allday = relation(y, m);
	cout << endl;
	calender(y, m);

	return 0;
}
