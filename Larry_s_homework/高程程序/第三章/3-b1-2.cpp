/*2351136 信03 李盛鹏*/
#include<iostream>
#include<iomanip>
using namespace std;
int main()
{
	double a, b, c, d, e, f,g;
	const double pi=3.14159;
	cout << "请输入半径和高度" << endl;
	cin >> a >> b;
	c = a*2*pi;
	d = a * a * pi;
	e = a * a * 4 * pi;
	f = a * a * a * 4 / 3 * pi;
	g = a * a * pi * b;
	cout << setiosflags(ios::fixed) << setprecision(2) << "圆周长     : " << c << endl;
	cout << setiosflags(ios::fixed) << setprecision(2) << "圆面积     : " << d << endl;
	cout << setiosflags(ios::fixed) << setprecision(2) << "圆球表面积 : " << e << endl;
	cout << setiosflags(ios::fixed) << setprecision(2) << "圆球体积   : " << f << endl;
	cout << setiosflags(ios::fixed) << setprecision(2) << "圆柱体积   : " << g << endl;
	return 0;

}
