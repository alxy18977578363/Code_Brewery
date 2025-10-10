/* 2351136 李盛鹏 大数据 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string.h>
#include"17-b1-TStringAdv.h"

/*===============================*/
/* 下面是继承类的函数 */
/*===============================*/

// 构造函数
TStringAdv::TStringAdv() : TString()
{
}

TStringAdv::TStringAdv(const char* str) : TString(str)
{
}

TStringAdv::TStringAdv(const TStringAdv& other) : TString(other)
{
}

TStringAdv::~TStringAdv()
{
}

TStringAdv::TStringAdv(const TString& other):TString(other)
{

}

// 赋值函数
TStringAdv& TStringAdv::assign(const TStringAdv& ts2)
{
	/* 在TString中已经实现 */
	*this = ts2;
	return *this;
}

TStringAdv& TStringAdv::assign(const char* s)
{
	*this = s;
	return *this;
}

// 追加函数
TStringAdv& TStringAdv::append(const TStringAdv& ts2)
{
	*this += ts2;
	return *this;
}

TStringAdv& TStringAdv::append(const char* s)
{
	*this += s;
	return *this;
}

TStringAdv& TStringAdv::append(const char& c)
{
	*this += c;
	return *this;
}

// 插入函数
TStringAdv& TStringAdv::insert(const TStringAdv& ts2, int pos)
{
	if (pos < 1 || pos > length() + 1)
	{
		return*this;
	}

	// 插入到字符串最前
	if (pos == 1)
	{
		TStringAdv temp = ts2 + *this; // 将 ts2 插入到字符串最前
		*this = temp;
	}
	// 插入到字符串最后
	else if (pos == length() + 1)
	{
		TStringAdv temp = *this + ts2; // 将 ts2 插入到字符串最后
		*this = temp;
	}
	// 插入到字符串中间
	else
	{
		TStringAdv temp = substr(1, pos - 1) + ts2 + substr(pos, length() - pos + 1);
		*this = temp;
	}
	return *this;
}

TStringAdv& TStringAdv::insert(const char* s, int pos)
{
	if (pos < 1 || pos > length() + 1)
	{
		return*this;
	}

	// 插入到字符串最前
	if (pos == 1)
	{
		TStringAdv temp = s + *this; // 将 ts2 插入到字符串最前
		*this = temp;
	}
	// 插入到字符串最后
	else if (pos == length() + 1)
	{
		TStringAdv temp = *this + s; // 将 ts2 插入到字符串最后
		*this = temp;
	}
	// 插入到字符串中间
	else
	{
		TStringAdv temp = substr(1, pos - 1) + s + substr(pos, length() - pos + 1);
		*this = temp;
	}

	return *this;
}

TStringAdv& TStringAdv::insert(const char& c, int pos)
{
	if (pos < 1 || pos > length() + 1)
	{
		return*this;
	}

	/* 如果插入的是\0，则\0后都删除 */
	if (c == '\0')
	{
		*this = substr(1, pos - 1);
		return *this;
	}

	// 插入到字符串最前
	if (pos == 1)
	{
		TStringAdv temp = c + *this; // 将 ts2 插入到字符串最前
		*this = temp;
	}
	// 插入到字符串最后
	else if (pos == length() + 1)
	{
		TStringAdv temp = *this + c; // 将 ts2 插入到字符串最后
		*this = temp;
	}
	// 插入到字符串中间
	else
	{
		TStringAdv temp = substr(1, pos - 1) + c + substr(pos, length() - pos + 1);
		*this = temp;
	}

	return *this;
}

// 删除函数
TStringAdv& TStringAdv::erase(const TStringAdv& ts2)
{
	TString::operator-=(ts2);
	return *this;
}

TStringAdv& TStringAdv::erase(const char* s)
{
	TString::operator-=(s);
	return *this;
}

TStringAdv& TStringAdv::erase(const char& c)
{
	TString::operator-=(c);
	return *this;
}

// 子串函数
TStringAdv TStringAdv::substr(const int pos, const int len) const
{
	/* 位置不符合题意 */
	if (pos<1 || pos>length())
	{
		return TStringAdv();		// 返回一个空的对象
	}

	int act_len = (len == DEFAULT_SUBLEN) ? length() : len;
	act_len = min(act_len, length());				// 一方面不破坏小于0的事实，另一方面能取到超过length长度的len

	if (act_len <= 0)
	{
		return TStringAdv();
	}

	/* 活到这说明len合格 */
	char* subContent = new char[act_len + 1];
	if (!subContent)
	{
		exit(-1);
	}
	strncpy(subContent, c_str() + pos - 1, act_len);
	subContent[act_len] = '\0';		// 补充\0

	TStringAdv result(subContent);
	delete[] subContent;
	return result;
}

// 访问函数
char& TStringAdv::at(const int n)
{
	return (*this)[n];		// 处理都在[n]内
}

// 长度函数
int TStringAdvLen(const TStringAdv& str)
{
	return str.length();
}


TStringAdv& TStringAdv::operator=(const TStringAdv& other)
{
	TString::operator=(other);
	return *this;
}

TStringAdv& TStringAdv::operator=(const TString& other)
{
	TString::operator=(other);
	return *this;
}

TStringAdv& TStringAdv::operator=(const char* str)
{
	TString::operator=(str);
	return *this;
}
TStringAdv TStringAdv::operator+(const TStringAdv& other) const
{
	return TStringAdv(TString::operator+(other));
}

TStringAdv TStringAdv::operator+(const char* str) const
{
	return TStringAdv(TString::operator+(str));
}

TStringAdv TStringAdv::operator+(const char c) const
{
	return TStringAdv(TString::operator+(c));
}

TStringAdv TStringAdv::operator-(const TStringAdv& other) const
{
	return TStringAdv(TString::operator-(other));
}

TStringAdv TStringAdv::operator-(const char* str) const
{
	return TStringAdv(TString::operator-(str));
}

TStringAdv TStringAdv::operator-(const char c) const
{
	return TStringAdv(TString::operator-(c));
}

TStringAdv& TStringAdv::operator+=(const TStringAdv& other)
{
	TString::operator+=(other);
	return *this;
}

TStringAdv& TStringAdv::operator+=(const TString& other)
{
	TString::operator+=(other);
	return *this;
}

TStringAdv& TStringAdv::operator+=(const char* str)
{
	TString::operator+=(str);
	return *this;
}

TStringAdv& TStringAdv::operator+=(const char c)
{
	TString::operator+=(c);
	return *this;
}

TStringAdv& TStringAdv::operator-=(const TStringAdv& other)
{
	TString::operator-=(other);
	return *this;
}

TStringAdv& TStringAdv::operator-=(const TString& other)
{
	TString::operator-=(other);
	return *this;
}

TStringAdv& TStringAdv::operator-=(const char* str)
{
	TString::operator-=(str);
	return *this;
}

TStringAdv& TStringAdv::operator-=(const char c)
{
	TString::operator-=(c);
	return *this;
}

TStringAdv TStringAdv::operator*(int n) const
{
	TStringAdv result = *this;
	result *= n;
	return result;
}

TStringAdv& TStringAdv::operator*=(int n)
{
	TString::operator*=(n);
	return *this;
}