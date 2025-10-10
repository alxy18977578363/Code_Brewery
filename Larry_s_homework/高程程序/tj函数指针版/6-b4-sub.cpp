/* 2351136 李盛鹏 信03 */

#include <cstdio>   //NULL
//不再允许包含任何系统头文件

/* ----- 不允许定义任何形式的全局变量/全部数组/只读全局变量/宏定义!!!!! ----- */

/* 函数实现部分，{ }内的东西可以任意调整，目前的return只是一个示例，可改变 */
/***************************************************************************
  函数名称：tj_strlen
  功    能：求字符串的长度
  输入参数：const char* str
  返 回 值：int
  说    明：输入一个字符数组，读到第一个\0为止。
***************************************************************************/
int tj_strlen(const char* str)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    if (str == NULL) {
        return 0;
    }

    int strlen_count = 0;//计数变量
    while (*str != '\0') {
        strlen_count++;
        str++;
    }

    return strlen_count; //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strcat
  功    能：将字符串s2追加到s1的\0后面
  输入参数：char* s1, const char* s2
  返 回 值：char*
  说    明：s2从s1的第一个\0开始接入，直到自己的第一个\0为止，要求s1[]要足够大
***************************************************************************/
char* tj_strcat(char* s1, const char* s2)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    
    if (s1 == NULL) {
        return NULL;
    }
    else if (s2 == NULL) {
        return s1;
    }

    int length_of_s1 = tj_strlen(s1), length_of_s2 = tj_strlen(s2);//借用tj_strlen,将指针s1定位到s1字符数组第一个\0处，由于要返回s1,所以最后要减去s1和s2的长度
    s1 += length_of_s1;
    while (*s2 != '\0') {
        *s1 = *s2;
        s1++;
        s2++;
    }
    *s1 = '\0'; //这里s1连接完已经在连接部分的后一位，赋值为\0能保证s1是字符串
    s1 = s1 - length_of_s1 - length_of_s2;

    return s1;
}

/***************************************************************************
  函数名称：tj_strncat
  功    能：将字符串s2的前len个字符追加到s1的\0后面
  输入参数：char* s1, const char* s2, const int len
  返 回 值：char*
  说    明：s2从s1的第一个\0开始接入，直到自己前len个字符为止，要求s1[]要足够大
***************************************************************************/
char* tj_strncat(char* s1, const char* s2, const int len)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    if (s1 == NULL) {
        return NULL;
    }
    else if (s2 == NULL) {
        return s1;
    }

    int length_of_s1 = tj_strlen(s1), length_of_s2 = tj_strlen(s2);//借用tj_strlen,将指针s1定位到s1字符数组第一个\0处，由于要返回s1,所以最后要减去s1和s2的长度
    s1 += length_of_s1;

    //进行len次循环或者当s2指针到\0时结束连接操作
    for (int i = 0; i < len&&*s2!='\0'; i++) {
        *s1 = *s2;
        s1++;
        s2++;
    }
    *s1 = '\0';//这里s1连接完已经在连接部分的后一位，赋值为\0能保证s1是字符串

    //下面这段话定义一个min，取length_of_s2和len小的一个数，从而确定s2指针在字符数组中的位置，让它方便回归到第一个位置
    int min = (length_of_s2 > len) ? len : length_of_s2;
    s1 = s1 - length_of_s1 - min;
    return s1;
}

/***************************************************************************
  函数名称：tj_strcpy
  功    能：将s2中内容复制盖到s1中，包括\0（自行添加）。
  输入参数：char* s1, const char* s2
  返 回 值：char*
  说    明：\0要自行添加
***************************************************************************/
char* tj_strcpy(char* s1, const char* s2)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
   
    if(s1 == NULL) {
        return NULL;
    }
    else if (s2 == NULL) {
        *s1 = '\0';
        return s1;
    }

    //下面定义一个变量count，记录s2的长度，后面s2指针位置会变，所以要提前定义count，其值能帮助s1指针回到第一个位置
    int count = tj_strlen(s2);

    while (*s2 != '\0') {
        *s1 = *s2;
        s1++;
        s2++;
    }
    *s1 = '\0';
    s1 -= count;

    return s1;
}

