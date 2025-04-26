class Solution
{
public:
    int maxCoins(vector<int>& nums)
    {
        int n = nums.size();
        vector<int> arr(n + 2, 1);          // 补充两侧的1
        for (int i = 1; i <= n; i++)    arr[i] = nums[i - 1];
        vector<vector<int>> dp(n + 2, vector<int>(n + 2, 0));       // 拓展一下

        for (int len = 1; len <= n; len++)
        {
            for (int i = 1; i + len <= n + 1; i++)
            {
                int j = i + len - 1;
                for (int k = i; k <= j; k++)
                {
                    dp[i][j] = max(dp[i][j], arr[i - 1] * arr[k] * arr[j + 1] + dp[i][k - 1] + dp[k + 1][j]);
                }
            }
        }
        return dp[1][n];
    }
};