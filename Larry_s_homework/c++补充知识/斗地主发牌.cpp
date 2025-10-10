/* 2351136 李盛鹏 大数据 */
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <time.h>
/* 如果有需要，此处可以添加头文件 */

using namespace std;

/* 允许定义常变量/宏定义，但不允许定义全局变量 */
#define TOTAL_NUM				54				// 总共有五十四张牌
#define A_KIND_TOTAL			13				// 一种花色有13张牌
#define COLOR_RANGE				4				// 共有四种花色
#define ALL_TURNS				17				// 总发牌轮数

/* 可以添加自己需要的函数 */
/* 这个函数要求用户来选择地主 */
void choose_landlord(int& landlord)
{
	/* 错误处理 */
	while (true)
	{
		cout << "请选择一个地主[0-2]:" << endl;
		cin >> landlord;

		/* 如果输入非法 */
		if (!cin.good())
		{
			cin.clear();
			cin.ignore(65536, '\n');
			continue;
		}

		/* 即便正确输入也要清除后面的输入 */
		cin.clear();
		cin.ignore(65536, '\n');

		/* 到了这里说明输入的不是非法 */
		if (landlord > 2 || landlord < 0)
		{
			continue;
		}

		/* 到了这里，landlord肯定是合理的范围 */
		break;
	}
}

/* 将剩下的牌发给地主 */
void left_to_landlord(unsigned long long* player, const int landlord)
{
	/* 所有的牌 */
	unsigned long long ALL = 0x002fffffffffffff;		// 由于要用到异或，所以全部都置于1	

	/* 已经发出去的牌是 */
	unsigned long long give_out = player[0] | player[1] | player[2];

	/* 剩下的牌 */
	unsigned long long left = ALL^give_out;

	/* 将剩下的牌发给地主 */
	player[landlord] |= left;
}

/***************************************************************************
  函数名称：print
  功    能：打印某个玩家的牌面信息，如果是地主，后面加标记
  输入参数：prompt携带输出的牌的来源的信息, landlord表示为地主, player表示输出的信息
  返 回 值：
  说    明：
 ***************************************************************************/
int print(const char* prompt, const bool landlord, const unsigned long long player)
{
	/* 只允许定义不超过三个基本类型的简单变量，不能定义数组变量、结构体、string等 */
	enum Flower_colors{Club = 0, Diamond, Heart, Spade};

	if (prompt)
	{
		cout << prompt;
	}

	/* 这里不包括大小王 */
	for (int i = 0; i < TOTAL_NUM - 2; i++)
	{
		bool own_or_not = (player >> i) & 1;

		if (own_or_not)
		{
			char color = i % COLOR_RANGE;
			switch (color)
			{
			case Club:   
				cout << char(5);
				break;
			case Diamond:
				cout << char(4); 
				break;
			case Heart: 
				cout << char(3);
				break;
			case Spade:
				cout << char(6);
				break;
			}

			int value = i / COLOR_RANGE;		//  因为是3333  4444 这样子存储的，所以要除以颜色种类
			if (value <= 6)						// 3~9的扑克最小，用value值0~7表示
			{
				cout << (value + 3) << " ";
			}
			else
			{
				const char* values[] = { "T","J", "Q", "K", "A", "2" };
				cout << values[value - 7] << " ";
			}
		}
	}

	for (int i = TOTAL_NUM - 2; i < TOTAL_NUM; i++)
	{
		bool own_or_not = (player >> i) & 1;
		if (own_or_not)
		{
			cout << (i == TOTAL_NUM - 2 ? "BJ " : "RJ ");
		}
	}

	if (landlord)
	{
		cout << "(地主)";
	}

	cout << endl;
	return 0;
}

/***************************************************************************
  函数名称：deal
  功    能：发牌（含键盘输入地主）
  输入参数：unsigned long long* player
  返 回 值：
  说    明：
 ***************************************************************************/
int deal(unsigned long long* player)
{
	/* 只允许定义不超过十个基本类型的简单变量，不能定义数组变量、结构体、string等 */
	srand((unsigned)time(NULL));		// 播撒随机种子

	int dealnum = 0;					// 这个表示你抽到的牌

	for (int turns = 1; turns <= ALL_TURNS; turns++)
	{
		for (int p = 0; p < 3; p++)
		{
			while (true)
			{
				dealnum = rand() % TOTAL_NUM;

				if ((player[0] >> dealnum & 1) || (player[1] >> dealnum & 1) || (player[2] >> dealnum & 1))
				{
					continue;
				}

				player[p] |= (1ULL << dealnum);
				break;
			}
		}

		cout << "第" << turns << "轮结束：" << endl;
		print("甲的牌：", false, player[0]);
		print("乙的牌：", false, player[1]);
		print("丙的牌：", false, player[2]);
	}

	/* 要求用户选择地主 */
	int landlord;
	choose_landlord(landlord);

	/* 将剩下的牌发给地主 */
	left_to_landlord(player, landlord);

	return landlord; //此处修改为选定的地主(0-2)
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：main函数，不准修改
 ***************************************************************************/
int main()
{
	unsigned long long player[3] = { 0 }; //存放三个玩家的发牌信息
	int landlord; //返回0-2表示哪个玩家是地主

	cout << "按回车键开始发牌";
	while (getchar() != '\n')
		;

	landlord = deal(player);
	print("甲的牌：", (landlord == 0), player[0]);
	print("乙的牌：", (landlord == 1), player[1]);
	print("丙的牌：", (landlord == 2), player[2]);

	return 0;
}