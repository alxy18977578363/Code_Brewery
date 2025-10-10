/* 2351136 李盛鹏 信03 */
#include <iostream>
using namespace std;

#define  N  10	/* 假设最多转换10个数字 */

/* 不允许再定义其它函数、全局变量 */

int main()
{
	/* 如果有不需要的变量，允许删除，但不允许添加或替换为其它类型的变量 */
	char str[256], * p;
	int  a[N] = { 0 }, * pnum, * pa;
	bool is_num;

	/* 上面的定义不准动(删除不需要的变量除外)，下面为程序的具体实现，要求不得再定义任何变量、常量、常变量 */

	//要求用户输入一个字符串
	cout << "请输入间隔含有若干正负数字的字符串" << endl;
	gets_s(str);

	//用*p去历遍str函数,pnum和pa的差值代表了数字的数量，pa用来存储数字。
	p = str;
	pnum = a;
	pa = a;
	
	for (p; *p != '\0'; p++) {
		//在每次开始前都默认是数字
		is_num = true;

		//如果是数字，那就把先前的数字向前移动一位，再加上这个数字。当先前是0时，其实就相当于是0+num。解决连着数字做整体的要求
		if (*p >= '0' && *p <= '9') {
			*pa = *pa * 10 + *p - '0';
		}
		//如果不是数字，置为false
		else {
			is_num = false;
		}

		//如果在p的读取时，前一个是数字，下一个是其他字符，那么pa地址++，存下一个数
		if (!is_num && *(p - 1) >= '0' && *(p - 1) <= '9'||(is_num&& *(p+1)=='\0')) {
			pa++;
			if (pa - pnum == N) {
				break;
			}
		}

	}

	//输出有几个数字并且每个数字是几
	cout << "共有" << pa - pnum << "个整数" << endl;

	//输出这些整数
	for (; pnum != pa; pnum++) {
		cout << *pnum << " ";
	}
	cout << endl;

	return 0;
}