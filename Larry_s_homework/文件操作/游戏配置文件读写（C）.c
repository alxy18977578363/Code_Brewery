//2351136 李盛鹏 大数据
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include<string.h>
#include<stdbool.h>
#include<ctype.h>
#if (__linux__)
#else
#include<conio.h>
#endif

//根据需要可加入其它头文件
#define WRONG_INPUT     -2      // 错误输入处理
#define OUT_OF_RANGE    -3      // 错误输入处理的超出范围

//此处为示例，允许修改结构体名称，允许修改结构体中的成员内容，要求sizeof必须是64
#pragma pack(push, 1) // 确保结构体按1字节对齐
typedef struct
{
    char name[16];              // 玩家的名字
    short health;              // 生命值
    short strength;            // 力量值
    short constitution;        // 体质
    short dexterity;           // 灵巧
    int money;                 // 金钱数量
    int fame;                  // 名声值
    int charisma;              // 魅力值
    long long game_Duration;   // 游戏持续时间
    unsigned char move_Speed;  // 移动速度
    unsigned char attack_Speed; // 攻击速度
    unsigned char attack_Range; // 攻击范围
    unsigned char reserved;     // 预留值，暂不用
    short attack_Power;        // 攻击力
    short defense_Power;       // 防御力
    unsigned char agility;      // 敏捷度
    unsigned char intelligence; // 智力
    unsigned char experience;   // 经验
    unsigned char level;        // 等级
    short magic_Points;        // 魔法值
    unsigned char magic_Cost;   // 使用魔法时每次消耗的魔法值
    unsigned char magic_Damage;  // 魔法伤害力
    unsigned char hitRate;      // 命中率
    unsigned char magic_Defense; // 魔法防御力
    unsigned char criticalRate; // 暴击率
    unsigned char stamina;      // 耐力
} Player;

/* 每个信息的类型 */
typedef enum
{
    INFO_NAME = 0,              // 玩家的名字
    INFO_HEALTH,                // 生命值
    INFO_STRENGTH,              // 力量值
    INFO_CONSTITUTION,          // 体质
    INFO_DEXTERITY,             // 灵巧
    INFO_MONEY,                 // 金钱数量
    INFO_FAME,                  // 名声值
    INFO_CHARISMA,              // 魅力值
    INFO_GAME_DURATION,         // 游戏累计时间
    INFO_MOVE_SPEED,            // 移动速度
    INFO_ATTACK_SPEED,          // 攻击速度
    INFO_ATTACK_RANGE,          // 攻击范围
    INFO_ATTACK_POWER,          // 攻击力
    INFO_DEFENSE_POWER,         // 防御力
    INFO_AGILITY,               // 敏捷度
    INFO_INTELLIGENCE,          // 智力
    INFO_EXPERIENCE,            // 经验
    INFO_LEVEL,                 // 等级
    INFO_MAGIC_POINTS,          // 魔法值
    INFO_MAGIC_COST,            // 消耗魔法值
    INFO_MAGIC_DAMAGE,          // 魔法伤害力
    INFO_HIT_RATE,              // 命中率
    INFO_MAGIC_DEFENSE,         // 魔法防御力
    INFO_CRITICAL_RATE,         // 暴击率
    INFO_STAMINA                // 耐力
}INFO_TYPE;

/* 这个结构体用来表示每个种类信息的范围 */
typedef struct 
{
    INFO_TYPE type;     // 该类型
    char* name;        // 名字
    long long min;      // 最小值
    long long max;      // 最大值
}info_range;

