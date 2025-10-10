/* 2351136 李盛鹏 大数据 */

/* 允许添加需要的头文件、宏定义等 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <string.h>
#include "17-b1-TString.h"
using namespace std;

/* 给出 TString 类的所有成员函数的体外实现 */

/* 构造函数 */
TString::TString() :content(nullptr), len(0)
{
}

/* 字符串转化构造函数 */
TString::TString(const char* str)
{
	/* 根据str做出抉择 */
	if (str && strlen(str) != 0)
	{
		len = strlen(str);
		content = new char[len + 1];
		if (!content)
		{
			exit(-1);
		}
		strcpy(content, str);
	}
	else
	{
		content = nullptr;
		len = 0;
	}
}

/* 同类型构造 */
TString::TString(const TString& other)
{
	if (other.content)
	{
		len = other.len;
		content = new char[len + 1];
		if (!content)
		{
			exit(-1);
		}
		strcpy(content, other.content);
	}
	else
	{
		content = nullptr;
		len = 0;
	}
}

/* 析构函数 */
TString::~TString()
{
	if (content)
	{
		delete[]content;
	}
}

/* 等号赋值 */
TString& TString:: operator=(const TString& other)
{
	/* 为了效率，如果本来就相同，不用操作了 */
	if (this != &other)
	{
		if (content)
		{
			delete[]content;
		}

		if (other.content)
		{
			len = other.len;
			content = new char[len + 1];
			if (!content)
			{
				exit(-1);
			}
			strcpy(content, other.content);
		}
		else
		{
			content = nullptr;
			len = 0;
		}
	}

	return *this;
}

/* 等号赋值 */
TString& TString::operator=(const char* str)
{
	/* 删除旧空间 */
	if (content)
	{
		delete[]content;
	}

	if (str && strlen(str) != 0)
	{
		len = strlen(str);
		content = new char[len + 1];
		if (!content)
		{
			exit(-1);
		}
		strcpy(content, str);
	}
	else
	{
		content = nullptr;
		len = 0;
	}

	return *this;
}

/* 加法 */
TString TString:: operator+ (const TString& other)const
{
	/* result经过初始化，已经是0，nullptr */
	TString result;

	if (content && other.content)
	{
		result.len = len + other.len;
		result.content = new char[result.len + 1];
		if (!result.content)
		{
			exit(-1);
		}
		strcpy(result.content, content);
		strcat(result.content, other.content);
	}
	else if (content)
	{
		result = *this;
	}
	else if (other.content)
	{
		result = other;
	}

	return result;
}

TString TString:: operator+ (const char* str)const
{
	TString result;
	if (content && str)
	{
		result.len = len + strlen(str);
		result.content = new char[result.len + 1];
		if (!result.content)
		{
			exit(-1);
		}
		strcpy(result.content, content);
		strcat(result.content, str);
	}
	else if (content)
	{
		result = *this;
	}
	else if (str)
	{
		result = TString(str);
	}

	return result;
}

TString TString::operator+(const char c)const
{


	TString result;
	if (content)
	{
		result.len = len + 1;
		result.content = new char[result.len + 1];
		if (!result.content)
		{
			exit(-1);
		}
		strcpy(result.content, content);
		result.content[len] = c;
		result.content[len + 1] = '\0';
	}
	else
	{
		result.len = 1;
		result.content = new char[2];
		if (!result.content)
		{
			exit(-1);
		}
		result.content[0] = c;
		result.content[1] = '\0';
	}

	return result;
}

/* 友元函数 */
TString operator+(const char* str, const TString& other)
{
	TString result;
	if (str && other.content)
	{
		result.len = strlen(str) + other.len;
		result.content = new char[result.len + 1];
		if (!result.content)
		{
			exit(-1);
		}
		strcpy(result.content, str);
		strcat(result.content, other.content);
	}
	else if (str)
	{
		result = TString(str);
	}
	else if (other.content)
	{
		result = other;
	}
	return result;
}