/***************************************************************************
  函数名称：tj_strncpy
  功    能：将s2前len个复制盖到s1中，复制时不含\0
  输入参数：char* s1, const char* s2, const int len
  返 回 值：char*
  说    明：不含\0
***************************************************************************/
char* tj_strncpy(char* s1, const char* s2, const int len)
{
    //如果s1是NULL，则返回NULL。如果s1不是NULL，s2是NULL，则返回一个空串
    if (s1 == NULL) {
        return NULL;
    }
    else if (s2 == NULL) {
        return s1;
    }

    //下面定义一个变量count，记录s2的长度，后面s2指针位置会变，所以要提前定义count，其值能帮助s1指针回到第一个位置
    int count = tj_strlen(s2);

    //下面的循环，当复制了len个字符或者*s2为\0时结束。
    for (int i = 0; i < len && *s2 != '\0'; i++) {
        *s1 = *s2;
        s1++;
        s2++;
    }


    //定义min为count和len中较小的一个，从而知道s1向后推了几个位置，方便归位到第一位
    int min = (count > len) ? len : count;
    s1 -= min;

    return s1;
}

/***************************************************************************
  函数名称：tj_strcmp
  功    能：区别s1和s2的大小，要分英文大小写
  输入参数：const char* s1, const char* s2
  返 回 值：int 
  说    明：比到一方的长度不足以支持接着比为止
***************************************************************************/
int tj_strcmp(const char* s1, const char* s2)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    //如果前者是NULL后者不是，返回-1。如果前者不是NULL，后者是，返回1
    if (s1 == NULL && s2 != NULL) {
        return -1;
    }
    else if (s1 != NULL && s2 == NULL) {
        return 1;
    }
    else if (s1 == NULL && s2 == NULL) {
        return 0;
    }

    while (*s1 != '\0' && *s2 != '\0') {
        if (*s1 != *s2) {
            return *s1 - *s2;
        }
        s1++;
        s2++;
    }

    return *s1 - *s2;
}

/***************************************************************************
  函数名称：tj_strcasecmp
  功    能：区别s1和s2的大小，要分英文大小写
  输入参数：const char* s1, const char* s2
  返 回 值：int 
  说    明：比到一方的长度不足以支持接着比为止,当同一位置上因大小写而不同时，统一转为小数来比较
***************************************************************************/
int tj_strcasecmp(const char* s1, const char* s2)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    //如果前者是NULL后者不是，返回-1。如果前者不是NULL，后者是，返回1
    if (s1 == NULL && s2 != NULL) {
        return -1;
    }
    else if (s1 != NULL && s2 == NULL) {
        return 1;
    }
    else if (s1 == NULL && s2 == NULL) {
        return 0;
    }

    //下面的num1和num2，分别表示字符数组遇到大写字符时对应小写的ASCII码，这是因为不能修改原数组的值导致的
    int num1=0, num2=0;
    //下面这个循环会在最短的字符数组到\0时结束，由于一方到\0时另一方不一定是\0，所以返回值是*s1-*s2而不用0
    while (*s1 != '\0' && *s2 != '\0') {
        num1 = *s1;
        num2 = *s2;
        //先转化为小写
        if (*s1 >= 'A' && *s1 <= 'Z') {
            num1 += 32;
        }
        if (*s2 >= 'A' && *s2 <= 'Z') {
            num2 += 32;
        }
        
        //当*s1和*s2不相等时，返回num1和num2差值
        if (num1 != num2) {
            return num1 - num2;
            break;
        }

        //推到下一位
        s1++;
        s2++;
    }

    num1 = *s1;
    num2 = *s2;
    //先转化为小写
    if (*s1 >= 'A' && *s1 <= 'Z') {
        num1 += 32;
    }
    if (*s2 >= 'A' && *s2 <= 'Z') {
        num2 += 32;
    }
    return num1-num2;
}