/* 每一种信息的取值范围 */
const info_range RANGE[] = {
    {INFO_NAME, "玩家昵称", 0, 0},                // 玩家昵称没有取值范围
    {INFO_HEALTH, "生命", 0, 10000},            // 生命值范围
    {INFO_STRENGTH, "力量", 0, 10000},          // 力量值范围
    {INFO_CONSTITUTION, "体质", 0, 8192},       // 体质范围
    {INFO_DEXTERITY, "灵巧", 0, 1024},          // 灵巧范围
    {INFO_MONEY, "金钱", 0, 100000000},         // 金钱范围
    {INFO_FAME, "名声", 0, 1000000},            // 名声范围
    {INFO_CHARISMA, "魅力", 0, 1000000},        // 魅力范围
    {INFO_GAME_DURATION, "游戏累计时间", 0, 10000000000000000}, // 游戏累计时间范围
    {INFO_MOVE_SPEED, "移动速度", 0, 100},        // 移动速度范围
    {INFO_ATTACK_SPEED, "攻击速度", 0, 100},      // 攻击速度范围
    {INFO_ATTACK_RANGE, "攻击范围", 0, 100},      // 攻击范围范围
    {INFO_ATTACK_POWER, "攻击力", 0, 2000},       // 攻击力范围
    {INFO_DEFENSE_POWER, "防御力", 0, 2000},      // 防御力范围
    {INFO_AGILITY, "敏捷度", 0, 100},              // 敏捷度范围
    {INFO_INTELLIGENCE, "智力", 0, 100},           // 智力范围
    {INFO_EXPERIENCE, "经验", 0, 100},             // 经验范围
    {INFO_LEVEL, "等级", 0, 100},                  // 等级范围
    {INFO_MAGIC_POINTS, "魔法值", 0, 10000},       // 魔法值范围
    {INFO_MAGIC_COST, "消耗魔法值", 0, 100},       // 消耗魔法值范围
    {INFO_MAGIC_DAMAGE, "魔法伤害力", 0, 100},     // 魔法伤害力范围
    {INFO_HIT_RATE, "魔法命中率", 0, 100},             // 命中率范围
    {INFO_MAGIC_DEFENSE, "魔法防御力", 0, 100},    // 魔法防御力范围
    {INFO_CRITICAL_RATE, "暴击率", 0, 100},        // 暴击率范围
    {INFO_STAMINA, "耐力", 0, 100}                 // 耐力范围
};

/* 此处允许新增函数，数量不限
   1、所有新增的函数，均不允许定义新的 fstream / ifstream / ofstream 流对象，并进行打开/读/写/关闭等操作
   2、所有新增的函数，均不允许用C方式进行文件处理
   3、上述两个限制同样适用于main函数
*/

/* 该枚举表示的是命令的结构体中每个命令位置对应的意义 */
enum COMMAND_LOCATION
{
    READ = 0,
    MODIFY,
    CLMAX           // 作为该枚举的最大值,没有意义            
};

static void Usage(const char* exe_name)
{
    printf("usage : %s--modify | --read\n", exe_name);
    return;
}