TString operator+(char c, const TString& other)
{

	TString result;
	if (other.content)
	{
		result.len = 1 + other.len;
		result.content = new char[result.len + 1];
		if (!result.content)
		{
			exit(-1);
		}
		result.content[0] = c;
		strcpy(result.content + 1, other.content);
	}
	else
	{
		result.len = 1;
		result.content = new char[2];
		if (!result.content)
		{
			exit(-1);
		}
		result.content[0] = c;
		result.content[1] = '\0';
	}
	return result;
}

TString& TString::operator+=(const TString& other)
{
	if (other.content)
	{
		char* newContent = new char[len + other.len + 1];
		if (!newContent)
		{
			exit(-1);
		}
		if (content)
		{
			strcpy(newContent, content);
			strcat(newContent, other.content);
		}
		else
		{
			strcpy(newContent, other.content);
		}
		delete[] content;
		content = newContent;
		len += other.len;
	}

	return *this;
}
TString& TString::operator+=(const char* str)
{
	if (str)
	{
		char* newContent = new char[len + strlen(str) + 1];
		if (!newContent)
		{
			exit(-1);
		}
		if (content)
		{
			strcpy(newContent, content);
			strcat(newContent, str);
		}
		else
		{
			strcpy(newContent, str);
		}
		delete[] content;
		content = newContent;
		len += strlen(str);
	}

	return *this;
}
TString& TString::operator+=(const char c)
{
	/* 如果添加不合法，直接返回就行 */
	if (c=='\0')
	{
		return *this;
	}

	char* newContent = new char[len + 2];
	if (!newContent)
	{
		exit(-1);
	}
	if (content)
	{
		strcpy(newContent, content);
		newContent[len] = c;
		newContent[len + 1] = '\0';
	}
	else
	{
		newContent[0] = c;
		newContent[1] = '\0';
	}
	delete[] content;
	content = newContent;
	len += 1;
	return *this;
}

/* 减法 */
TString TString::operator-(const TString& other) const
{
	TString result = *this;
	if (other.content)
	{
		char* pos = strstr(result.content, other.content);
		if (pos)
		{
			int newLen = result.len - other.len;
			char* newContent = new char[newLen + 1];
			if (!newContent)
			{
				exit(-1);
			}
			strncpy(newContent, result.content, pos - result.content);
			strcpy(newContent + (pos - result.content), pos + other.len);
			delete[] result.content;
			result.content = newContent;
			result.len = newLen;
		}
	}
	return result;
}

TString TString::operator-(const char* str) const
{
	TString result = *this;
	if (str)
	{
		char* pos = strstr(result.content, str);
		if (pos)
		{
			int newLen = result.len - strlen(str);
			char* newContent = new char[newLen + 1];
			if (!newContent)
			{
				exit(-1);
			}
			strncpy(newContent, result.content, pos - result.content);
			strcpy(newContent + (pos - result.content), pos + strlen(str));
			delete[] result.content;
			result.content = newContent;
			result.len = newLen;
		}
	}
	return result;
}

TString TString::operator-(char c) const
{
	if (c=='\0')
	{
		return *this;
	}

	TString result = *this;
	char* pos = strchr(result.content, c);
	if (pos)
	{
		int newLen = result.len - 1;
		char* newContent = new char[newLen + 1];
		if (!newContent)
		{
			exit(-1);
		}
		strncpy(newContent, result.content, pos - result.content);
		strcpy(newContent + (pos - result.content), pos + 1);
		delete[] result.content;
		result.content = newContent;
		result.len = newLen;
	}
	return result;
}

TString& TString::operator-=(const TString& other)
{
	if (other.content)
	{
		// 检查 content 是否为 NULL
		if (content == NULL)
		{
			return *this;
		}

		char* pos = strstr(content, other.content);
		if (pos)
		{
			int newLen = len - other.len;
			char* newContent = new char[newLen + 1];
			if (!newContent)
			{
				exit(-1);
			}
			strncpy(newContent, content, pos - content);
			strcpy(newContent + (pos - content), pos + other.len);
			delete[] content;
			content = newContent;
			len = newLen;
		}
	}
	return *this;
}

