/* 2351136 李盛鹏 信03 */
#include <iostream>
#include <iomanip>
using namespace std;


int min(int num1, int num2,int num3=0,int num4=0)
{
	int smaller1 = (num1 > num2) ? num2 : num1;
	int smaller2 = (num3 > num4) ? num4 : num3;
	
	if (smaller1>smaller2&&smaller2>0) {
		return smaller2;
	}
	else {
		return smaller1;
	}

}




int main()
{
	int account, num1, num2, num3, num4,smallest=0;

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
				if (cin.good()&&num1>0&&num2>0) {
					smallest = min(num1, num2);
					cout << "min=" << smallest << endl;
				}
				else {
					continue;
				}
				break;
			case 3:
				cin >> num1 >> num2 >> num3;
				if (cin.good() && num1 > 0 && num2 > 0&&num3>0) {
					smallest = min(num1, num2, num3);
					cout << "min=" << smallest << endl;
				}
				else {
					continue;
				}
				break;
			case 4:
				cin >> num1 >> num2 >> num3 >> num4;
				if (cin.good() && num1 > 0 && num2 > 0&&num3>0&&num4>0) {
					smallest = min(num1, num2, num3, num4);
					cout << "min=" << smallest << endl;
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