/* 打印player的信息 */
void print_Player_Info(const Player* player)
{
    /* 对齐需要的最长长度 */
    int align_length = 20;
    printf("%*s%s\n", align_length, "玩家昵称：", player->name);
    printf("%*s%d\n", align_length, "生命值：", player->health);
    printf("%*s%d\n", align_length, "力量值：", player->strength);
    printf("%*s%d\n", align_length, "体质值：", player->constitution);
    printf("%*s%d\n", align_length, "灵巧值：", player->dexterity);
    printf("%*s%d\n", align_length, "金钱值：", player->money);
    printf("%*s%d\n", align_length, "名声值：", player->fame);
    printf("%*s%d\n", align_length, "魅力值：", player->charisma);
    printf("%*s%lld\n", align_length, "游戏累计时间(us)值：", player->game_Duration);
    printf("%*s%.d\n", align_length, "移动速度值：", (int)player->move_Speed);
    printf("%*s%.d\n", align_length, "攻击速度值：", (int)player->attack_Speed);
    printf("%*s%.d\n", align_length, "攻击范围值：", (unsigned int)player->attack_Range);
    printf("%*s%d\n", align_length, "攻击力值：", player->attack_Power);
    printf("%*s%d\n", align_length, "防御力值：", player->defense_Power);
    printf("%*s%.d\n", align_length, "敏捷度值：", (unsigned int)player->agility);
    printf("%*s%.d\n", align_length, "智力值：", (unsigned int)player->intelligence);
    printf("%*s%d\n", align_length, "经验值：", player->experience);
    printf("%*s%d\n", align_length, "等级值：", player->level);
    printf("%*s%d\n", align_length, "魔法值：", player->magic_Points);
    printf("%*s%.d\n", align_length, "消耗魔法值：", (unsigned int)player->magic_Cost);
    printf("%*s%.d\n", align_length, "魔法伤害力值：", (unsigned int)player->magic_Damage);
    printf("%*s%.d\n", align_length, "命中率值：", (unsigned int)player->hitRate);
    printf("%*s%.d\n", align_length, "魔法防御力值：", (unsigned int)player->magic_Defense);
    printf("%*s%.d\n", align_length, "暴击率值：", player->criticalRate);
    printf("%*s%d\n", align_length, "耐力值：", player->stamina);

}
/* 简易表格打印player的信息 */
void print_Player_Info_graph(const Player* player)
{
    
    printf("--------------------------------------\n");
    printf("  游戏存档文件修改工具\n");
    printf("--------------------------------------\n");
    printf("  a.%-12s(%s)\n", RANGE[INFO_NAME].name, player->name);
    printf("  b.%-12s(%d)\n", RANGE[INFO_HEALTH].name, player->health);
    printf("  c.%-12s(%d)\n", RANGE[INFO_STRENGTH].name, player->strength);
    printf("  d.%-12s(%d)\n", RANGE[INFO_CONSTITUTION].name, player->constitution);
    printf("  e.%-12s(%d)\n", RANGE[INFO_DEXTERITY].name, player->dexterity);
    printf("  f.%-12s(%d)\n", RANGE[INFO_MONEY].name, player->money);
    printf("  g.%-12s(%d)\n", RANGE[INFO_FAME].name, player->fame);
    printf("  h.%-12s(%d)\n", RANGE[INFO_CHARISMA].name, player->charisma);
    printf("  i.%-12s(%lld)\n", RANGE[INFO_GAME_DURATION].name, player->game_Duration);
    printf("  j.%-12s(%d)\n", RANGE[INFO_MOVE_SPEED].name, (int)player->move_Speed);
    printf("  k.%-12s(%d)\n", RANGE[INFO_ATTACK_SPEED].name, (int)player->attack_Speed);
    printf("  l.%-12s(%d)\n", RANGE[INFO_ATTACK_RANGE].name, (int)player->attack_Range);
    printf("  m.%-12s(%d)\n", RANGE[INFO_ATTACK_POWER].name, player->attack_Power);
    printf("  n.%-12s(%d)\n", RANGE[INFO_DEFENSE_POWER].name, player->defense_Power);
    printf("  o.%-12s(%d)\n", RANGE[INFO_AGILITY].name, (int)player->agility);
    printf("  p.%-12s(%d)\n", RANGE[INFO_INTELLIGENCE].name, (int)player->intelligence);
    printf("  q.%-12s(%d)\n", RANGE[INFO_EXPERIENCE].name, (int)player->experience);
    printf("  r.%-12s(%d)\n", RANGE[INFO_LEVEL].name, (int)player->level);
    printf("  s.%-12s(%d)\n", RANGE[INFO_MAGIC_POINTS].name, player->magic_Points);
    printf("  t.%-12s(%d)\n", RANGE[INFO_MAGIC_COST].name, (int)player->magic_Cost);
    printf("  u.%-12s(%d)\n", RANGE[INFO_MAGIC_DAMAGE].name, (int)player->magic_Damage);
    printf("  v.%-12s(%d)\n", RANGE[INFO_HIT_RATE].name, (int)player->hitRate);
    printf("  w.%-12s(%d)\n", RANGE[INFO_MAGIC_DEFENSE].name, (int)player->magic_Defense);
    printf("  x.%-12s(%d)\n", RANGE[INFO_CRITICAL_RATE].name, (int)player->criticalRate);
    printf("  y.%-12s(%d)\n", RANGE[INFO_STAMINA].name, (int)player->stamina);
}

