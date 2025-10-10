/* 2351136 李盛鹏 大数据 */
#include <iostream>
#include <iomanip>
#include "17-b2-datetime.h"
using namespace std;

/* --- 给出DateTime类的成员函数的体外实现(含友元及其它必要的公共函数)  --- */ 
DateTime::DateTime() :Date(), Time(){}
DateTime::DateTime(const int& y, const int& m, const int& d, const int& h, const int& min, const int& s):Date(y, m, d),Time(h, min, s)
{
    int daysInMonth(int m, int y);

    /* 如果有错，那就修改 */
    if ((y < MIN_YEAR || y > MAX_YEAR) || (m < 1 || m > 12) || (d < 1 || d > daysInMonth(m, y)) ||
        (h > 23 || h < 0) || (min > 59 || min < 0) || (s > 59 || s < 0))
    {
        year = 1900;
        month = day = 1;
        hour = minute = second = 0;
    }
    
}
DateTime::DateTime(const int64_t& seconds)
{
    int days = (int)(seconds / SECONDS_SINGER_DAY);
    int act_seconds = (int)(seconds % SECONDS_SINGER_DAY);

    /* 利用临时变量得到需要的量 */
    Date temp_date(days);
    Time temp_time(act_seconds);

    int y, m, d, h, min, s;
    temp_date.get(y, m, d);
    temp_time.get(h, min, s);

    year = y;
    month = m;
    day = d;
    hour = h;
    minute = min;
    second = s;
}

void DateTime::set(const int& y, const int& m, const int& d, const int& h, const int& min, const int& s)
{
    int daysInMonth(int m, int y);

    /* 如果有错，那就修改 */
    if ((y < MIN_YEAR || y > MAX_YEAR) || (m < 1 || m > 12) || (d < 1 || d > daysInMonth(m, y)) ||
        (h > 23 || h < 0) || (min > 59 || min < 0) || (s > 59 || s < 0))
    {
        year = 1900;
        month = day = 1;
        hour = minute = second = 0;
    }
    else
    {
        Date::set(y, m, d);
        Time::set(h, min, s);
    }
}
void DateTime::get(int& y,int& m,int& d,int& h,int& min,int& s) const
{
    /* 设置日期 */
    y = year;
    m = month;
    d = day;

    /* 设置时间 */
    h = hour;
    min = minute;
    s = second;
}
void DateTime::show()const
{
    /* 由于有个endl影响，所以不得不自己写 */
    cout << year << "-" << setw(2) << setfill('0') << month << "-" << setw(2) << setfill('0') << day;
    cout << " ";
    cout << setw(2) << setfill('0') << hour << ":"
        << setw(2) << setfill('0') << minute << ":"
        << setw(2) << setfill('0') << second << setfill(' ') << endl;
}


DateTime& DateTime::operator=(const int64_t& seconds)
{
    int days = (int)(seconds / SECONDS_SINGER_DAY);
    int act_seconds = (int)(seconds % SECONDS_SINGER_DAY);

    /* 利用临时变量得到需要的量 */
    Date temp_date(days);
    Time temp_time(act_seconds);

    int y, m, d, h, min, s;
    temp_date.get(y, m, d);
    temp_time.get(h, min, s);

    year = y;
    month = m;
    day = d;
    hour = h;
    minute = min;
    second = s;
    return *this;
}
DateTime DateTime::operator+(const int& seconds) const
{
    /* 全部转为秒钟 */
    int64_t total_seconds = (long long)*this + seconds;
    return DateTime(total_seconds);
}
DateTime DateTime::operator+(const int64_t& seconds) const
{
    /* 全部转为秒钟 */
    int64_t total_seconds = (long long)*this + seconds;
    return DateTime(total_seconds);
}
DateTime DateTime::operator-(const int& seconds) const
{
    /* 全部转为秒钟 */
    int64_t total_seconds = (long long)*this - seconds;
    return DateTime(total_seconds);
}
DateTime DateTime::operator-(const int64_t& seconds) const
{
    /* 全部转为秒钟 */
    int64_t total_seconds = (long long)*this - seconds;
    return DateTime(total_seconds);
}
int64_t DateTime::operator-(const DateTime& other) const
{
    int64_t total_seconds = (long long)*this - (long long)other;

    return total_seconds;
}

DateTime::operator long long() const
{
    int64_t days = Date::operator int();
    int64_t seconds = Time::operator int();

    return days * SECONDS_SINGER_DAY + seconds;
}


/* 自增减 */
DateTime& DateTime::operator++()
{
    /* 先前hour不为0 */
    int temp_hour = hour;

    /* 时间增加 */
    Time::operator++();

    /* 如果引起日期增加 */
    if (temp_hour!=0 && hour == 0)
    {
        Date::operator++();
    }

    return *this;
}
DateTime DateTime::operator++(int)
{
    DateTime result = *this;

    /* 先前hour不为0 */
    int temp_hour = hour;

    /* 时间增加 */
    Time::operator++();

    /* 如果引起日期增加 */
    if (temp_hour != 0 && hour == 0)
    {
        Date::operator++();
    }

    return result;
}
DateTime& DateTime::operator--()
{
    /* 先前hour不为23 */
    int temp_hour = hour;

    /* 时间增加 */
    Time::operator--();

    /* 如果引起日期减少 */
    if (temp_hour != 23 && hour == 23)
    {
        Date::operator--();
    }

    return *this;
}
DateTime DateTime::operator--(int)
{
    DateTime result = *this;

    /* 先前hour不为23 */
    int temp_hour = hour;

    /* 时间增加 */
    Time::operator--();

    /* 如果引起日期减少 */
    if (temp_hour != 23 && hour == 23)
    {
        Date::operator--();
    }

    return result;
}

bool DateTime::operator==(const DateTime& other) const
{
    return Date::operator==(other) && Time::operator==(other);

}
bool DateTime::operator!=(const DateTime& other) const
{
    return !(Date::operator==(other) && Time::operator==(other));
}
bool DateTime::operator<(const DateTime& other) const
{
    if (Date::operator<(other)) return true;
    return Time::operator<(other);
}
bool DateTime::operator<=(const DateTime& other) const
{
    return !(*this > other);
}
bool DateTime::operator>(const DateTime& other) const
{
    if (Date::operator>(other)) return true;
    return Time::operator>(other);
}
bool DateTime::operator>=(const DateTime& other) const
{
    return !(*this < other);
}

ostream& operator<<(ostream& out, const DateTime& dt)
{
    /* 由于有个endl影响，所以不得不自己写 */
    out << dt.year << "-" << setw(2) << setfill('0') << dt.month << "-" << setw(2) << setfill('0') << dt.day;
    cout << " ";
    cout << setw(2) << setfill('0') << dt.hour << ":"
        << setw(2) << setfill('0') << dt.minute << ":"
        << setw(2) << setfill('0') << dt.second << setfill(' ') << endl;

    return out;
}
istream& operator>>(istream& in, DateTime& dt)
{
    int y, m, d, h, min, s;
    in >> y >> m >> d >> h >> min >> s;

    dt.set(y, m, d, h, min, s);
    return in;
}

DateTime operator+(const int& days, const DateTime& dt)
{
    return dt + days;
}


