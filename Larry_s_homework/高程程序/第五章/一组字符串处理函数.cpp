/* 信03 2351136 李盛鹏 */

/* 函数实现部分，{ }内的东西可以任意调整，目前的return 0只是一个示例，可改变 */

/* 不允许定义任何形式的外部全局、静态全局、宏定义、只读变量 */

/***************************************************************************
  函数名称：tj_strlen
  功    能：求字符串的长度
  输入参数：const char str[]
  返 回 值：int
  说    明：输入一个字符数组，读到第一个\0为止。
***************************************************************************/
int tj_strlen(const char str[])
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    int strlen_count = 0;//计数变量
    while (str[strlen_count] != '\0') {
        strlen_count++;
    }

    return strlen_count; //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strcat
  功    能：将字符串s2追加到s1的\0后面
  输入参数：char s1[], const char s2[]
  返 回 值：int
  说    明：s2从s1的第一个\0开始接入，直到自己的第一个\0为止，要求s1[]要足够大
***************************************************************************/
int tj_strcat(char s1[], const char s2[])
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    int strcat_count2 = 0;
    int length_of_s1 = tj_strlen(s1), length_of_s2 = tj_strlen(s2);//记录下这两个数，不能带进循环否则会变

    for (int strcat_count = length_of_s1; strcat_count < length_of_s1 + length_of_s2; strcat_count++) {
        s1[strcat_count] = s2[strcat_count2];
        strcat_count2++;
    }
    s1[length_of_s1+ length_of_s2] = '\0';
    return 0; //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strncat
  功    能：将字符串s2的前len个字符追加到s1的\0后面
  输入参数：char s1[], const char s2[], const int len
  返 回 值：int
  说    明：s2从s1的第一个\0开始接入，直到自己前len个字符为止，要求s1[]要足够大
***************************************************************************/
int tj_strncat(char s1[], const char s2[], const int len)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    int strncat_count2 = 0, numforstrnlen;
    (len >= tj_strlen(s2)) ? (numforstrnlen = tj_strlen(s2)) : (numforstrnlen = len);//这句话比较了最短的一个作为输入有效数位
    int length_of_s1 = tj_strlen(s1), length_of_s2 = tj_strlen(s2);//记录下这两个数，不能带进循环否则会变

    for (int strncat_count1= length_of_s1; strncat_count1< length_of_s1 + numforstrnlen;strncat_count1++){
        s1[strncat_count1] = s2[strncat_count2];
        strncat_count2++;
    }
    s1[length_of_s1 + numforstrnlen] = '\0';
    return 0; //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strcpy
  功    能：将s2中内容复制盖到s1中，包括\0（自行添加）。
  输入参数：char s1[], const char s2[]
  返 回 值：int
  说    明：\0要自行添加
***************************************************************************/
int tj_strcpy(char s1[], const char s2[])
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    int length_of_s2 = tj_strlen(s2);//不要把tj_strlen带到for里面否则乱套
    
    for (int strcpy_count = 0; strcpy_count < length_of_s2; strcpy_count++) {
        s1[strcpy_count] = s2[strcpy_count];
    }
    s1[length_of_s2] = '\0';

    return 0; //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strncpy
  功    能：将s2前len个复制盖到s1中，复制时不含\0
  输入参数：char s1[], const char s2[]
  返 回 值：int
  说    明：不含\0
***************************************************************************/
int tj_strncpy(char s1[], const char s2[], const int len)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    int numforstrncpy;//不要把tj_strlen带到for里面否则乱套
    
    (len >= tj_strlen(s2)) ? (numforstrncpy = tj_strlen(s2)) : (numforstrncpy = len);

    for (int strncpy_count = 0; strncpy_count < numforstrncpy; strncpy_count++) {
        s1[strncpy_count] = s2[strncpy_count];
    }

    return 0; //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strcmp
  功    能：区别s1和s2的大小，要分英文大小写
  输入参数：const char s1[], const char s2[]
  返 回 值：int 
  说    明：比到一方的长度不足以支持接着比为止
***************************************************************************/
int tj_strcmp(const char s1[], const char s2[])
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    bool forstrcmp = 1;
    int minlen = (tj_strlen(s1) <= tj_strlen(s2)) ? tj_strlen(s1) : tj_strlen(s2);//取最短的len长作为比较的终点
    
    for (int strcmp_count = 0; strcmp_count <=minlen&& forstrcmp; strcmp_count++) {
        if (s1[strcmp_count] != s2[strcmp_count]) {
            forstrcmp = false;
            return s1[strcmp_count]- s2[strcmp_count];
        }
    }
    return 0;//都比不出来，return 0.
    
}

