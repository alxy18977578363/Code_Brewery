/* 信03 2351136 李盛鹏*/
#include<iostream>
#include<iomanip>
using namespace std;
int main()
{
	int allday=0, month, year, week, day=0,weekday;

	while (1) {
		cout << "请输入年份(2000-2030)和月份(1-12) : ";
		cin >> year >> month;
		if (year <= 2030 && year >= 2000 && cin.good() && month <= 12 && month >= 1) {
			break;
		}

		if ((year > 2030 || year < 2000) && cin.good()) {
			cout << "输出非法，请重新输入" << endl;
			continue;
		}
		if (!(cin.good())) {
			cout << "输出非法，请重新输入" << endl;
			cin.clear();
			cin.ignore(1024, '\n');
			continue;
		}
		// 年的不正确处理

		if ((month > 12 || month < 1) && cin.good()) {
			cout << "输出非法，请重新输入" << endl;
			continue;
		}
		if (!(cin.good())) {
			cout << "输出非法，请重新输入" << endl;
			cin.clear();
			cin.ignore(1024, '\n');
			continue;
		}
		if ((month <= 12 || month >= 1) && cin.good()) {
			break;
		}
		// 月的不正确处理
		break;
	}


	bool isLeapYear = (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
	//判断闰年

	while (1) {
		cout << "请输入" << year << "年" << month << "月1日的星期(0-6表示星期日-星期六) : ";
		cin >> week;
		if (week <= 6 && week >= 0 && cin.good()) {
			break;
		}

		if ((week < 0 || week>6) && cin.good()) {
			cout << "输出非法，请重新输入" << endl;
			continue;
		}
		if (!(cin.good())) {
			cout << "输出非法，请重新输入" << endl;
			cin.clear();
			cin.ignore(1024, '\n');
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
			isLeapYear == 1 ? allday = 29 : allday=28;
			break;

		case 4:
		case 6:
		case 9:
		case 11:
			allday = 30;
			break;
	}//为每个月赋值
	
	cout << endl;
	cout << year << "年" << month << "月的月历为:" << endl;
	cout << "星期日  " << "星期一  " << "星期二  " << "星期三  " << "星期四  " << "星期五  " << "星期六" << endl;
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
	return 0;
}