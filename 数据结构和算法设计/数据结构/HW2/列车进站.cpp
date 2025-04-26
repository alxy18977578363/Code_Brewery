#include <iostream>
#include <iomanip>
using namespace std;

#define max_element            100            // 定义栈的最大元素量

static bool canExit(char(&entry)[max_element], int entry_num, char(&exit)[max_element], int exit_num)
{
    /* 顶指针 */
    int top = -1;
    char station[max_element];        // 车站
    int entry_index = 0;
    int exit_index = 0;

    /* 如果能从这个循环中走出,则说明符合题意 */
    while (exit_index < exit_num)
    {
        /*-------------------------------------
        入栈
        1. 入栈顺序有几个元素就最多只能进多少元素
        2. 入栈元素和出栈元素不相等才可以出栈
        --------------------------------------*/
        while (entry_index < entry_num && station[top] != exit[exit_index])
        {
            station[++top] = entry[entry_index];
            entry_index++;
        }

        /*----------------------------------------------------------------
        由于前面的while有两个条件，要么入栈序列还有数，要么栈顶等于出栈序列
        也就是说，如果过不了出栈的if，那就说明入栈序列没有数了，那么就说明false了
        -----------------------------------------------------------------*/
        /* 出栈 */
        if (top != -1 && station[top] == exit[exit_index])
        {
            top--;
            exit_index++;
        }
        else
        {
            return false;
        }
    }

    return true;

}


int main()
{
    /* 定义一个入栈序列 */
    char entry[max_element];

    /* 读入入栈的序列 */
    cin >> entry;

    int entry_num = 0;

    /* 长度 */
    while (entry[entry_num] != '\0')
    {
        entry_num++;
    }

    /* 定义一个出栈序列 */
    char exit[max_element];

    /* 遇到Eof会退出 */
    while (cin >> exit)
    {
        /* 出栈序列的数量 */
        int exit_num = 0;

        while (exit[exit_num] != '\0')
        {
            exit_num++;
        }

        if (canExit(entry, entry_num, exit, exit_num))
        {
            cout << "yes" << endl;
        }
        else
        {
            cout << "no" << endl;
        }
    }

    return 0;
}
