/* 2351136 李盛鹏 信03 */
#include <iostream>
#include <iomanip>
using namespace std;

//两个数的比大小
int max(int num1, int num2)
{
	if (num1 > num2) {
		return num1;
	}
	else {
		return num2;
	}
}

//三个数的比大小
int max(int num1, int num2, int num3)
{
	int bigger = (num1 > num2) ? num1: num2;
	
	return max(bigger, num3);
}

//四个数的比大小
int max(int num1, int num2, int num3,int num4)
{
	int bigger1 = (num1 > num2) ? num1 : num2;
	int bigger2 = (num3 > num4) ? num3 : num4;

	return max(bigger1, bigger2);
	
}



int main()
{
	int account, num1, num2, num3, num4,biggest=0;

	while (1) {
		if (cin.good()) {
			cout << "请输入个数num及num个正整数：" << endl;
		}
		cin >> account;

		if (!cin.good()) {
			cin.clear();
			cin.ignore(65536, '\n');
			continue;
		}

		//account归类
		switch (account) {
			case 2:
				cin >> num1 >> num2;
				if (cin.good()) {
					biggest = max(num1, num2);
					cout << "max=" << biggest << endl;
				}
				else {
					continue;
				}
				break;
			case 3:
				cin >> num1 >> num2 >> num3;
				if (cin.good()) {
					biggest = max(num1, num2, num3);
					cout << "max=" << biggest << endl;
				}
				else {
					continue;
				}
				break;
			case 4:
				cin >> num1 >> num2 >> num3 >> num4;
				if (cin.good()) {
					biggest = max(num1, num2, num3, num4);
					cout << "max=" << biggest << endl;
				}
				else {
					continue;
				}
				break;
			default:
				cout << "个数输入错误" << endl;
		}



		return 0;
	}
}