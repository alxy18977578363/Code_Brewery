/* 2351136 李盛鹏 信03 */
#include<iostream>
#include<iomanip>
#include <windows.h>
#include <conio.h>
#include"5-b7.h"
#define N 10

using namespace std;
//三个一维数组
int A[N], B[N], C[N];
//三个全局指针
int topA = -1, topB = -1, topC = -1;
//计数用的全局
int i = 0;
//一个静态全局变量
static int i_speed;
//一个是否显示数组内部的静态全局变量
static bool i_matrix;


// 暂停程序的函数
void my_pause()
{
    char key;
    bool ifstop = true;
    while (ifstop) {
        key = _getch();
        switch (key) {
            case '\r':
                ifstop = false;
                break;
            default:
                ifstop = true;
                break;
        }
    }
}

//模式的选择,也包括错误输入处理
int selection(int i_speed)
{
    int my_speed = 5000;
    if (i_speed == 0) {
        my_speed = 100;
    }
    else {

        for (int count = i_speed; count > 0; count--) {
            my_speed /= 2;
        }
    }
        return my_speed;
    
}

//初始化输出柱子
void my_tower(int A[],int B[],int C[])
{
    //对应位置上输出，如果有环，输出环。没环，输出空格
    for (int count = 0; count < N; count++) {
        cct_gotoxy(32, 15 - count - 1);
        if (A[count])
            cout << A[count];
        else
            cout << " ";
    }

    for (int count = 0; count < N; count++) {
        cct_gotoxy(32+10, 15 - count - 1);
        if (B[count])
            cout << B[count];
        else
            cout << " ";
    }

    for (int count = 0; count < N; count++) {
        cct_gotoxy(32+10+10, 15 - count - 1);
        if (C[count])
            cout << C[count];
        else
            cout << " ";
    }

    cct_gotoxy(30, 15);
    cout << "=========================" << endl;
    cct_gotoxy(30, 15 + 1);
    cout << "  A         B         C" << endl;

}
//数组初始化
void initial(int n, char src, char tmp, char dst)
{
    for (int in_count = 0; in_count < n; in_count++) {
        if (src == 'A') {
            A[in_count] = n - in_count;
            B[in_count] = 0;
            C[in_count] = 0;
            topA = n;
            topB = 0;
            topC = 0;
        }
        else if (src == 'B') {
            A[in_count] = 0;
            B[in_count] = n - in_count;
            C[in_count] = 0;
            topA = 0;
            topB = n;
            topC = 0;
        }
        else {
            A[in_count] = 0;
            B[in_count] = 0;
            C[in_count] = n - in_count;
            topA = 0;
            topB = 0;
            topC = n;
        }
    }

    my_tower(A,B,C);
    //输出初始化的那一行句子
    if (i_matrix) {
        cct_gotoxy(8, 15 + 6);
        cout << "初始:                ";
        cout << "A:";
        for (int printcount = 0; printcount < topA; printcount++) {
            cout << setw(2) << A[printcount];

        }
        for (int printcount = 0; printcount < N - topA; printcount++) {
            cout << "  ";
        }

        cout << " B:";
        for (int printcount = 0; printcount < topB; printcount++) {
            cout << setw(2) << B[printcount];
        }
        for (int printcount = 0; printcount < N - topB; printcount++) {
            cout << "  ";
        }

        cout << " C:";
        for (int printcount = 0; printcount < topC; printcount++) {
            cout << setw(2) << C[printcount];
        }
        for (int printcount = 0; printcount < N - topC; printcount++) {
            cout << "  ";
        }
        cout << endl;
    }


}

//展示现在每个环还有什么的函数
void printshow(int A[], int B[], int C[], char src, char dst, char n)
{
    cct_gotoxy(8+21, 15 + 6);
    cout << "A:";
    for (int printcount = 0; printcount < topA; printcount++) {
        cout << setw(2) << A[printcount];
    }
    for (int printcount = 0; printcount < N - topA; printcount++) {
        cout << "  ";
    }

    cout << " B:";
    for (int printcount = 0; printcount < topB; printcount++) {
        cout << setw(2) << B[printcount];
    }
    for (int printcount = 0; printcount < N - topB; printcount++) {
        cout << "  ";
    }
    
    cout << " C:";
    for (int printcount = 0; printcount < topC; printcount++) {
        cout << setw(2) << C[printcount];
    }
    for (int printcount = 0; printcount < N - topC; printcount++) {
        cout << "  ";
    }
    
    cout << endl;

}