/***************************************************************************
  函数名称：tj_strcasecmp
  功    能：区别s1和s2的大小，要分英文大小写
  输入参数：const char s1[], const char s2[]
  返 回 值：int 
  说    明：比到一方的长度不足以支持接着比为止,当同一位置上因大小写而不同时，统一转为小数来比较
***************************************************************************/
int tj_strcasecmp(const char s1[], const char s2[])
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    bool forstrcasecmp = 1;
    int minlen = (tj_strlen(s1) <= tj_strlen(s2)) ? tj_strlen(s1) : tj_strlen(s2);//取最短的len长作为比较的终点
    char num1 = 0, num2 = 0;   //用两个动态变量作为转为小写的变量

    for (int strcmp_count = 0; strcmp_count <= minlen && forstrcasecmp; strcmp_count++) {
        num1 = s1[strcmp_count], num2 = s2[strcmp_count];
        if (num1!= num2) {
            if (s1[strcmp_count] >= 'A' && s1[strcmp_count] <= 'Z') {
                num1 = s1[strcmp_count] + 32;
            }
            if (s2[strcmp_count] >= 'A' && s2[strcmp_count] <= 'Z') {
                num2 = s2[strcmp_count] + 32;
            }
            if (num1 != num2) {
                forstrcasecmp = false;
                return num1 - num2;
            }
        }
    }
    return 0;//都比不出来，return 0.
}

/***************************************************************************
  函数名称：tj_strncmp
  功    能：将s1和s2的前len个字符进行对比，区分大小写
  输入参数：const char s1[], const char s2[], const int len
  返 回 值：int 
  说    明：比到第len个字符为止
***************************************************************************/
int tj_strncmp(const char s1[], const char s2[], const int len)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    bool forstrcmp = 1;
    int mintamp = (tj_strlen(s1) <= tj_strlen(s2)) ? tj_strlen(s1) : tj_strlen(s2);//取s1和s2的最短长度
    int minlen = (mintamp >= len) ? len : mintamp;   //将len和mintamp作对比，将/取最短的作为比较的终点

    if (mintamp >= len) {
        for (int strncmp_count = 0; strncmp_count <minlen && forstrcmp; strncmp_count++) {
            if (s1[strncmp_count] != s2[strncmp_count]) {
                forstrcmp = false;
                return s1[strncmp_count] - s2[strncmp_count];
            }
        }
    }
    else {
        for (int strncmp_count = 0; strncmp_count <= minlen && forstrcmp; strncmp_count++) {
            if (s1[strncmp_count] != s2[strncmp_count]) {
                forstrcmp = false;
                return s1[strncmp_count] - s2[strncmp_count];
            }
        }

    }
    //分成两种情况，由len决定长度的，不必算到s1[len]。len超过mintamp的，要算到s1[mintamp]
    return 0;//都比不出来，return 0.
}

/***************************************************************************
  函数名称：tj_strcasencmp
  功    能：区别s1和s2的大小，要分英文大小写
  输入参数：const char s1[], const char s2[], const int len
  返 回 值：int 
  说    明：比到第len个字符为止,当同一位置上因大小写而不同时，统一转为小数来比较
***************************************************************************/
int tj_strcasencmp(const char s1[], const char s2[], const int len)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    bool forstrcasencmp = 1;
    int mintamp = (tj_strlen(s1) <= tj_strlen(s2)) ? tj_strlen(s1) : tj_strlen(s2);//取s1和s2的最短长度
    int minlen = (mintamp >= len) ? len : mintamp;   //将len和mintamp作对比，将/取最短的作为比较的终点
    char num1 = 0, num2 = 0;   //用两个动态变量作为转为小写的变量

    if (mintamp >= len) {
        for (int strcasencmp_count = 0; strcasencmp_count < minlen && forstrcasencmp; strcasencmp_count++) {
            num1 = s1[strcasencmp_count], num2 = s2[strcasencmp_count];
            if (num1 != num2) {
                if (s1[strcasencmp_count] >= 'A' && s1[strcasencmp_count] <= 'Z') {
                    num1 = s1[strcasencmp_count] + 32;
                }
                if (s2[strcasencmp_count] >= 'A' && s2[strcasencmp_count] <= 'Z') {
                    num2 = s2[strcasencmp_count] + 32;
                }
                if (num1 != num2) {
                    forstrcasencmp = false;
                    return num1 - num2;
                }
            }
        }
    }
    else {
        for (int strcasencmp_count = 0; strcasencmp_count <= minlen && forstrcasencmp; strcasencmp_count++) {
            num1 = s1[strcasencmp_count], num2 = s2[strcasencmp_count];
            if (num1 != num2) {
                if (s1[strcasencmp_count] >= 'A' && s1[strcasencmp_count] <= 'Z') {
                    num1 = s1[strcasencmp_count] + 32;
                }
                if (s2[strcasencmp_count] >= 'A' && s2[strcasencmp_count] <= 'Z') {
                    num2 = s2[strcasencmp_count] + 32;
                }
                if (num1 != num2) {
                    forstrcasencmp = false;
                    return num1 - num2;
                }
            }
        }
}
    return 0;//都比不出来，return 0.
}

