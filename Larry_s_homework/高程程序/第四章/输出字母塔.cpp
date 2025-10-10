/* 2351136 信03 李盛鹏 */
#include <iostream>
#include <iomanip>
#include <cstdio>
using namespace std;

/* -----------------------------------------------------------------------------------
		允许   ：1、按需增加一个或多个函数（包括递归函数），但是所有增加的函数中不允许任何形式的循环
				 2、定义符号常量
				 3、定义const型变量

		不允许 ：1、定义全局变量
				 2、除print_tower之外的其他函数中不允许定义静态局部变量
   ----------------------------------------------------------------------------------- */


void left(char start, char end)
{
	if (end < start) {
		return;
	}
	cout << end;
	left(start, end - 1);
}//从左边打字母

void right(char start, char end)
{
	if (start > end) {
		cout << endl;
		return;
	}
	cout << start;
	right(start + 1, end);
}

void kongge(char end, char end_ch)
{
	if (end == end_ch) {
		return;
	}
	cout << " ";
	kongge(end, end_ch + 1);
}


   /***************************************************************************
	 函数名称：print_tower
	 功    能：打印字母塔
	 输入参数：char start,char end_ch,char end,int mode
	 返 回 值：void 
	 说    明：形参按需设置
			   提示：有一个参数order，指定正序/倒序
   ***************************************************************************/
void print_tower(char start,char end_ch,char end,int mode)
{
	/* 允许按需定义最多一个静态局部变量（也可以不定义） */

	/* 按需实现，函数中不允许任何形式的循环，函数允许调用其它函数 */
	if (mode == 1) {
		if (end_ch < start) {
			return;
		}
		print_tower(start, end_ch - 1, end, 1);
		kongge(end, end_ch);
		left(start, end_ch);
		right(start + 1, end_ch);
	}
	
	if (mode == 2) {
		if (end_ch < start) {
			return;
		}
		kongge(end, end_ch);
		left(start, end_ch);
		right(start+1, end_ch);
		print_tower(start, end_ch - 1, end, 2);
	}
	
}

/***************************************************************************
  函数名称： main
  功    能：调用并输出字母塔 
  输入参数：char end_ch
  返 回 值：int 
  说    明：main函数中的...允许修改，其余位置不准修改
***************************************************************************/
int main()
{
	char end_ch;

	/* 键盘输入结束字符(仅大写有效，为避免循环出现，不处理输入错误) */
	cout << "请输入结束字符(A~Z)" << endl;
	end_ch = getchar();			//读缓冲区第一个字符
	if (end_ch < 'A' || end_ch > 'Z') {
		cout << "结束字符不是大写字母" << endl;
		return -1;
	}

	/* 正三角字母塔(中间为A) */
	cout << setw((2 * (end_ch - 'A')) + 1) << setfill('=') << '=' << endl;/* 按字母塔最大宽度输出=(不允许用循环) */
	cout << "正三角字母塔(" << end_ch << "->A)" << endl;
	cout << setw((2 * (end_ch - 'A')) + 1) << setfill('=') << '=' << endl;/* 按字母塔最大宽度输出=(不允许用循环) */
	print_tower('A',end_ch,end_ch,1); //正序打印 A~结束字符 
	cout << endl;

	/* 倒三角字母塔(中间为A) */
	cout << setw((2 * (end_ch - 'A')) + 1) << setfill('=') << '=' << endl;/* 按字母塔最大宽度输出=(不允许用循环) */
	cout << "倒三角字母塔(" << end_ch << "->A)" << endl;
	cout << setw((2 * (end_ch - 'A')) + 1) << setfill('=') << '=' << endl;/* 按字母塔最大宽度输出=(不允许用循环) */
	print_tower('A', end_ch, end_ch, 2); //逆序打印 A~结束字符 
	cout << endl;

	/* 合起来就是漂亮的菱形（中间为A） */
	cout << setw((2 * (end_ch - 'A')) + 1) << setfill('=') << '=' << endl;/* 按字母塔最大宽度输出= */
	cout << "菱形(" << end_ch << "->A)" << endl;
	cout << setw((2 * (end_ch - 'A')) + 1) << setfill('=') << '=' << endl;/* 按字母塔最大宽度输出= */
	print_tower('A', end_ch, end_ch, 1);   //打印 A~结束字符的正三角 
	print_tower('A', end_ch-1, end_ch, 2);   //打印 A~结束字符-1的倒三角 
	cout << endl;

	return 0;
}
