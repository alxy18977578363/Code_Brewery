#include <iostream>
#include <string>
#include <cstring>
using namespace std;

typedef struct stu_info
{
    string xuehao;
    string name;
} Student;

class studentlist
{
private:
    Student* a_student; // 动态数组元素
    int most_num; // 当前数组容量
    int num; // 当前元素个数

public:
    studentlist(int most_num) : most_num(most_num), num(0)
    {
        a_student = new Student[most_num]; // 初始化动态数组
    }

    ~studentlist()
    {
        delete[] a_student; // 销毁动态数组
    }

    void input_student(int n)
    {
        if (n > most_num)
        {
            n = most_num; // 限制最大输入数量
        }
        for (int i = 0; i < n; i++)
        {
            cin >> a_student[i].xuehao >> a_student[i].name;
        }
        num += n;
    }

    int insert(int index, const string& xuehao, const string& name)
    {
        if (index < 1 || index > num + 1) return -1; // 位置不合法

        // 扩展容量
        if (num >= most_num)
        {
            most_num += 100; // 每次扩展100
            Student* new_array = new Student[most_num];
            for (int i = 0; i < num; i++)
            {
                new_array[i] = a_student[i];
            }
            delete[] a_student; // 释放原数组
            a_student = new_array; // 更新指针
        }

        for (int i = num; i >= index; i--)
        {
            a_student[i] = a_student[i - 1]; // 移动元素
        }
        a_student[index - 1].xuehao = xuehao;
        a_student[index - 1].name = name;
        num++;
        return 0;
    }

    int remove(int index)
    {
        if (index < 1 || index > num) return -1; // 位置不合法

        for (int i = index; i < num; i++)
        {
            a_student[i - 1] = a_student[i]; // 移动元素
        }
        // 清空最后一个元素的信息（可选）
        a_student[num - 1].xuehao = ""; // 清空学号
        a_student[num - 1].name = "";   // 清空姓名

        num--;
        return 0;
    }

    void check_name(const string& name)
    {
        bool found = false; // 标记是否找到
        for (int i = 0; i < num; i++)
        {
            if (name == a_student[i].name)
            {
                cout << i + 1 << " " << a_student[i].xuehao << " " << a_student[i].name << endl; // 输出信息
                return;
            }
        }
        cout << -1 << endl; // 如果没有找到
    }

    void check_no(const string& xuehao)
    {
        for (int i = 0; i < num; i++)
        {
            if (xuehao == a_student[i].xuehao)
            {
                cout << i + 1 << " " << a_student[i].xuehao << " " << a_student[i].name << endl; // 输出信息
                return;
            }
        }
        cout << -1 << endl; // 如果没有找到
    }

    int end()
    {
        return num; // 返回当前学生数量
    }
};

int main()
{
    int n;
    cin >> n;
    string xuehao, name;
    string command;

    studentlist mylist(10000);
    mylist.input_student(n); // 读入学生

    while (cin >> command)
    {
        if (command == "insert")
        {
            int index;
            cin >> index >> xuehao >> name;
            cout << mylist.insert(index, xuehao, name) << endl;
        }
        else if (command == "remove")
        {
            int index;
            cin >> index;
            cout << mylist.remove(index) << endl;
        }
        else if (command == "check")
        {
            string object;
            cin >> object;

            if (object == "name")
            {
                cin >> name;
                mylist.check_name(name);
            }
            else if (object == "no")
            {
                cin >> xuehao;
                mylist.check_no(xuehao);
            }
        }
        else if (command == "end")
        {
            cout << mylist.end() << endl;
            break; // 结束循环
        }
    }

    return 0;
}
