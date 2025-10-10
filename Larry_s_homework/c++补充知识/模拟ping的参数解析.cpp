/* 大数据 2351136 李盛鹏 */
#define _CRT_SECURE_NO_WARNINGS
#include<iostream>
#include<cstring>
using namespace std;

#define NOT_FOUND						-2				/* 操作对象没有找到 */
#define IP_WRONG						-1				/* IP是错的 */
#define NOT_PARAMETER					-1				/* 参数后面不跟着参数 */

#define MAX_OUTPUT_SIZE					100				/* 最大的输出规模 */
#define TOTAL_INPUT_RANGE				5				/* 输入最多的参数数量 */
#define DEFAULT_BUFFER_SIZE				64				/* 缺省缓冲区-l大小 */
#define MIN_BUFFER_SIZE					32				/* 最小缓冲区大小 */
#define MAX_BUFFER_SIZE					64000			/* 最大缓冲区大小 */
#define DEFAULT_FILE_NUM				4				/* 缺省缓存文件-n数量 */
#define MIN_FILE_NUM					1				/* 最小缓存文件-n数量 */
#define MAX_FILE_NUM					1024			/* 最大缓存文件-n数量 */
#define DEFAULT_Ctrl_c					0				/* 缺省的Ctrl+c停止 */
#define MIN_INP_NUM						0				/* IP每个数字的最小值 */
#define MAX_INP_NUM						255				/* IP每个数字的最大值 */

/* 存储参数的值，如果添加参数，这里需要修改 */
typedef struct Parameter
{
	int buffer_size;              // -l,表示缓冲区大小
	int file_num;                 // -n,表示要缓存的文件数量
	bool Ctrl_c;                    // -t,表示是否需要ctrl+c结束
	char IP_name[20];             // ip地址

	// 构造函数
	Parameter()
		: buffer_size(DEFAULT_BUFFER_SIZE),
		file_num(DEFAULT_FILE_NUM),
		Ctrl_c(DEFAULT_Ctrl_c)
	{
		memset(IP_name, 0, sizeof(IP_name)); // 初始化 IP_name
	}
} Parameter;


/*===一个记录参数的阈值的结构体========
1.允许的最大值
2.允许的最小值
3.缺省值
==================================*/
typedef struct parameterInfo
{
	int min;
	int max;
	int default_value;
}ParameterInfo;

/* 每一个Operator下标的含义 */
enum Operator_index{buffer_size, file_num, Ctrl_c};

/* 每一个错误提示下标的含义 */
enum Tips_index{parameter,IP_wrong,parameter_without_next_value,invalid_parameter};

const char* Operator[] = { "l","n","t" };			/* 实现的可操作的对象 */
const char* tips[] = { "参数%s不存在","IP地址错误","参数%s没有后续参数","不是以-开头的合法参数"};				/* 错误提示 */

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int usage(const char* const procname)
{
	cout << "Usage: " << procname << "  [-l 大小] [-n 数量] [-t] IP地址" << endl;
	cout << "       ==================================" << endl;
	cout << "        参数 附加参数 范围        默认值" << endl;
	cout << "       ==================================" << endl;
	cout << "        -l   1        [32..64000] 64" << endl;
	cout << "        -n   1        [1..1024]   4" << endl;
	cout << "        -t   0        [0..1]      0" << endl;
	cout << "       ==================================" << endl;

	return 0;
}

/* 判断是否以“-”开头 */
bool is_parameter_start(const char*prompt)
{
	const char* ptr = prompt;

	/* 如果第一个不是“-”，那就是false */
	return (*ptr == '-') ? true : false;
	
}

/* 判断操作的对象是谁
=============参数说明================
1.promp:操作对象
2.Operator[]:目前可供操作的对象
====================================*/
int get_Operator(const char* prompt)
{
	/* 这里只负责判断操作的对象，第一位默认是"-" */
	const char* ptr = &prompt[1];						
	
	/* 一共有多少个操作可支持 */
	int operation_count = sizeof(Operator) / sizeof(Operator[0]);

	/* 如果不是我需要的操作对象，那就判错 */
	for (int i = 0; i < operation_count; i++)
	{
		if (strcmp(ptr, Operator[i]) == 0)
		{
			return i;			
		}
	}

	/* 如果到了这里还没有找到的话，那就返回 NOT_FOUND */
	return NOT_FOUND;
}

/* 处理默认缺省参数(如果要添加对象，这里需要修改)
=============参数说明===============================================
1.int& param，要设置的对象
2.ParameterInfo info，存储某个对象最大值最小值和缺省值的对象
3.ptr_default,操作对象下一个命令，可能是缺省值 ，也可能是下一个对象
================================================================*/
int set_parameter(int& param, ParameterInfo info, const char* ptr_default)
{
	int value = atoi(ptr_default);
	/*====================================
	1.ptr_default不是值时,value==0,或者小于0
	2.ptr_default不在期望的最大最小值内
	上面两种情况都要赋缺省值
	=====================================*/
	
	if (is_parameter_start(ptr_default) || value < 0)		/* 要么没参数要么负数 */
	{
		return NOT_PARAMETER;
	}

	if (value < info.min || value > info.max)	
	{
		param = info.default_value;
	}
	else			// 否则，按照得到的数赋值
	{
		param = value;
	}

	return 0;
}


