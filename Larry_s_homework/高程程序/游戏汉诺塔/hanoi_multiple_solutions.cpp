/* 信03 2351136 李盛鹏 */
#include "cmd_console_tools.h"
#include "hanoi.h"
using namespace std;

/* ----------------------------------------------------------------------------------

	 本文件功能：
	1、存放被 hanoi_main.cpp 中根据菜单返回值调用的各菜单项对应的执行函数

	 本文件要求：
	1、不允许定义外部全局变量（const及#define不在限制范围内）
	2、允许定义静态全局变量（具体需要的数量不要超过文档显示，全局变量的使用准则是：少用、慎用、能不用尽量不用）
	3、静态局部变量的数量不限制，但使用准则也是：少用、慎用、能不用尽量不用
	4、按需加入系统头文件、自定义头文件、命名空间等

   ----------------------------------------------------------------------------------- */


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
int Selection(int i_speed)
{
    int my_speed = 250;
    if (i_speed == 0) {
        my_speed = 100;
    }
    else {
        for (int count = 1; count <= i_speed; count++) {
            my_speed -= 50;
        }
    }
    return my_speed;

}

//初始化输出塔
void initial_tower(int choice)
{
    //对应位置上输出，如果有环，输出环。没环，输出空格
    for (int count = 0; count < N; count++) {
        if (choice == 9|| choice == 8) {
            cct_gotoxy(base_x + 2, base_y + N + 2 - count - 1);
        }
        else {
            cct_gotoxy(base_x + 2, base_y - count - 1);
        }
        if (A[count])
            cout << A[count];
        else
            cout << " ";
    }

    for (int count = 0; count < N; count++) {
        if (choice == 9|| choice == 8) {
            cct_gotoxy(base_x + 10 + 2, base_y + N + 2 - count - 1);
        }
        else {
            cct_gotoxy(base_x + 10 + 2, base_y - count - 1);
        }
        if (B[count])
            cout << B[count];
        else
            cout << " ";
    }

    for (int count = 0; count < N; count++) {
        if (choice == 9|| choice == 8) {
            cct_gotoxy(base_x + 10 + 10 + 2, base_y + N + 2 - count - 1);
        }
        else {
            cct_gotoxy(base_x + 10 + 10 + 2, base_y - count - 1);
        }
        if (C[count])
            cout << C[count];
        else
            cout << " ";
    }
    if (choice == 9|| choice == 8) {
        cct_gotoxy(base_x, base_y+N+2);
    }
    else {
        cct_gotoxy(base_x, base_y);
    }
        cout << "=========================" << endl;
    if (choice == 9|| choice == 8) {
       cct_gotoxy(base_x, base_y + N + 2+1);
    }
    else {
       cct_gotoxy(base_x, base_y + 1);
    }
    cout << "  A         B         C" << endl;
}
//动柱子
void my_tower(int choice)
{
    //对应位置上输出，如果有环，输出环。没环，输出空格
    for (int count = 0; count < N; count++) {
        if (choice == 8|| choice == 9) {
            cct_gotoxy(base_x + 2, base_y + N + 2 - count - 1);
        }
        else {
            cct_gotoxy(base_x + 2, base_y - count - 1);
        }
        if (A[count])
            cout << A[count];
        else
            cout << " ";
    }

    for (int count = 0; count < N; count++) {
        if (choice == 9||choice==8) {
            cct_gotoxy(base_x +10+ 2, base_y + N + 2 - count - 1);
        }
        else {
            cct_gotoxy(base_x +10+ 2, base_y - count - 1);
        }
        if (B[count])
            cout << B[count];
        else
            cout << " ";
    }

    for (int count = 0; count < N; count++) {
        if (choice == 9||choice==8) {
            cct_gotoxy(base_x + 10+10 + 2, base_y + N + 2 - count - 1);
        }
        else {
            cct_gotoxy(base_x + 10+10 + 2, base_y - count - 1);
        }
        if (C[count])
            cout << C[count];
        else
            cout << " ";
    }

}

 
//数组初始化
void initial(int n, char src, char tmp, char dst,int choice)
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

    
    if (choice == 9||choice==8) {
        cct_gotoxy(0, base_y + N + 7);
        cout << "初始:  ";
    }
    else if (choice == 3) {
        return;
    }
    else{
        cct_gotoxy(8, base_y + 6);
        cout << "初始:                ";
    }
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

