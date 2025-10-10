/* 信03 2351136 李盛鹏*/
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <windows.h> //取系统时间
using namespace std;
int main()
{
    //给出系统时间
    LARGE_INTEGER tick, begin, end;

    QueryPerformanceFrequency(&tick);	//获得计数器频率
    QueryPerformanceCounter(&begin);	//获得初始硬件计数器计数

    /* 此处是你的程序开始 */
    int num1, num2, num3, i = 0;

    for (num1 = 123; num1 <= 1953 / 3; num1++) {
        for (num2 = 123; num2 <= (1953 - num1) / 2; num2++) {
            for (num3 = 123; num3 <= 987; num3++) {


                // 检查每个数的每一位是否不同  
                int b1, b2, b3, c1, c2, c3, d1, d2, d3;
                b1 = num1 / 100;
                b2 = (num1 / 10) % 10;
                b3 = num1 % 10;
                c1 = num2 / 100;
                c2 = (num2 / 10) % 10;
                c3 = num2 % 10;
                d1 = num3 / 100;
                d2 = (num3 / 10) % 10;
                d3 = num3 % 10;

                //除掉可能为0的地方
                if (b1 == 0 || b2 == 0 || b3 == 0 || c1 == 0 || c2 == 0 || c3 == 0 || d1 == 0 || d2 == 0 || d3 == 0) {
                    continue;
                }

                //从低到高排序
                if (num1 >= num2 || num2 >= num3 || num1 >= num3) {
                    continue;
                }
                if (num1 + num2 + num3 != 1953) {
                    continue;
                }

                //让每一位都不同
                if (b1 != b2 && b1 != b3 && b1 != c1 && b1 != c2 && b1 != c3 && b1 != d1 && b1 != d2 && b1 != d3
                    && b2 != b3 && b2 != c1 && b2 != c2 && b2 != c3 && b2 != d1 && b2 != d2 && b2 != d3
                    && b3 != c1 && b3 != c2 && b3 != c3 && b3 != d1 && b3 != d2 && b3 != d3
                    && c1 != c2 && c1 != c3 && c1 != d1 && c1 != d2 && c1 != d3
                    && c2 != c3 && c2 != d1 && c2 != d2 && c2 != d3
                    && c3 != d1 && c3 != d2 && c3 != d3
                    && d1 != d2 && d1 != d3
                    && d2 != d3) {
                    i++;
                    cout << "No." << setw(3) << i << " : " << num1 << "+" << num2 << "+" << num3 << "=1953" << endl;
                }
            }
        }
    }
    cout << "total=" << i << endl;

    /* 此处是你的程序结束 */

    QueryPerformanceCounter(&end);		//获得终止硬件计数器计数

    cout << "计数器频率 : " << tick.QuadPart << "Hz" << endl;
    cout << "计数器计数 : " << end.QuadPart - begin.QuadPart << endl;
    cout << setiosflags(ios::fixed) << setprecision(6) << double(end.QuadPart - begin.QuadPart) / tick.QuadPart << "秒" << endl;

    return 0;
}