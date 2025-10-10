/* 2351136 李盛鹏 大数据 */
#pragma once

#include "17-b2-date.h"
#include "17-b2-time.h"
#include <cstdint>

/* 如果有其它全局函数需要声明，写于此处 */
#define SECONDS_SINGER_DAY	86400		// 一天86400秒

/* DateTime类的基本要求：
	1、不允许定义任何数据成员
	2、尽量少定义成员函数 
*/

class DateTime:public Date, public Time {
protected:
	/* 不允许再定义任何数据成员 */ 

public:
	/* 不允许再定义任何数据成员，允许需要的成员函数及友元函数的声明 */
	DateTime();
	DateTime(const int &y,const int& m,const int& d,const int& h,const int& min,const int& s);
    DateTime(const int64_t& seconds);


    DateTime& operator=(const int64_t& seconds);
    DateTime operator+(const int& seconds) const;
    DateTime operator+(const int64_t& seconds) const;
    DateTime operator-(const int& seconds) const;
    DateTime operator-(const int64_t& seconds) const;
    int64_t operator-(const DateTime& other) const;

    

    void set(const int& y = 1900, const int& m = 1, const int& d = 1, const int& h = 0, const int& min = 0, const int& s = 0);
    void get(int& y, int& m, int& d, int& h, int& min, int& s) const;
    void show()const;

    DateTime& operator++();
    DateTime operator++(int);
    DateTime& operator--();
    DateTime operator--(int);

    bool operator==(const DateTime& other) const;
    bool operator!=(const DateTime& other) const;
    bool operator<(const DateTime& other) const;
    bool operator<=(const DateTime& other) const;
    bool operator>(const DateTime& other) const;
    bool operator>=(const DateTime& other) const;

    friend ostream& operator<<(ostream& out, const DateTime& dt);
    friend istream& operator>>(istream& in, DateTime& dt);
    friend DateTime operator+(const int& days, const DateTime& dt);

    operator long long() const;

	/* 允许加入友元声明（如果有必要） */

};
