/* 2351136 信03 李盛鹏 */
#include<iostream>
#include<cmath>
using namespace std;
void NoTwoUnknowns(double a,double b,double c)
{
	cout << "不是一元二次方程" << endl;
	return;
}
//a=0时处理

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

	if(x1!=0) {
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
			cout << "x1="  << "i" << endl;
			cout << "x2=" << "-i" << endl;
		}
		else {
			cout << "x1="  << xu << "i" << endl;
			cout << "x2="  << "-" << xu << "i" << endl;
		}
	}
	return;
}
//delta<0时处理

void TwoEqual(double a, double b, double c)
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

int main()
{
	double a, b, c;
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
		NoTwoUnknowns(a, b, c);
	}
	else if (b * b - 4 * a * c > 1e-6) {
		TwoDifferent(a, b, c);
	}
	else if (b * b - 4 * a * c<-1e-6) {
		TwoImaginary(a, b, c);
	}
	else{
		TwoEqual(a, b, c);
	}

	return 0;


}