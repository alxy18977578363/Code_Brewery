/* 2351136 李盛鹏 信03 */
#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
#include<string.h>
#define L_xuehao 7
#define people 10

//除掉缓冲区空格的函数
void cleanspace()
{
	while (getchar() == '\n')
		;
}

//输入函数，负责把输入内容放入字符数组中,只负责输入一行的，具体是哪行由main的循环决定
void my_input(char xuehao[][L_xuehao+1], char name[][4 * 2 + 1],int score[],int paixu)
{
	//读入排在最前的学号，遇到空格就停止
	scanf("%s", &xuehao[paixu]);

	//除掉缓冲区空格
	cleanspace();

	//读入名字，遇到空格就停止
	scanf("%s", &name[paixu]);

	//除掉缓冲区空格
	cleanspace();

	//读入分数
	scanf("%d", &score[paixu]);
}

//排序函数，负责把里面的学号降序排列
void my_sort(char xuehao[][L_xuehao + 1], char name[][4 * 2 + 1], int score[])
{
	char tamp_xue[L_xuehao + 1] = { 0 }, tamp_name[4 * 2 + 1] = { 0 };
	int tamp_score = 0;
	
	//从第零个开始比，然后用冒泡的方法
	for(int count=0;count<people-1;count++){
		for (int i = people - 1; i > 0; i--) {
			//如果后面的学号比前面的大，则先把前面的学号放到tamp中，再借tamp放到后面
			if (score[i] > score[i - 1]) {
				//先换学号
				strcpy(tamp_xue, xuehao[i]);
				strcpy(xuehao[i], xuehao[i - 1]);
				strcpy(xuehao[i - 1], tamp_xue);

				//再换名字
				strcpy(tamp_name, name[i]);
				strcpy(name[i], name[i - 1]);
				strcpy(name[i - 1], tamp_name);

				//再换分数
				tamp_score = score[i];
				score[i] = score[i - 1];
				score[i - 1] = tamp_score;

			}

		}
	}


}

//输出函数，负责把及格的人输出出来
void my_output(char xuehao[][L_xuehao + 1], char name[][4 * 2 + 1], int score[])
{
	for (int i = 0; i < people; i++) {
		printf("%s %s %d\n", &name[i], &xuehao[i], score[i]);
	}
}


int main()
{
	//定义一个学号数组，一个名字数组,一个分数数组
	char xuehao[people][L_xuehao+1] = { 0 }, name[people][4 * 2 + 1];
	int score[people] = { 0 };

	//要求用户输入学号姓名成绩
	for (int paixu = 0; paixu < people; paixu++) {
		printf("请输入第%d个人的学号、姓名、成绩\n", (paixu + 1));
		my_input(xuehao, name, score, paixu);
	}

	//调用调整函数
	my_sort(xuehao, name, score);

	printf("\n");
	printf("全部学生(成绩降序):\n");

	//调用输出函数
	my_output(xuehao, name, score);



	return 0;
}