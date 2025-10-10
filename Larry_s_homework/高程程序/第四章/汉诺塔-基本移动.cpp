/* 2351136 李盛鹏 信03 */
#include <iostream>
#include <iomanip>
using namespace std;

/* ----具体要求----
   1、不允许添加其它头文件
   2、不允许定义全局变量、静态局部变量
   3、不允许添加其它函数
   4、main函数处理输入，允许循环
   --------------------------------------------------------------------- */

   /***************************************************************************
     函数名称：hanoi
     功    能：打印n层汉诺塔的移动顺序
     输入参数：int n：层数
               char src：起始柱
               char tmp：中间柱
               char dst：目标柱
     返 回 值：
     说    明：1、函数名、形参、返回类型均不准动
               2、本函数不允许出现任何形式的循环
   ***************************************************************************/
void hanoi(int n, char src, char tmp, char dst)
{
    if (n == 1) {
        cout << setw(2) << n << "# " << src << "-->" << dst<<endl;
        return;
    }
    else {
        hanoi(n - 1, src,dst,tmp);
        cout << setw(2) << n << "# " << src << "-->" << dst << endl;
        hanoi(n - 1, tmp, src, dst);
    }
}

/***************************************************************************
  函数名称：main
  功    能：输入，调用递归函数，处理输入错误
  输入参数：
  返 回 值：int
  说    明：1、完成输入、调用递归函数
            2、处理输入错误时，允许使用循环
            3、为了统一检查，不再允许添加其它函数（输入起始/目标柱的代码不要求统一函数处理，均直接放在main中）
***************************************************************************/
int main()
{
    int n;
    char src, tmp, dst;

    //处理汉诺塔层数的错误判断
    while (1) {
        cout << "请输入汉诺塔的层数(1-16)" << endl;
        cin >> n;
        if (n < 1 || n>16 || !cin.good()) {
            cin.clear();
            cin.ignore(65536, '\n');
        }
        if (n >= 1 && n <= 16) {
            cin.clear();
            cin.ignore(65536, '\n');
            break;
        }
    }

    //处理起始柱的错误判断
    while (1) {
        cout << "请输入起始柱(A-C)" << endl;
        cin >> src;
        if (src != 'a' && src != 'A' && src != 'b' && src != 'B' && src != 'c' && src != 'C' || !cin.good()) {
            cin.clear();
            cin.ignore(65536, '\n');
        }
        else {
            cin.clear();
            cin.ignore(65536, '\n');
            if (src == 'a' || src == 'b' || src == 'c') {
                src -= 32;
            }
            break;
        }
    }

    //处理目标柱的错误判断
    while (1) {
        cout << "请输入目标柱(A-C)" << endl;
        cin >> dst;
        if (dst == src || dst - 32 == src || src - 32 == dst) {
            if (dst == 'a' || dst == 'A') {
                cout << "目标柱(A)不能与起始柱(A)相同" << endl;
            }
            if (dst == 'b' || dst == 'B') {
                cout << "目标柱(B)不能与起始柱(B)相同" << endl;
            }
            if (dst == 'c' || dst == 'C') {
                cout << "目标柱(C)不能与起始柱(C)相同" << endl;
            }
            cin.clear();
            cin.ignore(65536, '\n');
            continue;
        }
        if (dst != 'a' && dst != 'A' && dst != 'b' && dst != 'B' && dst != 'c' && dst != 'C' || !cin.good()) {
            cin.clear();
            cin.ignore(65536, '\n');
        }
        else {
            cin.clear();
            cin.ignore(65536, '\n');
            if (dst == 'a' || dst == 'b' || dst=='c') {
                dst -= 32;
            }
            break;
        }
    }

    if (src == 'A' || src == 'a') {
        if (dst == 'B' || dst == 'b') {
            tmp = 'C';
        }
        else {
            tmp = 'B';
        }
    }
    else if (src == 'B' || src == 'b') {
        if (dst == 'A' || dst == 'a') {
            tmp = 'C';
        }
        else {
            tmp = 'A';
        }
    }
    else {
        if (dst == 'A' || dst == 'a') {
            tmp = 'B';
        }
        else {
            tmp = 'A';
        }
    }
    cout << "移动步骤为:" << endl;
    hanoi(n, src, tmp, dst);

    return 0;





}