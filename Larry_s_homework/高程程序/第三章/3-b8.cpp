/*2351136 信03 李盛鹏*/
#include<iostream>
#include<iomanip>
#include<math.h> 
using namespace std;
int main()
{
	cout << "请输入x的值[-10 ~ +65]" << endl;
	int x,i=0;
	double y=0,p=1;
	bool a=true;
	cin >> x;
	if (x < -10 || x>65) {
		a = false;
		cout << "输入非法，请重新输入" << endl;
	}//判断输入是否非法

	if (a) {
		while (fabs(p) > 1e-6) {
			y+=p;
			++i;
			p =p*x / i;
		}
		cout << setprecision(10) <<"e^" <<x<<"=" << y << endl;
	}//输出exp
	return 0;
}
