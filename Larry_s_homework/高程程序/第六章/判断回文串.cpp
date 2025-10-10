/* 2351136 李盛鹏 信03 */
#include <iostream>
#define length 80
using namespace std;

//下面这个函数，能够判断是否是回文串
bool judge_huiwen(char* start, char* end)
{
	//is_huiwen作为返回值对象，如果是true则为回文。
	bool is_huiwen = true;
	//历遍ch，如果两个指针一直相等，则是回文
	while (start < end) {
		//为方便阅读，因此这里不做简化，当*start和*end相等时，向下推一位
		if (*start == *end) {
			start++;
			end--;
		}
		else {
			is_huiwen = false;
			break;
		}
	}

	return is_huiwen;
}



//主函数，用以调用是否回文串的函数。main负责用fgets输入字符串，引用函数，根据返回来给出yes或no
int main()
{
	//要求用户输入一个字符串
	cout << "请输入一个长度小于" << length << "的字符串（回文串）" << endl;

	char ch[length];
	//下面这行用fgets读入字符串，读入时会读入空格，会读入回车
	fgets(ch, length,stdin);
	// 去除末尾的换行符
	ch[strcspn(ch, "\n")] = '\0';
	
	char* start = ch;
	char* end = ch + strlen(ch)-1;

	if (judge_huiwen(start, end)) {
		cout << "yes" << endl;
	}
	else {
		cout << "no" << endl;
	}

	return 0;

}