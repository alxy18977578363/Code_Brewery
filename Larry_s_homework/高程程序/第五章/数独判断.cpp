/* 2351136 李盛鹏 信03 */
#include<iostream>
#define N 9
using namespace std;

bool Judge(int matrix[N][N], int function)
{
    bool valid = 1;
    // 如果 function 参数为1,检查每一行。
    if (function == 1) {
        for (int row = 0; row < N && valid; row++) {
            for (int column = 0; column < N && valid; column++) {
                for (int count = column + 1; count < N; count++) {
                    if (matrix[row][column] == matrix[row][count]) {
                        valid = false;
                        break;
                    }
                }
            }
        }
    }

    // 如果 function 参数为2，检查每一列
    if (function==2) {
        for (int column = 0; column < N && valid; column++) {
            for (int row = 0; row < N; row++) {
                for (int count = row + 1; count < N; count++) {
                    if (matrix[row][column] == matrix[count][column]) {
                        valid = false;
                        break;
                    }
                }
            }
        }
    }

     // 如果 function 参数为3，检查小方格3*3
    if (function == 3) {
        int startrow = 0, startcolumn = 0, matrixof3[9];

        //外围是检查竖着的
        while(valid && startrow < (N / 3 + 1) * 3){
            startcolumn = 0;
            while (valid && startcolumn < (N / 3 + 1) * 3) {
                int count = 0;
                for (int row = startrow; row < startrow + 3 && valid; row++) {
                    for (int column = startcolumn; column < startcolumn + 3 && valid; column++) {
                        matrixof3[count] = matrix[row][column];
                    }
                }
                //先检查横着的
                startcolumn += 3;
                for (int i = 0; i < 9 && valid; i++) {
                    for (int j = 0; j < 9 && valid; j++) {
                        if (matrix[i] == matrix[j]) {
                            valid = false;
                        }
                    }
                }
            }
            startrow += 3;
        }
    }
    return valid;
}

int main()
{
    int matrix[N][N], row = 0, column = 0, number = 0;

    //判断输入是否符合要求
    cout << "请输入9*9的矩阵，值为1-9之间" << endl;
    for (row = 0; row < N; row++) {
        for (column = 0; column < N; column++) {
            cin >> number;
            if (!cin.good()) {
                cin.clear();
                cin.ignore(65536, '\n');
                cout << "请重新输入第" << row + 1 << "行" << column + 1 << "列(行列均从1开始计数)的值" << endl;
                column--;
                continue;
            }
            if (cin.good() && number <= 9 && number >= 1) {
                matrix[row][column] = number;
            }
            else {
                cout << "请重新输入第" << row + 1 << "行" << column + 1 << "列(行列均从1开始计数)的值" << endl;
            }
        }
    }

    //判断是否为数独
    bool valid = 1;
    for(int count = 1; count <= 3&&valid; count++) {
        valid = Judge(matrix, count); 
    }
    //判断每个小空格


    if (valid == 0) {
        cout << "不是数独的解" << endl;
    }
    else {
        cout << "是数独的解" << endl;
    }

    return 0;
}
