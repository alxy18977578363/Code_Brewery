class Solution
{
public:
    vector<vector<string>> partition(string s)
    {
        int n = s.size();
        vector<vector<bool>> dp(n, vector<bool>(n, true));
        vector<vector<string>> res;
        vector<string> one_part;

        // 创建动态规划数组
        for (int i = n - 1; i >= 0; i--)
        {
            for (int j = i + 1; j < n; j++)
            {
                dp[i][j] = (s[i] == s[j]) && dp[i + 1][j - 1];
            }
        }

        // 利用回溯算法去搜索
        auto dfs = [&](auto&& dfs, int i) {
            if (i == n)
            {
                res.push_back(one_part);
                return;
            }
            else
            {
                for (int j = i; j < n; j++)
                {
                    if (dp[i][j])
                    {
                        one_part.push_back(s.substr(i, j - i + 1));
                        dfs(dfs, j + 1);
                        one_part.pop_back();
                    }
                }
            }
            };

        dfs(dfs, 0);
        return res;
    }
};