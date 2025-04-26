class Solution
{
public:
    int longestSubstring(string s, int k)
    {
        /* 终止条件 */
        if (s.size() < k)
        {
            return 0;
        }
        /* 先记录数据 */
        unordered_set<char> keys(s.begin(), s.end());
        unordered_map<char, int>counter;

        for (const char& ch : s)
        {
            counter[ch]++;
        }

        for (const char& ch : keys)
        {
            /* 将原string根据不满足题意的key分为多个子串 */
            vector<string> son_string;
            if (counter[ch] < k)
            {
                split(s, son_string, ch);
                int res = 0;
                for (const auto& ss : son_string)
                {
                    res = max(res, longestSubstring(ss, k));
                }
                return res;
            }


        }

        return s.size();
    }

    void split(const string s, vector<string>& son_string, const char& ch)
    {
        /* 采用getline来取对应的子串 */
        son_string.clear();
        istringstream iss(s);
        string temp;

        while (getline(iss, temp, ch))
        {
            son_string.push_back(temp);
        }
    }
};