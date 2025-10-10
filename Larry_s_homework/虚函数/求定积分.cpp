/* 2351136 李盛鹏 大数据 */
#include <iostream>
#include <cmath>
using namespace std;

/* 从此处到标记替换行之间，给出各种类的定义及实现
    1、不允许定义全局变量（不含const和#define）
    2、不允许添加其它系统头文件
*/
class integral
{
protected:
    double lower;  // 积分下限
    double upper;  // 积分上限
    int n;         // 划分数


public:
    integral();
    bool is_value();        // 判断输入的数是否value
    virtual void get_type_name() = 0;   // 取类型名
    virtual void show_answer() = 0;     // 展示结果
    virtual double value() = 0;  // 纯虚函数，用于计算积分值
    friend istream& operator>>(istream& is, integral& f);  // 重载输入运算符
};

integral::integral() :lower(0), upper(0), n(0)
{
}

bool  integral::is_value()      // 判断输入的数是否value
{
    if (n <= 0)
    {
        return false;
    }

    if (lower > upper)
    {
        return false;
    }

    return true;
}
istream& operator>>(istream& is, integral& f)
{

    while (true)
    {
        /* 提示信息 */
        cout << "请输入";
        f.get_type_name();
        cout << "的下限、上限及区间划分数量" << endl;

        is >> f.lower >> f.upper >> f.n;

        if (is.fail() || !f.is_value())
        {
            cout << "数据输入错误，请重新输入" << endl;
            is.clear();
            is.ignore(65536, '\n');
            continue;
        }
        else
        {
            break;
        }

    }

    f.show_answer();        // 输出结果
    return is;
}

class integral_sin : public integral
{
public:
    double value() override;  // 实现 sin(x) 的积分计算
    void get_type_name() override;   // 取类型名
    void show_answer() override;     // 展示结果
};

double integral_sin::value()
{
    double h = (upper - lower) / n;
    double sum = 0;
    for (int i = 1; i <= n; i++)
    {
        double x = lower + i * h;
        sum += sin(x);
    }
    return sum * h;
}

void integral_sin::get_type_name()
{
    cout << "sinxdx";
}

void integral_sin::show_answer()
{
    cout << "sinxdx[" << lower << "~" << upper << "/n=" << n << "] : " << value() << endl;
}


class integral_cos : public integral
{
public:
    double value() override;  // 实现 cos(x) 的积分计算
    void get_type_name() override;   // 取类型名
    void show_answer() override;     // 展示结果
};

double integral_cos::value()
{
    double h = (upper - lower) / n;
    double sum = 0;
    for (int i = 1; i <= n; i++)
    {
        double x = lower + i * h;
        sum += cos(x);
    }
    return sum * h;
}

void integral_cos::get_type_name()
{
    cout << "cosxdx";
};   // 取类型名

void integral_cos::show_answer()
{
    cout << "cosxdx[" << lower << "~" << upper << "/n=" << n << "] : " << value() << endl;
}

class integral_exp : public integral
{
public:
    double value() override;  // 实现 exp(x) 的积分计算
    void get_type_name() override;   // 取类型名
    void show_answer() override;    // 展示结果
};

double integral_exp::value()
{
    double h = (upper - lower) / n;
    double sum = 0;
    for (int i = 1; i <= n; i++)
    {
        double x = lower + i * h;
        sum += exp(x);
    }
    return sum * h;
}

void integral_exp::get_type_name()
{
    cout << "e^xdx";
}   // 取类型名

void integral_exp::show_answer()
{
    cout << "e^xdx[" << lower << "~" << upper << "/n=" << n << "] : " << value() << endl;
}

/* -- 替换标记行 -- 本行不要做任何改动 -- 本行不要删除 -- 在本行的下面不要加入任何自己的语句，作业提交后从本行开始会被替换 -- 替换标记行 -- */

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：fun_integral不准动，思考一下，integral应如何定义
***************************************************************************/
void fun_integral(integral& fRef)
{
    cin >> fRef;	//输入上下限、划分数
    cout << fRef.value() << endl;
    return;
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：main函数不准动
***************************************************************************/
int main()
{
    integral_sin s1;
    integral_cos s2;
    integral_exp s3;

    fun_integral(s1); //计算sinxdx的值
    fun_integral(s2); //计算cosxdx的值
    fun_integral(s3); //计算expxdx的值

    return 0;
}

//注：矩形计算取右值，输出为正常double格式