/* 这个函数用来要求用户确定修改的对象 */
bool comfirm_modify(char *ch)
{
    /* 适用的选项范围 */
    char choice_range[] = { 'a','A','b','B','c','C','d','D','e','E',
                           'f','F','g','G','h','H','i','I','j','J',
                           'k','K','l','L','m','M','n','N','o','O',
                           'p','P','q','Q','r','R','s','S','t','T',
                           'u','U','v','V','w','W','x','X','y','Y',
                           'z','Z','0','1' };

    printf("--------------------------------------\n");
    printf("  0.放弃修改\n");
    printf("  1.存盘退出\n");
    printf("--------------------------------------\n");
    printf("请选择[a..y, 0..1] ");

#if (__linux__)
    *ch = getchar();
#else
    *ch = _getch();
#endif
    bool found = false;
    for (int i = 0; i < (int)sizeof(choice_range); i++)
    {
        /* 如果属于正常选项，就输出该选项 */
        if (*ch == choice_range[i])
        {
            found = true;

#if (__linux__)
#else
            printf("%c\n\n", *ch);
           
#endif
            break;
        }
    }

    /* 如果不是正常选项，就返回false表示错误 */
    return found;
}

/* 错误处理函数 */
int WRONG_INPUT_DEAL(long long min, long long max, long long input,const int ret)
{
    /* 如果输入错误 */
    if (ret!=1)
    {
        // 清除输入缓冲区
        while (getchar() != '\n');  // 读取并丢弃直到换行符为止
        return WRONG_INPUT;
    }

    if (input<min || input>max)
    {
        return OUT_OF_RANGE;
    }

    return 0;
}

