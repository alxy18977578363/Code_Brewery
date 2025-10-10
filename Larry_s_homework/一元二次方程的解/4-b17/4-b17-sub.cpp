/* 2351136 信03 李盛鹏 */
#include<iostream>
#include<cmath>
using namespace std;

extern double a, b, c;

void NoTwoUnknowns()
{
	cout << "不是一元二次方程" << endl;
	return;
}
//delta>0时处理

void TwoDifferent()
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
//两个不同数的处理

void TwoImaginary()
{
	double x1 = (-b) / (2 * a);
	double x2 = (-b) / (2 * a);


	if (fabs(x1) < 1e-6) {
		x1 = 0;
	} // 忽略掉小于1e-6的部分
	if (fabs(x2) < 1e-6) {
		x2 = 0;
	} // 忽略掉小于1e-6的部分

	double xu = fabs(sqrt(-(b * b - 4 * a * c)) / (2 * a));

	if (fabs(xu) < 1e-6) {
		xu = 0;
	} // 忽略掉小于1e-6的部分

	cout << "有两个虚根：" << endl;

	if (x1 != 0) {
		if (fabs(fabs(xu) - 1) < 1e-6) {
			cout << "x1=" << x1 << "+i" << endl;
			cout << "x2=" << x2 << "-i" << endl;
		}
		else {
			cout << "x1=" << x1 << "+" << xu << "i" << endl;
			cout << "x2=" << x1 << "-" << xu << "i" << endl;
		}
	}
	else {
		if (fabs(fabs(xu) - 1) < 1e-6) {
			cout << "x1=" << "i" << endl;
			cout << "x2=" << "-i" << endl;
		}
		else {
			cout << "x1=" << xu << "i" << endl;
			cout << "x2=" << "-" << xu << "i" << endl;
		}
	}
	return;
}
//delta<0时处理

void TwoEqual()
{

	double x1 = (-b) / (2 * a);
	double x2 = (-b) / (2 * a);

	if (fabs(x1) < 1e-6) {
		x1 = 0;
	}

	cout << "有两个相等实根：" << endl;
	cout << "x1=x2=" << x1 << endl;

	return;
}
//delta=0时处理