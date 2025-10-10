/* 2351136 信03 李盛鹏 */
#include<iostream>
#include<cmath>
using namespace std;

void NoTwoUnknowns();
void TwoDifferent();
void TwoImaginary();
void TwoEqual();

double a, b, c;
int main()
{
	cout << "请输入一元二次方程的三个系数a,b,c:" << endl;

	cin >> a >> b >> c;

	//判断输入
	if (fabs(a) < 1e-6) {
		a = 0;
	}
	if (fabs(b) < 1e-6) {
		b = 0;
	}
	if (fabs(c) < 1e-6) {
		c = 0;
	}


	if (a == 0) {
		NoTwoUnknowns();
	}
	else if (b * b - 4 * a * c > 1e-6) {
		TwoDifferent();
	}
	else if (b * b - 4 * a * c < -1e-6) {
		TwoImaginary();
	}
	else {
		TwoEqual();
	}

	return 0;


}