/* 2351136 李盛鹏 大数据 */
#pragma once

#include <iostream>
using namespace std;

/* 如果有其它全局函数需要声明，写于此处 */
#define MIN_YEAR		1900
#define MAX_YEAR		2099
#define MAX_DAYS		73049

/* Date类的声明 */ 
class Date {
protected:
	/* 除这三个以外，不允许再定义任何数据成员 */ 
	int year;
	int month;
	int day;
public:
	/* 允许需要的成员函数及友元函数的声明 */
	Date();				// 无参构造
	Date(const int& y, const int& m, const int& d);		// 三参构造
	Date(const int& days);								/* 从天数构造 */

	void set(const int& y = 1900, const int& m = 1, const int& d = 1);			// set设置函数
	void get(int& y, int& m, int& d) const;						// 取得当前日期
	void show()const;												// 展示函数

	operator int() const;										// 转为int的类型转化函数

	Date& operator=(const int& days);								// 转化构造函数
	Date operator+(const int &days) const;
	Date operator-(const int &days) const;
	int operator-(const Date& d) const;

	Date& operator++();
	Date operator++(int);
	Date& operator--();
	Date operator--(int);

	bool operator==(const Date& other) const;
	bool operator!=(const Date& other) const;
	bool operator<(const Date& other) const;
	bool operator<=(const Date& other) const;
	bool operator>(const Date& other) const;
	bool operator>=(const Date& other) const;

	friend ostream& operator<<(ostream& out, const Date& date);
	friend istream& operator>>(istream& in, Date& date);
	friend Date operator+(const int& days, const Date& date);
	/* 允许加入友元声明（如果有必要） */

};
