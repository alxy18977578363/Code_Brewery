/* 2351136 大数据 李盛鹏 */
#include<iostream>
#include<fstream>
#include<cstring>
using namespace std;

struct student
{
	int no;
	char name[9];
	int score;
	struct student* next;
};

// 释放内存
void releaseMemory(student* head)		
{
	student* p = head;
	while (p != nullptr)
	{
		student* temp = p;
		p = p->next;
		delete temp; // 释放当前节点
	}
}

int main()
{
	ifstream infile;
	infile.open("list.txt", ios::in);
	if (infile.is_open() == 0)		// 文件打开错误处理
	{
		cout << "文件打开失败" << endl;
		return -1;
	}

	student* head = nullptr;
	student* p = nullptr;
	student* q = nullptr;		// 定义三个指针

	int no;

	while (true)
	{
		infile >> no;
		if (no == 9999999)			// 表示结束
		{
			break;
		}

		p = new(nothrow)student;
		if (p == nullptr)			// 错误处理
		{
			cout << "内存申请失败" << endl;
			releaseMemory(head);
			return -1;
		}

		p->no = no;
		infile >> p->name >> p->score;		// 赋值
		p->next = nullptr;

		if (head == nullptr)			// 如果是第一个学生
		{
			head = q = p;
		}
		else
		{
			q->next = p;
			q = p;
		}
	}

	for (p = head; p; p = p->next)			// 遍历，然后输出
	{
		cout << p->no << " " << p->name << " " << p->score << endl;
	}

	// 后期处理
	infile.close();			// 关闭文件
	releaseMemory(head);
	return 0;
}