//2351136 李盛鹏 大数据
#include <iostream>
#include <fstream>
#include<iomanip>
#include<string>
#include<cstring>
#include<ctype.h>
#if (__linux__)
#else
#include<conio.h>
#endif

//根据需要可加入其它头文件
#define WRONG_INPUT     -2      // 错误输入处理
#define OUT_OF_RANGE    -3      // 错误输入处理的超出范围
using namespace std;

//此处为示例，允许修改结构体名称，允许修改结构体中的成员内容，要求sizeof必须是64
#pragma pack(push, 1) // 确保结构体按1字节对齐
struct Player
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
};

/* 每个信息的类型 */
enum INFO_TYPE
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
};

/* 这个结构体用来表示每个种类信息的范围 */
struct info_range
{
    INFO_TYPE type;     // 该类型
    string name;        // 名字
    long long min;      // 最小值
    long long max;      // 最大值
};

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
    cout << "usage : "<< exe_name<< "--modify | --read" << endl;
    return;
}

/* 打印player的信息 */
void print_Player_Info(const Player& player)
{
    /* 对齐需要的最长长度 */
    int align_length = 20;

    cout << right << setw(align_length) << "玩家昵称：" << player.name << endl;
    cout << right << setw(align_length) << "生命值：" << player.health << endl;
    cout << right << setw(align_length) << "力量值：" << player.strength << endl;
    cout << right << setw(align_length) << "体质值：" << player.constitution << endl;
    cout << right << setw(align_length) << "灵巧值：" << player.dexterity << endl;
    cout << right << setw(align_length) << "金钱值：" << player.money << endl;
    cout << right << setw(align_length) << "名声值：" << player.fame << endl;
    cout << right << setw(align_length) << "魅力值：" << player.charisma << endl;
    cout << right << setw(align_length) << "游戏累计时间(us)值：" << player.game_Duration << endl;
    cout << right << setw(align_length) << "移动速度值：" << static_cast<int>(player.move_Speed) << endl;
    cout << right << setw(align_length) << "攻击速度值：" << static_cast<int>(player.attack_Speed) << endl;
    cout << right << setw(align_length) << "攻击范围值：" << static_cast<int>(player.attack_Range) << endl;
    cout << right << setw(align_length) << "攻击力值：" << player.attack_Power << endl;
    cout << right << setw(align_length) << "防御力值：" << player.defense_Power << endl;
    cout << right << setw(align_length) << "敏捷度值：" << static_cast<int>(player.agility) << endl;
    cout << right << setw(align_length) << "智力值：" << static_cast<int>(player.intelligence) << endl;
    cout << right << setw(align_length) << "经验值：" << static_cast<int>(player.experience) << endl;
    cout << right << setw(align_length) << "等级值：" << static_cast<int>(player.level) << endl;
    cout << right << setw(align_length) << "魔法值：" << player.magic_Points << endl;
    cout << right << setw(align_length) << "消耗魔法值：" << static_cast<int>(player.magic_Cost) << endl;
    cout << right << setw(align_length) << "魔法伤害力值：" << static_cast<int>(player.magic_Damage) << endl;
    cout << right << setw(align_length) << "命中率值：" << static_cast<int>(player.hitRate) << endl;
    cout << right << setw(align_length) << "魔法防御力值：" << static_cast<int>(player.magic_Defense) << endl;
    cout << right << setw(align_length) << "暴击率值：" << static_cast<int>(player.criticalRate) << endl;
    cout << right << setw(align_length) << "耐力值：" << static_cast<int>(player.stamina) << endl;
}
/* 简易表格打印player的信息 */
void print_Player_Info_graph(const Player& player)
{
    cout << setw(38) << setfill('-') << "-" << setfill(' ') << endl;
    cout << "  游戏存档文件修改工具" << endl;
    cout << setw(38) << setfill('-') << "-" << setfill(' ') << endl;
    cout << "  " << "a." << setw(12) << left << setfill(' ') << RANGE[INFO_NAME].name << "(" << player.name << ")" << endl;
    cout << "  " << "b." << setw(12) << left << setfill(' ') << RANGE[INFO_HEALTH].name << "(" << player.health << ")" << endl;
    cout << "  " << "c." << setw(12) << left << setfill(' ') << RANGE[INFO_STRENGTH].name << "(" << player.strength << ")" << endl;
    cout << "  " << "d." << setw(12) << left << setfill(' ') << RANGE[INFO_CONSTITUTION].name << "(" << player.constitution << ")" << endl;
    cout << "  " << "e." << setw(12) << left << setfill(' ') << RANGE[INFO_DEXTERITY].name << "(" << player.dexterity << ")" << endl;
    cout << "  " << "f." << setw(12) << left << setfill(' ') << RANGE[INFO_MONEY].name << "(" << player.money << ")" << endl;
    cout << "  " << "g." << setw(12) << left << setfill(' ') << RANGE[INFO_FAME].name << "(" << player.fame << ")" << endl;
    cout << "  " << "h." << setw(12) << left << setfill(' ') << RANGE[INFO_CHARISMA].name << "(" << player.charisma << ")" << endl;
    cout << "  " << "i." << setw(12) << left << setfill(' ') << RANGE[INFO_GAME_DURATION].name << "(" << player.game_Duration << ")" << endl;
    cout << "  " << "j." << setw(12) << left << setfill(' ') << RANGE[INFO_MOVE_SPEED].name << "(" << static_cast<int>(player.move_Speed) << ")" << endl;
    cout << "  " << "k." << setw(12) << left << setfill(' ') << RANGE[INFO_ATTACK_SPEED].name << "(" << static_cast<int>(player.attack_Speed) << ")" << endl;
    cout << "  " << "l." << setw(12) << left << setfill(' ') << RANGE[INFO_ATTACK_RANGE].name << "(" << static_cast<int>(player.attack_Range) << ")" << endl;
    cout << "  " << "m." << setw(12) << left << setfill(' ') << RANGE[INFO_ATTACK_POWER].name << "(" << player.attack_Power << ")" << endl;
    cout << "  " << "n." << setw(12) << left << setfill(' ') << RANGE[INFO_DEFENSE_POWER].name << "(" << player.defense_Power << ")" << endl;
    cout << "  " << "o." << setw(12) << left << setfill(' ') << RANGE[INFO_AGILITY].name << "(" << static_cast<int>(player.agility) << ")" << endl;
    cout << "  " << "p." << setw(12) << left << setfill(' ') << RANGE[INFO_INTELLIGENCE].name << "(" << static_cast<int>(player.intelligence) << ")" << endl;
    cout << "  " << "q." << setw(12) << left << setfill(' ') << RANGE[INFO_EXPERIENCE].name << "(" << static_cast<int>(player.experience) << ")" << endl;
    cout << "  " << "r." << setw(12) << left << setfill(' ') << RANGE[INFO_LEVEL].name << "(" << static_cast<int>(player.level) << ")" << endl;
    cout << "  " << "s." << setw(12) << left << setfill(' ') << RANGE[INFO_MAGIC_POINTS].name << "(" << player.magic_Points << ")" << endl;
    cout << "  " << "t." << setw(12) << left << setfill(' ') << RANGE[INFO_MAGIC_COST].name << "(" << static_cast<int>(player.magic_Cost) << ")" << endl;
    cout << "  " << "u." << setw(12) << left << setfill(' ') << RANGE[INFO_MAGIC_DAMAGE].name << "(" << static_cast<int>(player.magic_Damage) << ")" << endl;
    cout << "  " << "v." << setw(12) << left << setfill(' ') << RANGE[INFO_HIT_RATE].name << "(" << static_cast<int>(player.hitRate) << ")" << endl;
    cout << "  " << "w." << setw(12) << left << setfill(' ') << RANGE[INFO_MAGIC_DEFENSE].name << "(" << static_cast<int>(player.magic_Defense) << ")" << endl;
    cout << "  " << "x." << setw(12) << left << setfill(' ') << RANGE[INFO_CRITICAL_RATE].name << "(" << static_cast<int>(player.criticalRate) << ")" << endl;
    cout << "  " << "y." << setw(12) << left << setfill(' ') << RANGE[INFO_STAMINA].name << "(" << static_cast<int>(player.stamina) << ")" << endl;
}

