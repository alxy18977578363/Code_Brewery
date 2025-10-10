/*2351136 信03 李盛鹏*/ 
#include<iostream>
#include<iomanip>
#include<cmath>
using namespace std;
int main()
{
	const double pi = 3.14159;
	int a, b, c;
	float s;
	cout << "请输入三角形的两边及其夹角（角度）" << endl;
	cin >> a >> b >> c;
	s =float (1.0F * a * b / 2 * sin(pi * c / 180));
	cout <<setiosflags(ios::fixed)<<setprecision(3)<< "三角形的面积为 : " << s << endl;
	return 0;

}