/* 输出范围提示 */
void input_range_tips(int type, Player player)
{
    // 使用printf来格式化提示信息
    switch (type)
    {
    case INFO_NAME:
        printf("玩家昵称，当前值=%s，请输入 : ", player.name);
        break;
    case INFO_HEALTH:
        printf("生命，当前值=%d，范围[%lld..%lld]，请输入 : ", player.health, RANGE[INFO_HEALTH].min, RANGE[INFO_HEALTH].max);
        break;
    case INFO_STRENGTH:
        printf("力量，当前值=%d，范围[%lld..%lld]，请输入 : ", player.strength, RANGE[INFO_STRENGTH].min, RANGE[INFO_STRENGTH].max);
        break;
    case INFO_CONSTITUTION:
        printf("体质，当前值=%d，范围[%lld..%lld]，请输入 : ", player.constitution, RANGE[INFO_CONSTITUTION].min, RANGE[INFO_CONSTITUTION].max);
        break;
    case INFO_DEXTERITY:
        printf("灵巧，当前值=%d，范围[%lld..%lld]，请输入 : ", player.dexterity, RANGE[INFO_DEXTERITY].min, RANGE[INFO_DEXTERITY].max);
        break;
    case INFO_MONEY:
        printf("金钱，当前值=%d，范围[%lld..%lld]，请输入 : ", player.money, RANGE[INFO_MONEY].min, RANGE[INFO_MONEY].max);
        break;
    case INFO_FAME:
        printf("名声，当前值=%d，范围[%lld..%lld]，请输入 : ", player.fame, RANGE[INFO_FAME].min, RANGE[INFO_FAME].max);
        break;
    case INFO_CHARISMA:
        printf( "魅力，当前值=%d，范围[%lld..%lld]，请输入 : ", player.charisma, RANGE[INFO_CHARISMA].min, RANGE[INFO_CHARISMA].max);
        break;
    case INFO_GAME_DURATION:
        printf("游戏累计时间，当前值=%lld，范围[%lld..%lld]，请输入 : ", player.game_Duration, RANGE[INFO_GAME_DURATION].min, RANGE[INFO_GAME_DURATION].max);
        break;
    case INFO_MOVE_SPEED:
        printf("移动速度，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.move_Speed, RANGE[INFO_MOVE_SPEED].min, RANGE[INFO_MOVE_SPEED].max);
        break;
    case INFO_ATTACK_SPEED:
        printf( "攻击速度，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.attack_Speed, RANGE[INFO_ATTACK_SPEED].min, RANGE[INFO_ATTACK_SPEED].max);
        break;
    case INFO_ATTACK_RANGE:
        printf( "攻击范围，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.attack_Range, RANGE[INFO_ATTACK_RANGE].min, RANGE[INFO_ATTACK_RANGE].max);
        break;
    case INFO_ATTACK_POWER:
        printf( "攻击力，当前值=%d，范围[%lld..%lld]，请输入 : ", player.attack_Power, RANGE[INFO_ATTACK_POWER].min, RANGE[INFO_ATTACK_POWER].max);
        break;
    case INFO_DEFENSE_POWER:
        printf( "防御力，当前值=%d，范围[%lld..%lld]，请输入 : ", player.defense_Power, RANGE[INFO_DEFENSE_POWER].min, RANGE[INFO_DEFENSE_POWER].max);
        break;
    case INFO_AGILITY:
        printf( "敏捷度，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.agility, RANGE[INFO_AGILITY].min, RANGE[INFO_AGILITY].max);
        break;
    case INFO_INTELLIGENCE:
        printf( "智力，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.intelligence, RANGE[INFO_INTELLIGENCE].min, RANGE[INFO_INTELLIGENCE].max);
        break;
    case INFO_EXPERIENCE:
        printf( "经验，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.experience, RANGE[INFO_EXPERIENCE].min, RANGE[INFO_EXPERIENCE].max);
        break;
    case INFO_LEVEL:
        printf( "等级，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.level, RANGE[INFO_LEVEL].min, RANGE[INFO_LEVEL].max);
        break;
    case INFO_MAGIC_POINTS:
        printf( "魔法值，当前值=%d，范围[%lld..%lld]，请输入 : ", player.magic_Points, RANGE[INFO_MAGIC_POINTS].min, RANGE[INFO_MAGIC_POINTS].max);
        break;
    case INFO_MAGIC_COST:
        printf( "消耗魔法值，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.magic_Cost, RANGE[INFO_MAGIC_COST].min, RANGE[INFO_MAGIC_COST].max);
        break;
    case INFO_MAGIC_DAMAGE:
        printf( "魔法伤害力，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.magic_Damage, RANGE[INFO_MAGIC_DAMAGE].min, RANGE[INFO_MAGIC_DAMAGE].max);
        break;
    case INFO_HIT_RATE:
        printf( "命中率，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.hitRate, RANGE[INFO_HIT_RATE].min, RANGE[INFO_HIT_RATE].max);
        break;
    case INFO_MAGIC_DEFENSE:
        printf( "魔法防御力，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.magic_Defense, RANGE[INFO_MAGIC_DEFENSE].min, RANGE[INFO_MAGIC_DEFENSE].max);
        break;
    case INFO_CRITICAL_RATE:
        printf( "暴击率，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.criticalRate, RANGE[INFO_CRITICAL_RATE].min, RANGE[INFO_CRITICAL_RATE].max);
        break;
    case INFO_STAMINA:
        printf( "耐力，当前值=%d，范围[%lld..%lld]，请输入 : ", (int)player.stamina, RANGE[INFO_STAMINA].min, RANGE[INFO_STAMINA].max);
        break;
    default:
        printf( "未知类型，无法提供范围提示。");
        break;
    }

}

/***************************************************************************
  函数名称：read
  功    能：读取文件中每一个内容
  输入参数：
  返 回 值：
  说    明：整个函数，只允许出现一次open、一次read（因为包含错误处理，允许多次close）
***************************************************************************/
int read()
{
    /* 本函数中只允许定义一个 FILE* */
    FILE* fp;
    Player player;          // 定义一个结构体，存储这个fp的信息

    /* 文件打开，具体要求为：
        1、要求以读方式打开，打开方式***自行指定
        2、除本次fopen外，本函数其它地方不允许再出现fopen/freopen  */
    fp = fopen("game.dat", "rb");

    /* 进行后续操作，包括错误处理、读文件、显示各游戏项的值、关闭文件等，允许调用函数
       其中：只允许用一次性读取64字节的方法将game.dat的内容读入***（缓冲区名称、结构体名称自行指定）
                 fp.read(***, sizeof(demo));
    */

    /* 1.错误处理 */
    if (fp == NULL)
    {
        printf("文件打开失败\n");
        return -1;
    }

    // 移动到文件末尾以获取文件大小
    fseek(fp, 0, SEEK_END);
    int fileSize = (int)ftell(fp); // 获取文件大小

    // 检查文件大小是否符合预期
    if (fileSize != (int)sizeof(Player))
    {
        printf("文件game.dat的字节大小不正确\n");
        fclose(fp);
        return -1;
    }

    // 移动回文件开头以进行读取
    fseek(fp, 0, SEEK_SET);

    /* 2.读取文件 */
    fread(&player, sizeof(Player), 1, fp);

    /* 3.根据是否读取成功，给出各游戏项的值 */
    if (ftell(fp) != sizeof(Player))
    {
        // 读取成功
        printf("文件读取失败\n");
        fclose(fp);   // 关闭文件
        return -1;
    }
    else
    {
        print_Player_Info(&player);
        fclose(fp);   // 关闭文件
        return 0;
    }

}

/***************************************************************************
  函数名称：modify
  功    能：修改game.dat中的参数
  输入参数：无
  返 回 值：
  说    明：整个函数，只允许出现一次open、一次read、一次write（因为包含错误处理，允许多次close）
***************************************************************************/
int modify()
{
    /* 本函数中只允许定义一个 FILE* */
    FILE* fp;
    Player player;

    /* 文件打开，具体要求为：
       1、要求以读方式打开，打开方式***自行指定
       2、除本次fopen外，本函数其它地方不允许再出现fopen/freopen  */
    fp = fopen("game.dat", "rb+");

    /* 进行后续操作，包括错误处理、读文件、显示各游戏项的值、关闭文件等，允许调用函数
       其中：只允许用一次性读取64字节的方法将game.dat的内容读入***（缓冲区名称、结构体名称自行指定）
                 fread(***, 1, sizeof(demo), fp);
    */
    /* 1.错误处理 */
    if (fp  == NULL)        // 无法打开文件
    {
        printf("文件打开失败\n");
        return -1;
    }

    /* dat大小不正确 */
    fseek(fp ,0, SEEK_END); // 移动到文件末尾
    int fileSize = ftell(fp); // 获取文件大小

    if (fileSize != (int)sizeof(Player))
    {
        printf("文件game.dat的字节大小不正确\n");
        fclose(fp);
        return -1;
    }

    fseek(fp, 0, SEEK_SET); // 确保写入从文件开头开始

    /* 2.读取文件 */
    fread(&player, sizeof(Player), 1, fp);

    /* 3.根据是否读取成功，给出各游戏项的值 */
    if (ftell(fp) != sizeof(Player))
    {
        printf("文件读取失败\n");
        fclose(fp);          // 关闭文件
        return -1;
    }
    else
    {
        while (true)
        {
            char ch=0;        // 要读取的选项
            print_Player_Info_graph(&player);        /* 图形格式打印出来 */
            if (comfirm_modify(&ch) == false)        // ch已经在函数中修改
            {
                continue;
            }

            /* 能到达这里说明输入的选项是正确的 */
            /* 1.存盘退出 */
            if (ch == '1')
            {
                fseek(fp, 0, SEEK_SET); // 确保写入从文件开头开始
                fwrite((const char*)&player, sizeof(Player),1,fp);
                fclose(fp);          // 关闭文件
                break;
            }
            else if (ch == '0')
            {
                fclose(fp);          // 关闭文件
                break;
            }
            else        // 每个选项
            {
                long long temp;

                if (RANGE[tolower(ch) - 'a'].type == INFO_NAME)
                {
                    input_range_tips(RANGE[tolower(ch) - 'a'].type, player);
                    fgets(player.name, sizeof(player.name), stdin);
                    // 检查输入的长度
                    if (strlen(player.name) >= 15)
                    {
                        // 清除缓冲区
                        while (getchar() != '\n');
                    }
                    else
                    {
                        // 确保字符串以 '\0' 结尾
                        size_t len = strlen(player.name);
                        if (len > 0 && player.name[len - 1] == '\n')
                        {
                            player.name[len - 1] = '\0';  // 替换换行符
                        }
                    }
                }
                else      
                {
                    while (true)
                    {
                        input_range_tips(RANGE[tolower(ch) - 'a'].type, player);
                        int ret=scanf("%lld", &temp);

                        /* 非法的输入 */
                        if (WRONG_INPUT_DEAL(RANGE[RANGE[tolower(ch) - 'a'].type].min, RANGE[RANGE[tolower(ch) - 'a'].type].max, temp,ret) == WRONG_INPUT)
                            continue;

                        // 错误处理已经在内部处理
                        if (WRONG_INPUT_DEAL(RANGE[RANGE[tolower(ch) - 'a'].type].min, RANGE[RANGE[tolower(ch) - 'a'].type].max, temp,ret) == OUT_OF_RANGE)
                        {       // 错误的范围
                            printf("非法的%s值：%lld\n", RANGE[RANGE[tolower(ch) - 'a'].type].name, temp);
                            continue;
                        }

                        /* 到了这里说明合法 */
                        switch (RANGE[tolower(ch) - 'a'].type)
                        {
                        case INFO_HEALTH:
                            player.health = (short)temp;
                            break;
                        case INFO_STRENGTH:
                            player.strength = (short)temp;
                            break;
                        case INFO_CONSTITUTION:
                            player.constitution = (short)temp;
                            break;
                        case INFO_DEXTERITY:     // 灵巧
                            player.dexterity = (short)temp;
                            break;
                        case INFO_MONEY:        // 金钱
                            player.money = (int)temp;
                            break;
                        case INFO_FAME:         // 名声
                            player.fame = (int)temp;
                            break;
                        case INFO_CHARISMA:
                            player.charisma = (int)temp;
                            break;
                        case INFO_GAME_DURATION:
                            player.game_Duration = temp;
                            break;
                        case INFO_MOVE_SPEED:
                            player.move_Speed = (unsigned char)(temp);
                            break;
                        case INFO_ATTACK_SPEED:
                            player.attack_Speed =(unsigned char)(temp);
                            break;
                        case INFO_ATTACK_RANGE:
                            player.attack_Range =(unsigned char)(temp);
                            break;
                        case INFO_ATTACK_POWER:
                            player.attack_Power = (short)temp;
                            break;
                        case INFO_DEFENSE_POWER:
                            player.defense_Power = (short)temp;
                            break;
                        case INFO_AGILITY:
                            player.agility =(unsigned char)(temp);
                            break;
                        case INFO_INTELLIGENCE:
                            player.intelligence =(unsigned char)(temp);
                            break;
                        case INFO_EXPERIENCE:
                            player.experience =(unsigned char)(temp);
                            break;
                        case INFO_LEVEL:
                            player.level =(unsigned char)(temp);
                            break;
                        case INFO_MAGIC_POINTS:
                            player.magic_Points = (short)temp;
                            break;
                        case INFO_MAGIC_COST:
                            player.magic_Cost =(unsigned char)(temp);
                            break;
                        case INFO_MAGIC_DAMAGE:
                            player.magic_Damage =(unsigned char)(temp);
                            break;
                        case INFO_HIT_RATE:
                            player.hitRate =(unsigned char)(temp);
                            break;
                        case INFO_MAGIC_DEFENSE:
                            player.magic_Defense =(unsigned char)(temp);
                            break;
                        case INFO_CRITICAL_RATE:
                            player.criticalRate =(unsigned char)(temp);
                            break;
                        case INFO_STAMINA:
                            player.stamina =(unsigned char)(temp);
                            break;
                        default:
                            break;
                        }
                        break;
                    }
                }

            }

        }// end of while
    }// end of if_else


    return 0;
}

/***************************************************************************
  函数名称：main
  功    能：
  输入参数：
  返 回 值：
  说    明：main函数允许带参数，不允许进行文件读写
***************************************************************************/
int main(int argc, char** argv)
{
    /* 可供实现的命令 */
    const char* Command[3] = { "--read","--modify","" };

    /* 1.错误处理 */
    if (argc != 2)
    {
        Usage(argv[0]);
        return -1;
    }

    /* 到了这里肯定是符合条件的，终止条件是"" */
    for (int i = 0; strcmp(Command[i], "") != 0; i++)
    {
        /* 已经在函数内部关闭了文件 */
        if (strcmp(argv[1], Command[READ]) == 0)
        {
            read();
            break;
        }
        else if (strcmp(argv[1], Command[MODIFY]) == 0)
        {
            modify();
            break;
        }
        else
        {
            /* 命令是错误的 */
            Usage(argv[0]);
            return -1;
        }

    }



    return 0;
}