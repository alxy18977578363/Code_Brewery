/* 信03 2351136 李盛鹏 */
#include <iostream>
#include<math.h>
using namespace std;

/***************************************************************************
  函数名称：calc_bonus
  功    能：根据利润计算奖金（四舍五入，精确到元）
  输入参数：profit
  返 回 值：int型的bonus 
  说    明：只允许用 if-else语句，用switch-case语句则得分为0
***************************************************************************/
int calc_bonus(int profit)
{
	double bonus=0;
	if (profit >= 1 && profit <= 100000) {
		bonus = profit * 0.1;
	}
	else if (profit > 100000 && profit <= 200000) {
		bonus = 100000 * 0.1 + (profit - 100000) * 0.075;
	}
	else if (profit > 200000 && profit <= 400000) {
		bonus = 100000 * 0.1 + 100000 * 0.075 + (profit - 200000) * 0.05;
	}
	else if (profit > 400000 && profit <= 600000) {
		bonus = 100000 * 0.1 + 100000 * 0.075 + 200000 * 0.05 + (profit - 400000) * 0.03;
	}
	else if (profit > 600000 && profit <= 1000000) {
		bonus = 100000 * 0.1 + 100000 * 0.075 + 200000 * 0.05 + 200000 * 0.03 + (profit - 600000) * 0.015;
	}
	else if (profit > 1000000) {
		bonus = 100000 * 0.1 + 100000 * 0.075 + 200000 * 0.05 + 200000 * 0.03 + 400000 * 0.015 + (profit - 1000000) * 0.01;
	}

	double xiaoshu = bonus - int(bonus);
	if (fabs(xiaoshu) >= 0.5) {
		bonus = int(bonus) + 1;
	}
	else {
		bonus = int(bonus);
	}
	return int(bonus);
}//计算每一个分段的奖金并且将其四舍五入 

/***************************************************************************
  函数名称：get_business_profit
  功    能：计算最终得到的奖金
  输入参数：从键盘读取一个int型正整数，有错误则按错误处理逻辑的规则，给出输出提示后再次读
  返 回 值：int型的输入的数shuru 
  说    明： 
***************************************************************************/
int get_business_profit()
{
	int shuru;

	while (1) {
		cin >> shuru;
		if (!cin.good()) {
			cin.clear();
			cin.ignore(65536, '\n');
		}

		if (shuru < 1) {
			cout << "请输入利润" << endl;
		}
		if (shuru >= 1 && cin.good()) {
			break;
		}
	}
	return shuru;
}

/***************************************************************************
  函数名称：main
  功    能：调用函数，输出结果 
  输入参数：int profit 
  返 回 值：0
  说    明：main函数不准动
***************************************************************************/
int main()
{
	int profit;
	cout << "请输入利润" << endl;
	profit = get_business_profit();
	cout << "应发奖金数 : " << calc_bonus(profit) << endl;

	return 0;
}
