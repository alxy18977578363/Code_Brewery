class Solution
{
public:
    int findMinimumTime(vector<vector<int>>& tasks)
    {
        int n = tasks.size();
        sort(tasks.begin(), tasks.end(), [&](vector<int> t1, vector<int>t2) {
            return t1[1] < t2[1];
            });

        vector<int> run(tasks[n - 1][1] + 1, 0);        // 制作一个时间轴
        int res = 0;
        for (int i = 0; i < n; i++)
        {
            int start = tasks[i][0], end = tasks[i][1], duration = tasks[i][2];
            duration -= accumulate(run.begin() + start, run.begin() + end + 1, 0);
            res += max(duration, 0);
            for (int j = end; i >= 0 && duration > 0; j--)
            {
                if (run[j] == 0)
                {
                    run[j] = 1;
                    duration--;
                }
            }
        }

        return res;
    }
};