#include<iostream>
using namespace std;
int main()
{
	const char* month[] = { "Invalid","January","February","March","April","May","June","July","August","September","October","November","December"}; 
	cout << "ÇëÊäÈëÔÂ·Ý(1-12)" << endl;
	int p = 0;
	cin >> p;
	if (!cin.good() || p < 1 || p>12)
		cout << month[0]<<endl;
	else
		cout << month[p]<<endl; 
	return 0;
}
