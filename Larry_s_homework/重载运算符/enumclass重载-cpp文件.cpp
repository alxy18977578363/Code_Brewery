/* 2351136 李盛鹏 大数据 */

/* 允许添加需要的头文件、宏定义等 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string>
#include <algorithm>
#include "16-b6.h"

using namespace std;
const char* WEEK_IN_CHINESE[] = { "星期日","星期一","星期二","星期三","星期四","星期五","星期六"};

#define WRONG_WEEK  -1        
                              
/* 辅助函数 */                 
week string_to_week(const string& str)
{
    /* 小写整个week，方便大小写不敏感 */
    string lower_str = str;
    transform(lower_str.begin(), lower_str.end(), lower_str.begin(), ::tolower);

    if (lower_str == "sun" || lower_str == "星期日") return week::sun;
    if (lower_str == "mon" || lower_str == "星期一") return week::mon;
    if (lower_str == "tue" || lower_str == "星期二") return week::tue;
    if (lower_str == "wed" || lower_str == "星期三") return week::wed;
    if (lower_str == "thu" || lower_str == "星期四") return week::thu;
    if (lower_str == "fri" || lower_str == "星期五") return week::fri;
    if (lower_str == "sat" || lower_str == "星期六") return week::sat;

    return static_cast<week>(WRONG_WEEK);       // 
}

bool is_week_valid(const week w)
{
    return  (w >= week::sun && w <= week::sat);
}

/* 给出 enum 类的所有成员函数的体外实现 */
ostream& operator<<(ostream& out, const week& w)
{
    if (is_week_valid(w))
        out << WEEK_IN_CHINESE[((int(w) % 7) + 7) % 7];
    else
        out << "错误";
    return out;
}

istream& operator>>(istream& in, week& w)
{
    string input;
    in >> input;
    w = string_to_week(input);
    return in;
}

// 重载递增运算符
week& operator++(week& w)           // 前置++
{
    w = static_cast<week>(abs(int(w) + 1) % 7);
    return w;
}

/* 后置++ */
week operator++(week& w,int)           // 后置++
{
    week result= w;
    w = static_cast<week>(abs(int(w) + 1) % 7);
    return result;
}

week& operator--(week& w)
{
    w = ((int(w) - 1) < 0) ? week::sat : static_cast<week>((int(w) - 1) % 7);
    return w;
}
week operator--(week& w, int)
{
    week result = w;
    w = ((int(w) - 1) < 0) ? week::sat : static_cast<week>((int(w) - 1) % 7);
    return result;
}

week operator+(const week& w, int n)
{
    return static_cast<week>((static_cast<int>(w) + n) % 7);
}

week operator-(const week& w, int n)
{
    return static_cast<week>((static_cast<int>(w) - (n % 7) + 7) % 7);
}

week& operator+=(week& w, const int n)
{
    w = static_cast<week>((static_cast<int>(w) + n) % 7);
    return w;
}

week& operator-=(week& w, const int n)
{
    w = static_cast<week>((static_cast<int>(w) + 7 - (n % 7)) % 7);
    return w;
}