class Solution
{
public:
    int wiggleMaxLength(vector<int>& nums)
    {
        int n = nums.size();
        if (n < 2) return n;

        int lastdiff = nums[1] - nums[0];      // 初始化上一个差
        int maxlen = lastdiff == 0 ? 1 : 2;

        for (int i = 2; i < n; i++)
        {
            int diff = nums[i] - nums[i - 1];
            if ((diff > 0 && lastdiff <= 0) || (diff < 0 && lastdiff >= 0))
            {
                maxlen++;
                lastdiff = diff;
            }
        }

        return maxlen;
    }
};