//只负责移动
void my_move(char src, char dst, int n)
{
    //这里用一个tamp缓存一下要调走的环
    int tamp = 0;
    if (src == 'A') {
        tamp = A[--topA];
        A[topA] = 0;
    }
    else if (src == 'B') {
        tamp = B[--topB];
        B[topB] = 0;
    }
    else {
        tamp = C[--topC];
        C[topC] = 0;
    }

    if (dst == 'A') {
        A[topA++] = tamp;
    }
    else if (dst == 'B') {
        B[topB++] = tamp;
    }
    else {
        C[topC++] = tamp;
    }
}



//汉诺函数，负责递归移动和调用输出
void hanoi(int n, char src, char tmp, char dst)
{
    if (n == 0) {
        i++;

        return;
    }
    else {

        hanoi(n - 1, src, dst, tmp);//先把上面的n-1搬到中间柱

        //下面这段是暂停函数的运用
        if (i_speed == 0) { // 如果速度设置为0，暂停程序
            my_pause();
        }
        Sleep(selection(i_speed));
        cct_gotoxy(8, 15 + 6);
        cout << "第" << setw(4) << i << " 步(" << setw(2) << n << "): " << src << "-->" << dst << " ";
        
       
        my_move(src, dst, n);//把最下面的搬到结束柱
        my_tower(A, B, C);

        //此处是对于是否输出内部数组的判断
        if (i_matrix) {
            printshow(A, B, C, src, dst, n);
        }


        hanoi(n - 1, tmp, src, dst);//再把上面的n-1搬到结束柱

    }
}

/***************************************************************************
  函数名称：main
  功    能：负责处理各种输入输出的错误，调initial函数来初始化柱塔，调hanoi来完成输出，并且给出程序终止
  输入参数：无
  返 回 值：int
  说    明：各功能的整合和实现
***************************************************************************/
int main()
{

    int n;
    char src, tmp, dst;

    //处理汉诺塔层数的错误判断
    while (1) {
        cout << "请输入汉诺塔的层数(1-10)" << endl;
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
            if (dst == 'a' || dst == 'b' || dst == 'c') {
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

    bool for_i_speed = false;
    while (!for_i_speed) {
        //提示用户输入移动速度
        cout << "请输入移动速度(0-5: 0-按回车单步演示 1-延时最长 5-延时最短)" << endl;
        cin >> i_speed;
        if (!cin.good()) {
            cin.clear();
            cin.ignore(65536, '\n');
        }
        else if (i_speed == 1 || i_speed == 2 || i_speed == 3 || i_speed == 4 || i_speed == 5 || i_speed == 0) {
            for_i_speed = true;
        }
    }
    
    
    //提示用户输入移动速度
    bool for_i_matrix = false;
    while (!for_i_matrix) {
        
        cout << "请输入是否显示内部数组值(0-不显示 1-显示)" << endl;
        cin >> i_matrix;
        if (!cin.good()) {
            cin.clear();
            cin.ignore(65536, '\n');
        }
        else if (i_matrix == 0 || i_matrix == 1) {
            for_i_matrix = true;
            cin.clear();
            cin.ignore(65536, '\n');
        }

    }
    

    //清屏
    cct_cls();

    cout << "从 " << src << " 移动到 " << dst << "，共 " << n << " 层，延时设置为 " << i_speed << "，";
    if (i_matrix) {
        cout << "显示内部数组值" << endl;
    }
    else {
        cout << "不显示内部数组值" << endl;
    }
    //初始化柱子
    initial(n, src, tmp, dst);
    //调用能输出步骤和数组内部变化的hanoi
    hanoi(n, src, tmp, dst);


	system("pause"); //最后用这句表示暂停（注意：只适合于特定程序，无特别声明的程序加此句则得分为0）
	return 0;
}