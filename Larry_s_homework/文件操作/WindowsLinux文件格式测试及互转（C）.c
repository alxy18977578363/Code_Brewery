/* 2351136 大数据 李盛鹏 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include<stdbool.h>

/* 枚举 */
enum Format
{
    UNKNOWN,
    WINDOWS,
    LINUX,
    FAIL_OPENED
};



/* 输入格式 */
static void Usage(const char* file_name)
{
    printf("Usage: %s --check 文件名 | --convert{ wtol | ltow } 源文件名 目标文件名\n", file_name);
    printf("       %s --check a.txt\n", file_name);
    printf("       %s --convert wtol a.win.txt a.linux.txt\n", file_name);
    printf("       %s --convert ltow a.linux.txt a.win.txt\n", file_name);
}

/*===================================
    处理输入的文本，并返回文本类型
不能判断的情况:
1.既有\r\n又有\n 单独存在
2.没有\n
====================================*/
enum Format checkFormat(const char* filename)
{
    /* 打开失败处理 */
    FILE* file= fopen(filename, "rb");
    if (file == NULL)
    {
        return FAIL_OPENED; // 文件打开失败
    }

    int ch = -1;                    // 本次ch
    int last_ch = -1;               // 上次的ch
    bool hasLF = false;        /* 表示是否有\n */
    bool is_windows = false;   /* 判断是否为windows文本 */
    bool is_linux = false;     /* 判断是否为linux系统 */

    while ((ch = fgetc(file)) != EOF)
    {
        /* \r\n要同时出现才能说明问题 */
        if (ch == '\r')
        {
        }
        else if (ch == '\n')
        {
            hasLF = true;           // 有\n出现

            /* 如果前一个不是\r那就是linux系统 */
            if (last_ch != '\r')   is_linux = true;
            else                   is_windows = true;

        }

        last_ch = ch;       // 继承上一次的ch
    }


    /* 没有\n或者两种情况都有那就无法分辨 */
    if ((is_linux && is_windows) || (!hasLF))          /* 文件是否可以分辨 */
    {
        return UNKNOWN; // 文件格式无法识别
    }


    if (is_windows)
    {
        return WINDOWS; // Windows格式
    }
    else if (is_linux)
    {
        return LINUX; // Linux格式
    }

    return UNKNOWN; // 文件格式无法识别
}

/* 从windows转化为linux */
void convertWtoL(const char* inputFile, const char* outputFile)
{
    /* 1.input文件无法打开 */
    FILE* file= fopen(inputFile, "rb");
    if (file == NULL)
    {
        printf("文件打开失败\n");
        return;
    }

    /* 文件不是windows类型 */
    enum Format format = checkFormat(inputFile);
    if (format != WINDOWS)
    {
        printf("文件格式无法识别\n");
        fclose(file);
        return;
    }

    int num = 0;            /* 转化时转化的数量 */
    FILE* outFile = fopen(outputFile, "wb");

    /* 跳过\r输入 */
    int ch;
    while ((ch = fgetc(file)) != EOF)
    {
        if (ch == '\r')
        {
            num++;
            continue; // 跳过CR
        }
        fputc(ch, outFile);
    }

    printf("转换完成，去除%d个0x0D\n", num);
    fclose(file);
    fclose(outFile);
}

/* 从linux转化为windows */
void convertLtoW(const char* inputFile, const char* outputFile)
{
    /* input文件无法打开 */
    FILE* file = fopen(inputFile, "rb");
    if (file == NULL)
    {
        printf("文件打开失败\n");
        return;
    }

    enum Format format = checkFormat(inputFile);
    if (format != LINUX)
    {
        printf("文件格式无法识别\n");
        fclose(file);
        return;
    }

    int num = 0;            /* 转化时转化的数量 */
    FILE* outFile = fopen(outputFile, "wb");
    if (outFile == NULL)
    {
        printf("目标文件打开失败\n");
        fclose(file);
        return;
    }

    int ch;
    while ((ch = fgetc(file)) != EOF)
    {
        if (ch == '\n')
        {
            fputc('\r',outFile); // 在每个LF前添加CR
            num++;
        }
        fputc(ch,outFile);
    }

    printf("转换完成，加入%d个0x0D\n",num);
    fclose(file);
    fclose(outFile);
}

int main(int argc, char* argv[])
{
    /* 1.输入内容不符合要求 */
    if (argc < 3 || argc > 5)
    {
        Usage(argv[0]);
        return 1;
    }


    /* 这里的输入肯定参数超过两个 */
    char* command = argv[1];
    if (strcmp(command, "--check") == 0)       // 检查输入的文件种类
    {
        const char* filename = argv[2];           // 输入参数至少是两个，argv[2]一定存在
        enum Format format = checkFormat(filename);  // 检查名称是哪一个
        switch (format)
        {
        case WINDOWS:
            printf("Windows格式\n");
            break;
        case LINUX:
            printf("Linux格式\n");
            break;
        case UNKNOWN:
            printf("文件格式无法识别\n");
            break;
        case FAIL_OPENED:
            printf("文件打开失败\n");
            break;
        }
    }
    else if (strcmp(command, "--convert") == 0)        /* 如果是转化文件 */
    {
        if (argc != 5)                      /* 参数数量不对，返回错误 */
        {
            Usage(argv[0]);
            return 1;
        }
        const char* type = argv[2];               /* 转化类型 */
        const char* input_File = argv[3];          /* 转化的对象 */
        const char* output_File = argv[4];         /* 输出的对象 */

        if (strcmp(type, "wtol") == 0)
        {
            convertWtoL(input_File, output_File);
        }
        else if (strcmp(type, "ltow") == 0)
        {
            convertLtoW(input_File, output_File);
        }
        else
        {
            Usage(argv[0]);
            return 1;
        }
    }
    else
    {
        Usage(argv[0]);
        return 1;
    }

    return 0;
}