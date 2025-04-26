#include<iostream>
using namespace std;

typedef struct _node Node;
typedef struct _node
{
    // 一个系数，一个指数，和下一个节点
    int value;
    int zhishu;
    Node* next;

    _node(int value, int zhishu) : value(value), zhishu(zhishu), next(nullptr)
    {
    }
};

class duoxiangshi
{
private:
    Node* head;  // 多项式的头指针,可访问自己结构体内成员
public:
    duoxiangshi() : head(nullptr)
    {
    } // 构造函数
    ~duoxiangshi()
    {
        Node* current = head;
        while (current != nullptr)
        {
            Node* next = current->next;
            delete current;
            current = next;
        }
    }
    // 插入一个新的节点
    void insert(int value, int zhishu)
    {
        if (value == 0)    return;            // 系数为0的不用看

        Node* newnode = new Node{ value, zhishu };
        newnode->next = nullptr;
        Node* p = head;
        Node* p_prev = nullptr;    // 由于没有前指针，所以给它配一个p_prev
        if (!head)
        {
            head = p = newnode;        // 如果head为空,则同指向这块空间
            return;
        }

        while (p != nullptr)
        {
            // 分成两种情况，一种是同类项合并（为0 舍去）,另一种是找到位置
            if (newnode->zhishu >= p->zhishu)
            {
                if (newnode->zhishu == p->zhishu)
                {
                    p->value += newnode->value;
                    if (p->value == 0)        // 如果合并同类项后为0，释放这块空间
                    {
                        if (p_prev)        p_prev->next = p->next;        // 把前后连接上，但是p_prev可能是nullptr
                        else        head = p->next;

                        delete p;
                    }
                    delete newnode;
                    break;
                }
                else if (newnode->zhishu > p->zhishu)
                {
                    if (p->next == nullptr)        // 如果这是最后一项，就把newnode放到最后一项
                    {
                        p->next = newnode;
                        break;
                    }
                }

            }
            else        // 小于的情况,插入
            {
                if (newnode->zhishu < head->zhishu)        // 比头指针还小
                {
                    newnode->next = head;
                    head = newnode;
                    break;
                }
                if (p_prev != nullptr)        p_prev->next = newnode;
                newnode->next = p;
            }

            p_prev = p;        // 记录下前件
            p = p->next;
        }
    }

    void add(const duoxiangshi& other, duoxiangshi& result)        // 多项式相加，返回一个多项式
    {
        Node* p1 = head;
        Node* p2 = other.head;

        while (p1 != nullptr || p2 != nullptr)
        {
            if (p1 == nullptr)                // 前两个情况，既包含到结尾的，也包含错误处理nullptr
            {
                result.insert(p2->value, p2->zhishu);
                p2 = p2->next;
            }
            else if (p2 == nullptr)
            {
                result.insert(p1->value, p1->zhishu);
                p1 = p1->next;
            }
            else if (p1->zhishu < p2->zhishu)                // 三和四判断谁更小，小的一方插入
            {
                result.insert(p1->value, p1->zhishu);
                p1 = p1->next;
            }
            else if (p1->zhishu > p2->zhishu)
            {
                result.insert(p2->value, p2->zhishu);
                p2 = p2->next;
            }
            else
            {
                result.insert(p1->value + p2->value, p1->zhishu);        // 这里是合并同类项，指数取p1的
                p1 = p1->next;
                p2 = p2->next;
            }
        }

    }

    void multiply(const duoxiangshi& other, duoxiangshi& result)
    {
        for (Node* p1 = head; p1; p1 = p1->next)
        {
            for (Node* p2 = other.head; p2; p2 = p2->next)
            {
                result.insert(p1->value * p2->value, p1->zhishu + p2->zhishu);
            }
        }
    }

    void polynomial_print()            // 多项式打印
    {
        Node* p = head;
        while (p != nullptr)
        {
            cout << p->value << " " << p->zhishu << " ";
            p = p->next;
        }
        cout << endl;
    }

};

int main()
{
    duoxiangshi duo1, duo2;
    int value, zhishu;        // 系数，指数
    int p1_num, p2_num;        // 两个多项式的项数
    int choice;

    cin >> p1_num;
    for (int i = 0; i < p1_num; i++)    // 读入第一个多项式
    {
        cin >> value >> zhishu;
        duo1.insert(value, zhishu);
    }

    cin >> p2_num;
    for (int j = 0; j < p2_num; j++)    // 读入第二个多项式
    {
        cin >> value >> zhishu;
        duo2.insert(value, zhishu);
    }

    cin >> choice;
    if (choice == 0)        // 做加法
    {
        duoxiangshi duo_result;
        duo1.add(duo2, duo_result);
        duo_result.polynomial_print();


    }
    else if (choice == 1)    // 做乘法
    {
        duoxiangshi duo_result;
        duo1.multiply(duo2, duo_result);
        duo_result.polynomial_print();

    }
    else
    {
        duoxiangshi duo_add;
        duo1.add(duo2, duo_add);
        duoxiangshi duo_mul;
        duo1.multiply(duo2, duo_mul);
        duo_add.polynomial_print();
        duo_mul.polynomial_print();

    }



    return 0;
}