/* 下面的函数用于判断对象是否存在，存在则赋值 (如果要添加对象，这里需要修改)
* argv[]：命令行
num:该参数所在的argv下标
p1：用于存储参数的值的结构体
temp[]:输出信息
==========================================================================*/
int deal_operator(int num, Parameter& p1,int argc, char* argv[])
{
	ParameterInfo info;					// 存储 “-某参数” 最大最小值和缺省值信息的结构体
	int opIndex;
	char temp[MAX_OUTPUT_SIZE];

	// 观察是否为期望操作对象
	opIndex = get_Operator(argv[num]);

	/* 观察是否为期望操作对象 */
	if (opIndex == NOT_FOUND)
	{
		/* 没有找到操作对象，返回找不到该对象 */
		sprintf(temp, tips[parameter], argv[num]);
		cout << temp << endl;
		return NOT_FOUND;
	}
	else	/* 如果是期望的操作对象 */
	{
		/* 如果是最后已知接的是地址 */
		if (num + 1 == argc - 1)			// 报错，后一个接的不是参数
		{
			sprintf(temp, tips[parameter_without_next_value], argv[num]);
			cout << temp << endl;

			return NOT_PARAMETER;
		}

		/* 如果后面接的不是地址 */
		switch (opIndex)
		{
		case buffer_size:		// 如果是-l
			info = { MIN_BUFFER_SIZE, MAX_BUFFER_SIZE, DEFAULT_BUFFER_SIZE };

			if (num + 1 < argc)
			{
				/* 如果下一个不是参数 */
				if (set_parameter(p1.buffer_size, info, argv[num + 1]) == NOT_PARAMETER)	// 加1表示参数下一个，是否是value
				{
					sprintf(temp, tips[parameter_without_next_value], argv[num]);
					cout << temp << endl;

					return NOT_PARAMETER;
				}
			}
			break;
		case file_num:			// 如果是-n
			info = { MIN_FILE_NUM, MAX_FILE_NUM, DEFAULT_FILE_NUM };

			if (num + 1 < argc)
			{
				/* 如果下一个不是参数 */
				if (set_parameter(p1.file_num, info, argv[num + 1]) == NOT_PARAMETER)	// 加1表示参数下一个，是否是value
				{
					sprintf(temp, tips[parameter_without_next_value], argv[num]);
					cout << temp << endl;

					return NOT_PARAMETER;
				}
			}
			break;
		default:
			break;
		}
	}

	return 0;
}

/*===========================================================
下面的函数用于判断IP格式是否正确
const char *IP:表示要处理的IP

说明：如果IP不是由四个数组成，并且这四个数的值不是0~255，就输出错
=============================================================*/
int deal_IP(const char *IP)
{
	int num1, num2, num3, num4;

	/* 如果返回的数不够四个 */
	if (sscanf(IP, "%d.%d.%d.%d", &num1, &num2, &num3, &num4) != 4)
	{
		return IP_WRONG;
	}

	/* 如果四个数的值有不在0~255的 */
	if (!(num1 >= MIN_INP_NUM && num1 <= MAX_INP_NUM && num2 >= MIN_INP_NUM && num2 <= MAX_INP_NUM &&
		num3 >= MIN_INP_NUM && num3 <= MAX_INP_NUM && num4 >= MIN_INP_NUM && num4 <= MAX_INP_NUM))
	{
		return IP_WRONG;
	}

	return 0;
}

/* 参数检查通过的输出 */
void print(const Parameter& p1)
{
	cout << "参数检查通过" << endl;
	cout << "-l 参数：" << p1.buffer_size << endl;
	cout << "-n 参数：" << p1.file_num << endl;
	cout << "-t 参数：" << p1.Ctrl_c << endl;
	cout << "IP地址：" << p1.IP_name << endl;
}

/*===========所有情况===============
1.什么参数都没有，usage使用说明
2.只要第一个不是"-",就要判断是否是地址，及其是否合理
3.只要是"-"，就要判断对象是谁,对象不是预期中的，就说明不是对象
*/

int main(int argc, char* argv[])
{
	/* 如果只有一个参数，那就告知用户使用说明 */
	if (argc == 1){
		/* 使用说明的打印 */
		usage(argv[0]);
	}
	else	/* 此时参数不止一个 */
	{
		/* 定义一个参数结构体，记录每一个参数设置情况 */
		Parameter my_para;

		/* 默认IP地址是最后一位，如果IP不对，输出IP不对退出程序 */
		if (deal_IP(argv[argc - 1]) == IP_WRONG)
		{
			cout << tips[IP_wrong] << endl;
			return -1;
		}

		/* 能到这里的说明IP地址是对的，所以需要把IP地址赋值到结构体中 */
		strcpy(my_para.IP_name, argv[argc - 1]);

		for (int num = 1; num < argc - 1;)			// 这里对num不做处理，在后面的情况中做了处理
		{
			/* 如果这条是一个参数，那就处理这个参数 */
			if (is_parameter_start(argv[num]))
			{
				/* 得到当前的参数 */
				int opIndex = get_Operator(argv[num]);

				/* 如果是-t要特殊处理，因为它不用接value */
				if (opIndex != Ctrl_c)		// 不等于-t
				{
					/*====================================================
					首先，不是期望命令，会在该函数中输出xx不存在
					其次，如果是期望命令，下一个指令不是value,就按缺省赋值
					最后，如果是期望命令，并且下一个命令是value,就按value赋值
					=======================================================*/
					int result = deal_operator(num, my_para, argc, argv);
					if(result==NOT_FOUND|| result == NOT_PARAMETER){
						return result;
					}

					/* 如果参数后一个不是参数就加2，是参数就加一 */
					(num += (is_parameter_start(argv[num + 1])) ? 1 : 2);
				}
				else 
				{
					my_para.Ctrl_c = 1;
					num++;
				}

			}
			else			// 不是参数
			{
				cout << tips[invalid_parameter] << endl;
				return -1;
			}
			
		}

		/* 能到这说明全部符合题意 */
		print(my_para);
	}

	return 0;
}