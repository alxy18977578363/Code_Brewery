/* 2351136 李盛鹏 信03 */
#include <iostream>
using namespace std;

/* 1、不允许定义任何类型的全局变量，包括常变量及宏定义等
   2、不允许给出任何形式的全局函数
*/

/* --- 将类的定义补充完整 --- */
class Days
{
private:
	int year;
	int month;
	int day;
	//除上面的三个private数据成员外，不再允许添加任何类型的数据成员

	/* 下面可以补充需要的类成员函数的定义（不提供给外界，仅供本类的其它成员函数调用，因此声明为私有，数量不限，允许不定义） */

public:
	int calc_days();     //计算是当年的第几天

	/* 下面可以补充其它需要的类成员函数的定义(体外实现)，数量不限，允许不定义 */
	Days(int input_year,int input_month,int input_day);
};

/* --- 此处给出类成员函数的体外实现 --- */
Days::Days(int input_year, int input_month, int input_day)
{
	year = input_year;
	month = input_month;
	day = input_day;
}

int Days::calc_days()
{
	//先判断是否是闰年
	bool is_leap_year = (year % 4 == 0 && year % 100 != 0 || year % 400 == 0);

	//定义一个数组，记录每个月的天数（这里为了月份一一对应，浪费部分空间）
	int month_day[13] = { 0,31,28,31,30,31,30,31,31,30,31,30,31 };
	//二月天数特殊处理
	if (is_leap_year)
	{
		month_day[2] = 29;
	}
	else
		month_day[2] = 28;

	//错误处理，包括月份不对，日月关系不对
	//月份不对
	if (month > 12 || month < 1)
	{
		return -1;           //-1表示错误
	}

	//日月关系错误
	if (day > month_day[month])
	{
		return -1;           
	}

	//计算天数
	int allday = 0;
	//一直加到第month-1月，第month月加上day即可
	for (int i = 1; i < month; i++)
	{
		allday += month_day[i];
	}
	allday += day;

	return allday;

}
/***************************************************************************
  函数名称：main()
  功    能：负责调用Days这个类的公共接口，达到最后的输出
  输入参数：
  返 回 值：
  说    明：main函数不准动
 ***************************************************************************/
int main()
{
	if (1)
	{
		Days d1(2020, 3, 18);
		cout << "应该输出78， 实际是：" << d1.calc_days() << endl;
	}

	if (1)
	{
		Days d1(2023, 3, 18);
		cout << "应该输出77， 实际是：" << d1.calc_days() << endl;
	}

	if (1)
	{
		Days d1(2020, 12, 31);
		cout << "应该输出366，实际是：" << d1.calc_days() << endl;
	}

	if (1)
	{
		Days d1(2023, 12, 31);
		cout << "应该输出365，实际是：" << d1.calc_days() << endl;
	}

	if (1)
	{
		Days d1(2020, 2, 29);
		cout << "应该输出60， 实际是：" << d1.calc_days() << endl;
	}

	if (1)
	{
		Days d1(2023, 2, 29);
		cout << "应该输出-1， 实际是：" << d1.calc_days() << endl;
	}

	return 0;
}