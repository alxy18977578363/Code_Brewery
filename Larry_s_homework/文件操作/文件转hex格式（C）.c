/* 大数据 2351136 李盛鹏 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include<stdbool.h>

typedef int Status;
#define NO_OPENED       -1          // 文件未打开
#define OK              1           // 表示成功
#define LINE_LIMIT_LENGTH    16      /* 一行十六个 */
#define DEVIDOR_LINE_WIDTH    2

typedef struct Param
{
    const char* command;            // 命令
    int happen;                     // 出现次数
    const char* file_name;

}Param;

enum Command_location
{
    INFILE = 0,
    OUTFILE,
    LOC_MAX
};

/*=======================================
用来提示用户使用本exe时应当输入的格式
exe_name：表示本exe的名字
=========================================*/
static void Usage(const char* exe_name)
{
    printf("Usage :  %s --infile 原始文件[--outfile hex格式文件]\n", exe_name);
    printf("         %s --infile a.docx\n", exe_name);
    printf("         %s --infile a.docx --outfile a.hex\n", exe_name);
}

// 解析命令行参数
void parse_Commands(int argc, char* argv[], Param* param_info)
{
    for (int argc_count = 1; argc_count < argc;)
    {
        bool found = false;

        for (int info_count = 0; strcmp(param_info[info_count].command, "") != 0; info_count++)
        {
            if (strcmp(param_info[info_count].command, argv[argc_count]) == 0)
            {
                /* 找到该名字 */
                found = true;

                param_info[info_count].happen++;
                param_info[info_count].file_name = argv[argc_count + 1];

                argc_count += 2;
                break;
            }

        }

        if (!found)
        {
            ++argc_count;
        }
    }
}

static Status Print_in_hex(FILE* infile, FILE* outfile)
{
    if (infile == NULL)
    {
        return NO_OPENED; // 表示未打开
    }

    // 选择输出流
    FILE* out_stream = (outfile != NULL) ? outfile : stdout;

    unsigned char buffer[16];
    int bytesRead = 0;
    int offset = 0;

    // 处理正常行,读取内容同时得到读取的个数
    while ((bytesRead = fread(buffer, 1, sizeof(buffer), infile)) > 0)
    {

        // 地址一共八位
        fprintf(out_stream, "%08x  ", offset);

        for (int i = 0; i < 16; ++i)
        {
            /* 分隔符 */
            if (i == LINE_LIMIT_LENGTH / 2)
            {
                (bytesRead <= LINE_LIMIT_LENGTH / 2) ? fprintf(out_stream, "  ") : fprintf(out_stream, "- ");
            }

            if (i < bytesRead)
            {
                fprintf(out_stream, "%02x", buffer[i]);
            }
            else
            {
                fprintf(out_stream, "  ");
            }

            /* 每个十六进制之间的分隔 */
            if (i < LINE_LIMIT_LENGTH - 1)
            {
                fprintf(out_stream, " ");
            }
        }

        // 右边间隔五个空格
        fprintf(out_stream, "     ");

        for (int i = 0; i < 16; ++i)
        {
            if (i < bytesRead)
            {
                char c = buffer[i];
                if (c >= 33 && c <= 126)
                {
                    fputc(c, out_stream);
                }
                else
                {
                    fputc('.', out_stream);
                }
            }
        }

        fprintf(out_stream, "\n");
        offset += 16;
    }


    return OK;
}


int main(int argc, char* argv[])
{
    Param param_info[3] = { {"--infile",0},{"--outfile",0},{"",0} };

    /* 解析infile和outfile */
    parse_Commands(argc, argv, param_info);

    /* 如果没有infile */
    if (param_info[INFILE].happen == 0)
    {
        Usage(argv[0]);
        return 0;
    }

    FILE* in = fopen(param_info[INFILE].file_name, "rb");
    FILE* out = (param_info[OUTFILE].happen != 0) ? fopen(param_info[OUTFILE].file_name, "w") : NULL;

    /* 如果没打开 */
    if (in == NULL)
    {
        Usage(argv[0]);
        return 0;
    }

    // 将十六进制内容转换回原始文件
    Print_in_hex(in, out);

    // 记得关闭文件
    fclose(in);
    if (out != NULL) fclose(out);

    return 0;
}