/* 这个函数用来要求用户确定修改的对象 */
bool comfirm_modify(char &ch)
{
    /* 适用的选项范围 */
    char choice_range[] = { 'a','A','b','B','c','C','d','D','e','E',
                           'f','F','g','G','h','H','i','I','j','J',
                           'k','K','l','L','m','M','n','N','o','O',
                           'p','P','q','Q','r','R','s','S','t','T',
                           'u','U','v','V','w','W','x','X','y','Y',
                           'z','Z','0','1' };

    cout << setw(38) << setfill('-') << "-" << setfill(' ') << endl;
    cout << "  0.放弃修改" << endl;
    cout << "  1.存盘退出" << endl;
    cout << setw(38) << setfill('-') << "-" << setfill(' ') << endl;
    cout << "请选择[a..y, 0..1] ";

#if (__linux__)
    ch = getchar();
#else
    ch = _getch();
#endif
    bool found = false;
    for (size_t i = 0; i < sizeof(choice_range); i++)
    {
        /* 如果属于正常选项，就输出该选项 */
        if (ch == choice_range[i])
        {
            found = true;

#if (__linux__)
#else
            cout << ch << endl << endl;
#endif
            break;
        }
    }

    /* 如果不是正常选项，就返回false表示错误 */
    return found;
}

