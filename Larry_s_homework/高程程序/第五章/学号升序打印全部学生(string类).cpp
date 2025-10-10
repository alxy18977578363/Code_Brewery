/* 2351136 李盛鹏 信03 */
#include<iostream>
#include <string>
#include<string.h>
#define L_xuehao 7
#define people 10

using namespace std;
//除掉缓冲区空格的函数
void cleanspace()
{
	while (getchar() == '\n')
		;
}

//输入函数，负责把输入内容放入字符数组中,只负责输入一行的，具体是哪行由main的循环决定
void my_input(string xuehao[], string name[], int score[], int paixu)
{
	//读入排在最前的学号，遇到空格就停止
	cin >> xuehao[paixu];

	//除掉缓冲区空格
	cleanspace();

	//读入名字，遇到空格就停止
	cin >> name[paixu];

	//除掉缓冲区空格
	cleanspace();

	//读入分数
	cin >> score[paixu];
}

//排序函数，负责把里面的学号降序排列
void my_sort(string xuehao[], string name[], int score[])
{
	string tamp_xue, tamp_name;
	int tamp_score = 0;

	//从第零个开始比，然后用冒泡的方法
	for (int count = 0; count < people - 1; count++) {
		for (int i = people - 1; i > 0; i--) {
			//如果后面的学号比前面的大，则先把前面的学号放到tamp中，再借tamp放到后面
			if (xuehao[i].compare(xuehao[i-1])<0) {
				//先换学号
				tamp_xue = xuehao[i];
				xuehao[i] = xuehao[i - 1];
				xuehao[i - 1] = tamp_xue;

				//再换名字
				tamp_name = name[i];
				name[i] = name[i - 1];
				name[i - 1] = tamp_name;

				//再换分数
				tamp_score = score[i];
				score[i] = score[i - 1];
				score[i - 1] = tamp_score;

			}

		}
	}


}

//输出函数，负责把及格的人输出出来
void my_output(string xuehao[], string name[], int score[])
{
	for (int i = 0; i < people; i++) {
		cout << name[i] << " " << xuehao[i] << " " << score[i] << endl;
	}
}


int main()
{
	//定义一个学号数组，一个名字数组,一个分数数组
	string xuehao[people], name[people];
	int score[people] = { 0 };


	//要求用户输入学号姓名成绩
	for (int paixu = 0; paixu < people; paixu++) {
		cout << "请输入第" << paixu + 1 << "个人的学号、姓名、成绩" << endl;
		my_input(xuehao, name, score, paixu);
	}

	//调用调整函数
	my_sort(xuehao, name, score);

	cout << endl;
	cout << "全部学生(学号升序):" << endl;

	//调用输出函数
	my_output(xuehao, name, score);
	
	return 0;
}