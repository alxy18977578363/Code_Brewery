class Solution
{
public:
    vector<int> smallestRange(vector<vector<int>>& nums)
    {
        int left_num = 0, right_num = INT_MAX;
        int n = nums.size();     //  维护n个指针
        vector<int>ptr(n);

        // 定义比较匿名函数，这个&表示捕获所有的区域变量
        auto cmp = [&](const int& u, const int& v) {
            return nums[u][ptr[u]] > nums[v][ptr[v]];
            };

        priority_queue<int, vector<int>, decltype(cmp)>pq(cmp);
        int minValue = 0, maxValue = INT_MIN;
        for (int i = 0; i < n; ++i)
        {
            pq.emplace(i);
            maxValue = max(maxValue, nums[i][0]);
        }

        while (true)
        {
            int row = pq.top();
            pq.pop();
            minValue = nums[row][ptr[row]];

            if (maxValue - minValue < right_num - left_num)
            {
                left_num = minValue;
                right_num = maxValue;
            }
            if (ptr[row] == nums[row].size() - 1)
            {
                break;
            }

            ptr[row]++;
            maxValue = max(maxValue, nums[row][ptr[row]]);
            pq.emplace(row);
        }

        return { left_num,right_num };
    }
};