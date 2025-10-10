/* 2351136 李盛鹏 大数据 */
#include <iostream>
#include <iomanip>
#include "17-b2-time.h"
using namespace std;

/* --- 给出Time类的成员函数的体外实现(含友元及其它必要的公共函数)  --- */ 

// 三种类型构造
Time::Time():hour(0),minute(0),second(0){}
Time::Time(const int& h, const int& m, const int& s)
{
	/* 任何一个错误都设置为0时0分0秒 */
	if ((h > 23 || h < 0) || (m > 59 || m < 0) || (s > 59 || s < 0))
	{
		hour = minute = second = 0;
	}
	else
	{
		hour = h;
		minute = m;
		second = s;
	}
}
Time::Time(const int& s)
{
	int total_second = ((s % SECONDS_SINGER_DAY) + SECONDS_SINGER_DAY) % SECONDS_SINGER_DAY;

	/* 计算时钟 */
	hour = total_second / 3600;
	total_second = total_second % 3600;

	/* 计算分钟 */
	minute = total_second / 60;
	total_second = total_second % 60;

	/* 计算秒钟 */
	second = total_second;
}

/* set函数 */
void Time::set(const int& h, const int& m, const int& s)
{
	/* 任何一个错误都设置为0时0分0秒 */
	if ((h > 23 || h < 0) || (m > 59 || m < 0) || (s > 59 || s < 0))
	{
		hour = minute = second = 0;
	}
	else
	{
		hour = h;
		minute = m;
		second = s;
	}
}

/* get函数 */
void Time::get(int& h, int& m, int& s) const
{
	h = hour;
	m = minute;
	s = second;
}

/* show函数 */
void Time::show()const
{
	cout << setw(2) << setfill('0') << hour << ":"
		<< setw(2) << setfill('0') << minute << ":"
		<< setw(2) << setfill('0') << second << setfill(' ') << endl;

}

/* 基础加减赋值 */
Time& Time::operator=(const Time& other)
{
	if (this != &other)
	{
		hour = other.hour;
		minute = other.minute;
		second = other.second;
	}
	return *this;
}
Time Time::operator+(const int& seconds) const
{
	int result = (int)(*this) + seconds;
	return Time(result);
}
Time Time::operator-(const int& seconds) const
{
	int result = (int)(*this) - seconds;
	return Time(result);
}
int Time::operator-(const Time& other)const
{
	int result = (int)(*this) - (int)other;
	return result;
}

/* 自加减运算符 */
Time& Time::operator++()
{
	*this = *this + 1;
	return *this;
}
Time Time::operator++(int)
{
	Time result = *this;
	*this = *this + 1;
	return result;
}
Time& Time::operator--()
{
	*this = *this - 1;
	return *this;
}
Time Time::operator--(int)
{
	Time result = *this;
	*this = *this - 1;
	return result;
}
Time& Time::operator+=(const int& seconds)
{
	*this = *this + seconds;
	return *this;
}
Time& Time::operator-=(const int& seconds)
{
	*this = *this - seconds;
	return *this;
}

/* 比较运算符重载 */
bool Time::operator==(const Time& other)const
{
	return hour == other.hour && minute == other.minute && second == other.second;
}
bool Time::operator!=(const Time& other)const
{
	return !(hour == other.hour && minute == other.minute && second == other.second);
}
bool Time::operator>(const Time& other)const
{
	if (hour != other.hour)		return hour > other.hour;
	if (minute != other.minute)		return minute > other.minute;
	return second > other.second;
}
bool Time::operator>=(const Time& other)const
{
	return !(*this < other);
}
bool Time::operator<(const Time& other)const
{
	if (hour != other.hour)		return hour < other.hour;
	if (minute != other.minute)		return minute < other.minute;
	return second < other.second;

}
bool Time::operator<=(const Time& other)const
{
	return !(*this > other);
}


/* 输入输出运算符重载 */
ostream& operator<<(ostream& out, const Time& t)
{
	out << setw(2) << setfill('0') << t.hour << ":"
		<< setw(2) << setfill('0') << t.minute << ":"
		<< setw(2) << setfill('0') << t.second << setfill(' ') << endl;

	return out;
}
istream& operator>>(istream& in, Time& t)
{
	int h, m, s;
	in >> h >> m >> s;
	t.set(h, m, s);
	return in;
}

/* 类型转化函数 */
Time::operator int() const
{
	unsigned int total_second = hour * 3600 + minute * 60 + second;
	return total_second;
}