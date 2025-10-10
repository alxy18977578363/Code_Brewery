/* 2351136 信03 李盛鹏 */
#include<iostream>
#include<cmath>
using namespace std;


void TwoDifferent(double a, double b, double c)
{
	double x1 = (-b + sqrt(b * b - 4 * a * c)) / (2 * a);
	double x2 = (-b - sqrt(b * b - 4 * a * c)) / (2 * a);

	cout << "有两个不等实根：" << endl;
	if (fabs(x1) < 1e-6) {
		x1 = 0;
	} // 忽略掉小于1e-6的部分
	if (fabs(x2) < 1e-6) {
		x2 = 0;
	} // 忽略掉小于1e-6的部分


	cout << "x1=" << x1 << endl;
	cout << "x2=" << x2 << endl;

	return;
}
//delta>0时处理