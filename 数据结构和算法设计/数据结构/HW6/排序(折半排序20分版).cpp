class Solution
{
public:
    vector<int> mySort(vector<int>& list)
    {
        int n = list.size();
        for (int i = 1; i < n; i++)
        {
            if (list[i] < list[i - 1])
            {
                int low = 0, high = i - 2;


                /* ²ÉÓÃÕÛ°ë²åÈëµÄ·½·¨ */
                while (low <= high)
                {
                    int mid = (low + high) / 2;

                    if (list[i] > list[mid])   low = mid + 1;
                    else        high = mid - 1;
                }

                for (int j = i - 2; j >= high + 1; j--)
                {
                    list[j+1] = list[j];
                }

                list[high + 1] = list[i];
            }
        }

        return list;
    }

};
