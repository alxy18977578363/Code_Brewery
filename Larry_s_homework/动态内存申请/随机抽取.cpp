/* 2351136 大数据 李盛鹏 */
#define _CRT_SECURE_NO_WARNINGS
#include<iostream>
#include<fstream>
#include<cstring>
#include<ctime>
using namespace std;

typedef struct student student;		// 为了防止后面废话
struct student
{
	char studentID[12];		// 报名号
	char name[12];		// 姓名
	char school[12];	// 毕业学校
};

int main()
{
	ifstream infile;
	ofstream fout;
	infile.open("stulist.txt", ios::in);		// 打开文件
	if (infile.is_open() == 0)
	{
		cout << "打开文件失败" << endl;
		return -1;
	}

	int N, M;
	infile >> N >> M;		// N表示录取人数，M表示报名人数

	student* head;
	srand(static_cast<unsigned>(time(NULL))); // 设置随机种子

	head = new(nothrow)student[M];
	if (head == NULL)			// 内存申请失败处理
	{
		cout << "内存申请失败" << endl;
		return -1;
	}

	for (int i = 0; i < M; i++)					// 读入数据
	{
		infile >> head[i].studentID >> head[i].name >> head[i].school;
	}

	unsigned short* selected = new(nothrow)unsigned short[N];		// 用short就够用了
	if (selected == NULL)
	{
		cout << "内存申请失败" << endl;
		delete[]head;	// 到了这一步，head肯定已经申请成功了
		return -1;
	}

	int count = 0;
	while (count < N)
	{
		int index = rand() % M; // 生成随机索引

		// 检查索引是否已经被选择
		bool already_Selected = false;
		for (int j = 0; j < count; j++)
		{
			if (selected[j] == index)
			{
				already_Selected = true;
				break;
			}
		}

		// 如果没有被选择，记录这个索引
		if (!already_Selected)
		{
			selected[count] = index;
			count++;
		}
	}

	// 为里面的内容排序
	for (int i = 0; i < N; i++)
	{
		for (int j = i + 1; j < N; j++)
		{
			if (selected[i] > selected[j])			// 从小到大排列
			{
				int temp = selected[i];
				selected[i] = selected[j];
				selected[j] = temp;
			}
		}
	}

	// 输出内容
	fout.open("result.txt", ios::out);		// 打开文件
	if (fout.is_open() == 0)			// 错误处理
	{
		cout << "文件打开失败" << endl;
		delete[]head;
		delete[]selected;
		return -1;
	}

	cout << "结果详情请见result.txt" << endl;
	fout << "最终的挑选名单是：" << endl;
	for (int i = 0; i < N; i++)
	{
		fout << head[selected[i]].studentID << " " << head[selected[i]].name << " " << head[selected[i]].school << endl;
	}

	// 最后处理
	fout.close();
	infile.close();
	delete[]head;
	delete[]selected;
	
	return 0;
}
// 我认为这道题应该申请连续的一块空间而不是链表，因为通过随机数处理我们得到的是原名单中的第i个学生，而我们通过连续空间能直接访问到第i个元素
// 链表在这方面的复杂度比连续的空间要大