/* 2351136 李盛鹏 大数据 */
#include <iostream>
#include "16-b4.h"
using namespace std;


/* 给出 Date 类的所有成员函数的体外实现 */

/* 无参构造函数 */
Date::Date():year(2000), month(1), day(1){}

/* 三参构造函数 */
Date::Date(const int &y, const int &m, const int &d)
{
    year = (y < MIN_YEAR || y > MAX_YEAR) ? 2000 : y;
    month = (m < 1 || m > 12) ? 1 : m;

    /* 由于year应该是实际存入的，所以这里用year */
    day = (d < 1 || d > daysInMonth(m, year)) ? 1 : d;
    
}

/* 天数构造函数 */
Date::Date(const int& days)
{
    if (days <= 1)
    {
        year = 1900;
        month = 1;
        day = 1;
    }
    else if (days >= 73049)
    {
        year = 2099;
        month = 12;
        day = 31;
    }
    else
    {
        // 计算日期
        int totalDays = days - 1;
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
        month = 1;
        while (totalDays >= daysInMonth(month, year))
        {
            totalDays -= daysInMonth(month, year);
            month++;
        }
        day = totalDays + 1;

    }
}

/* set函数 */
void Date::set(const int& y, const int& m, const int& d)
{
    /* 如果输入的为0就保持不变，如果输入不为0,缺省是一月一号，年份不能缺省 */
    if (y != 0)
    {
        year = (y < MIN_YEAR || y > MAX_YEAR) ? 2000 : y;
    }
    if (m != 0)
    {
        month = (m < 1 || m > 12) ? 1 : m;
    }
    if (d != 0)
    {
        day = (d < 1 || d > daysInMonth(month, year)) ? 1 : d;
    }

    /* 判断最后的值是否符合题意 */
    if (day > daysInMonth(month, year))
    {
        day = 1;
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
void Date::show()
{
    cout << year << " 年 " << month << " 月 " << day << " 日" << endl;
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
    totaldays += day;
    return totaldays;
}

/* 转化构造函数 */
Date& Date:: operator=(const int& d)       // 转化构造函数
{
    /* 任何小于1的都是1900.1.1 */
    if (d <= MIN_DAY)
    {
        year = 1900;
        month = 1;
        day = 1;
        return*this;
    }

    /* 任何超过最大的都是2099.12.31 */
    else if (d >= MAX_DAY)
    {
        year = 2099;
        month = 12;
        day = 31;
        return*this;
    }

    else
    {
        /* 接下来是正经的计算 */
        int totalDays = d - 1; // 从1900.1.1开始的天数
        year = 1900;

        /* 计算年份 */
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

        // 剩余的天数就是日期
        day = totalDays + 1;

        return *this;
    }
   
}				

/* 重载加函数 */
Date Date::operator+(const int days) const
{
    Date result = *this;
    int totaldays = (int)result + days;
    return Date(totaldays);
}

/* 重载减函数 */
Date Date::operator-(const int days)const
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

bool Date::operator==(const Date&other)const
{
    return year == other.year && month == other.month && day == other.day;
}

bool Date::operator!=(const Date&other)const
{
    return !(year == other.year && month == other.month && day == other.day);
}

bool Date::operator<(const Date&other)const
{
    if (year != other.year) return year < other.year;
    if (month != other.month) return month < other.month;
    return day < other.day;
}

bool Date::operator>(const Date&other)const
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
    out << date.year << " 年 " << date.month << " 月 " << date.day << " 日" << endl;
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