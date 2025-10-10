/* 2351136 李盛鹏 信03 */
#include <iostream>
#include <string>

#define Lmin 12
#define Lmax 16
#define generation 10
using namespace std;

//其他字符必须从这个数组中取值
static const char other[] = "!@#$%^&*-_=+,.?";

//读走第一行
void my_getline()
{
	while (getchar() != '\n') {
		;
	}
}



int main()
{
	//读走第一行
	my_getline();

	int length, daxie, xiaoxie, number, others;
	bool is_valid = true;
	cin >> length >> daxie >> xiaoxie >> number >> others;

	//读走回车
	my_getline();

	for (int count = 1; count <= generation&&is_valid; count++) {
		//用四个int变量表示读取到的真实值，后面与理论值比较，is_valid判断是否有错，一旦有错终止程序输出错误
		int true_d = 0, true_x = 0, true_n = 0, true_o = 0, other_length = strlen(other);

		//定义一个字符数组承载生成的密码，getline赋值的同时，覆盖上一次记录的密码
		char password[Lmax + 1] = { 0 };
		cin.getline(password, Lmax + 1);

		//如果长度不够，直接报错结束
		if (strlen(password) < length) {
			is_valid = false;
		}
		else {
			//如果长度够，历遍字符数组，利用ASCII码值来计数
			for (int i = 0; i < length; i++) {
				if (password[i] >= 'A' && password[i] <= 'Z') {
					true_d++;
				}
				else if (password[i] >= 'a' && password[i] <= 'z') {
					true_x++;
				}
				else if (password[i] >= '0' && password[i] <= '9') {
					true_n++;
				}
				else {
					for (int j = 0; j < other_length; j++) {
						if (password[i] == other[j]) {
							true_o++;
							break;
						}
					}
				}
			}
		}

		//计算是否相等
		if (length != true_d + true_x + true_n + true_o) {
			is_valid = false;
		}

		//比较真实值和最小值
		if (true_d < daxie || true_x < xiaoxie || true_n < number || true_o < others) {
			is_valid = false;
		}
	
	}

	//根据bool的值，来判断输出的是正确还是错误
	if (is_valid) 
		cout << "正确" << endl;
	else 
		cout << "错误" << endl;

	return 0;
}