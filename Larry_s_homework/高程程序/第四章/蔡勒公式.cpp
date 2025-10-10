/* 2351136 李盛鹏 信03 */
#include <iostream>
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

bool relation(int y,int m,int d)
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
		cout << "请输入年[1900-2100]、月、日：" << endl;
		cin >> y >> m >> d;

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

		bool connection = relation(y, m, d);
		if (d < 1 || connection) {
			cout << "日不正确，请重新输入" << endl;
			cin.ignore(1024,'\n');
			continue;
		}
	
		break;
	}//判断错误

	int w = zeller(y, m, d);
	switch (w) {
		case 0:
			cout << "星期日" << endl;
			break;
		case 1:
			cout << "星期一" << endl;
			break;
		case 2:
			cout << "星期二" << endl;
			break;
		case 3:
			cout << "星期三" << endl;
			break;
		case 4:
			cout << "星期四" << endl;
			break;
		case 5:
			cout << "星期五" << endl;
			break;
		case 6:
			cout << "星期六" << endl;
			break;
		default:
			cout << "error";
			break;
	}//输出星期几

	return 0;
}
