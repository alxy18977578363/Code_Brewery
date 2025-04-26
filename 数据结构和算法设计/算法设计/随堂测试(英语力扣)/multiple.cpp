class Solution
{
public:
    int multiply(long long multiplier, long long multiplicand)
    {
        if (multiplicand)
        {
            // 处理负数乘数：转换为正数计算，结果取反
            if (multiplicand < 0)
            {
                return -multiply(multiplier, -multiplicand);
            }

            // 递归分解乘数为二进制位：multiplier * (b0 * 2^0 + b1 * 2^1 + ...)
            if (multiplicand & 1)
            { // 当前二进制位为1
// 累加当前位值并处理高位：multiplier<<1相当于乘2，multiplicand>>1移向下一位
                return multiply(multiplier << 1, multiplicand >> 1) + multiplier;
            }
            else
            {                // 当前二进制位为0
                return multiply(multiplier << 1, multiplicand >> 1);
            }
        }
        return 0; // 递归终止条件：乘数分解完毕
    }
};