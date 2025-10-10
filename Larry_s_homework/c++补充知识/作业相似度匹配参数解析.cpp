/* 大数据 2351136 李盛鹏 */
#define _CRT_SECURE_NO_WARNINGS
#include<iostream>
#include<cstring>
using namespace std;

#define MAX_ID				7				/* 最长的id是七位数 */
#define MAX_CPP_NAME		32				/* 最长的cpp名字长度 */
#define MAX_TXT_NAME		32				/* 最长的TXT名字长度 */
#define DEFAULT_MATCH_GATE	80				/* 缺省的阈值 */

/* 该枚举表示每一个输入main函数的参数的下标含义 */
enum meaning
{
	id_To_Check = 1, id_To_match, cpp_name, match_gate, txt_name
};			// 从1开始，因为0代表demo的名字

/* 这个枚举指的是每一个错误提示下标对应的意义 */
enum TipIndex
{
	TIP_INVALID_LENGTH,
	TIP_INVALID_DIGIT,
	TIP_CHECK_ALL,
	TIP_MATCH_INVALID_LENGTH,
	TIP_MATCH_INVALID_DIGIT,
	TIP_CPP_TOO_LONG,
	TIP_OUTPUT_FILENAME_TOO_LONG,
	TIP_COUNT // 记录提示信息的数量
};


/* ==============================
检查id里面的数字长度
1.length:数字的长度
2.ptr：学号字符串
函数遇到字母就终止计数
===================================*/
void check_id_length(int &length,const char *ptr)
{
	/* 长度初始化为0 */
	length = 0;
	while (*ptr != '\0')
	{
		/* 如果遇到了期望之外的字符，就退出这个函数，length不再改变 */
		if (*ptr < '0' || *ptr > '9')
		{
			return;
		}

		/* 能到这的说明都是正常数字 */
		length++;

		// 移动到下一个字符
		ptr++;
	}
}

/* 处理检查学号是否合格的函数 */
int is_id_valid(const char*prompt, const char* length_Message, const char* digit_Message)
{
	/* 如果学号长度不是7位，首先就判不过 */
	if (strlen(prompt) != MAX_ID)
	{

		/* 输出长度不足 */
		if (length_Message)
		{
			cout << length_Message << endl;
			return -1;
		}

	}

	/* 如果学号内有字母，有可能导致不是七位 */
	int length = 0;

	check_id_length(length, prompt);
	if (length != MAX_ID)
	{
		/* 输出数字的长度不足 */
		if (digit_Message)
		{
			cout << digit_Message << endl;
			return -1;
		}
		return -1;
	}

	/* 如果都足 */
	return 0;
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int usage(const char* const procname)
{
	cout << "Usage: " << procname << " 要检查的学号/all 匹配学号/all 源程序名/all 相似度阀值(60-100) 输出(filename/screen)" << endl << endl;
	cout << "e.g. : " << procname << " 2159999 2159998 all       80 screen" << endl;
	cout << "       " << procname << " 2159999 all     14-b1.cpp 75 result.txt" << endl;
	cout << "       " << procname << " all     all     14-b2.cpp 80 check.dat" << endl;
	cout << "       " << procname << " all     all     all       85 screen" << endl;

	return 0;
}

/* 参数检查通过的输出 */
void print(char* argv[])
{
	cout << "参数检查通过" << endl;
	cout << "检查学号：" << argv[id_To_Check] << endl;
	cout << "匹配学号：" << argv[id_To_match] << endl;
	cout << "源文件名：" << argv[cpp_name] << endl;

	// 将输入的匹配阈值转换为整数
	int threshold = atoi(argv[match_gate]); // argv[1]为第一个命令行参数

	// 检查匹配阈值
	if (threshold < 60 || threshold > 100)
	{
		threshold = DEFAULT_MATCH_GATE; // 设置缺省值
	}

	// 输出匹配阈值
	cout << "匹配阈值：" << threshold << endl;
	cout << "输出目标：" << argv[txt_name] << endl;
}


int main(int argc, char* argv[])
{
	/* 如果只有一个参数，那就进行检查 */
	if (argc <= 5||argc > 6)				// 我一共有五个参数，少于五个就不行
	{
		usage(argv[0]);
	}
	else		// 输出我读到的数据
	{

		char temp1[100];					/* 暂时要输出的内容 */
		char temp2[100];					
		const char* tips[] = { "要检查的学号不是%d位",
							"要检查的学号不是%d位数字",
							"检查学号是all，匹配学号必须是all",
							"要匹配的学号不是%d位",
							"要匹配的学号不是%d位数字",
							"源程序文件名超过%d字节",
							"输出结果文件名超过了%d字节"
		};

		/* 如果检查的学号是all，那么匹配的学号也要是all */
		if (strcmp(argv[id_To_Check], "all") == 0)
		{
			/* 如果检查学号不是all，那么就输出错误提示 */
			if (strcmp(argv[id_To_match], "all") != 0)
			{
				sprintf(temp1, tips[TIP_CHECK_ALL], MAX_ID);			/* tips[2]表示前后都要是all */
				cout << temp1 << endl;

				return -1;
			}
		}
		else				// 如果第一项不是all，那就要照例进行学号检查
		{
			/* 检查第一个学号是否符合题意 */
			{
				/* 将提示信息temp里 */
				sprintf(temp1, tips[TIP_INVALID_LENGTH], MAX_ID);			/* TIP_INVALID_LENGTH表示将要检查的学号位数 */
				sprintf(temp2, tips[TIP_INVALID_DIGIT], MAX_ID);			/* TIP_INVALID_DIGIT表示要检查的学号数字位数 */

				/* 检查是否第一个学号是符合题意的 */
				if (is_id_valid(argv[id_To_Check], temp1, temp2) == -1)
				{
					return -1;
				}
			}


			/* 检查第二个学号是否符合题意,如果是all，通过 */
			if (strcmp(argv[id_To_match], "all") == 0)
			{
				;
			}
			else					/* 如果不是all */
			{
				/* 将匹配的学号赋值入temp里 */
				sprintf(temp1, tips[TIP_MATCH_INVALID_LENGTH], MAX_ID);			/* TIP_MATCH_INVALID_LENGTH表示将要匹配的学号位数 */
				sprintf(temp2, tips[TIP_MATCH_INVALID_DIGIT], MAX_ID);			/* TIP_MATCH_INVALID_DIGIT表示要匹配的学号数字位数 */

				/* 检查是否第一个学号是符合题意的 */
				if (is_id_valid(argv[id_To_match], temp1, temp2) == -1)
				{
					return -1;
				}
			}
		}

		


		/* 如果输入的cpp文件太长 */
		if (strlen(argv[cpp_name]) > MAX_CPP_NAME)
		{
			sprintf(temp1, tips[TIP_CPP_TOO_LONG], MAX_CPP_NAME);
			cout << temp1 << endl;
			return -1;
		}

		/* 如果txt的长度超过32 */
		if (strlen(argv[txt_name]) > MAX_TXT_NAME)
		{
			sprintf(temp1, tips[TIP_OUTPUT_FILENAME_TOO_LONG], MAX_TXT_NAME);
			cout << temp1 << endl;
			return -1;
		}

	
		/* 能到这说明全部符合题意 */
		print(argv);

	}

	return 0;
}