/***************************************************************************
  函数名称：tj_strncmp
  功    能：将s1和s2的前len个字符进行对比，区分大小写
  输入参数：const char* s1, const char* s2, const int len
  返 回 值：int 
  说    明：比到第len个字符为止
***************************************************************************/
int tj_strncmp(const char* s1, const char* s2, const int len)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    //如果前者是NULL后者不是，返回-1。如果前者不是NULL，后者是，返回1
    if (s1 == NULL && s2 != NULL) {
        return -1;
    }
    else if (s1 != NULL && s2 == NULL) {
        return 1;
    }
    else if (s1 == NULL && s2 == NULL) {
        return 0;
    }

    int mintamp = (tj_strlen(s1) <= tj_strlen(s2)) ? tj_strlen(s1) : tj_strlen(s2);//取s1和s2的最短长度
    int minlen = ((mintamp+1) >= len) ? len : (mintamp+1);   //将len和mintamp作对比，将/取最短的作为比较的终点

    for (int i = 0; i < minlen;i++) {
        if (*s1 != *s2) {
            return *s1 - *s2;
        }
        s1++;
        s2++;
    }

    return 0;
}

/***************************************************************************
  函数名称：tj_strcasencmp
  功    能：区别s1和s2的大小，要分英文大小写
  输入参数：const char* s1, const char* s2, const int len
  返 回 值：int 
  说    明：比到第len个字符为止,当同一位置上因大小写而不同时，统一转为小数来比较
***************************************************************************/
int tj_strcasencmp(const char* s1, const char* s2, const int len)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

     //如果前者是NULL后者不是，返回-1。如果前者不是NULL，后者是，返回1
    if (s1 == NULL && s2 != NULL) {
        return -1;
    }
    else if (s1 != NULL && s2 == NULL) {
        return 1;
    }
    else if (s1 == NULL && s2 == NULL) {
        return 0;
    }

    int mintamp = (tj_strlen(s1) <= tj_strlen(s2)) ? tj_strlen(s1) : tj_strlen(s2);//取s1和s2的最短长度
    int minlen = ((mintamp+1) >= len) ? len : (mintamp+1);   //将len和mintamp作对比，将/取最短的作为比较的终点

    //下面的num1和num2，分别表示字符数组遇到大写字符时对应小写的ASCII码，这是因为不能修改原数组的值导致的
    int num1 = 0, num2 = 0;
    //下面这个循环会在最短的字符数组到\0时结束，由于一方到\0时另一方不一定是\0，所以返回值是*s1-*s2而不用0
    for (int i = 0; i < minlen; i++) {
        num1 = *s1;
        num2 = *s2;
        //先转化为小写
        if (*s1 >= 'A' && *s1 <= 'Z') {
            num1 += 32;
        }
        if (*s2 >= 'A' && *s2 <= 'Z') {
            num2 += 32;
        }

        //当*s1和*s2不相等时，返回num1和num2差值
        if (num1 != num2) {
            return num1 - num2;
            break;
        }

        //推到下一位
        s1++;
        s2++;
    }

    
    return 0;
}

/***************************************************************************
  函数名称：tj_strupr
  功    能：将str中所有小写都转为大写
  输入参数：char* str
  返 回 值：char*
  说    明：转为大写放在同一个位置
***************************************************************************/
char* tj_strupr(char* str)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    //如果指针为NULL，则返回NULL
    if (str == NULL) {
        return NULL;
    }

    //用count记录下字符数组长度的值，方便后面str指针归位到初始位置
    int count = tj_strlen(str);

    while(*str!='\0') {
        if (*str >= 'a' && *str <= 'z') {
            *str -= 32;
        }
        str++;
    }

    //将str指针归位到初始位置
    str -= count;
    return str;
}

/***************************************************************************
  函数名称：tj_strlwr
  功    能：将str中所有大写都转为小写
  输入参数：char* str
  返 回 值：char*
  说    明：转为小写放在同一个位置
***************************************************************************/
char* tj_strlwr(char* str)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    //如果指针为NULL，则返回NULL
    if (str == NULL) {
        return NULL;
    }

    //用count记录下字符数组长度的值，方便后面str指针归位到初始位置
    int count = tj_strlen(str);

    while (*str != '\0') {
        if (*str >= 'A' && *str <= 'Z') {
            *str += 32;
        }
        str++;
    }

    //将str指针归位到初始位置
    str -= count;
    return str;
}

