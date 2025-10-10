/* 大数据 2351136 李盛鹏 */
#include <iostream>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <cstring>
using namespace std;

typedef int Status;
#define NO_OPENED       -1          // 文件未打开
#define OK              1           // 表示成功
#define LINE_LIMIT_LENGTH    16      /* 一行十六个 */
#define DEVIDOR_LINE_WIDTH    2

/*=======================================
用来提示用户使用本exe时应当输入的格式
exe_name：表示本exe的名字
=========================================*/
static void Input_tips(const char* exe_name)
{

    cout << "Usage : " << exe_name << " --infile 原始文件[--outfile hex格式文件]" << endl;
    cout.width(strlen("Usage : "));
    cout << " " << exe_name << " --infile a.docx" << endl;

     cout.width(strlen("Usage : "));
    cout << " " << exe_name << " --infile a.docx --outfile a.hex" << endl;

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

static Status Print_in_hex(std::ifstream& infile, std::ofstream& outfile)
{
    if (!infile.is_open())
    {
        return NO_OPENED; // 表示未打开
    }

    // 选择输出流
    ostream& out_stream = outfile.is_open() ? outfile : std::cout;

    char buffer[16];
    size_t bytesRead = 0;
    size_t offset = 0;

    // 处理正常行
    while (infile.read(buffer, sizeof(buffer))|| (bytesRead = infile.gcount())>0)
    {
        bytesRead = infile.gcount();

        // 地址一共八位
        out_stream << setw(8) << setfill('0') << hex << offset << "  ";

        for (size_t i = 0; i < 16; ++i)
        {
            /* 分隔符 */
            if (i == LINE_LIMIT_LENGTH / 2)
            {
                (bytesRead <= LINE_LIMIT_LENGTH / 2) ? out_stream << "  " : out_stream << "- ";
            }

            if (i < bytesRead)
            {
                out_stream << setw(2) <<setfill('0') << static_cast<int>(static_cast<unsigned char>(buffer[i]));
            }
            else
            {
                out_stream << "  ";
            }

            /* 每个十六进制之间的分隔 */
            if (i < LINE_LIMIT_LENGTH - 1)
            {
                out_stream << " ";
            } 
        }

        // 右边间隔五个空格
        out_stream << setfill(' ') << setw(5) << " ";

        for (size_t i = 0; i < 16; ++i)
        {
            if (i < bytesRead)
            {
                char c = buffer[i];
                if (c >= 33 && c <= 126)
                {
                    out_stream << c;
                }
                else
                {
                    out_stream << '.';
                }
            }
        }

        out_stream << endl;
        offset += 16;
    }


    return OK;
}


int main(int argc, char* argv[])
{
    /* 解析infile和outfile */
    char* infile = NULL;
    char* outfile = NULL;
    parse_Commands(argc, argv, infile, outfile);

    /* 如果没有infile */
    if (infile == NULL)
    {
        Input_tips(argv[0]);
        return 0;
    }

    ifstream in;
    ofstream out;
    if (infile) in.open(infile, ios::in | ios::binary);
    if (outfile) out.open(outfile, ios::out);

    /* 如果没打开 */
    if (in.is_open() == 0)
    {
        Input_tips(argv[0]);
        return 0;
    }

    // 将十六进制内容转换回原始文件
    Print_in_hex(in, out);

    // 记得关闭文件
    in.close();
    out.close();

    return 0;
}