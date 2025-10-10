/* 2351136 李盛鹏 大数据 */
#include <iostream>
#include <iomanip>
#include "17-b2-date.h"
using namespace std;

int daysInMonth(int m, int y);          // 声明一下

/* --- 给出Date类的成员函数的体外实现(含友元及其它必要的公共函数)  --- */ 

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
/* 无参构造函数 */
Date::Date() :year(1900), month(1), day(1){}

/* 三参构造函数 */
Date::Date(const int& y, const int& m, const int& d)
{

    /* 三参中任何一参有问题都设置为1900-1-1 */
    if ((y < MIN_YEAR || y > MAX_YEAR) || (m < 1 || m > 12) || (d < 1 || d > daysInMonth(m, y)))
    {
        year = 1900;
        month = 1;
        day = 1;
    }
    else
    {
        year = y;
        month = m;
        day = d;
    }

}

/* 天数构造函数 */
Date::Date(const int& days)
{
    /* 由于天数是一个环所以只需考虑days>0即可 */
    int act_days = (days % MAX_DAYS + MAX_DAYS) % MAX_DAYS;     // 此时得到的是一个不大于MAX_DAYS的正数

    // 计算日期
    int totalDays = act_days;

    /* 计算年份 */
    year = 1900;
    while (totalDays >= 365)
    {
        if (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0))
        {
            if (totalDays >= 366)
            {
                totalDays -= 366;
            }
            else
            {
                break;
            }
        }
        else
        {
            totalDays -= 365;
        }
        year++;
    }

    /* 计算月份 */
    month = 1;
    while (totalDays >= daysInMonth(month, year))
    {
        totalDays -= daysInMonth(month, year);
        month++;
    }

    /* 计算日子 */
    day = totalDays + 1;
       
}
/* set函数 */
void Date::set(const int& y, const int& m, const int& d)
{
    /* 给出0，表示错误，也要设置为1900-1-1 */
    /* 三参中任何一参有问题都设置为1900-1-1 */
    if ((y < MIN_YEAR || y > MAX_YEAR) || (m < 1 || m > 12) || (d < 1 || d > daysInMonth(m, year)))
    {
        year = 1900;
        month = 1;
        day = 1;
    }
    else
    {
        year = y;
        month = m;
        day = d;
    }
}

/* get函数 */
void Date::get(int& y, int& m, int& d) const
{
    y = year;
    m = month;
    d = day;
}

/* show函数 */
void Date::show()const
{
    cout << year << "-" << setw(2)<<setfill('0') << month << "-" << setw(2) << setfill('0') << day <<setfill(' ') << endl;
}

/* 转int的类型转化函数 */
Date::operator int() const
{
    int totaldays = 0;

    /* 计算到该年一共经历了多少天 */
    for (int y = MIN_YEAR; y < year; ++y)
    {
        totaldays += (y % 4 == 0 && (y % 100 != 0 || y % 400 == 0)) ? 366 : 365;
    }

    /* 计算到该月一共经历了多少天 */
    for (int m = 1; m < month; ++m)
    {
        totaldays += daysInMonth(m, year);
    }

    /* 加上目前经历了多少天 */
    totaldays += day - 1;           // 将第一天视为0
    return totaldays;
}

/* 转化构造函数 */
Date& Date:: operator=(const int& days)       // 转化构造函数
{
    *this = Date(days);
    return *this;
}

/* 重载加函数 */
Date Date::operator+(const int &days) const
{
    Date result = *this;
    int totaldays = (int)result + days;
    return Date(totaldays);
}

/* 重载减函数 */
Date Date::operator-(const int &days)const
{
    Date result = *this;
    int totaldays = (int)result - days;
    return Date(totaldays);
}

/* 重载减函数反向 */
int Date::operator-(const Date& other) const
{
    return int(*this) - int(other);
}

/* 前置++ */
Date& Date::operator++()
{
    *this = *this + 1;
    return *this;
}

/* 后置++ */
Date Date::operator++(int)
{
    Date temp = *this;
    *this = *this + 1;
    return temp;
}

/* 前置-- */
Date& Date::operator--()
{
    *this = *this - 1;
    return *this;
}

/* 后置-- */
Date Date::operator--(int)
{
    Date temp = *this;
    *this = *this - 1;
    return temp;
}

bool Date::operator==(const Date& other)const
{
    return year == other.year && month == other.month && day == other.day;
}

bool Date::operator!=(const Date& other)const
{
    return !(year == other.year && month == other.month && day == other.day);
}

bool Date::operator<(const Date& other)const
{
    if (year != other.year) return year < other.year;
    if (month != other.month) return month < other.month;
    return day < other.day;
}

bool Date::operator>(const Date& other)const
{
    if (year != other.year) return year > other.year;
    if (month != other.month) return month > other.month;
    return day > other.day;
}

bool Date::operator>=(const Date& other)const
{
    return !(*this < other);
}

bool Date::operator<=(const Date& other)const
{
    return !(*this > other);
}

/* 如果有需要的其它全局函数的实现，可以写于此处 */
int daysInMonth(int m, int y)
{
    if (m == 2)
    {
        return (y % 4 == 0 && (y % 100 != 0 || y % 400 == 0)) ? 29 : 28;
    }
    return (m == 4 || m == 6 || m == 9 || m == 11) ? 30 : 31;
}

/* <<输出 */
ostream& operator<<(ostream& out, const Date& date)
{

    out << date.year << "-" << setw(2) << setfill('0') << date.month << "-" << setw(2) << setfill('0') << date.day <<setfill(' ') << endl;
    return out;
}
/* >>读入 */
istream& operator>>(istream& in, Date& date)
{
    int y, m, d;
    in >> y >> m >> d;
    date.set(y, m, d);

    return in;
}

Date operator+(const int& days, const Date& date)
{
    int result = days + (int)date;
    return Date(result);
}