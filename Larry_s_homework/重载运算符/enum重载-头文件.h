/* 2351136 李盛鹏 大数据 */
#pragma once

#include <iostream>
using namespace std;

enum week
{
	sun, mon, tue, wed, thu, fri, sat
};

/* 允许添加相应的函数声明 */
ostream& operator<<(ostream& out, const week& w);
istream& operator>>(istream& in, week& w);

// 重载递增递减运算符
week& operator++(week& w);
week operator++(week& w, int);
week& operator--(week& w);
week operator--(week& w, int);

// 重载加减运算符
week operator+(const week& w, int n);
week operator-(const week& w, int n);

week& operator+=(week& w, const int n);
week& operator-=(week& w, const int n);
