/* 2351136 李盛鹏 信03 */
#include <iostream>
#define num_place 32
#define jinzhi 2
using namespace std;

//二进制转化为十进制的函数,输入一个指向\0前一位的指针*start通过不断地反推"除二取余"，也就是从最高位开始乘二加*start，算出十进制数
unsigned int turn_to_ten(char* start)
{
	unsigned int total = 0;
	//因为是字符串，所以可以根据\0来作为结束的命令,没完成一位就指向下一个位置
	while (*start != 0) {
		total = total * jinzhi + (*start - '0');
		start++;
	}

	return total;
}


int main()
{
	//要求用户输入一个0\1的字符串，把它储存在一个字符数组my_01[]中
	cout << "请输入一个0/1组成的字符串，长度不超过" << num_place << endl;

	//由cin存入my_01中，后面清除缓存区其实本题没用，但是毕竟有可能有空格，多余的数据提早清除，防止对后面输入影响
	char my_01[num_place + 1] = { 0 };//比储存的位数多1来存放尾0
	cin >> my_01;
	cin.ignore(65536, '\n');

	//定义一个指针*start指向字符数组的开始地址，并且引用进制转化函数，其返回值就是结果，而且可以根据需求修改jinzhi的值，让它成为n进制转为10进制函数
	char* start = my_01;
	cout << turn_to_ten(start) << endl;
}