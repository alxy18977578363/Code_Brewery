#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

struct student
{
    int* no;
    char* name;
    int* score;
    struct student* next;
};

void release_memory(struct student* head)
{
    struct student* p = head;
    while (p != NULL)
    {
        struct student* temp = p;
        p = p->next;
        if (temp->name != NULL)
            free(temp->name);
        if (temp->no != NULL)
            free(temp->no);
        if (temp->score != NULL)
            free(temp->score);
        free(temp);
    }
}

int main()
{
    FILE* infile = fopen("list.txt", "r"); // read方式读入文件
    if (infile == NULL) // 处理文件读入失败
    {
        printf("文件读入失败\n");
        return -1;
    }

    int no;
    char name[9];
    struct student* head = NULL;
    struct student* p = NULL;
    struct student* q = NULL; // 定义三个指针串成一个数组
    while (true)
    {
        fscanf(infile, "%d", &no); // 读入学号
        if (no == 9999999)
        {
            break; // 结束的标志
        }

        p = (struct student*)malloc(sizeof(struct student)); // 动态申请空间
        if (p == NULL) // 动态内存申请失败处理
        {
            printf("申请内存失败\n");
            release_memory(head); // 释放之前分配的内存
            return -1;
        }

        p->no = (int*)malloc(sizeof(int)); // 申请no的空间
        if (p->no == NULL)
        {
            printf("申请内存失败\n");
            free(p); // 释放当前节点的内存
            release_memory(head); // 释放之前分配的内存
            return -1;
        }
        *(p->no) = no;

        fscanf(infile, "%s", name);
        int name_length = strlen(name) + 1; // 计算长度
        p->name = (char*)malloc(sizeof(char) * name_length); // 申请名字的空间
        if (p->name == NULL)
        {
            printf("申请内存失败\n");
            free(p->no); // 释放已分配的学号内存
            free(p); // 释放当前节点的内存
            release_memory(head); // 释放之前分配的内存
            return -1;
        }
        strcpy(p->name, name);

        p->score = (int*)malloc(sizeof(int)); // 申请分数的空间
        if (p->score == NULL)
        {
            printf("申请内存失败\n");
            free(p->name); // 释放已分配的名字内存
            free(p->no); // 释放已分配的学号内存
            free(p); // 释放当前节点的内存
            release_memory(head); // 释放之前分配的内存
            return -1;
        }
        fscanf(infile, "%d", p->score);

        p->next = NULL;

        if (head == NULL)
        {
            head = q = p; // 第一个元素
        }
        else
        {
            q->next = p;
            q = p;
        }
    }

    // 输出内容
    p = head;
    while (p != NULL)
    {
        printf("%d %s %d\n", *(p->no), p->name, *(p->score));
        p = p->next;
    }

    // 后期处理
    fclose(infile); // 关闭文件
    release_memory(head); // 释放所有分配的内存
    return 0;
}