/* 错误处理函数 */
int WRONG_INPUT_DEAL(long long min,long long max,long long input)
{
    /* 如果输入错误 */
    if (cin.fail())
    {
        cin.clear();
        cin.ignore(65536, '\n');
        return WRONG_INPUT;
    }

    if (input<min || input>max)
    {
        return OUT_OF_RANGE;
    }

    return 0;
}

/* 输出范围提示 */
string input_range_tips(INFO_TYPE type, const Player player)
{
    string Tips;        // 范围提示的string

    switch (type)
    {
    case INFO_NAME:              // 玩家的名字
        Tips = "玩家昵称，当前值=" + (string)(player.name) + "，请输入 : ";
        break;
    case INFO_HEALTH:                // 生命值
        Tips = "生命，当前值=" + to_string(player.health) + "，范围[" + to_string(RANGE[INFO_HEALTH].min) + ".." + to_string(RANGE[INFO_HEALTH].max) + "]，请输入 : ";
        break;
    case INFO_STRENGTH:              // 力量值
        Tips = "力量，当前值=" + to_string(player.strength) + "，范围[" + to_string(RANGE[INFO_STRENGTH].min) + ".." + to_string(RANGE[INFO_STRENGTH].max) + "]，请输入 : ";
        break;
    case INFO_CONSTITUTION:
        Tips = "体质，当前值=" + to_string(player.constitution) + "，范围[" + to_string(RANGE[INFO_CONSTITUTION].min) + ".." + to_string(RANGE[INFO_CONSTITUTION].max) + "]，请输入 : ";
        break;
    case INFO_DEXTERITY: // 灵巧
        Tips = "灵巧，当前值=" + to_string(player.dexterity) + "，范围[" + to_string(RANGE[INFO_DEXTERITY].min) + ".." + to_string(RANGE[INFO_DEXTERITY].max) + "]，请输入 : ";
        break;
    case INFO_MONEY: // 金钱数量
        Tips = "金钱，当前值=" + to_string(player.money) + "，范围[" + to_string(RANGE[INFO_MONEY].min) + ".." + to_string(RANGE[INFO_MONEY].max) + "]，请输入 : ";
        break;
    case INFO_FAME: // 名声值
        Tips = "名声，当前值=" + to_string(player.fame) + "，范围[" + to_string(RANGE[INFO_FAME].min) + ".." + to_string(RANGE[INFO_FAME].max) + "]，请输入 : ";
        break;
    case INFO_CHARISMA: // 魅力值
        Tips = "魅力，当前值=" + to_string(player.charisma) + "，范围[" + to_string(RANGE[INFO_CHARISMA].min) + ".." + to_string(RANGE[INFO_CHARISMA].max) + "]，请输入 : ";
        break;
    case INFO_GAME_DURATION: // 游戏累计时间
        Tips = "游戏累计时间，当前值=" + to_string(player.game_Duration) + "，范围[" + to_string(RANGE[INFO_GAME_DURATION].min) + ".." + to_string(RANGE[INFO_GAME_DURATION].max) + "]，请输入 : ";
        break;
    case INFO_MOVE_SPEED: // 移动速度
        Tips = "移动速度，当前值=" + to_string(static_cast<int>(player.move_Speed)) + "，范围[" + to_string(RANGE[INFO_MOVE_SPEED].min) + ".." + to_string(RANGE[INFO_MOVE_SPEED].max) + "]，请输入 : ";
        break;
    case INFO_ATTACK_SPEED: // 攻击速度
        Tips = "攻击速度，当前值=" + to_string(static_cast<int>(player.attack_Speed)) + "，范围[" + to_string(RANGE[INFO_ATTACK_SPEED].min) + ".." + to_string(RANGE[INFO_ATTACK_SPEED].max) + "]，请输入 : ";
        break;
    case INFO_ATTACK_RANGE: // 攻击范围
        Tips = "攻击范围，当前值=" + to_string(static_cast<int>(player.attack_Range)) + "，范围[" + to_string(RANGE[INFO_ATTACK_RANGE].min) + ".." + to_string(RANGE[INFO_ATTACK_RANGE].max) + "]，请输入 : ";
        break;
    case INFO_ATTACK_POWER: // 攻击力
        Tips = "攻击力，当前值=" + to_string(player.attack_Power) + "，范围[" + to_string(RANGE[INFO_ATTACK_POWER].min) + ".." + to_string(RANGE[INFO_ATTACK_POWER].max) + "]，请输入 : ";
        break;
    case INFO_DEFENSE_POWER: // 防御力
        Tips = "防御力，当前值=" + to_string(player.defense_Power) + "，范围[" + to_string(RANGE[INFO_DEFENSE_POWER].min) + ".." + to_string(RANGE[INFO_DEFENSE_POWER].max) + "]，请输入 : ";
        break;
    case INFO_AGILITY: // 敏捷度
        Tips = "敏捷度，当前值=" + to_string(static_cast<int>(player.agility)) + "，范围[" + to_string(RANGE[INFO_AGILITY].min) + ".." + to_string(RANGE[INFO_AGILITY].max) + "]，请输入 : ";
        break;
    case INFO_INTELLIGENCE: // 智力
        Tips = "智力，当前值=" + to_string(static_cast<int>(player.intelligence)) + "，范围[" + to_string(RANGE[INFO_INTELLIGENCE].min) + ".." + to_string(RANGE[INFO_INTELLIGENCE].max) + "]，请输入 : ";
        break;
    case INFO_EXPERIENCE: // 经验
        Tips = "经验，当前值=" + to_string(static_cast<int>(player.experience)) + "，范围[" + to_string(RANGE[INFO_EXPERIENCE].min) + ".." + to_string(RANGE[INFO_EXPERIENCE].max) + "]，请输入 : ";
        break;
    case INFO_LEVEL: // 等级
        Tips = "等级，当前值=" + to_string(static_cast<int>(player.level)) + "，范围[" + to_string(RANGE[INFO_LEVEL].min) + ".." + to_string(RANGE[INFO_LEVEL].max) + "]，请输入 : ";
        break;
    case INFO_MAGIC_POINTS: // 魔法值
        Tips = "魔法值，当前值=" + to_string(player.magic_Points) + "，范围[" + to_string(RANGE[INFO_MAGIC_POINTS].min) + ".." + to_string(RANGE[INFO_MAGIC_POINTS].max) + "]，请输入 : ";
        break;
    case INFO_MAGIC_COST: // 消耗魔法值
        Tips = "消耗魔法值，当前值=" + to_string(static_cast<int>(player.magic_Cost)) + "，范围[" + to_string(RANGE[INFO_MAGIC_COST].min) + ".." + to_string(RANGE[INFO_MAGIC_COST].max) + "]，请输入 : ";
        break;
    case INFO_MAGIC_DAMAGE: // 魔法伤害力
        Tips = "魔法伤害力，当前值=" + to_string(static_cast<int>(player.magic_Damage)) + "，范围[" + to_string(RANGE[INFO_MAGIC_DAMAGE].min) + ".." + to_string(RANGE[INFO_MAGIC_DAMAGE].max) + "]，请输入 : ";
        break;
    case INFO_HIT_RATE: // 命中率
        Tips = "命中率，当前值=" + to_string(static_cast<int>(player.hitRate)) + "，范围[" + to_string(RANGE[INFO_HIT_RATE].min) + ".." + to_string(RANGE[INFO_HIT_RATE].max) + "]，请输入 : ";
        break;
    case INFO_MAGIC_DEFENSE: // 魔法防御力
        Tips = "魔法防御力，当前值=" + to_string(static_cast<int>(player.magic_Defense)) + "，范围[" + to_string(RANGE[INFO_MAGIC_DEFENSE].min) + ".." + to_string(RANGE[INFO_MAGIC_DEFENSE].max) + "]，请输入 : ";
        break;
    case INFO_CRITICAL_RATE: // 暴击率
        Tips = "暴击率，当前值=" + to_string(static_cast<int>(player.criticalRate)) + "，范围[" + to_string(RANGE[INFO_CRITICAL_RATE].min) + ".." + to_string(RANGE[INFO_CRITICAL_RATE].max) + "]，请输入 : ";
        break;
    case INFO_STAMINA: // 耐力
        Tips = "耐力，当前值=" + to_string(static_cast<int>(player.stamina)) + "，范围[" + to_string(RANGE[INFO_STAMINA].min) + ".." + to_string(RANGE[INFO_STAMINA].max) + "]，请输入 : ";
        break;
    default:
        Tips = "未知类型，无法提供范围提示。";
        break;
    }

    return Tips; // 返回范围提示
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
    /* 本函数中只允许定义一个 ifstream流对象，不再允许定义任何形式的fstream/ifstream/ofstream流对象，也不允许使用C方式的文件处理 */
    ifstream gfile;
    Player player;          // 定义一个结构体，存储这个gfile的信息

    /* 文件打开，具体要求为：
       1、要求以读方式打开，打开方式***自行指定
       2、除本次open外，本函数其它地方不允许再出现open  */
    gfile.open("game.dat", ios::in | ios::binary);

    /* 进行后续操作，包括错误处理、读文件、显示各游戏项的值、关闭文件等，允许调用函数
       其中：只允许用一次性读取64字节的方法将game.dat的内容读入***（缓冲区名称、结构体名称自行指定）
                 gfile.read(***, sizeof(demo));
    */

    /* 1.错误处理 */
    if (gfile.is_open() == 0)
    {
        cout << "文件打开失败" << endl;
        return -1;
    }

    // 移动到文件末尾以获取文件大小
    gfile.seekg(0, ios::end);
    int fileSize = (int)gfile.tellg(); // 获取文件大小

    // 检查文件大小是否符合预期
    if (fileSize != (int)sizeof(Player))
    {
        cout << "文件game.dat的字节大小不正确" << endl;
        gfile.close();
        return -1;
    }

    // 移动回文件开头以进行读取
    gfile.seekg(0, ios::beg);

    /* 2.读取文件 */
    gfile.read((char*) & player, sizeof(Player));       // 格式转化

    /* 3.根据是否读取成功，给出各游戏项的值 */
    if (gfile.gcount()!=sizeof(Player))
    {
        // 读取成功
        cout << "文件读取失败" << endl;
        gfile.close();
        return -1;
    }
    else
    {
        print_Player_Info(player);
        gfile.close();
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
    /* 本函数中只允许定义一个 fstream流对象，不再允许定义任何形式的fstream/ifstream/ofstream流对象，也不允许使用C方式的文件处理 */
    fstream gfile;
    Player player;

    /* 文件打开，具体要求为：
       1、要求以读写方式打开，打开方式***自行指定
       2、除本次open外，本函数其它地方不允许再出现open  */
    gfile.open("game.dat", ios::in | ios::out | ios::binary);

    /* 进行后续操作，包括错误处理、读文件、显示各游戏项的值、关闭文件等，允许调用函数
       其中：只允许用一次性读取64字节的方法将game.dat的内容读入***（缓冲区名称、结构体名称自行指定）
                 gfile.read(***, sizeof(demo));
             只允许用一次性写入64字节的方法将***的内容写入game.dat中（缓冲区名称、结构体名称自行指定）
                 gfile.write(***, sizeof(demo));
    */
    /* 1.错误处理 */
    if (gfile.is_open() == 0)
    {
        cout << "文件打开失败" << endl;
        return -1;
    }

    gfile.seekp(0, ios::end); // 移动到文件末尾
    int fileSize = (int)gfile.tellp(); // 获取文件大小

    if (fileSize != (int)sizeof(Player))
    {
        cout << "文件game.dat的字节大小不正确" << endl;
        gfile.close();
        return -1;
    }

    gfile.seekp(0, ios::beg); // 确保写入从文件开头开始

    /* 2.读取文件 */
    gfile.read((char*)&player, sizeof(Player));       // 格式转化

    /* 3.根据是否读取成功，给出各游戏项的值 */
    if (gfile.gcount() != sizeof(Player))
    {
        cout << "文件读取失败" << endl;
        gfile.close();          // 关闭文件
        return -1;
    }
    else
    {
        while (true)
        {
            char ch;        // 要读取的选项
            print_Player_Info_graph(player);        /* 图形格式打印出来 */
            if (comfirm_modify(ch) == false)        // ch已经在函数中修改
            {
                continue;
            }

            /* 能到达这里说明输入的选项是正确的 */
            /* 1.存盘退出 */
            if (ch == '1')
            {
                gfile.seekp(0,ios::beg); // 确保写入从文件开头开始
                gfile.write((const char*)&player, sizeof(Player)); // 格式转化
                gfile.close();          // 关闭文件
                break;
            }
            else if (ch == '0')
            {
                gfile.close();          // 关闭文件
                break;
            }
            else        // 每个选项
            {
                string Tips;
                long long temp;

                if (RANGE[tolower(ch) - 'a'].type == INFO_NAME)
                {
                    Tips = input_range_tips(RANGE[tolower(ch) - 'a'].type, player);
                    cout << Tips;
                    cin.getline(player.name, sizeof(player.name)); // 从屏幕读取一行输入
                    // 检查输入的长度
                    if (strlen(player.name) >= 15)
                    {
                        cin.ignore(65536, '\n'); // 清除缓冲区
                    }
                    else
                    {
                        // 确保字符串以 '\0' 结尾
                        player.name[15] = '\0';
                    }
                }
                else       // 生命值
                {
                    while (true)
                    {
                        Tips = input_range_tips(RANGE[tolower(ch) - 'a'].type, player);
                        cout << Tips;
                        cin >> temp;           
                        
                        /* 非法的输入 */
                        if (WRONG_INPUT_DEAL(RANGE[RANGE[tolower(ch) - 'a'].type].min, RANGE[RANGE[tolower(ch) - 'a'].type].max, temp) == WRONG_INPUT)
                            continue;
                        
                        // 错误处理已经在内部处理
                        if (WRONG_INPUT_DEAL(RANGE[RANGE[tolower(ch) - 'a'].type].min, RANGE[RANGE[tolower(ch) - 'a'].type].max, temp) == OUT_OF_RANGE)
                        {       // 错误的范围
                            cout << "非法的" << RANGE[RANGE[tolower(ch) - 'a'].type].name << "值：" << temp << endl;
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
                            player.move_Speed = static_cast<unsigned char>(temp);
                            break;
                        case INFO_ATTACK_SPEED:
                            player.attack_Speed = static_cast<unsigned char>(temp);
                            break;
                        case INFO_ATTACK_RANGE:
                            player.attack_Range = static_cast<unsigned char>(temp);
                            break;
                        case INFO_ATTACK_POWER:
                            player.attack_Power = (short)temp;
                            break;
                        case INFO_DEFENSE_POWER:
                            player.defense_Power = (short)temp;
                            break;
                        case INFO_AGILITY:
                            player.agility = static_cast<unsigned char>(temp);
                            break;
                        case INFO_INTELLIGENCE:
                            player.intelligence = static_cast<unsigned char>(temp);
                            break;
                        case INFO_EXPERIENCE:
                            player.experience = static_cast<unsigned char>(temp);
                            break;
                        case INFO_LEVEL:
                            player.level = static_cast<unsigned char>(temp);
                            break;
                        case INFO_MAGIC_POINTS:
                            player.magic_Points = (short)temp;
                            break;
                        case INFO_MAGIC_COST:
                            player.magic_Cost = static_cast<unsigned char>(temp);
                            break;
                        case INFO_MAGIC_DAMAGE:
                            player.magic_Damage = static_cast<unsigned char>(temp);
                            break;
                        case INFO_HIT_RATE:
                            player.hitRate = static_cast<unsigned char>(temp);
                            break;
                        case INFO_MAGIC_DEFENSE:
                            player.magic_Defense = static_cast<unsigned char>(temp);
                            break;
                        case INFO_CRITICAL_RATE:
                            player.criticalRate = static_cast<unsigned char>(temp);
                            break;
                        case INFO_STAMINA:
                            player.stamina = static_cast<unsigned char>(temp);
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
        if (strcmp(argv[1], Command[READ])==0)
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