TString& TString::operator-=(const char* str)
{
	if (str)
	{
		// 检查 content 是否为 NULL
		if (content == NULL)
		{
			return *this;
		}

		char* pos = strstr(content, str);
		if (pos)
		{
			int newLen = len - strlen(str);
			char* newContent = new char[newLen + 1];
			if (!newContent)
			{
				exit(-1);
			}
			strncpy(newContent, content, pos - content);
			strcpy(newContent + (pos - content), pos + strlen(str));
			delete[] content;
			content = newContent;
			len = newLen;
		}
	}
	return *this;
}

TString& TString::operator-=(char c)
{
	// 检查 content 是否为 NULL
	if (content == NULL)
	{
		return *this;
	}

	char* pos = strchr(content, c);
	if (pos)
	{
		int newLen = len - 1;
		char* newContent = new char[newLen + 1];
		if (!newContent)
		{
			exit(-1);
		}
		strncpy(newContent, content, pos - content);
		strcpy(newContent + (pos - content), pos + 1);
		delete[] content;
		content = newContent;
		len = newLen;
	}
	return *this;
}

TString TString::operator*(int n) const
{
	TString result;
	if (content && n > 0)
	{
		result.len = len * n;
		result.content = new char[result.len + 1];
		if (!result.content)
		{
			exit(-1);
		}
		for (int i = 0; i < n; ++i)
		{
			strcpy(result.content + i * len, content);
		}
	}
	return result;
}

TString& TString::operator*=(int n)
{
	if (content && n > 0)
	{
		int newLen = len * n;
		char* newContent = new char[newLen + 1];
		if (!newContent)
		{
			exit(-1);
		}
		for (int i = 0; i < n; ++i)
		{
			strcpy(newContent + i * len, content);
		}
		delete[] content;
		content = newContent;
		len = newLen;
	}
	return *this;
}

TString TString::operator!() const
{
	TString result = *this;
	if (content)
	{
		for (int i = 0; i < len / 2; ++i)
		{
			char temp = result.content[i];
			result.content[i] = result.content[len - i - 1];
			result.content[len - i - 1] = temp;
		}
	}
	return result;
}

bool TString::operator==(const TString& other) const
{
	if (len != other.len) return false;
	if (content == nullptr && other.content == nullptr) return true;
	if (content == nullptr || other.content == nullptr) return false;
	return strcmp(content, other.content) == 0;
}

bool TString::operator!=(const TString& other) const
{
	return !(*this == other);
}

bool TString::operator<(const TString& other) const
{
	if (content == nullptr && other.content == nullptr) return false;
	if (content == nullptr) return true;
	if (other.content == nullptr) return false;
	return strcmp(content, other.content) < 0;
}

bool TString::operator>(const TString& other) const
{
	if (content == nullptr && other.content == nullptr) return false;
	if (content == nullptr) return false;
	if (other.content == nullptr) return true;
	return strcmp(content, other.content) > 0;
}

bool TString::operator<=(const TString& other) const
{
	if (content == nullptr && other.content == nullptr) return true;
	if (content == nullptr) return true;
	if (other.content == nullptr) return false;
	return strcmp(content, other.content) <= 0;
}

bool TString::operator>=(const TString& other) const
{
	if (content == nullptr && other.content == nullptr) return true;
	if (content == nullptr) return false;
	if (other.content == nullptr) return true;
	return strcmp(content, other.content) >= 0;
}

char& TString::operator[](int index)
{
	return content[index];
}

const char& TString::operator[](int index) const
{
	return content[index];
}

int TString::length() const
{
	return len;
}

const char* TString::c_str() const
{
	return content;
}

ostream& operator<<(ostream& out, const TString& str)
{
	if (str.content&& str.len)
	{
		out << str.content;
	}
	else
	{
		out << "<EMPTY>";
	}
	return out;
}

istream& operator>>(istream& in, TString& str)
{
	char buffer[1024];
	in >> buffer;
	str = buffer;
	return in;
}


int TStringLen(const TString& str)
{
	return str.length();
}

