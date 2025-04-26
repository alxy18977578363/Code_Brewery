#include<iostream>
#define max_row        1000
#define max_col        1000    
using namespace std;

int map[max_row + 10][max_col + 10];
char mark_matrix[max_row + 10][max_col + 10];

/*-----------------------------------------
下面的这个函数利用递归来寻找周围的标记部位
input_index：需要计算区域数的数组
mark_index：标记哪些位置曾经遍历过。
area：哪些区域曾经经历过
------------------------------------------*/
void Markers(int row_y, int col_x, const int input_row, const int input_col)
{
    /* 如果这个位置被标记过,说明经历过，要返回，防止重复计数 */
    if (mark_matrix[row_y][col_x] == '*')
    {
        return;
    }

    /* 否则,上记号 */
    mark_matrix[row_y][col_x] = '*';



    /* 到了这里肯定是没有遍历过的 */
    /* 判断是否为边界 */
    /* 向左检查 */
    if (col_x > 0 && map[row_y][col_x - 1])
    {
        Markers(row_y, col_x - 1, input_row, input_col);
    }

    /* 向右检查 */
    if (col_x < input_col - 1 && map[row_y][col_x + 1])
    {
        Markers(row_y, col_x + 1, input_row, input_col);
    }

    /* 向上检查 */
    if (row_y > 0 && map[row_y - 1][col_x])
    {
        Markers(row_y - 1, col_x, input_row, input_col);
    }

    /* 向下检查 */
    if (row_y < input_row - 1 && map[row_y + 1][col_x])
    {
        Markers(row_y + 1, col_x, input_row, input_col);
    }
}

int main()
{
    int input_row = -1, input_col = -1;            // 输入的row和col
    int area = 0;                                    // 表示区域数

    cin >> input_row >> input_col;

    /* 将数组读入结构体 */
    for (int row = 0; row < input_row; row++)
    {
        for (int col = 0; col < input_col; col++)
        {
            /* 对应位置的值,input_col表示一列的元素数量，而row表示当前行 */
            cin >> map[row][col];
        }
    }

    /* 将结构体内部数组打上标记 */
    /* 这里由于只在边缘的区域不算总数,所以只管中间的就行 */
    for (int row = 1; row < input_row - 1; row++)
    {
        for (int col = 1; col < input_col - 1; col++)
        {
            /* 如果这个区域没有被经历，而且存在细胞，区域增加 */
            if (map[row][col] && mark_matrix[row][col] != '*')
            {
                area++;
                Markers(row, col, input_row, input_col);
            }
        }
    }


    /* 最后输出区域数 */
    cout << area;

    return 0;
}