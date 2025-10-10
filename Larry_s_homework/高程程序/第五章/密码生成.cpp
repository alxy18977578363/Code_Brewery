/* 2351136 李盛鹏 信03 */
#include<iostream>
#include<windows.h>
#include<time.h>

#define Lmin 12
#define Lmax 16
#define generation 10
using namespace std;

//静态全局的其他字符用到的数组
static const char other[] = "!@#$%^&*-_=+,.?";

//输入内容，依据choice来决定输入的是什么类型的字符
void input_password(char password[], int length, int num, int choice)
{
	char daxiecase = 'Z' - 'A' + 1, xiaoxiecase = 'z' - 'a' + 1, numbercase = '9' - '0' + 1, othercase =strlen(other);
	//以随机数i来挑选一个在0到（length-1）的位置安排大写字符
	for (int count = 0; count < num; count++) {
		int i = rand() % length;
		char j;
		//以随机数j来决定是哪个大写字符
		if (choice == 1)
			j = rand() % daxiecase + 'A';
		else if (choice == 2)
			j = rand() % xiaoxiecase + 'a';
		else if (choice == 3)
			j = rand() % numbercase + '0';
		else {
			j = other[rand() % othercase];
		}

		while (password[i] != 0) {
			i = rand() % length;
		}
		password[i] = j;

	}

}

int main()
{
	cout << "请输入密码长度(12-16)， 大写字母个数(≥2)， 小写字母个数(≥2)， 数字个数(≥2)， 其它符号个数(≥2)" << endl;

	//定义长度，大写字符，小写字符，数字，其他字符的数量
    int length=0, daxie = 0, xiaoxie = 0, number = 0, others = 0;
	bool if_valid = false;
	cin >> length >> daxie >> xiaoxie >> number >> others;

	//输入错误的提示顺序
	//1.输入非法
	//2.密码长度不正确
	//3.某个字符个数小于规定的最小个数
	//4.字符之和大于整个密码的长度
	if (!cin.good()) {
		cout << "输入非法" << endl;
	}
	else if (length > Lmax || length < Lmin) {
		cout << "密码长度[" << length << "]不正确" << endl;
	}
	else if (daxie < 2 || xiaoxie < 2 || number < 2 || others < 2) {
		if (daxie < 2) {
			cout << "大写字母个数[" << daxie << "]不正确" << endl;
		}
		else if (xiaoxie < 2) {
			cout<< "小写字母个数[" << xiaoxie<< "]不正确" << endl;
		}
		else if (number < 2) {
			cout << "数字个数[" << number << "]不正确" << endl;
		}
		else{
			cout << "其它符号个数[" << others << "]不正确" << endl;
		}
	}
	else if (daxie + xiaoxie + number + others > length) {
		cout << "所有字符类型之和[" << daxie << "+" << xiaoxie << "+" << number << "+" << others << "]大于总密码长度[" << length << "]" << endl;
	}
	else {
		if_valid = true;
	}

	//只有if_valid为true的时候才能继续程序，只要是false就结束程序
	if (!if_valid) {
		return 0;
	}
	
	//向用户展示读入的五个数据
	cout << length << " " << daxie <<" " << xiaoxie<<" " << number<<" " << others << endl;

	srand(time(NULL)); //使用srand()函数设置随机数种子
	//重复该过程10次
	for (int count = 0; count < generation; count++) {
		char password[Lmax + 1] = { 0 };

		//给每个字符安排位置
		input_password(password, length, daxie, 1);
		input_password(password, length, xiaoxie, 2);
		input_password(password, length, number, 3);
		input_password(password, length, others, 4);

		//给剩余的位置安排字符
		int remained = length - daxie - xiaoxie - number - others;
		for (int i = 0; i < remained; i++) {
			input_password(password, length, 1, rand() % 4 + 1);
		}

		cout << password << endl;
	}

	return 0;
}