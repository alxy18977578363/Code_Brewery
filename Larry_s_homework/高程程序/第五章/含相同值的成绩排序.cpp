/* 2351136 李盛鹏 信03 */
#include<iostream>
#define N 1000
using namespace std;
int main() {
    cout << "请输入成绩（最多1000个），负数结束输入" << endl;
    int form[N], person = 0, num = 0;
    
    for (person = 0; person < N; person++) {
        int number = 0;
        cin >> number;

        if (number < 0 || !cin.good()) {
            break;
        }

        if (number >= 0 && number <= 100) {
            form[num] = number;
            num++;
        }
    }

    // 输出原数组
    cout << "输入的数组为:" << endl;
    for (person = 0; person < num; person++) {
        cout << form[person] << " ";
        if ((person + 1) % 10 == 0) {
            cout << endl;
        }
    }
    cout << endl;

    // 调整次序
    for (person = 0; person < num; person++) {
        for (int person2 = person; person2 < num; person2++) {
            if (form[person2] >= form[person]) {
                int temp = form[person];
                form[person] = form[person2];
                form[person2] = temp;
            }
        }
    }

    // 输出排名表
    cout << "分数与名次的对应关系为:" << endl;
    int rank = 1, count = 0, i = 0;
    for (person = 0; person < num; person++) {
        if (person > 0 && form[person] != form[person - 1]) {
            rank += count;
            i = count;
            count = 1;
        }
        else {
            count++;
        }
        cout << form[person] << " " << rank << endl;
    }

	return 0;
}

