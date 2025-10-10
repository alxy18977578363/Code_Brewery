/* 2351136 李盛鹏 大数据 */
#include <iostream>
#include <cmath>
#define M_PI        3.14159
using namespace std;

class Shape
{
protected:
    //根据需要加入相应的成员，也可以为空
public:
    virtual void ShapeName() = 0; //此句不准动
    //根据需要加入相应的成员，也可以为空
    virtual double area() = 0;      // area函数
};

//此处给出五个类的定义及实现(成员函数采用体外实现形式)
class Circle : public Shape
{
private:
    double radius;
public:
    Circle(double r);
    void ShapeName() override;
    double area();
};

Circle::Circle(double r) : radius(r)
{
}

void Circle::ShapeName()
{
    cout << "Circle: ";
}

double Circle::area()
{
    return (radius > 0) ? M_PI * radius * radius : 0;
}

class Square : public Shape
{
private:
    double side;
public:
    Square(double s);
    void ShapeName() override;
    double area();
};

Square::Square(double s) : side(s)
{
}

void Square::ShapeName()
{
    cout << "Square: ";
}

double Square::area()
{
    return (side > 0) ? side * side : 0;
}

class Rectangle : public Shape
{
private:
    double length, width;
public:
    Rectangle(double l, double w);
    void ShapeName() override;
    double area();
};

Rectangle::Rectangle(double l, double w) : length(l), width(w)
{
}

void Rectangle::ShapeName()
{
    cout << "Rectangle: ";
}

double Rectangle::area()
{
    return (length > 0 && width > 0) ? length * width : 0;
}


class Triangle : public Shape
{
private:
    double a, b, c;
public:
    Triangle(double s1, double s2, double s3);
    void ShapeName() override;
    double area();
};

Triangle::Triangle(double s1, double s2, double s3) : a(s1), b(s2), c(s3)
{
}

void Triangle::ShapeName()
{
    cout << "Triangle: ";
}

double Triangle::area()
{
    if (a > 0 && b > 0 && c > 0 && a + b > c && a + c > b && b + c > a)
    {
        double s = (a + b + c) / 2;
        return sqrt(s * (s - a) * (s - b) * (s - c));
    }
    else
    {
        return 0;
    }
}

class Trapezoid : public Shape
{
private:
    double top, bottom, height;
public:
    Trapezoid(double t, double b, double h);
    void ShapeName() override;
    double area();
};

Trapezoid::Trapezoid(double t, double b, double h) : top(t), bottom(b), height(h)
{
}

void Trapezoid::ShapeName()
{
    cout << "Trapezoid: ";
}

double Trapezoid::area()
{
    return (top > 0 && bottom > 0 && height > 0) ? (top + bottom) * height / 2 : 0;
}
/* -- 替换标记行 -- 本行不要做任何改动 -- 本行不要删除 -- 在本行的下面不要加入任何自己的语句，作业提交后从本行开始会被替换 -- 替换标记行 -- */

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：给出的是main函数的大致框架，允许进行微调或改变初值
***************************************************************************/
int main()
{
    if (1)
    {
        Circle    c1(5.2);           //半径（如果<=0，面积为0）
        Square    s1(5.2);           //边长（如果<=0，面积为0）
        Rectangle r1(5.2, 3.7);      //长、宽（如果任一<=0，面积为0）
        Trapezoid t1(2.3, 4.4, 3.8); //上底、下底、高（如果任一<=0，面积为0）
        Triangle  t2(3, 4, 5);       //三边长度（如果任一<=0或不构成三角形，面积为0）
        Shape* s[5] = { &c1, &s1, &r1, &t1, &t2 };

        int   i;
        for (i = 0; i < 5; i++)
        {
            s[i]->ShapeName(); //分别打印不同形状图形的名称（格式参考demo）
            cout << s[i]->area() << endl; //分别打印不同形状图形的面积（格式参考demo）
            cout << endl;
        }
    }

    if (1)
    {
        Circle    c1(-1);           //半径（如果<=0，面积为0）
        Square    s1(-1);           //边长（如果<=0，面积为0）
        Rectangle r1(5.2, -1);      //长、宽（如果任一<=0，面积为0）
        Trapezoid t1(2.3, -1, 3.8); //上底、下底、高（如果任一<=0，面积为0）
        Triangle  t2(3, 4, -1);       //三边长度（如果任一<=0或不构成三角形，面积为0）
        Shape* s[5] = { &c1, &s1, &r1, &t1, &t2 };

        cout << "============" << endl;
        int   i;
        for (i = 0; i < 5; i++)
        {
            s[i]->ShapeName(); //分别打印不同形状图形的名称（格式参考demo）
            cout << s[i]->area() << endl; //分别打印不同形状图形的面积（格式参考demo）
            cout << endl;
        }
    }

    return 0;
}

