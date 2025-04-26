#include <iostream>
#include <cstring>
#define stack_init_size            100        // 定义初始化空间大小
#define stack_increment            10        // 定义增量

#define SOVERFLOW -2
#define ERROR -1
#define OK    0

typedef char SElemType;  // 元素类型
typedef int Status;        // 返回值类型，状态
using namespace std;

struct sqstack
{
private:
    SElemType* top;
    SElemType* base;
    int size;
public:
    sqstack();        // 构造函数
    ~sqstack();        // 析构函数
    Status getTop(SElemType& e);        // 取顶端元素
    Status pop(SElemType& e);            // 删除顶端元素
    Status push(SElemType e);            // 将元素压入栈中
    Status clear();                        // 清理整个栈
    bool is_stack_empty();
};

sqstack::sqstack()
{
    /* 申请base的空间，不成功就返回 */
    base = new(nothrow)SElemType[stack_init_size];
    if (!base)
    {
        exit(SOVERFLOW);
    }

    /* 到了这里,肯定已经申请成功了 */
    top = base;
    size = stack_init_size;

}

sqstack::~sqstack()
{
    if (base)
        delete base;

    size = 0;
}

/* 取得顶上的元素,由于top的位置始终比原来的位置大1，所以要减一 */
Status sqstack::getTop(SElemType& e)
{
    if (top == base)
        return ERROR;
    e = *(top - 1);
    return OK;

}

/* 将一个元素压入栈 */
Status sqstack::push(SElemType e)
{
    /* 如果空间不够，补充空间 */
    if (top - base >= size)
    {
        SElemType* newstack = new(nothrow)SElemType[size + stack_increment];

        /* 错误处理 */
        if (!newstack)
        {
            exit(SOVERFLOW);
        }

        /* 将旧栈搬入新栈,删除旧栈,移向新栈 */
        memcpy(newstack, base, sizeof(SElemType) * size);
        delete base;
        base = newstack;
        top = base + size;
        size += stack_increment;
    }
    /* 如果空间足够，或者说补充空间后空间足够 */
    *(top++) = e;        // 先在原位置记录为e,top再++
    return OK;

}

/* 将一个元素压出栈 */
Status sqstack::pop(SElemType& e)
{
    if (base == top)
    {
        return ERROR;
    }

    /* 到了这里肯定不是空栈 */
    e = *(top - 1);
    top--;
    return OK;
}

Status sqstack::clear()
{
    //先销毁原有空间
    if (base)
        delete base;
    //重新申请
    base = new(nothrow) SElemType[stack_init_size];
    if (!base)
        exit(SOVERFLOW);

    top = base;
    size = stack_init_size;
    return OK;
}

bool sqstack::is_stack_empty()
{
    return base == top;
}

/* 下面的这个函数用来处理操作符的作用 */
static void operation(sqstack& value_stack, sqstack& op_stack)
{
    char ch;
    op_stack.pop(ch); // 取出一个运算符

    switch (ch)
    {
    case '|': {
        char ch1, ch2;
        value_stack.pop(ch2);
        value_stack.pop(ch1);
        value_stack.push((ch1 == 'V' || ch2 == 'V') ? 'V' : 'F');
        break;
    }
    case '&': {
        char ch1, ch2;
        value_stack.pop(ch2);
        value_stack.pop(ch1);
        value_stack.push((ch1 == 'V' && ch2 == 'V') ? 'V' : 'F');
        break;
    }
    case '!': {
        char get;
        value_stack.pop(get);
        value_stack.push(get == 'V' ? 'F' : 'V');
        break;
    }
    }

}

int main()
{
    sqstack value_stack, op_stack;        // value栈存命题,op栈存操作符

    SElemType ch, get = 0;            // 一个是读入，一个是从栈中取出来的元素

    int row_num = 1;        // 表示第几个表达式

    while ((ch = getchar()) != EOF)
    {
        /* 如果遇到回车，也就是一个表达式结束 */
        if (ch == '\n')
        {
            /* 将布尔运算完成,由于函数运算总是push一个元素到value栈内，所以value栈不可能为空 */
            while (!op_stack.is_stack_empty())
            {
                operation(value_stack, op_stack);
            }

            /* 不知道是否表达式合格，所以这里我只默认它合格 */
            SElemType answer;
            value_stack.pop(answer);
            value_stack.clear();

            cout << "Expression " << row_num << ": " << answer << endl;

            /* 表达式增加1 */
            row_num++;
        }

        /* 这里是准备入栈元素，实际上并没有入栈 */
        switch (ch)
        {
            /* 把正误都压入value栈 */
        case 'F':
        case 'V':
            value_stack.push(ch);
            break;
        case '(':
            op_stack.push(ch);
            break;
        case ')':
            /* 如果没找到左括号就要一直进入表达式,如果value表达式没值了就不能带表达式了 */
            while (!op_stack.is_stack_empty() && (op_stack.getTop(get), get != '('))
            {
                operation(value_stack, op_stack);
            }

            SElemType temp;
            /* 删除掉左括号  */
            op_stack.pop(temp);

            break;

            /* 要进栈的运算符更小一点，就要算之前的运算符 */
            /* 下面的逻辑运算符，遇到比自己优先级更大的元素就不再计算  */
        case'|':
            /* 首先，“|”前面肯定需要别的运算符，才可以运算 */
            /* 然后，只有!的优先级比|大,"("虽然优先级大，但是要等右括号 */
            while (!op_stack.is_stack_empty() && (op_stack.getTop(get), get == '!' || get == '&'))
            {
                operation(value_stack, op_stack);
            }
            /* 读入'|''&' */
            op_stack.push(ch);
            break;
        case'&':
            /* 首先，“|”前面肯定需要别的运算符，才可以运算 */
            /* 然后，只有!的优先级比|大,"("虽然优先级大，但是要等右括号 */
            while (!op_stack.is_stack_empty() && (op_stack.getTop(get), get == '!'))
            {
                operation(value_stack, op_stack);
            }
            /* 读入'|''&' */
            op_stack.push(ch);
            break;

            /* "！"需要对象才能编辑，此时刚读到"|",让它入栈即可 */
        case '!':
            op_stack.push(ch);
            break;
        default:
            break;
        }
    }

    return 0;
}