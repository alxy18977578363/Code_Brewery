/* 2351136 信03 李盛鹏 */
#include"7-b2.h"
#include<iostream>
#include"cmd_console_tools.h"
#include <conio.h>
#define tuxiang_x 2

using namespace std;
/* 1、按需加入头文件
   2、不允许定义全部变量，包括静态全局，但不限制const及define
   3、允许定义需要的结构体、函数等，但仅限本源程序文件使用 */

   /* 例：声明仅本源程序文件需要的结构体，不要放到.h中
          仅为示例，不需要可删除 */


/***************************************************************************
  函数名称：even()
  功    能：输入一个值，把它向上补成偶数
  输入参数：int a
  返 回 值：
  说    明：定义仅本源程序文件需要的函数，设置为static即可
***************************************************************************/
static int even(int a)
{
    if (a % 2 != 0)
    {
        return a + 1;
    }
    else
    {
        return a;
    }
}

//下面这个函数用来判断最后一个字符是不是汉字的前半字符
bool judge_hanzi(const char* ptr, int width)
{
    //一开始默认不是汉字前半段
    bool last_hanzi = false;

    //遇到一个0xA1-0xFE之间的ASCII码值就转化      //最后ptr指向width的后一位
    for (int i = 0; i < width; i++)
    {
        unsigned char p = *ptr;
        if (p >= 0xA1 && p<= 0xFE)
        {
            if (last_hanzi)
            {
                last_hanzi = false;
            }
            else
                last_hanzi = true;
        }

        ptr++;
    }

    
    return last_hanzi;
}

//该函数用来截断
static char* content(char array[], const char* ptr, int width)
{
    int i = 0;

    //将内容复制给array
    for (i = 0; i < width && *ptr != '\0'; i++)
    {
        array[i] = *ptr;
        ptr++;
    }

    //如果最后一位是汉字的前半边字符，那就用' '代替
    if (judge_hanzi(array,width))
    {
        array[i - 1] = ' ';
    }

    //最后一位补尾0
    array[i] = '\0';

    return array;         //把复制好的内容返回给pop_menu
}

