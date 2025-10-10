/* 2351136 李盛鹏 大数据 */
#pragma once

#include <iostream>
using namespace std;

/* 如果有其它全局函数需要声明，写于此处 */
int daysInMonth(int m, int y);

/* 如果有需要的宏定义、只读全局变量等，写于此处 */
#define  MIN_YEAR  1900
#define  MAX_YEAR  2099
#define	 MIN_DAY	1
#define  MAX_DAY	73049

/* 补全Date类的定义，所有成员函数均体外实现，不要在此处体内实现 */
class Date
{
private:
	int year;
	int month;
	int day;
	/* 不允许添加数据成员 */
public:
	/* 根据需要定义所需的成员函数、友元函数等(不允许添加数据成员) */
	Date();				// 无参构造
	Date(const int& y, const int& m, const int& d);		// 三参构造
	Date(const int& days);								/* 从天数构造 */

	void set(const int& y = 0, const int& m = 1, const int& d = 1);			// set设置函数
	void get(int& y, int& m, int& d) const;						// 取得当前日期
	void show();												// 展示日期

	operator int() const;										// 转为int的类型转化函数
	Date& operator=(const int& d);								// 转化构造函数

	Date operator+(const int days) const;
	Date operator-(const int days) const;
	int operator-(const Date& d) const;

	Date& operator++();
	Date operator++(int);
	Date& operator--();
	Date operator--(int);

	friend ostream& operator<<(ostream& out, const Date& date);
	friend istream& operator>>(istream& in, Date& date);

	bool operator==(const Date& other) const;
	bool operator!=(const Date& other) const;
	bool operator<(const Date& other) const;
	bool operator<=(const Date& other) const;
	bool operator>(const Date& other) const;
	bool operator>=(const Date& other) const;
};

