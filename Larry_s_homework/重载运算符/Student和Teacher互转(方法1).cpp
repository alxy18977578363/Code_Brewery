/* 2351136 李盛鹏 大数据 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <cstring>
using namespace std;

/* 此处允许添加必须的定义或声明（不允许全局变量） */

/* Student 类的定义（成员函数不允许体内实现） */
class Student
{
private:
	int num;	//学号
	char name[16];	//姓名
	char sex;	//性别，只能是 F/M 两种，大小写不敏感
	char addr[64];	//家庭住址
	//私有部分不允许添加任何内容
public:
	Student();
	Student(const int num1, const char* name1, const char sex1, const char* addr1);
	friend ostream& operator<<(ostream& out, const Student& stu);
	friend class Teacher;
	//公有部分不允许添加任何内容
};

/* ----给出Student类成员函数及友元函数的体外实现---- */
Student::Student()		// 无参构造函数
{
	//缺省值 - 学号：2150000 姓名：<学生S> 性别：M 地址：四平路1239号
	num = 2150000;
	strcpy(name, "<学生S>");
	sex = 'M';
	strcpy(addr, "四平路1239号");
}

// 有参构造函数
Student::Student(const int num1, const char* name1, const char sex1, const char* addr1)
{
	num = num1;
	strncpy(name, name1, sizeof(name) - 1);
	name[sizeof(name) - 1] = '\0'; // 确保字符串以'\0'结尾
	sex = sex1;
	strncpy(addr, addr1, sizeof(addr) - 1);
	addr[sizeof(addr) - 1] = '\0'; // 确保字符串以'\0'结尾
}

/* 输出重载函数 */
ostream& operator<<(ostream& out, const Student& stu)
{
	out << stu.num << " " << stu.name << " " << stu.sex << " " << stu.addr;
	return out;
}

/* Teacher 类的定义（成员函数不允许体内实现） */
class Teacher
{
private:
	int num;	//工号
	char name[16];	//姓名
	char sex;	//性别，只能是 F/M 两种，大小写不敏感
	char addr[64];	//家庭住址
	//私有部分不允许添加任何内容
public:
	Teacher();
	Teacher(const int num1, const char* name1, const char sex1, const char* addr1);
	friend ostream& operator<<(ostream& out, const Teacher& te);
	//公有部分允许添加成员函数（体外实现），不允许添加数据成员、友元声明
	Teacher& operator=(const Student& stu);
	//类型转换函数
	operator Student();
};

/* ----给出Teacher类成员函数及友元函数的体外实现---- */
Teacher::Teacher()
{
	num = 21000;
	strcpy(name, "<教师T>");
	sex = 'M';
	strcpy(addr, "四平路1239号衷和楼");
}

/* 教师含参构造 */
Teacher::Teacher(const int num1, const char* name1, const char sex1, const char* addr1)
{
	num = num1;
	strncpy(name, name1, sizeof(name) - 1);
	name[sizeof(name) - 1] = '\0'; // 确保字符串以'\0'结尾
	sex = sex1;
	strncpy(addr, addr1, sizeof(addr) - 1);
	addr[sizeof(addr) - 1] = '\0'; // 确保字符串以'\0'结尾
}

/* 输出重载函数 */
ostream& operator<<(ostream& out, const Teacher& te)
{
	out << te.num << " " << te.name << " " << te.sex << " " << te.addr;
	return out;
}

Teacher& Teacher::operator=(const Student& stu)
{
	/* 学生转教师测试：
		学号转工号规则：工号 = 21 + 学号后三位
		姓名转换规则：前两个汉字转换为"教师"，后续字符不变
		性别转换规则：原样转换
		地址转换规则：原地址后加"电信学院"(不考虑字符串越界)    */
	num = 21000 + (stu.num % 1000); // 工号 = 21 + 学号后三位

	strcpy(name, "教师"); // 姓名转换为"教师"
	strncpy(name + 4, stu.name + 4, sizeof(name) - 5); // 后续字符不变
	name[sizeof(name) - 1] = '\0'; // 确保字符串以'\0'结尾

	sex = stu.sex; // 性别原样转换
	strcpy(addr, stu.addr); // 复制地址
	strcat(addr, "电信学院"); // 地址后加"电信学院"

	return *this;
}

Teacher:: operator Student()
{
	/* 教师转学生测试：
		工号转学号规则：学号 = 2150 + 工号后三位
		姓名转换规则：前两个汉字转换为"学生"，后续字符不变
		性别转换规则：原样转换
		地址转换规则：原地址后加"101室"(不考虑字符串越界)    */
	Student temp;
	temp.num = 2150000 + (num % 1000);

	strcpy(temp.name, "学生"); // 姓名转换为"学生"
	strncpy(temp.name+4, name + 4, sizeof(name) - 5); // 后续字符不变
	name[sizeof(name) - 1] = '\0'; // 确保字符串以'\0'结尾

	temp.sex = sex; // 性别原样转换

	strcpy(temp.addr, addr); // 复制地址
	strcat(temp.addr, "101室"); // 地址后加"101室"

	return temp;
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
	Student s1;	//缺省值 - 学号：2150000 姓名：<学生S> 性别：M 地址：四平路1239号
	Student s2 = Student(2151234, "学生甲", 'M', "曹安公路4800号");
	Teacher t1;	//缺省值 - 工号：21000 姓名：<教师T> 性别：M 地址：四平路1239号衷和楼
	Teacher t2 = Teacher(21123, "教师A", 'F', "曹安公路4800号智信馆");

	/* 打印原始学生信息 */
	cout << "学生信息：" << s1 << endl;				//期望输出："学生信息：2150000 <学生S> M 四平路1239号"
	cout << "学生信息：" << s2 << endl;				//期望输出："学生信息：2151234 学生甲 M 曹安公路4800号"
	cout << endl;

	/* 打印原始教师信息 */
	cout << "教师信息：" << t1 << endl;				//期望输出："教师信息：21000 <教师T> M 四平路1239号衷和楼"
	cout << "教师信息：" << t2 << endl;				//期望输出："教师信息：21123 教师A F 曹安公路4800号智信馆"
	cout << endl;

	/* 学生转教师测试：
		学号转工号规则：工号 = 21 + 学号后三位
		姓名转换规则：前两个汉字转换为"教师"，后续字符不变
		性别转换规则：原样转换
		地址转换规则：原地址后加"电信学院"(不考虑字符串越界)    */
	t1 = s2;
	cout << "学生信息：" << s2 << endl;				//期望输出："学生信息：2151234 学生甲 M 曹安公路4800号"
	cout << "转换为教师的信息：" << t1 << endl;		//期望输出："转换为教师的信息：21234 教师甲 M 曹安公路4800号电信学院"
	cout << endl;

	/* 教师转学生测试：
		工号转学号规则：学号 = 2150 + 工号后三位
		姓名转换规则：前两个汉字转换为"学生"，后续字符不变
		性别转换规则：原样转换
		地址转换规则：原地址后加"101室"(不考虑字符串越界)    */
	s1 = t2;
	cout << "教师信息：" << t2 << endl;				//期望输出："教师信息：21123 教师A F 曹安公路4800号智信馆"
	cout << "转换为学生的信息：" << s1 << endl;		//期望输出："转换为学生的信息：2150123 学生A F 曹安公路4800号智信馆101室"
	cout << endl;

	return 0;
}
