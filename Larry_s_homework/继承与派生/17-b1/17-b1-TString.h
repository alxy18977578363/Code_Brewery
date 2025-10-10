/* 2351136 李盛鹏 大数据 */

#pragma once

#include <iostream>
using namespace std;

/* 补全TString类的定义，所有成员函数均体外实现，不要在此处体内实现 */
class TString
{
private:
	char* content;
	int   len;
	/* 根据需要定义所需的数据成员、成员函数、友元函数等 */
public:
	/* 根据需要定义所需的数据成员、成员函数、友元函数等 */
	TString();
	TString(const char* str);
	TString(const TString& other);
	~TString();

	/* 等号赋值 */
	TString& operator=(const TString& other);
	TString& operator=(const char* str);

	/* 加法运算 */
	TString operator+(const TString& other) const;
	TString operator+(const char* str) const;
	TString operator+(const char c)const;


	/* 索引操作 */
	char& operator[](int index);
	const char& operator[](int index) const;

	friend TString operator+(const char* str, const TString& other);
	friend TString operator+(const char c, const TString& other);

	/* 自增操作 */
	TString& operator+=(const TString& other);
	TString& operator+=(const char* str);
	TString& operator+=(const char c);

	/* 减法 */
	TString operator-(const TString& other)const;
	TString operator-(const char* str)const;
	TString operator-(const char c)const;

	/* 自减操作 */
	TString& operator-=(const TString& other);
	TString& operator-=(const char* str);
	TString& operator-=(const char c);

	/* 复制操作 */
	TString operator*(int n) const;

	/* 自己复制操作 */
	TString& operator*=(int n);

	/* 反转 */
	TString operator!() const;

	/* 比较操作 */
	bool operator==(const TString& other) const;
	bool operator!=(const TString& other) const;
	bool operator<(const TString& other) const;
	bool operator>(const TString& other) const;
	bool operator<=(const TString& other) const;
	bool operator>=(const TString& other) const;

	/* 输入输出 */
	friend ostream& operator<<(ostream& out, const TString& str);
	friend istream& operator>>(istream& in, TString& str);

	/* 取长度 */
	int length() const;

	/* 取字符串操作 */
	const char* c_str() const;

};

/* 如果有其它全局函数需要声明，写于此处 */
int TStringLen(const TString& str);