/***************************************************************************
  函数名称：tj_strupr
  功    能：将str中所有小写都转为大写
  输入参数：char str[]
  返 回 值：int
  说    明：转为大写放在同一个位置
***************************************************************************/
int tj_strupr(char str[])
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    for (int strupr_count = 0; strupr_count < tj_strlen(str); strupr_count++) {
        if (str[strupr_count] >= 'a' && str[strupr_count] <= 'z') {
            str[strupr_count] -= 32;
        }
    }

    return 0; //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strlwr
  功    能：将str中所有大写都转为小写
  输入参数：char str[]
  返 回 值：int
  说    明：转为小写放在同一个位置
***************************************************************************/
int tj_strlwr(char str[])
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    for (int strupr_count = 0; strupr_count < tj_strlen(str); strupr_count++) {
        if (str[strupr_count] >= 'A' && str[strupr_count] <= 'Z') {
            str[strupr_count] += 32;
        }
    }

    return 0; //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strchr
  功    能：从str[]中寻找到ch第一次出现的地方，返回该位置
  输入参数：const char str[], char ch
  返 回 值：int
  说    明：从左到右，从str[]中寻找到ch第一次出现的地方，返回该位置
***************************************************************************/
int tj_strchr(const char str[], char ch)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    bool for_strchr = true;
    int strchr_count = 0;
    for (strchr_count = 0; strchr_count < tj_strlen(str)&& for_strchr; strchr_count++) {
        if (str[strchr_count]==ch) {
            for_strchr = false;
        }
    }
    if (for_strchr) {
        return 0;
    }
    else {
        return strchr_count;
    }                        //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strstr
  功    能：从str[]中寻找到substr[]第一次出现的地方，返回该位置
  输入参数：const char str[], const char substr[]
  返 回 值：int
  说    明：从左到右，从str[]中寻找到ch第一次出现的地方，返回该位置，找不到就返回0
***************************************************************************/
int tj_strstr(const char str[], const char substr[])
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    bool for_strstr = true;
    int strstr_count = 0;
    for (strstr_count = 0; strstr_count <=tj_strlen(str)- tj_strlen(substr) && for_strstr; strstr_count++) {
        if (!tj_strncmp(&str[strstr_count], substr,tj_strlen(substr))) {
            for_strstr = false;
        }
        
    }
    if (for_strstr) {
        return 0;
    }
    else {
        return strstr_count;
    }                        //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strrchr
  功    能：从str[]中寻找到ch第一次出现的地方，返回该位置
  输入参数：const char str[], char ch
  返 回 值：int
  说    明：从右到左，从str[]中寻找到ch第一次出现的地方，返回该位置
***************************************************************************/
int tj_strrchr(const char str[], const char ch)
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    bool for_strchr = true;
    int strchr_count = 0, location;
    for (strchr_count = 0; strchr_count < tj_strlen(str); strchr_count++) {
        if (str[strchr_count] == ch) {
            for_strchr = false;
            location = strchr_count + 1;
        }
    }
    if (for_strchr) {
        return 0;
    }
    else {
        return location;
    }                        //return值可根据需要修改

}

/***************************************************************************
  函数名称：tj_strrstr
  功    能：从str[]中寻找到substr[]第一次出现的地方，返回该位置
  输入参数：const char str[], const char substr[]
  返 回 值：int
  说    明：从右到左，从str[]中寻找到ch第一次出现的地方，返回该位置，找不到就返回0
***************************************************************************/
int tj_strrstr(const char str[], const char substr[])
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    bool for_strstr = true;
    int strstr_count = 0, location;
    for (strstr_count = 0; strstr_count <= tj_strlen(str) - tj_strlen(substr); strstr_count++) {
        if (!tj_strncmp(&str[strstr_count], substr, tj_strlen(substr))) {
            for_strstr = false;
            location = strstr_count+1;
        }

    }
    if (for_strstr) {
        return 0;
    }
    else {
        return location;
    }                        //return值可根据需要修改
}

/***************************************************************************
  函数名称：tj_strrev
  功    能：字符串反转，放入原字符数组中
  输入参数：str[]
  返 回 值：int
  说    明：
***************************************************************************/
int tj_strrev(char str[])
{
    /* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
    for (int count_strrev = 0; count_strrev < tj_strlen(str)/2; count_strrev++) {
        char tamp = str[count_strrev];
        str[count_strrev] = str[tj_strlen(str) - 1 - count_strrev];
        str[tj_strlen(str) - 1 - count_strrev] = tamp;
    }

    return 0; //return值可根据需要修改
}