/* 大数据 2351136 李盛鹏 */
/* 2352748 杨钦战 2352036 雷达 2351582 程亦诚 2351867 毛经纶 2351268 祝叶安达 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include<stdbool.h>

typedef int Status;
#define NO_OPENED       -1          // 文件未打开
#define OK              1           // 表示成功
#define VALID_LENGTH    24      /* 有效数据区域 */
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

    printf("Usage : %s --infile hex格式文件 --outfile bin格式文件\n", exe_name);
    printf("        %s --infile a.hex --outfile a.bin\n", exe_name);

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

/* ================================================
将十六进制文件的内容转换回原始文件
================================================= */
static Status Convert_hex_to_original(FILE* infile, FILE* outfile)
{
    if (infile == NULL)
    {
        return NO_OPENED; // 表示未打开
    }

    // 选择输出流
    FILE* out_stream = (outfile != NULL) ? outfile : stdout;

    char line[256];
    while (fgets(line, sizeof(line), infile))
    {
        char* ptr;
        char* loc = line;
        char BASE[3] = { '\0' };       /* 十六进制值 */
        bool baseModified = false;   // 用于判断BASE是否被修改

        // 跳过地址部分
        while (*loc != ' ') loc++;
        while (*loc == ' ') loc++;

        // 读取十六进制值并写入原始文件
        for (ptr = loc; ptr < loc + VALID_LENGTH;)
        {
            baseModified = false; // 重置标记
            for (int i = 0; i < 2; i++)
            {
                if ((*ptr >= '0' && *ptr <= '9') || (*ptr >= 'a' && *ptr <= 'f') || (*ptr >= 'A' && *ptr <= 'F'))
                {
                    BASE[i] = *ptr;
                    baseModified = true; // 标记BASE已被修改
                    ptr++;
                }
            }
            ptr++;

            // 只有在BASE被修改的情况下才进行转换和输出
            if (baseModified)
            {
                char hexValue = (char)strtol(BASE, NULL, 16); // 使用strtol转换为整数
                fputc(hexValue, out_stream);
            }
        }

        /* 跳过中间的分割线 */
        ptr += DEVIDOR_LINE_WIDTH;
        loc = ptr;

        // 读取十六进制值并写入原始文件
        for (ptr = loc; ptr < loc + VALID_LENGTH;)
        {
            baseModified = false; // 重置标记
            for (int i = 0; i < 2; i++)
            {
                if ((*ptr >= '0' && *ptr <= '9') || (*ptr >= 'a' && *ptr <= 'f') || (*ptr >= 'A' && *ptr <= 'F'))
                {
                    BASE[i] = *ptr;
                    baseModified = true; // 标记BASE已被修改
                    ptr++;
                }
            }
            ptr++;

            // 只有在BASE被修改的情况下才进行转换和输出
            if (baseModified)
            {
                char hexValue = (char)strtol(BASE, NULL, 16); // 使用strtol转换为整数
                fputc(hexValue, out_stream);
            }
        }
    }

    return OK;
}

// 检查文件名是否以 .hex 结尾
bool isHexFile(const char* filename)
{
    const char* ext = ".hex";
    size_t len_filename = strlen(filename);
    size_t len_ext = strlen(ext);
    return (len_filename >= len_ext) && (strcmp(filename + len_filename - len_ext, ext) == 0);
}

int main(int argc, char* argv[])
{
    /* 解析infile和outfile */
    Param param_info[3] = { {"--infile",0,NULL},{"--outfile",0,NULL},{"",0,NULL} };
    parse_Commands(argc, argv, param_info);

    /* 如果没有infile */
    if (param_info[INFILE].happen == 0 || !isHexFile(param_info[INFILE].file_name))
    {
        Usage(argv[0]);
        return 0;
    }

    /* 到了这里说明一定有infile */
    FILE* in = fopen(param_info[INFILE].file_name, "r");
    FILE* out = (param_info[OUTFILE].happen != 0) ? fopen(param_info[OUTFILE].file_name, "wb") : NULL;

    /* 如果没打开 */
    if (in == NULL)
    {
        Usage(argv[0]);
        return 0;
    }

    // 将十六进制内容转换回原始文件
    Convert_hex_to_original(in, out);

    // 记得关闭文件
    fclose(in);
    if (out != NULL)  fclose(out);

    return 0;
}