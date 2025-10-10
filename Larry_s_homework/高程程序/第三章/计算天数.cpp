/*2351136 信03 李盛鹏*/
#include <iostream>
using namespace std;
int main()
{
	cout << "请输入年，月，日" << endl;
	int year, month, day, day2 = 0, allday;
	cin >> year >> month >> day;
	bool isLeapYear = (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);//判断闰年

	bool a = true;
	if (month > 12 || month < 1) {
		a = false;
		cout << "输入错误-月份不正确" << endl;
	}
	else {
		switch (month) {
			case 1:
			case 3:
			case 5:
			case 7:
			case 8:
			case 10:
			case 12:
				day2 = 31;
				break;
			case 4:
			case 6:
			case 9:
			case 11:
				day2 = 30;
				break;
			case 2:
				day2 = isLeapYear ? 29 : 28;
				break;
		}
		if (day<1 || day>day2) {
			a = false;
			cout << "输入错误-日与月关系非法" << endl;
			return 0;//判断日月关系和月是否错误
		}
	}
	switch (month) {
		case 1:
			allday = day;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 2:
			allday = day + 31;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 3:
			allday = day + 31 + (day2 = isLeapYear ? 29 : 28);
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 4:
			allday = day + 31 + (day2 = isLeapYear ? 29 : 28) + 31;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 5:
			allday = day + 31 + (day2 = isLeapYear ? 29 : 28) + 31 + 30;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 6:
			allday = day + 31 + (day2 = isLeapYear ? 29 : 28) + 31 + 30 + 31;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 7:
			allday = day + 31 + (day2 = isLeapYear ? 29 : 28) + 31 + 30 + 31 + 30;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 8:
			allday = day + 31 + (day2 = isLeapYear ? 29 : 28) + 31 + 30 + 31 + 30 + 31;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 9:
			allday = day + 31 + (day2 = isLeapYear ? 29 : 28) + 31 + 30 + 31 + 30 + 31 + 31;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 10:
			allday = day + 31 + (day2 = isLeapYear ? 29 : 28) + 31 + 30 + 31 + 30 + 31 + 31 + 30;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 11:
			allday = day + 31 + (day2 = isLeapYear ? 29 : 28) + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
		case 12:
			allday = day + 31 + (day2 = isLeapYear ? 29 : 28) + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30;
			cout << year << "-" << month << "-" << day << "是" << year << "年的第" << allday << "天" << endl;
			break;
	}
	return 0;
}