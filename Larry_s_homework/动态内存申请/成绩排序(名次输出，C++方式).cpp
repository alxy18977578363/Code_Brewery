/* 2351136 大数据 李盛鹏 */
#include<iostream>
#include<fstream>
using namespace std;
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
	ifstream infile;		// 文件
	infile.open("student.txt", ios::in);		// 打开文件
	if (infile.is_open() == 0)		// 打开文件错误处理
	{
		cout << "文件打开失败" << endl;	
		return -1;
	}

	infile >> num;
	student* a_student = new(nothrow) student[num];		// 申请足够的空间

	if (a_student == NULL)		// 申请空间错误处理
	{
		cout << "申请空间错误" << endl;
		return -1;	
	}


	for (int i = 0; i < num; i++)
	{
		infile >> a_student[i].no >> a_student[i].name >> a_student[i].score;
	}

	// 冒泡法排序成绩
	for (int i = 0; i < num; i++)
	{
		bool have_change = false;		// 如果发现没变化，就提前结束
		for (int j = 0; j < num-1-i; j++)		// 排到最后面的不会浮动了
		{
			if (a_student[j].score < a_student[j + 1].score)
			{
				student temp = a_student[j];
				a_student[j] = a_student[j + 1];
				a_student[j + 1] = temp;
				have_change = true;
			}
		}
		if (!have_change)	// 如果不变化，这里开始结束
		{
			break;			
		}
	}

	// 排名
	for (int i = 0; i < num; i++)
	{
		if (i == 0)
		{
			a_student[i].rank = 1;		// 第一名
		}
		else
		{
			if (a_student[i].score == a_student[i - 1].score)		// i>=1部分
			{
				a_student[i].rank = a_student[i - 1].rank;
			}
			else
			{
				a_student[i].rank = i + 1;		// 否则，就是一个新的成绩
			}
		}
		
	}

	// 选择法排序学号
	for (int i = 0; i < num; i++)
	{
		for (int j = i + 1; j < num; j++)
		{
			if (a_student[i].score == a_student[j].score)		// 只对成绩相同的进行排序
			{
				if (a_student[i].no > a_student[j].no)
				{
					student temp = a_student[i];
					a_student[i] = a_student[j];
					a_student[j] = temp;
				}
			}
		}
	}

	// 输出最终结果
	for (int i = 0; i < num; i++)
	{
		cout << a_student[i].no << " " << a_student[i].name << " " << a_student[i].score << " " << a_student[i].rank << endl;
	}

	// 记住释放空间
	delete[]a_student;
	infile.close();			// 关闭文件

	return 0;
}
