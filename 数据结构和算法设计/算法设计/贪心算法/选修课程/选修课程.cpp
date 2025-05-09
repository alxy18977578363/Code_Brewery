class Solution
{
public:
    int scheduleCourse(vector<vector<int>>& courses)
    {
        ranges::sort(courses, [](const auto& a, const auto& b) {
            return a[1] < b[1];
            });

        priority_queue<int>pq;      // ×î´ó¶Ñ
        int day = 0;
        for (auto& c : courses)
        {
            int duration = c[0], last_day = c[1];
            if (day + duration <= last_day)
            {
                day += duration;
                pq.push(duration);
            }
            else if (!pq.empty() && duration < pq.top())
            {
                day -= pq.top() - duration;
                pq.pop();
                pq.push(duration);
            }
        }

        return pq.size();
    }
};