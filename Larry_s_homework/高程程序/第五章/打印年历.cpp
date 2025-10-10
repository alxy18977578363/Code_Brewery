/* 2351136 李盛鹏 信03 */
#include <iostream>
#include<iomanip>
#define N 23
using namespace std;


//zeller公式，用来结算该日为星期几
int zeller(int y, int m, int d=1)
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

//初始化函数
void initial(int monthofthree[][N], int year, int month, int dayofmonth[])
{
	for (int i = 0; i < 3; i++) {
		int week = zeller(year, month);
		int my_count = 1;
		for (int i = 0 ; i < 6 ; i++) {
			if (i == 0) {
				int j = 0 + 8 * ((month - 1) % 3);
				for (j = week + 8 * ((month - 1) % 3); j < 7+ 8 * ((month - 1) % 3); j++) {
					monthofthree[i][j] = my_count;
					my_count++;
				}
			}
			else {
				int j = 0+ 8 * ((month - 1) % 3);
				for (j = 0+ 8 * ((month - 1) % 3); j < 7 + 8 * ((month - 1) % 3); j++) {
					if (my_count <= dayofmonth[month]) {
						monthofthree[i][j] = my_count;
						my_count++;
					}
				}
			}
		}
		month++;
	}
}

//这个函数用来判断是不是闰年
bool relation(int year)
{
	bool isLeapYear = (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
	return isLeapYear;
}

void printcalender(int year,int month,int monthofthree[][N])
{
	if(month<10)
	cout << "            "<< month << "月" << "                             " << (month + 1) << "月" << "                             " << (month + 2) << "月" << endl;
	else
		cout<< "           " << month << "月" << "                            " << (month + 1) << "月" << "                            " << (month + 2) << "月" << endl;
	cout << "Sun Mon Tue Wed Thu Fri Sat     Sun Mon Tue Wed Thu Fri Sat     Sun Mon Tue Wed Thu Fri Sat" << endl;

	for (int i = 0; i < 5; i++) {
		for (int j = 0; j < N; j++) {
			if (monthofthree[i][j])
				cout << setw(3) << setiosflags(ios::left) << monthofthree[i][j] << " ";
			else{
				cout << "    ";
			}
			
		}
		cout << endl;
		
	}
	bool ifendl = false;
	for (int j = 0; j < N&&!ifendl; j++) {
		if (monthofthree[5][j] != 0) {
			ifendl = true;
		}
	}
	if(ifendl){
		for (int j = 0; j < N; j++) {
			if (monthofthree[5][j])
				cout << setw(3) << setiosflags(ios::left) << monthofthree[5][j] << " ";
			else {
				cout << "    ";
			}
		}
		cout << endl;
		cout << endl;
	}
	else {
		cout << endl;
	}
}


int main()
{

	int monthofthree[6][N] = {0};
	int dayofmonth[] = { 0,31,28,31,30,31,30,31,31,30,31,30,31 };
	

	//输入年份的错误输入判断
	int year;
	bool validyear = false;
	while (!validyear) {
		cout << "请输入年份[1900-2100]" << endl;
		cin >> year;
		if (!cin.good()) {
			cin.clear();
			cin.ignore(65536,'\n');
		}
		if (year <= 2100 && year >= 1900) {
			validyear = true;
		}
		else {
			continue;
		}
	}
	cout << year << "年的日历:" << endl;
	cout << endl;

	bool isLeapyear = relation(year);
	if (isLeapyear) {
		dayofmonth[2]++;
	}
	//下面的程序先帮数组初始化，再输出，再清零这个数组，才进循环
	for (int i = 1; i <= 4; i++) {
		initial(monthofthree, year, -2+3*i, dayofmonth);
		printcalender(year,-2+3*i, monthofthree);

		for (int y= 0; y< 6; y++) {
			for (int x = 0; x < N; x++) {
				monthofthree[y][x] = 0;
			}
		}
	}
		
	cout << endl;
	
	
	//calender(y, m);

	return 0;
}