/***************************************************************************
  函数名称：tj_strchr
  功    能：从str中寻找到ch第一次出现的地方，返回该位置
  输入参数：const char* str, const char ch
  返 回 值：int
  说    明：从左到右，从str[]中寻找到ch第一次出现的地方，返回该位置
***************************************************************************/
int tj_strchr(const char* str, const char ch)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    //当输入的指针是NULL时，返回0
    if (str == NULL) {
        return 0;
    }
    
    //定义一个技术变量count，用来计算在第几个位置找到的
    int count = 0;
    while (*str != '\0') {
        count++;
        if (*str == ch) {
            return count;
        }

        //指针后移
        str++;
    }
    
    return 0;
     
}

/***************************************************************************
  函数名称：tj_strstr
  功    能：从str[]中寻找到substr[]第一次出现的地方，返回该位置
  输入参数：const char* str, const char* substr
  返 回 值：int
  说    明：从左到右，从str[]中寻找到ch第一次出现的地方，返回该位置，找不到就返回0
***************************************************************************/
int tj_strstr(const char* str, const char* substr)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    //当输入的指针是NULL时，返回0
    if (str == NULL|| substr==NULL) {
        return 0;
    }

    //定义一个技术变量count，用来计算在第几个位置找到的
    int count = 0;

    //下面的循环，如果根据比较能找到，就返回count，否则，在结束循环后返回0
    while(*str!='\0') {
        count++;
        if (!tj_strncmp(str, substr, tj_strlen(substr))) {
            return count;
        }
        str++;
    }
     
    return 0;
    
}

/***************************************************************************
  函数名称：tj_strrchr
  功    能：从str中寻找到ch第一次出现的地方，返回该位置
  输入参数：const char* str, const char ch
  返 回 值：int
  说    明：从右到左，从str[]中寻找到ch第一次出现的地方，返回该位置
***************************************************************************/
int tj_strrchr(const char* str, const char ch)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    //当输入的指针是NULL时，返回0
    if (str == NULL) {
        return 0;
    }

    //定义一个技术变量count，用来计算在第几个位置找到的,再定义一个location，抹除前一个ch位置，记录后出现的位置
    int count = 0;
    int location = 0;
    while (*str != '\0') {
        count++;
        if (*str == ch) {
            location = count;
        }

        //指针后移
        str++;
    }

    //由于前面已经默认location是0了，所以如果有，location被赋值返回位。如果没有，返回0.
    return location;
}

/***************************************************************************
  函数名称：tj_strrstr
  功    能：从str[]中寻找到substr[]第一次出现的地方，返回该位置
  输入参数：const char* str, const char* substr
  返 回 值：int
  说    明：从右到左，从str[]中寻找到ch第一次出现的地方，返回该位置，找不到就返回0
***************************************************************************/
int tj_strrstr(const char* str, const char* substr)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    //当输入的指针是NULL时，返回0
    if (str == NULL || substr == NULL) {
        return 0;
    }

    //定义一个技术变量count，用来计算在第几个位置找到的.定义一个location，记录count，抹除前面的count，记录最后面的count
    int count = 0;
    int location = 0;

    //下面的循环，如果根据比较能找到，就返回count，否则，在结束循环后返回0
    while (*str != '\0') {
        count++;
        if (!tj_strncmp(str, substr, tj_strlen(substr))) {
            location = count;
        }
        str++;
    }

    //由于前面已经默认location是0了，所以如果有，location被赋值返回位。如果没有，返回0.
    return location;
}

/***************************************************************************
  函数名称：tj_strrev
  功    能：字符串反转，放入原字符数组中
  输入参数：char* str
  返 回 值：char*
  说    明：
***************************************************************************/
char* tj_strrev(char* str)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */

    //当输入的指针是NULL时，返回0
    if (str == NULL) {
        return NULL;
    }

    //下面的变量表示字符数组的长度
    int length = tj_strlen(str);

    //下面的指针指向str中\0前一个字符,缓存字符
    char* end = str + length-1;
    char tamp = 0;

    while (str < end) {
        tamp = *str;
        *str = *end;
        *end = tamp;

        //指针后移
        str++;
        end--;
    }

    //将指针归位到原先的位置
    str -= (length / 2);
    return str;
}