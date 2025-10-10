/* 2351136 李盛鹏 大数据 */
#pragma once

#include <iostream>
using namespace std;

#define SECONDS_SINGER_DAY	86400		// 一天86400秒

/* 如果有其它全局函数需要声明，写于此处 */

/* Time类的声明 */ 
class Time {
protected:
	/* 除这三个以外，不允许再定义任何数据成员 */ 
	int hour;
	int minute;
	int second;
public:
	/* 允许需要的成员函数及友元函数的声明 */
	Time();			// 三种类型构造
	Time(const int &h,const int &m,const int &s);
	Time(const int &s);

	void set(const int &h = 0,const int &m = 0,const int &s = 0);
	void get(int& h, int& m, int& s) const;
	void show()const;

	Time& operator=(const Time& other);
	Time operator+(const int &seconds) const;
	Time operator-(const int &seconds) const;
	int operator-(const Time& other)const;

	/* 自加减运算符 */
	Time& operator++();
	Time operator++(int);
	Time& operator--();
	Time operator--(int);
	Time& operator+=(const int&seconds);
	Time& operator-=(const int&seconds);

	/* 比较运算符重载 */
	bool operator==(const Time& other)const;
	bool operator>(const Time& other)const;
	bool operator>=(const Time& other)const;
	bool operator<(const Time& other)const;
	bool operator<=(const Time& other)const;
	bool operator!=(const Time& other)const;
	
	/* 输入输出运算符重载 */
	friend ostream& operator<<(ostream& out, const Time& t);
	friend istream& operator>>(istream& in, Time& t);

	operator int() const;
	/* 允许加入友元声明（如果有必要） */

};
