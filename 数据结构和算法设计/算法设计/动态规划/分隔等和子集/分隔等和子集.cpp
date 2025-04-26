class Solution
{
public:
    bool canPartition(vector<int>& nums)
    {
        int sum = std::accumulate(nums.begin(), nums.end(), 0);

        // 如果总和为奇数，不能分割成两个子集
        if (sum % 2 != 0)
        {
            return false;
        }

        sum = sum / 2;  // 目标子集和

        // 创建 dp 数组，dp[i] 表示是否能找到和为 i 的子集
        vector<bool> dp(sum + 1, false);
        dp[0] = true;  // 和为 0 时，子集为空集

        // 遍历每个数
        for (int num : nums)
        {
            // 从大到小更新 dp 数组
            for (int i = sum; i >= num; --i)
            {
                dp[i] = dp[i] || dp[i - num];  // 如果 dp[i - num] 为 true，就更新 dp[i]
            }
        }

        return dp[sum];  // 如果 dp[sum] 为 true，说明可以分成两个和相等的子集
    }
};
