/* 2351136 信03 李盛鹏 */
#include <iostream>
using namespace std;


int main()
{
	int arrange[20], i1 = 0, i2 = 0, number = 0, another, num = 0;

	cout << "请输入任意个正整数（升序，最多20个），0或负数结束输入" << endl;
	//开始输入
	for (i1 = 0; i1 < 20; i1++) {
		cin >> number;
		if (number > 0) {
			num++;
			arrange[i1] = number;
		}
		if (!cin.good() || number <= 0) {
			break;
		}


	}

	//清空缓存
	cin.clear();
	cin.ignore(65536, '\n');




	if (i1 == 0) {
		cout << "无有效输入" << endl;
	}
	else {
		cout << "原数组为：" << endl;

		//按照一开始的输入列出原始排列
		for (i2 = 0; i2 < i1; i2++) {
			if (arrange[i2] > 0) {
				cout << arrange[i2] << " ";
			}
		}
		cout << endl;
		cout << "请输入要插入的正整数" << endl;


		//插入一个正整数
		int tamp = 0;
		cin >> another;

		cout << "插入后的数组为：" << endl;
		for (i1 = 0; i1 <num ; i1++) {

			if (another > arrange[i1]) {
				tamp = i1+1;
			}
		}

		for (i1 = 0; i1 < tamp; i1++) {
			
				cout << arrange[i1] << " ";
			
		}
		cout << another << " ";

		for (i1 = tamp; i1 < num; i1++) {
				cout << arrange[i1] << " ";
			
		}
		cout << endl;
	}

	return 0;
}