//横着展示每个环上还有什么数
void printshow(int A[], int B[], int C[], char src, char dst, char n)
{
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
void my_move(char src, char dst)
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
void hanoi(int n, char src, char tmp, char dst, int choice)
{
    if (n == 1) {
        hanoicase(n, src, tmp, dst, choice);
        return;
    }
    else {
        hanoi(n - 1, src, dst, tmp, choice);
        hanoicase(n, src, tmp, dst, choice);
        hanoi(n - 1, tmp, src, dst, choice);
    }
}

//负责处理不同的模式
void hanoicase(int n, char src, char tmp, char dst, int choice)
{
    if (choice == 1) {
        i++;
        cout << setw(2) << n << "# " << src << "-->" << dst << endl;
    }
    else if (choice == 2) {
        i++;
        cout << "第" << setw(4) << i << " 步(" << setw(2) << n << "): " << src << "-->" << dst << endl;
    }
    else if (choice == 3) {
        i++;
        cout << "第" << setw(4) << i << " 步(" << setw(2) << n << "): " << src << "-->" << dst << " ";
        my_move(src, dst);//把最下面的搬到结束柱
        printshow(A, B, C, src, dst, n);
    }
    else if (choice == 4) {
        i++;
        //下面这段是暂停函数的运用
        if (i_speed == 0) { // 如果速度设置为0，变成按回车才动一次
            my_pause();
        }
        Sleep(Selection(i_speed));
        //输出第几步是哪到哪
        cct_gotoxy(8, base_y + 6);
        cout << "第" << setw(4) << i << " 步(" << setw(2) << n << "): " << src << "-->" << dst << " ";
        
        my_move(src, dst);//把最下面的搬到结束柱
        my_tower(choice);
        cct_gotoxy(8 + 21, base_y + 6);
        printshow(A, B, C, src, dst, n);
    }
    else if (choice == 7) {
        i++;
        if (i == 1) {
            ring_move(n, src, dst,choice);
            my_move(src, dst);
        }
    }
    else if (choice == 8) {
        i++;
        if (i_speed == 0) { // 如果速度设置为0，变成按回车才动一次
            my_pause();
        }
        Sleep(Selection(i_speed));
        ring_move(n, src, dst,choice);
        my_move(src, dst);//把最下面的搬到结束柱
        cct_gotoxy(0, base_y + N + 7);
        cout << "第" << setw(4) << i << " 步(" << setw(2) << n << "): " << src << "-->" << dst << " ";

        my_tower(choice);
        cct_gotoxy(0 + 21, base_y + N + 7);
        printshow(A, B, C, src, dst, n);
        cct_gotoxy(60, base_y + N + 9);
    }
}

void wait_for_enter()
{
    cout << endl << endl;
    cout << "按回车键继续" << endl;
    char input;
    while (1) {
        input = _getch();
        if (input == '\r') {
            break;
        }
        
    }
    cct_cls();
}

char input_src()
{
    char src;
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
    return src;
}

int input_n()
{
    int n;
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
    return n;
}

char input_dst(char src)
{
    char dst;
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
    return dst;
}

char input_tmp(char src, char dst)
{
    char tmp;
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
    return tmp;
}

int input_i_speed()
{
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
    return 0;
}

//用来做柱子图像的函数
void tower_setup()
{
    int y=base_y;
    //底座的搭建
    for (int count = 0; count < 3; count++) {
        cct_showch(1+count*(2*(N+1)+1+9), base_y, ' ', COLOR_HYELLOW, COLOR_HYELLOW, 2 * (N +1)+ 1);
    }

    //柱子的搭建
    for (int y = base_y;  y> base_y-N-2; y--) {
        for (int count = 0; count < 3; count++) {
            cct_showch(1 + count * (2 * (N+1) + 1 + 9) + N+1, y-1, ' ', COLOR_HYELLOW, COLOR_HYELLOW, 1);
            Sleep(100);
        }
    }

    //恢复缺省颜色
    cct_setcolor();
    cct_gotoxy(0, base_y+base_y/4);
}

//用来做盘子的函数
void ring_setup(int n,char src)
{
    int tamp = n;//为了让变量n不进入循环，用这个tamp来做中间变量
    for (int y = base_y; y > base_y - tamp; y--) {
           cct_showch(1 +(N+1-n) + (2 * (N+1) + 1 + 9) * (src - 'A'), y - 1, ' ', n, n, 2 * n + 1);
           n--;
            Sleep(100);
    }
    cct_setcolor();
    cct_gotoxy(0, base_y + base_y / 4);
}

void main_case(int choice)
{
    if (choice == 1 || choice == 2 || choice == 3 || choice == 4||choice==6) {
        //给n、src、dst、tmp分别赋值，tmp是最后出的所以写最后，输入src和dst导出tmp
        int n = input_n();
        char src = input_src();
        char dst = input_dst(src);
        char tmp = input_tmp(src, dst);

        if (choice == 3 || choice == 4) {
            if (choice == 4) {
                input_i_speed();//为i_speed赋值
                //清屏
                cct_cls();
            }
            //初始化柱子，会出现“初始：”那句话
            initial(n, src, tmp, dst,choice);
            if (choice == 4) {
                //调用这个函数可以输出数字柱子最初始的状态
                initial_tower(choice);
            }
        }

        //调用能输出步骤和数组内部变化的hanoi
        hanoi(n, src, tmp, dst, choice);


    }
    if (choice == 5) {
        //清屏
        cct_cls();
        //建立一开始的柱子的图案
        tower_setup();
    }
    if (choice == 6) {
        int n = input_n();
        char src = input_src();
        char dst = input_dst(src);
        char tmp = input_tmp(src, dst);
        cct_cls();
        tower_setup();
        //给初始化柱子套上初始化盘子
        ring_setup(n,src);
    }
    if (choice == 7||choice==8) {
        int n = input_n();
        char src = input_src();
        char dst = input_dst(src);
        char tmp = input_tmp(src, dst);
        if (choice == 8) {
            input_i_speed();//为i_speed赋值
            //清屏
            cct_cls();
        }
        initial(n, src, tmp, dst,choice);
        cct_cls();
        if (choice == 8) {
            initial(n, src, tmp, dst, choice);
                initial_tower(choice);//调用这个函数可以输出数字柱子最初始的状态
        }
        tower_setup();
        //给初始化柱子套上初始化盘子
        ring_setup(n, src);
        hanoi(n, src, tmp, dst, choice);
    }
    else if (choice == 9) {
        int n = input_n();
        char src = input_src();
        char dst = input_dst(src);
        char tmp = input_tmp(src, dst);

        initial(n, src, tmp, dst,choice);
        cct_cls();
        cout << "从 " << src << " 移动到 " << dst << "，共 " << n << " 层" << endl;
        tower_setup();
        //给初始化柱子套上初始化盘子
        ring_setup(n, src);

        //初始化uid
        initial_tower(choice);
        initial(n, src, tmp, dst, choice);
        cct_gotoxy(0, base_y + N + 9);
        cout << "请输入移动的柱号(命令形式：AC=A顶端的盘子移动到C，Q=退出) ：";
        hanoi_game(choice,dst,n);
        return;
    }
}

//上移函数
void ring_move_up(int n,char src,int choice)
{
    int y;
    if (src == 'A') {
        y = base_y - topA;
    }
    else if (src == 'B') {
        y = base_y - topB;
    }
    else {
        y = base_y - topC;
    }

        /* 将一串字符从下向上移动 */
        //画到min_y，比min_y大的都要在画完后停0.3秒清除，柱子的长是N+2，所以比base_y-N-2-1大的都要清了重画，最后位置在（1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (src - 'A')，min_y）
        for (y; y > min_y-1; y--) {
            
            cct_showstr(1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (src - 'A'), y, " ", n, n, 2*n+1);

            if (choice == 8) {
                Sleep(Selection(i_speed));
            }
            else {        /* 延时0.3秒 */
                Sleep(300);
            }

            if (y >min_y) {
                /* 清除显示(最后一次保留)，清除方法为用正常颜色+空格重画一遍刚才的位置 */
                cct_showch(1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (src - 'A'), y, ' ', COLOR_BLACK, COLOR_WHITE, 2*n+1);
            }
            if(y > base_y - N - 2 - 1){
                cct_showch(1 + (N + 1) + (2 * (N + 1) + 1 + 9) * (src - 'A'), y, ' ', COLOR_HYELLOW, COLOR_HYELLOW, 1);
            }
            //恢复缺省颜色
            cct_setcolor();
            cct_gotoxy(0, base_y + base_y / 4);

        } //end of for
    
}

//平移函数
void ring_move_parallel(int n, char src, char dst,int choice)
{
    int x;
    if (src == 'A' || (src == 'B' && dst == 'C')) {
        for (x = 1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (src - 'A'); x <= 1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (dst - 'A'); x++) {
            cct_showstr(x, min_y, " ", n, n, 2 * n + 1);

            if (choice == 8) {
                Sleep(Selection(i_speed));
            }
            else {        /* 延时0.1秒 */
                Sleep(100);
            }

            /* 在产生的同时将比dst所在柱x坐标小的都清除 */
            if (x < 1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (dst - 'A')) {
                cct_showch(x, min_y, ' ', COLOR_BLACK, COLOR_WHITE, 2 * n + 1);
            }
            //恢复缺省颜色
            cct_setcolor();
            cct_gotoxy(0, base_y + base_y / 4);
        }
    }
    else if (src == 'C' || (src == 'B' && dst == 'A')) {
        for (x = 1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (src - 'A'); x >= 1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (dst - 'A'); x--) {
            cct_showstr(x, min_y, " ", n, n, 2 * n + 1);

            if (choice == 8) {
                Sleep(Selection(i_speed));
            }
            else {        /* 延时0.1秒 */
                Sleep(100);
            }

            /* 在产生的同时将比dst所在柱x坐标大的都清除 */
            if (x > 1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (dst - 'A')) {
                cct_showstr(x, min_y, " ", COLOR_BLACK, COLOR_WHITE, 2 * n + 1);
            }
            //恢复缺省颜色
            cct_setcolor();
            cct_gotoxy(0, base_y + base_y / 4);
        }
    }
}

//下移函数
void ring_move_down(int n, char dst,int choice)
{
    //用一个y来负责动态变化的y坐标值，用tamp来做y的终点
    int y, tamp=0;
    if (dst == 'A') {
        tamp = base_y - topA - 1;
    }
    else if (dst == 'B') {
        tamp = base_y - topB - 1;
    }
    else if (dst == 'C') {
        tamp = base_y - topC - 1;
    }


    //下落过程，是从min_y到(base_y-topx-1)的过程中，先打印环，再等300ms消去环，只留下最后位置的环
    for (y = min_y; y <= tamp; y++) {
        cct_showstr(1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (dst - 'A'), y, " ", n, n, 2 * n + 1);

        if (choice == 8) {
            Sleep(Selection(i_speed));
        }
        else {        /* 延时0.3秒 */
            Sleep(300);
        }
        
        if (y < tamp) {
            cct_showch(1 + (N + 1 - n) + (2 * (N + 1) + 1 + 9) * (dst - 'A'), y, ' ', COLOR_BLACK, COLOR_WHITE, 2 * n + 1);
        }
        if (y >= base_y - N - 2&&y< tamp) {
            cct_showch(1 + (N + 1) + (2 * (N + 1) + 1 + 9) * (dst - 'A'), y, ' ', COLOR_HYELLOW, COLOR_HYELLOW, 1);
        }
        //恢复缺省颜色
        cct_setcolor();
        cct_gotoxy(0, base_y + base_y / 4);
    }
}

//移动联合函数
void ring_move(int n, char src, char dst,int choice)
{
    if (choice == 9) {
        if (src == 'A' && dst == 'C') {
            ring_move_up(A[topA - 1], src,choice);
            ring_move_parallel(A[topA - 1], src, dst,choice);
            ring_move_down(A[topA - 1], dst,choice);
        }
        else if (src == 'A' && dst == 'B') {
            ring_move_up(A[topA - 1], src,choice);
            ring_move_parallel(A[topA - 1], src, dst,choice);
            ring_move_down(A[topA - 1], dst,choice);
        }
        else if (src == 'B' && dst == 'C') {
            ring_move_up(B[topB - 1], src,choice);
            ring_move_parallel(B[topB - 1], src, dst,choice);
            ring_move_down(B[topB - 1], dst,choice);
        }
        else if (src == 'B' && dst == 'A') {
            ring_move_up(B[topB - 1], src,choice);
            ring_move_parallel(B[topB - 1], src, dst,choice);
            ring_move_down(B[topB - 1], dst,choice);
        }
        else if (src == 'C' && dst == 'B') {
            ring_move_up(C[topC - 1], src,choice);
            ring_move_parallel(C[topC - 1], src, dst,choice);
            ring_move_down(C[topC - 1], dst,choice);
        }
        else if (src == 'C' && dst == 'A') {
            ring_move_up(C[topC - 1], src,choice);
            ring_move_parallel(C[topC - 1], src, dst,choice);
            ring_move_down(C[topC - 1], dst,choice);
        }
    }
    else
    {
        ring_move_up(n, src,choice);
        ring_move_parallel(n, src, dst,choice);
        ring_move_down(n, dst,choice);
    }
}

//汉诺塔游戏
void hanoi_game(int choice,char game_dst,int n)
{
    char src, tmp, dst;
    bool not_exit = true;

    while (not_exit) {
        //堆满了，游戏结束
        if (game_dst == 'A') {
            if (topA == n) {
                cct_gotoxy(0, base_y + N + 10);
                cout << "游戏中止!!!!!" << endl;
                break;
            }
        }
        if (game_dst == 'B') {
            if (topB == n) {
                cct_gotoxy(0, base_y + N + 10);
                cout << "游戏中止!!!!!" << endl;
                break;
            }
        }
        if (game_dst == 'C') {
            if (topC == n) {
                cct_gotoxy(0, base_y + N + 10);
                cout << "游戏中止!!!!!" << endl;
                break;
            }
        }
        src = getchar();
        //结束条件
        if (src == 'Q') {
            cct_gotoxy(0, base_y + N + 10);
            cout << "游戏中止!!!!!" << endl;
            not_exit = false;
        }
        dst = getchar();
        if (src == 'a' || src == 'b' || src == 'c') {
            src -= 32;
        }
        if (dst == 'a' || dst == 'b' || dst == 'c') {
            dst -= 32;
        }
        if ((src == 'A' && (dst == 'B' || dst == 'C')) || (src == 'B' && (dst == 'A' || dst == 'C')) || (src == 'C' && (dst == 'B' || dst == 'A'))) {
            tmp = input_tmp(src, dst);
        }
        cin.ignore(65536, '\n');
        //清除输入
        cct_gotoxy(60, base_y + N + 9);
        cout << "                                                 ";
        cct_gotoxy(60, base_y + N + 9);

        if (ring_exist(src)&& ring_can_move(src, dst)) {
            ring_move(0, src, dst, choice);
            i++;
            cct_gotoxy(0, base_y + N + 7);
            cout << "第" << setw(4) << i << " 步(" << setw(2) << n << "): " << src << "-->" << dst << " ";

            my_move(src, dst);//把最下面的搬到结束柱
            my_tower(choice);
            cct_gotoxy(0 + 21, base_y + N + 7);
            printshow(A, B, C, src, dst, n);
            cct_gotoxy(60, base_y + N + 9);
        }
        else if (!ring_exist(src)) {
                cct_gotoxy(0, base_y + N + 10);
                cout << "柱源为空！";
                Sleep(1000);
                cct_gotoxy(0, base_y + N + 10);
                cout << "            ";
                cct_gotoxy(60, base_y + N + 9);
        }
        else {
            cct_gotoxy(0, base_y + N + 10);
            cout << "大盘压小盘，非法移动！";
            Sleep(1000);
            cct_gotoxy(0, base_y + N + 10);
            cout << "                          ";
            cct_gotoxy(60, base_y + N + 9);
        }
    }
    return;
}


bool ring_exist(char src)
{
    if (src == 'A') {
        if (topA == 0) {
            return false;
        }
        else {
           return true;
        }
    }
    if (src == 'B') {
        if (topB == 0) {
            return false;
        }
        else {
            return true;
        }
    }
    if (src == 'C') {
        if (topC == 0) {
            return false;
        }
        else {
            return true;
        }
    }
    return true;
}

bool ring_can_move(char src, char dst)
{
    if (src == 'A' && dst == 'C') {
        if (A[topA - 1] > C[topC - 1]&& C[topC - 1]>0) {
            return false;
        }
        else {
            return true;
        }
    }
    else if (src == 'A' && dst == 'B') {
        if (A[topA - 1] > B[topB - 1]&& B[topB - 1]>0) {
            return false;
        }
        else {
            return true;
        }
    }
    else if (src == 'B' && dst == 'C') {
        if (B[topB - 1] > C[topC - 1]&& C[topC - 1]>0) {
            return false;
        }
        else {
            return true;
        }
    }
    else if (src == 'B' && dst == 'A') {
        if (B[topB - 1] > A[topA - 1]&& A[topA - 1]>0) {
            return false;
        }
        else {
            return true;
        }
    }
    else if (src == 'C' && dst == 'B') {
        if (C[topC - 1] > B[topB - 1]&& B[topB - 1]>0) {
            return false;
        }
        else {
            return true;
        }
    }
    else if (src == 'C' && dst == 'A') {
        if (C[topC - 1] > A[topA - 1]&& A[topA - 1]>0) {
            return false;
        }
        else {
            return true;
        }
    }
    return true;
}