/***************************************************************************
  函数名称：pop_menu()
  功    能：供测试用例调用的函数，函数声明在头文件中
  输入参数：const char menu[][MAX_ITEM_LEN], const struct PopMenu* original_para
  返 回 值：int
  说    明：
***************************************************************************/
int pop_menu(const char menu[][MAX_ITEM_LEN], const struct PopMenu* original_para)
{
    //下面的计数变量表示第几个选项,另一个表示第几列
    int count = 1, col = 1;

    //下面的定义用来作为内容复制的承载数组
    char array[100] = { 0 };

    //下面的定义能把所有后续要调用的值变成偶数                       //取title和width较大的一个值作为宽度     //打印menu的高度，取menu和original_para->high更小的一个
    int title = even(strlen(original_para->title)), width = original_para->width > title ? original_para->width : title, high = (original_para->high > 10 ? 10 : original_para->high);//width = even(original_para->width) > title ? even(original_para->width) : title

    //制表符"╔", "╚", "╗", "╝", "═", "║", "╦", "╩", "╠", "╣", "╬"
    //输出"╔════╗"
    cct_showstr(original_para->start_x, original_para->start_y, "╔", original_para->bg_color, original_para->fg_color);
    cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y, "═", original_para->bg_color, original_para->fg_color, even(width)/2);
    cct_showstr(original_para->start_x + tuxiang_x +even(width), original_para->start_y, "╗", original_para->bg_color, original_para->fg_color);


    //输出title
    cct_showstr(original_para->start_x + tuxiang_x + (even(width) - title) / tuxiang_x / 2 * 2, original_para->start_y, content(array, original_para->title, strlen(original_para->title)), original_para->bg_color, original_para->fg_color);


    //输出数组框架
    for (int i = 1; i <= high; i++)
    {
        //先把底座画好
        cct_showstr(original_para->start_x, original_para->start_y + i, "║", original_para->bg_color, original_para->fg_color);
        cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + i, " ", original_para->bg_color, original_para->fg_color, even(width));
        cct_showstr(original_para->start_x + tuxiang_x + even(width), original_para->start_y + i, "║", original_para->bg_color, original_para->fg_color);
    }


    //输出下边框
   //输出"╚════╝"
    cct_showstr(original_para->start_x, original_para->start_y + high + 1, "╚", original_para->bg_color, original_para->fg_color);
    cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + high + 1, "═", original_para->bg_color, original_para->fg_color, even(width) / 2);
    cct_showstr(original_para->start_x + tuxiang_x + even(width), original_para->start_y + high + 1, "╝", original_para->bg_color, original_para->fg_color);

    //输出menu内容         

    for (int i = 1; i <= high; i++)
    {
        int length = ((int)strlen(menu[i - 1]) >(int) width ? width : (int)strlen(menu[i - 1]));     //取较短的一段作为输出长度
        cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + i, content(array, menu[i - 1], length), original_para->bg_color, original_para->fg_color);
    }
    
    //将选中的给染色
    int length = ((int)strlen(menu[0]) > (int)width ? width : (int)strlen(menu[0]));     //取较短的一段作为输出长度

    cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + col, " ", original_para->fg_color, original_para->bg_color, even(width));
    cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + col, content(array, menu[0], length), original_para->fg_color, original_para->bg_color);

    while (1)
    {
        //读第一个ASCII码如果是上下键，则第一个是224，而且留下一个ASCII码值在缓冲区
        unsigned char key = _getch();
        if (key == 224||key==0)
        {
            key = _getch();
            switch (key)
            {
            case 72:        //上移
                if (count > 1)           //菜单往上一格。
                    count--;
                if (col > 1)
                    col--;

                           //闪烁变化
                
                    for (int i = 1; i <= high; i++)     //从上方往下一个high行
                    {
                        length = ((int)strlen(menu[count - col + i - 1]) >(int) width ? width : (int)strlen(menu[count - col + i - 1]));
                        //输出白格子,抹除前一次的输出
                        cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + i, " ", original_para->bg_color, original_para->fg_color, even(width));
                        //输出内容
                        cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + i, content(array, menu[count - col + i - 1], length), original_para->bg_color, original_para->fg_color);
                    }
                    //选中染色
                    length = ((int)strlen(menu[count - 1]) > (int)width ? width : (int)strlen(menu[count - 1]));
                    cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + col, " ", original_para->fg_color, original_para->bg_color, even(width));
                    cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + col, content(array, menu[count - 1], length), original_para->fg_color, original_para->bg_color);

                
                break;
            case 80:
                if (count < 10)           //菜单往下一格。
                    count++;
                if (col < high)
                    col++;
                
                   

                    for (int i = 1; i <= high; i++)     //从上方往下一个high行
                    {
                        length = ((int)strlen(menu[count - col + i - 1]) >(int) width ? width : (int)strlen(menu[count - col + i - 1]));
                        //输出白格子,抹除前一次的输出
                        cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + i, " ", original_para->bg_color, original_para->fg_color, even(width));
                        //输出内容
                        cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + i, content(array, menu[count - col + i - 1], length), original_para->bg_color, original_para->fg_color);
                    }
                    length = ((int)strlen(menu[count - 1]) > (int)width ? width : (int)strlen(menu[count - 1]));
                    //选中染色
                    cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + col, " ", original_para->fg_color, original_para->bg_color, even(width));
                    cct_showstr(original_para->start_x + tuxiang_x, original_para->start_y + col, content(array, menu[count - 1], length), original_para->fg_color, original_para->bg_color);

                
                break;
            default:
                break;

            }
        }
        else if (key == '\r')
            break;


    }
    
    
    return count; //按需返回
}