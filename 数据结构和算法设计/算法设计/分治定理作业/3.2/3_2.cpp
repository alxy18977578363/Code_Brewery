class Solution
{
public:
    int trainWays(int num)
    {
        if (num < 2)     return 1;
        vector<int>dp(num + 1, 1);           // 浪费一个格子来方便记录
        dp[1] = 1;
        dp[2] = 2;
        // 利用状态转移方程求解，动态规划问题
        for (int i = 3; i <= num; i++)
        {
            dp[i] = (dp[i - 1] + dp[i - 2]) % (int)(1e9 + 7);
        }

        return dp[num];
    }
};