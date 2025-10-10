#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <fstream>
#include <cstring>
using namespace std;

struct student
{
    int* no;
    char* name;
    int* score;
    struct student* next;
};

// 清除申请空间
void release_Memory(student* head)
{
    student* p = head;
    while (p != nullptr)
    {
        student* temp = p; // 先保存当前节点
        p = p->next; // 移动到下一个节点

        delete temp->no;
        delete[] temp->name;
        delete temp->score;
        delete temp; // 释放当前节点
    }
}

template<typename T>
void elem_shenqing(T*& p, bool& memoryAllocationFailed) // 这个是元素的动态申请
{
    p = new(nothrow) T;
    if (p == nullptr)
    {
        cout << "元素内存申请失败" << endl;
        memoryAllocationFailed = true;
    }
    else
    {
        memoryAllocationFailed = false;
    }
}

int main()
{
    ifstream infile("list.txt"); // 直接在构造函数中打开文件
    if (!infile.is_open()) // 文件打开错误处理
    {
        cout << "文件打开失败" << endl;
        return -1;
    }

    student* head = nullptr;
    student* p = nullptr;
    student* q = nullptr; // 定义三个指针

    int no;
    bool memoryAllocationFailed = false; // 此bool变量为申请空间是否错误

    while (true)
    {
        infile >> no;
        if (no == 9999999) // 表示结束
        {
            break;
        }

        elem_shenqing(p, memoryAllocationFailed); // 申请p的空间
        if (memoryAllocationFailed)
        {
            release_Memory(head);
            return -1;
        }

        elem_shenqing(p->no, memoryAllocationFailed); // 申请p->no的空间,读入学号
        if (memoryAllocationFailed)
        {
            delete p; // 释放当前节点
            release_Memory(head);
            return -1;
        }
        *(p->no) = no;

        char name[9]; // 先读到这里，再判断大小
        infile >> name; // 先读入name，再根据name大小分配空间
        size_t name_length = strlen(name) + 1;
        p->name = new(nothrow) char[name_length]; // 按照长度分配空间
        if (p->name == nullptr)
        {
            cout << "数组内存分配失败" << endl;
            delete p->no;
            delete p; // 释放当前节点
            release_Memory(head);
            return -1;
        }
        strcpy(p->name, name);

        elem_shenqing(p->score, memoryAllocationFailed); // 读入分数
        if (memoryAllocationFailed)
        {
            delete[] p->name; // 释放已分配的名字内存
            delete p->no; // 释放已分配的学号内存
            delete p; // 释放当前节点
            release_Memory(head);
            return -1;
        }
        infile >> *(p->score);

        p->next = nullptr;

        if (head == nullptr) // 如果是第一个学生
        {
            head = q = p;
        }
        else
        {
            q->next = p;
            q = p;
        }
    }

    // 遍历，然后输出
    for (p = head; p; p = p->next)
    {
        cout << *(p->no) << " " << p->name << " " << *(p->score) << endl;
    }

    // 后期处理
    infile.close(); // 关闭文件
    release_Memory(head);
    return 0;
}
