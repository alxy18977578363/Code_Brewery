class Solution
{
public:
    string largestNumber(vector<int>& nums)
    {
        /* 用lambda函数的形式替换sort的排序规则，返回true则x在y前 */
        sort(nums.begin(), nums.end(), [](const int& x, const int& y) {
            return to_string(x) + to_string(y) > to_string(y) + to_string(x);
            });

        if (nums[0] == 0)
        {
            return "0";
        }

        string result;
        for (const auto& num : nums)
        {
            result += to_string(num);
        }

        return result;
    }
};