/* 大数据 2351136 李盛鹏 */
#include <iostream>
using namespace std;

template<typename T, size_t N>
/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void test(T (& array)[N])	// 首先要用引用，否则默认是传入指针，指针不能携带N
{
	cout << sizeof(array) << endl;	//array为形参名
}

/***************************************************************************
  函数名称：tj_strcpy_s
  功    能：将s的字符串拷贝到前一个地址中
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
template<typename T, typename T1,size_t N>
char* tj_strcpy_s(T (& dst)[N], T1 src)	//将...替换为相应内容
{
	char* d = dst;		//dst为要复制的目标串
	const char* s = src;	//src为要复制的源串

	while (*s != '\0' && d - dst < int(sizeof(dst)) - 1)
		*d++ = *s++;
	*d = '\0';

	return dst;
}

/***************************************************************************
  函数名称：main()
  功    能：完成函数的测试
  输入参数：无
  返 回 值：int
  说    明：
***************************************************************************/
int main()
{
	int t1[10];
	double t2[20];
	test(t1);	//期望输入40
	test(t2);	//期望输出160

	char s1[10], s2[20];
	const char* s = "Welcome to Tongji University!";
	cout << tj_strcpy_s(s1, s) << '*' << endl; //期望输出：Welcome t*
	cout << tj_strcpy_s(s2, s) << '*' << endl; //期望输出：Welcome to Tongji U*

	return 0;
}