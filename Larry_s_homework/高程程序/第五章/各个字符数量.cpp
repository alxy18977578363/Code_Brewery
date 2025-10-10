/* 信03 2351136 李盛鹏 */
#include <iostream>
#include<string.h>
#define sentence 3
#define length 128

using namespace std;

//引用下面这个函数，读入输入的话到字符数组中
void my_cin(char str[][length])
{
	for (int i = 1; i <= sentence; i++) {
		//给出输入提示
		cout << "请输入第" << i << "行" << endl;
		cin.getline(str[i-1], length);
	}
}


int main()
{
	//定义数组并且带到输入的函数中
	char str[sentence][length] = { 0 };
	my_cin(str);

	//通过str里面的ASCII码值来计数

	//5个类型的符号的对应变量
	int DaXie = 0, XiaoXie = 0, Number = 0, Space = 0, Others = 0;

	//逐个寻找ASCII码值
	int i = 0, j = 0;
	for (i = 0; i < sentence; i++) {
		for(j=0;j<length&&str[i][j];j++){
			for (j = 0; j < length && str[i][j]; j++) {
				if (str[i][j] >= 'A' && str[i][j] <= 'Z') {
					DaXie++;
				}
				else if (str[i][j] >= 'a' && str[i][j] <= 'z') {
					XiaoXie++;
				}
				else if (str[i][j] >= '1' && str[i][j] <= '9') {
					Number++;
				}
				else if (str[i][j] == ' ') {
					Space++;
				}
				else {
					Others++;
				}
			}
		}
	}
	

	//打印各个类型字符有多少个
	cout << "大写 : " << DaXie << endl;
	cout << "小写 : " << XiaoXie << endl;
	cout << "数字 : " << Number << endl;
	cout << "空格 : " << Space << endl;
	cout << "其它 : " << Others << endl;

	return 0;
}