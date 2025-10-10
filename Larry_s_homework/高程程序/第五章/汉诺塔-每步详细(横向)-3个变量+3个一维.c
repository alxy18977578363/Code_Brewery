/* 2351136 李盛鹏 信03 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#define N 10

//三个一维数组
int A[N], B[N], C[N];
//三个全局指针
int topA = -1, topB = -1, topC = -1;
//计数用的全局
int i = 0;


//数组初始化
void initial(int n,char src,char tmp,char dst)
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
        else if (src == 'B'){
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

    //输出初始化的那一行句子
    printf("初始:                ");
    printf("A:");
    for (int printcount = 0; printcount < topA; printcount++) {
        printf("%2d", A[printcount]);
    }
    for (int printcount = 0; printcount < N - topA; printcount++) {
        printf("  ");
    }
    
    printf(" B:");
    for (int printcount = 0; printcount < topB; printcount++) {
        printf("%2d", B[printcount]);
    }
    for (int printcount = 0; printcount < N - topB; printcount++) {
        printf("  ");
    }

    printf(" C:");
    for (int printcount = 0; printcount < topC; printcount++) {
        printf("%2d", C[printcount]);
    }
    for (int printcount = 0; printcount < N - topC; printcount++) {
        printf("  ");
    }
    printf("\n");
}

//展示现在每个环还有什么的函数
void printshow(int A[],int B[],int C[],char src,char dst,char n)
{
    printf("A:");
    for (int printcount = 0; printcount < topA; printcount++) {
        printf("%2d", A[printcount]);
    }
    for (int printcount = 0; printcount < N - topA; printcount++) {
        printf("  ");
    }

    printf(" B:");
    for (int printcount = 0; printcount < topB; printcount++) {
        printf("%2d", B[printcount]);
    }
    for (int printcount = 0; printcount < N - topB; printcount++) {
        printf("  ");
    }

    printf(" C:");
    for (int printcount = 0; printcount < topC; printcount++) {
        printf("%2d", C[printcount]);
    }
    for (int printcount = 0; printcount < N - topC; printcount++) {
        printf("  ");
    }
    printf("\n");

}

//移动的打印
void moveshow(char src, char dst, int n)
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
    
    printshow(A, B, C, src, dst,n);
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
        printf("第%4d 步(%2d): %c-->%c ", i, n, src, dst);
        moveshow(src, dst, n);//把最下面的搬到结束柱


        hanoi(n - 1, tmp, src, dst);//再把上面的n-1搬到结束柱

    }
}


int main()
{

    int n;
    char src, tmp, dst;

    //处理汉诺塔层数的错误判断
    while (1) {
        printf("请输入汉诺塔的层数(1-10)\n");
        int ret = scanf("%d", &n);

        if (n < 1 || n>N || ret == 0) {
            while (getchar() != '\n') {
                ;
            }
        }
        if (n >= 1 && n <= N) {
            while (getchar() != '\n') {
                ;
            }
            break;
        }
    }



    //处理起始柱的错误判断
    while (1) {
        printf("请输入起始柱(A-C)\n");
        int ret1 = scanf("%c", &src);
        if (src != 'a' && src != 'A' && src != 'b' && src != 'B' && src != 'c' && src != 'C' || ret1 == 0) {
            while (getchar() != '\n') {
                ;
            }
        }
        else {
            while (getchar() != '\n') {
                ;
            }
            if (src == 'a' || src == 'b' || src == 'c') {
                src -= 32;
            }
            break;
        }
    }

    //处理目标柱的错误判断
    while (1) {
        printf("请输入目标柱(A-C)\n");
        int ret2 = scanf("%c", &dst);
        if (dst == src || dst - 32 == src || src - 32 == dst) {
            if (dst == 'a' || dst == 'A') {
                printf("目标柱(A)不能与起始柱(A)相同\n");
            }
            if (dst == 'b' || dst == 'B') {
                printf("目标柱(B)不能与起始柱(B)相同\n");
            }
            if (dst == 'c' || dst == 'C') {
                printf("目标柱(C)不能与起始柱(C)相同\n");
            }
            while (getchar() != '\n') {
                ;
            }
            continue;
        }
        if (dst != 'a' && dst != 'A' && dst != 'b' && dst != 'B' && dst != 'c' && dst != 'C' || ret2 == 0) {
            while (getchar() != '\n') {
                ;
            }
        }
        else {
            while (getchar() != '\n') {
                ;
            }
            if (dst == 'a' || dst == 'b' || dst == 'c') {
                dst -= 32;
            }
            break;
        }
    }

    //确认中间柱
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


    //初始化柱子
    initial(n, src, tmp, dst);
    hanoi(n, src, tmp, dst);

    return 0;


}