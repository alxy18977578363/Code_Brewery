#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

// 辅助函数：对 5 个或更少的元素进行排序并返回中位数
int findMedian(vector<int>& arr, int left, int right)
{
    sort(arr.begin() + left, arr.begin() + right + 1);
    return arr[left + (right - left) / 2];
}

// 主选择函数
int select(vector<int>& arr, int left, int right, int k)
{
    if (k > 0 && k <= right - left + 1)
    {
        int n = right - left + 1;
        vector<int> medians;

        // 将数组划分为 5 个一组，计算每组的中位数
        for (int i = 0; i < n / 5; i++)
        {
            int groupLeft = left + i * 5;
            int groupRight = groupLeft + 4;
            medians.push_back(findMedian(arr, groupLeft, groupRight));
        }

        // 处理最后一组（可能不足 5 个元素）
        if (n % 5 != 0)
        {
            int lastGroupLeft = left + (n / 5) * 5;
            int lastGroupRight = right;
            medians.push_back(findMedian(arr, lastGroupLeft, lastGroupRight));
        }

        // 递归计算中位数的中位数 pivot
        int pivot = (medians.size() == 1) ? medians[0] : select(medians, 0, medians.size() - 1, medians.size() / 2);

        // 划分数组（类似快速排序的 partition）
        int pivotIndex = -1;
        for (int i = left; i <= right; i++)
        {
            if (arr[i] == pivot)
            {
                pivotIndex = i;
                break;
            }
        }
        swap(arr[pivotIndex], arr[right]); // 将 pivot 移到末尾

        int i = left;
        for (int j = left; j < right; j++)
        {
            if (arr[j] <= pivot)
            {
                swap(arr[i], arr[j]);
                i++;
            }
        }
        swap(arr[i], arr[right]); // 将 pivot 放回正确位置

        // 判断递归方向
        int pos = i - left + 1;
        if (pos == k)
        {
            return arr[i];
        }
        else if (pos > k)
        {
            return select(arr, left, i - 1, k);
        }
        else
        {
            return select(arr, i + 1, right, k - pos);
        }
    }
    return -1; // 无效输入
}

int main()
{
    vector<int> arr = { 12, 3, 5, 7, 19, 4, 1 };
    int k = 4;

    int result = select(arr, 0, arr.size() - 1, k);
    cout << "第 " << k << " 小的元素是: " << result << endl;

    return 0;
}