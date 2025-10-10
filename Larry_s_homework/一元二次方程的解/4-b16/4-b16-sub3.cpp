/* 2351136 信03 李盛鹏 */
#include<iostream>
#include<cmath>
using namespace std;

void TwoImaginary(double a, double b, double c)
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