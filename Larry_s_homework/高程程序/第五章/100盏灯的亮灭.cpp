/* 2351136 信03 李盛鹏 */
#include <iostream>
using namespace std;


int main()
{

	//设置初始状态
    int i=0,person=0;
	int Switch[100] = {0};
	
	
	//用问号表达式表示开关
	for (person = 1; person <= 100; person++) {
		for (i = 0; i < 100; i++) {
			if ((i + 1) % person == 0) {
				Switch[i] = (Switch[i] == 0) ? 1 : 0;
			}
		}
	}

	//输出开灯的
	bool isFirst = true; // 用于跟踪是否是第一个满足条件的数

	for (int i = 0; i < 100; i++) {
		if (Switch[i] == 1) {
			if (!isFirst) {
				cout << " "; // 在非第一个满足条件的数之前输出空格
			}
			cout << i + 1;
			isFirst = false; // 标记已经输出了第一个满足条件的数
		}
	}
	cout << endl;

	return 0;
}
