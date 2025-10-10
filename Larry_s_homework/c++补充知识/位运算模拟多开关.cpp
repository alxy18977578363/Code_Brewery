/* 2351136 大数据 李盛鹏 */
#define  _CRT_SECURE_NO_WARNINGS

#include<iostream>
#include <stdio.h>
#include<cstring>
#include <cctype> 
#include<iomanip>

#define MAX_LENGTH				100			// 最长的输入内容长度
#define daxie_start				'A'
#define daxie_end				'J'
#define stop_num				'Q'
#define NOT_INITED				-999		// 没有初始化就用这个值表示
#define INITED					1			// 初始化就用这个值表示

using namespace std;

/* 下面这个函数用来把目标字符变成大写 */
void topper_char(char *src)
{
	if (*src >= 'a' && *src <= 'z')
	{
		*src -= 32;
	}
}

/* 下面这个函数用来把目标字符串变成大写 */
void topper_string(char *src)
{
	/* 将地址赋值给ptr */
	char* ptr = src;

	while (*ptr != '\0')
	{
		/* 将这个字符变成大写 */
		topper_char(ptr);
		ptr++;
	}
}

/*================================================== 
下面的函数根据输入的命令和对象进行开关操作
short &my_switch:我现在开关表，在该函数中修改开关关系
const char* object：我要操作的具体switch是哪一个
const char command[]：我的操作是on还是off
====================================================*/
void turn_switch(short &my_switch,const char* object, const char command[])
{

	// 确保对象在'A'到'H'的范围内
	if (*object < daxie_start || *object > daxie_end)
	{
		return; // 处理无效输入
	}

	// 计算开关位置
	short switchMask = 1 << (*object - 'A');

	if (strcmp(command, "ON") == 0)
	{
		// 打开开关
		my_switch |= switchMask; // 使用“或”运算打开开关
	}
	else if (strcmp(command, "OFF") == 0)
	{
		// 关闭开关
		my_switch &= ~switchMask; // 使用“与”运算关闭开关
	}

}

/*==================================================
下面的函数根据输入的命令和对象进行开关操作
short &my_switch:我现在开关表，在该函数中修改开关关系
====================================================*/
void print_switch(const short& my_switch)
{
	/* 定义一个bool数组记录每一个开关的开关情况
	要加一，实际数量比相减大一
	==========================================*/
	bool status[daxie_end - daxie_start + 1] = { 0 };

	// 提取每一位的开关状态
	for (int bit_num = 0; bit_num < daxie_end - daxie_start + 1; ++bit_num)
	{
		status[bit_num] = (my_switch >> bit_num) & 1;        // 直接使用位与操作
	}

	/* 输出"A  B  C  D..." */
	for (int bit_num = 0; bit_num < daxie_end - daxie_start + 1; bit_num++)
	{
		cout << setw(4) << setiosflags(ios::left) << (char)('A' + bit_num);
	}
	cout << endl;

	/* 输出“on  off   on   off”  */
	for (int bit_num = 0; bit_num < daxie_end - daxie_start + 1; bit_num++)
	{
		if (status[bit_num] == 0)
		{
			cout << setw(4) << setiosflags(ios::left) << "OFF";
		}
		else
		{
			cout << setw(4) << setiosflags(ios::left) << "ON";
		}
	}
	// 恢复默认对齐
	cout << resetiosflags(ios::left);

	cout << endl;
}

/* 要求读入Q on和off才能退出，如果不是on或者off还不能退出 */
int main()
{
	short my_switch=0;		//  short型的开关，从最低位开始往前十个记录A~J十个开关的开关记录
	char command[10] = { 0 };							//  命令行的读入
	char object = 0;									//  命令的对象
	int inited = NOT_INITED;									//  确认是否是初始化过

	/* 输出初始状态 */


	/* 错误处理，只有正确的指令可以离开这个循环 */
	while (true)
	{
		/* 如果初始化过，就输出当前状态，否则输出初始状态 */
		if (inited == NOT_INITED)			//  没有初始化过
		{
			/* 输出初始状态 */				// 用零填充	// short有4个四位 
			cout << "初始状态：" << "0x" << setfill('0') << setw(4)<< hex << (short)my_switch << endl;      // 设置宽度为2
			// 恢复默认填充字符
			std::cout << std::setfill(' '); // 将填充字符还原为默认空格

			print_switch(my_switch);

			inited = INITED;		// 
		}

		if (inited == INITED)
		{
			/* 要求用户按照格式输入 */
			cout << endl << "请以(\"A On / J Off\"形式输入，输入\"Q on / off\"退出)" << endl;

			/* 读入整个命令 */
			cin >> object >> command;			
			
		}
		

		/* 将读入的指令和对象进行大写改变 */
		topper_char(&object);
		topper_string(command);

		/* 只有符合题目要求的才可以带入函数 */
		/* 要么是退出，要么是我期望的对象 */
		if ((object >= daxie_start && object <= daxie_end) || object == stop_num)
		{
			/* 要么是on，要么是off */
			if (strcmp(command, "ON") == 0 || strcmp(command, "OFF") == 0)
			{
				/* 如果是daxie_end，就要退出程序 */
				if (object == stop_num)
				{
					return 0;
				}

				/* 到了这里说明object不是stop_num */
				turn_switch(my_switch, &object, command);

				cout << "当前状态：" << "0x" << setfill('0') << setw(4) << hex << (short)my_switch << endl;
				// 恢复默认填充字符
				std::cout << std::setfill(' '); // 将填充字符还原为默认空格

				print_switch(my_switch);
			}

		}

		/* 不管是否输入正确，都要从头 */
		continue;
	}
	

}