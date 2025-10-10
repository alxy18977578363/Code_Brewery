/* 2351136 大数据 李盛鹏 */
#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
#include<stdlib.h>
#include<stdbool.h>

struct student
{
	int no;		// 学号
	char name[9];	// 姓名
	int score;		// 分数
	struct student* next;
};

// 释放空间
void releaseMemory(struct student* head)
{
	struct student* p = head;
	while (p != NULL)
	{
		struct student* temp = p;
		p = p->next;
		free(temp); // 释放当前节点
	}
}

int main()
{
	FILE* infile = fopen("list.txt", "r");		// read方式读入文件
	if (infile == NULL)				// 处理文件读入失败
	{
		printf("文件读入失败\n");
		return -1;
	}

	int no;
	struct student* head = NULL;
	struct student* p = NULL;
	struct student* q = NULL;		// 定义三个指针串成一个数组
	while (true)
	{
		fscanf(infile, "%d", &no);		// 读入学号
		if (no == 9999999)
		{
			break;			// 结束的标志
		}

		p = (struct student*)malloc(sizeof(struct student));		// 动态申请空间
		if (p == NULL)			// 动态内存申请失败处理
		{
			printf("申请内存失败\n");
			releaseMemory(head);
			return -1;
		}

		p->no = no;
		fscanf(infile, "%s %d", p->name, &p->score);	// 到了这一步说明文件读入并没有结束
		p->next = NULL;

		if (head == NULL)
		{
			head = q = p;	// 第一个元素
		}
		else
		{
			q->next = p;
			q = p;
		}
	}

	p = head;
	while (p != NULL)
	{
		printf("%d %s %d\n", p->no, p->name, p->score);
		p = p->next;
	}

	// 后期处理
	fclose(infile);		// 关闭文件
	releaseMemory(head);

	return 0;
}