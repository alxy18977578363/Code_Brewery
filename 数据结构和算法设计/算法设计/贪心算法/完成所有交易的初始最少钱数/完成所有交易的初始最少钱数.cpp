class Solution
{
public:
    long long minimumMoney(vector<vector<int>>& transactions)
    {
        long long total_lose = 0;
        int max_cost_in_earning = 0;
        int max_cashback_in_lost = 0;
        for (auto& t : transactions)
        {
            total_lose += max(t[0] - t[1], 0);       // ¼ÆËã×î´ó¿÷Ëð
            if (t[0] < t[1])     max_cost_in_earning = max(max_cost_in_earning, t[0]);
            else        max_cashback_in_lost = max(max_cashback_in_lost, t[1]);
        }

        long long res = total_lose + max(max_cashback_in_lost, max_cost_in_earning);
        return res;
    }
};