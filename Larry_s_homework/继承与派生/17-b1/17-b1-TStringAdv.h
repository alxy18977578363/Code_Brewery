/* 2351136 李盛鹏 大数据 */
#pragma once
#define DEFAULT_SUBLEN		-1			// 缺省的len长     

#include"17-b1-TString.h"

/* 如果有需要的宏定义、只读全局变量等，写于此处 */
class TStringAdv :public TString
{
public:

	// 构造函数
	TStringAdv();
	TStringAdv(const char* str);
	TStringAdv(const TString& other);
	TStringAdv(const TStringAdv& other);
	~TStringAdv();

	// 赋值函数
	TStringAdv& assign(const TStringAdv& ts2);
	TStringAdv& assign(const char* s);

	// 追加函数
	TStringAdv& append(const TStringAdv& ts2);
	TStringAdv& append(const char* s);
	TStringAdv& append(const char& c);

	// 插入函数
	TStringAdv& insert(const TStringAdv& ts2, int pos);
	TStringAdv& insert(const char* s, int pos);
	TStringAdv& insert(const char& c, int pos);

	// 删除函数
	TStringAdv& erase(const TStringAdv& ts2);
	TStringAdv& erase(const char* s);
	TStringAdv& erase(const char& c);

	// 子串函数
	TStringAdv substr(const int pos, const int len = -1) const;

	// 访问函数
	char& at(const int n);

	// 长度函数
	friend int TStringAdvLen(const TStringAdv& str);


	/* 等号赋值 */
	TStringAdv& operator=(const TStringAdv& other);
	TStringAdv& operator=(const TString& other);
	TStringAdv& operator=(const char* str);

	/* 继承加法 */
	TStringAdv operator+(const TStringAdv& other) const;
	TStringAdv operator+(const char* str) const;
	TStringAdv operator+(const char c) const;
	
	/* 继承减法 */
	TStringAdv operator-(const TStringAdv& other)const;
	TStringAdv operator-(const char* str) const;
	TStringAdv operator-(const char c) const;
		
	/* 继承+-=操作 */
	TStringAdv& operator+=(const TStringAdv& other);
	TStringAdv& operator+=(const TString& other);
	TStringAdv& operator+=(const char* str);
	TStringAdv& operator+=(const char c);
	TStringAdv& operator-=(const TStringAdv& other);
	TStringAdv& operator-=(const TString& other);
	TStringAdv& operator-=(const char* str);
	TStringAdv& operator-=(const char c);
	TStringAdv& operator*=(int n);

	/* 继承*操作 */
	TStringAdv operator*(int n) const;
	
	
};