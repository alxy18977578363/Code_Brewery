/* 2351136 李盛鹏 大数据 */
#include <iostream>
#include <iomanip>
using namespace std;

#define STUDENT_NUM	4
#define SCORE_NUM	5

/* --- 不允许定义任何形式的全局变量 --- */

/***************************************************************************
  函数名称：average
  功    能：求第一门课的平均分
  输入参数：int(*score)[STUDENT_NUM]
  返 回 值：void
  说    明：输入一个行数组的指针，当是第0行的地址时为第1门课
***************************************************************************/
void average(int(*score)[STUDENT_NUM])
{
    /* 函数定义语句部分：
       1、本函数中仅允许定义 1个简单变量 + 1个指针变量 */

       /* 函数执行语句部分：
          1、不允许再定义任何类型的变量，包括 for (int i=0;...）等形式定义变量
          2、循环变量必须是指针变量，后续语句中不允许出现[]形式访问数组
             不允许：int a[10], i;
                     for(i=0; i<10; i++)
                         cout << a[i];
             允许  ：int a[10], p;
                     for(p=a; p<a+10; p++)
                         cout << *p;          */
    double sum = 0;
    int* p = *score;

    for (; p < *score + STUDENT_NUM; p++)
    {
        sum += *p;
    }
    cout << sum / STUDENT_NUM << endl;

}

/***************************************************************************
  函数名称：fail
  功    能：找出有两门以上课程不及格的学生
  输入参数：int(*score)[STUDENT_NUM]
  返 回 值：void 
  说    明：
***************************************************************************/
void fail(int(*score)[STUDENT_NUM])
{
    /* 函数定义语句部分：
       1、本函数中仅允许定义 3个简单变量 + 1个行指针变量 + 1个简单指针变量 */

       /* 函数执行语句部分（要求同average）*/
    int num; // 不及格课程数
    double sum; // 平均分
    int(*hang)[STUDENT_NUM] = score; // 行指针
    int* elem; // 学生成绩指针

    for (int student = 0; student < STUDENT_NUM; student++)
    {
        num = 0; // 每个学生的不及格课程数重置
        sum = 0; // 平均分重置
        elem = *hang + student; 

        for (; elem < *hang + STUDENT_NUM * SCORE_NUM; elem += STUDENT_NUM)
        {
            if (*elem < 60)
            {
                num++;
            }
            sum += *elem; // 累加成绩
        }

        if (num >= 2)
        {
            cout << "No：" << student + 1 << " ";
            for (elem = *hang + student; elem <*hang + student + STUDENT_NUM * SCORE_NUM; elem += STUDENT_NUM)
            {
                cout << *elem << " ";
            }
            cout << "平均：" << sum / SCORE_NUM << endl;
        }
    }
    

}

/***************************************************************************
  函数名称：
  功    能：找出平均成绩在90分以上或全部成绩在85分以上的学生
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void good(int(*score)[STUDENT_NUM])
{
    /* 函数定义语句部分：
       1、本函数中仅允许定义 3个简单变量 + 1个行指针变量 + 1个简单指针变量 */

       /* 函数执行语句部分（要求同average）*/
    int(*hang)[STUDENT_NUM] = score;
    int* p = *hang;
    int num = 0;
    double sum = 0;

    for (int student = 0; student < STUDENT_NUM; student++)
    {
        num = 0, sum = 0;
        p = *hang + student;

        for (; p < *hang + STUDENT_NUM * SCORE_NUM; p += STUDENT_NUM)
        {
            if (*p >= 85)
            {
                num++;
            }
            sum += *p;
        }

        if (num == SCORE_NUM || sum / SCORE_NUM >= 90)
        {
            cout << "No：" << student + 1<<" ";
            for (p = *hang + student; p < *hang + student + STUDENT_NUM * SCORE_NUM; p += STUDENT_NUM)
            {
                cout << *p << " ";
            }
            cout << "平均：" << sum / SCORE_NUM << endl;
        }
    }

}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int main()
{
    int a[SCORE_NUM][STUDENT_NUM] = {
        {91,92,93,97},  //第1-4个学生的第1门课成绩
        {81,82,83,85},  //第1-4个学生的第2门课成绩
        {71,72,99,87},  //第1-4个学生的第3门课成绩
        {61,32,80,91},  //第1-4个学生的第4门课成绩
        {51,52,95,88} };//第1-4个学生的第5门课成绩
    /* 除上面的预置数组外，本函数中仅允许定义 1个行指针变量 + 1个简单指针变量 */

    /* 函数执行语句部分（要求同average）*/
    int(*hang)[STUDENT_NUM] = a;
    int* p = *hang;

    cout << "初始信息：" << endl;
    for (; hang < a + SCORE_NUM; hang++)
    {
        cout << "No.1-4学生的第" << hang - a + 1 << "门课的成绩：";
        for (p = *hang; p < *hang + STUDENT_NUM; p++)
        {
            cout << *p << " ";
        }
        cout << endl;
    }
    cout << endl;
    // 第一门课平均分
    cout << "第1门课平均分：";
    average(&a[0]);
    cout << endl;

    // 2门以上不及格的学生自身平均分
    cout << "2门以上不及格的学生：" << endl;
    fail(&a[0]);
    cout << endl;

    // 平均90以上或全部85以上的学生
    cout << "平均90以上或全部85以上的学生：" << endl;
    good(&a[0]);

    return 0;
}