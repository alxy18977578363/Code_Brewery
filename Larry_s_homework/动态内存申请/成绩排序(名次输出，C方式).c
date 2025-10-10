/* 2351136 大数据 李盛鹏 */
#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
#include<stdlib.h>
#include<stdbool.h>

typedef struct student student;		// 为了防止太多废话，特别定义
struct student
{
	int no;		// 学号
	char name[9];	// 姓名
	int score;		// 分数
	int rank;		// 排名
};
int main()
{
	int num;
	FILE* infile;
	infile = fopen("student.txt", "r");		// read 方式读入
	if (infile == NULL)			// 失败处理
	{
		printf("读入文件失败\n");
		return -1;
	}
	fscanf(infile, "%d", &num);		// fscanf读入数量


	student* head = (student*)malloc(sizeof(student) * num);	// 动态申请
	student* p = head;

	if (head == NULL)
	{
		printf("申请空间错误\n");
		return -1;
	}

	for (p=head; p < num+head; p++)		// 读入数据
	{
		fscanf(infile, "%d %s %d", &p->no, p->name, &p->score);
	}

	// 冒泡法排序成绩
	for (int i = 0; i < num; i++)
	{
		bool have_change = false;
		for (p=head; p < head+num - 1 - i; p++)
		{
			if (p->score < (p + 1)->score)		// 如果比后一个人分数低，就往后冒泡
			{
				student temp = *p;
				*p = *(p + 1);
				*(p + 1) = temp;
				have_change = true;
			}
		}
		if (!have_change)			// 不交换后，结束循环
		{
			break;
		}
	}

	// 排名
	for (p = head; p < head + num; p++)
	{
		if (p == head)
		{
			p->rank = 1;		// 第一名
		}
		else
		{
			if (p->score == (p - 1)->score)			// 分数相同，排名相同
			{
				p->rank = (p - 1)->rank;
			}
			else
			{
				p->rank = (p - head) + 1;
			}
		}
	}

	// 选择法排学号
	for (p = head; p < head + num; p++)
	{
		for (student* q = p + 1; q < head + num; q++)
		{
			if (p->score == q->score)
			{
				if (p->no > q->no)
				{
					student temp = *p;
					*p = *q;
					*q = temp;
				}
			}
		}
	}

	// 输出最后结果
	for (p = head; p < head + num; p++)
	{
		printf("%d %s %d %d\n", p->no, p->name, p->score, p->rank);
	}
	
	fclose(infile);		// 关闭文件
	free(head);	// 释放空间

	return 0;
}
