/* 2351136 李盛鹏 信03 */
#define _CRT_SECURE_NO_WARNINGS		//使用了VS认为unsafe的函数
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <ctime>
#include <conio.h>	//用getch，因此不需要支持Linux
#include <string.h>	//Dev/CB的strlen需要
using namespace std;

struct tj_time {
	int tj_year;	//表示年份
	int tj_month;	//表示月(1-12)
	int tj_day;	//表示日(1-28/29/30/31)
	int tj_hour;	//表示小时(0-23)
	int tj_minute;	//表示分(0-59)
	int tj_second;	//表示秒(0-59)
};

/* 可以在此定义其它需要的函数 */
bool isLeapYear(int year)
{
	//如果这个数能被4整除但不能被100整除，返回真
	//如果这个数能被400整除，返回真
	return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}


/***************************************************************************
  函数名称：wait_for_enter
  功    能：给出提示并等待回车键
  输入参数：const char* const prompt = NULL
  返 回 值：void
  说    明：形参默认是空指针，输出"按回车键继续"，否则输出指针内容
***************************************************************************/
void wait_for_enter(const char* const prompt = NULL)
{
	if ((prompt == NULL) || (strlen(prompt) == 0)) //思考一下，||的左右两个条件能否互换
		cout << endl << "按回车键继续";
	else
		cout << endl << prompt << "，按回车键继续";

	while (_getch() != '\r')
		;
	cout << endl << endl;
}

/***************************************************************************
  函数名称：system_time_output
  功    能：调用系统的转换函数将整型秒值转换为与本题相似的结构体并输出
  输入参数：const time_t input_time
  返 回 值：void
  说    明：
***************************************************************************/
void system_time_output(const time_t input_time)  //time_t的本质是64位无符号整数
{
	struct tm* tt;	//struct tm 为系统定义的结构体

	tt = localtime(&input_time);	//localtime为系统函数

	/* tm_*** 为struct tm中的成员，和本题的struct tj_time具体的内容不完全符合，具体含义自己查找相关资料 */
	cout << setfill('0') << setw(4) << tt->tm_year + 1900 << '-'
		<< setw(2) << tt->tm_mon + 1 << '-'
		<< setw(2) << tt->tm_mday << ' '
		<< setw(2) << tt->tm_hour << ':'
		<< setw(2) << tt->tm_min << ':'
		<< setw(2) << tt->tm_sec << endl;

	return;
}

/***************************************************************************
  函数名称：tj_time_output
  功    能：自定义转换结果输出函数
  输入参数：const struct tj_time* const tp
  返 回 值：void
  说    明：
***************************************************************************/
void tj_time_output(const struct tj_time* const tp)
{
	/* 实现自定义结构的输出，输出形式与system_time_output相同 */
	cout << setfill('0') << setw(4) << tp->tj_year << '-'
		<< setw(2) << tp->tj_month << '-'
		<< setw(2) << tp->tj_day << ' '
		<< setw(2) << tp->tj_hour << ':'
		<< setw(2) << tp->tj_minute << ':'
		<< setw(2) << tp->tj_second << endl;
}

/***************************************************************************
  函数名称：tj_time_convert
  功    能：自定义转换函数
  输入参数：int input_time
  返 回 值：struct tj_time*
  说    明：输入一个时间，返回result的地址
***************************************************************************/
struct tj_time* tj_time_convert(int input_time)
{
	static struct tj_time result;	//定义静态局部变量，不准动

	/* 实现过程开始，在下面添加相应的定义及执行语句即可 */

		//下面两个变量记录了闰年的时长和平年的时长,year表示起始年份
		int leapyear = 366 * 24 * 60 * 60, common_year = 365 * 24 * 60 * 60, year = 1970;

		//下面的变量为最终结果，在最后会赋值到result中。hour初始为8表示东八区，下面也有一处特殊处理
		int month = 1, day = 1, hour = 0, minute = 0, second = 0;

		//补上8小时东八区的误差
		input_time += 8 * 60 * 60;

		//下面这个循环能将input_time减小到一年时间以下，最后year的值即为题目所要的year
		while (input_time >= common_year) {            
			//如果是闰年，减去一个闰年的时间
			if (isLeapYear(year)&& input_time >= leapyear)
				input_time -= leapyear;
			else     //如果是平年，减去一个平年的时间
				input_time -= common_year;

			//增加一年
			year++;
		}
		
		//定义一个数组mouth_day，记录每个月的日数，为了方便阅读，数组浪费一个位置
		int month_day[13] = { 0,31,0,31,30,31,30,31,31,30,31,30,31 };
		month_day[2] = 28 + isLeapYear(year);     //为二月赋值，如果今年是闰年，则二月为29天，否则为28天

		//下面这个循环从一月到十二月减少对应月份的时间
		for (int i = 1; i <= 12; i++) {
			if (input_time >= month_day[i] * 24 * 60 * 60) {
				//减去这个月的时间
				input_time -= (month_day[i] * 24 * 60 * 60);
			}
			else {
				break;
			}

			month++;
		}

		//下面这个表达式表达的是第几日
		day += input_time / (24 * 60 * 60);
		
		//把input_time减去这几日的时间  因为day初始化为1，所以实际上只增加了day-1天，减去这些天
		input_time -= ((day-1) * 24 * 60 * 60);

		//下面计算的是第几个小时
		hour+= input_time / (60 * 60);

		//把input_time减去这小时的时间,减8表示东八区
		input_time -= (hour *60 * 60);

		//下面计算的是第几分钟
		minute += input_time / 60;

		//把input_time减去这几分钟的时间
		input_time -= (minute * 60);

		//下面计算的是第几秒
		second += input_time;

		//一一赋值
		result.tj_year = year;
		result.tj_month = month;
		result.tj_day = day;
		result.tj_hour = hour;
		result.tj_minute = minute;
		result.tj_second = second;
	
		


	/* 实现过程结束 */

	return &result;	//注意，返回的是静态局部变量的地址，本语句不准动
}

/***************************************************************************
  函数名称：main
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int main()
{
	int read_time;
	struct tj_time* tp;

	for (;;) {
		cin >> read_time; //因为采用输入重定向，此处不加任何提示

		/* 输入错误或<0则退出循环 */
		if (cin.good() == 0 || read_time < 0)
			break;

		cout << "秒数             : " << read_time << endl;
		cout << "系统转换的结果   : ";
		system_time_output(read_time);

		cout << "自定义转换的结果 : ";
		tp = tj_time_convert(read_time);
		tj_time_output(tp);

		wait_for_enter();
	}

	if (1) {
		struct tj_time* tp;
		int t = (int)time(0);		//系统函数，取当前系统时间（从1970-01-01 00:00:00开始的秒数）

		cout << "当前系统时间     : " << t << endl;
		cout << "系统转换的结果   : ";
		system_time_output(t);

		cout << "自定义转换的结果 : ";
		tp = tj_time_convert(t);
		tj_time_output(tp);

		wait_for_enter();
	}

	return 0;
}