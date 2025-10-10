/* 大数据 2351136 李盛鹏 */
/* 2252036 苏惠 2352475 易阳 2352036 雷达 2352748 杨钦战 2351582 程亦诚 2351126 谢诗阳 */
#include <iostream>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <cstring>
using namespace std;

typedef int Status;
#define NO_OPENED       -1          // 文件未打开
#define OK              1           // 表示成功
#define VALID_LENGTH    24      /* 有效数据区域 */
#define DEVIDOR_LINE_WIDTH    2

/*=======================================
用来提示用户使用本exe时应当输入的格式
exe_name：表示本exe的名字
=========================================*/
static void Input_tips(const char* exe_name)
{

    cout << "Usage : " << exe_name << " --infile hex格式文件 --outfile bin格式文件" << endl;
    cout.width(strlen("Usage : "));
    cout << " " << exe_name << " --infile a.hex --outfile a.bin" << endl;

}

// 解析命令行参数
void parse_Commands(int argc, char* argv[], char* (&infile), char* (&outfile))
{
    for (int i = 1; i < argc; ++i)
    {
        if (strcmp(argv[i], "--infile") == 0 && i + 1 < argc)
        {
            infile = argv[++i];
        }
        else if (strcmp(argv[i], "--outfile") == 0 && i + 1 < argc)
        {
            outfile = argv[++i];
        }
    }
}

/* ================================================
将十六进制文件的内容转换回原始文件
================================================= */
static Status Convert_hex_to_original(ifstream& infile, ofstream& outfile)
{
    if (infile.is_open() == 0)
    {
        return NO_OPENED; // 表示未打开
    }

    // 选择输出流
    ostream& out_stream = outfile.is_open() ? outfile : cout;

    char line[256];
    while (infile.getline(line, sizeof(line)))
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
                int hexValue = stoi(BASE, nullptr, 16); // 转换为整数
                out_stream << static_cast<char>(hexValue);
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
                int hexValue = stoi(BASE, nullptr, 16); // 转换为整数
                out_stream << static_cast<char>(hexValue);
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
    char* infile = NULL;
    char* outfile = NULL;
    parse_Commands(argc, argv, infile, outfile);

    /* 如果没有infile */
    if (infile == NULL || !isHexFile(infile))
    {
        Input_tips(argv[0]);
        return 0;
    }

    ifstream in;
    ofstream out;
    if (infile) in.open(infile, ios::in | ios::binary);
    if (outfile) out.open(outfile, ios::out | ios::binary);

    /* 如果没打开 */
    if (in.is_open() == 0)
    {
        Input_tips(argv[0]);
        return 0;
    }

    // 将十六进制内容转换回原始文件
    Convert_hex_to_original(in, out);

    // 记得关闭文件
    in.close();
    out.close();

    return 0;
}
