#include <iostream>
#include<vector>
using namespace std;


// 改为局部变量传递，避免全局状态污染
int Merge(vector<int>& arr, int low, int mid, int high, vector<int>& temp)
{
    int i = low, j = mid + 1, k = low;
    int result = 0;
    // 复制当前处理的范围到临时数组
    for (int idx = low; idx <= high; idx++)
    {
        temp[idx] = arr[idx];
    }
    while (i <= mid && j <= high)
    {
        if (temp[i] <= temp[j])
        {
            arr[k++] = temp[i++];
        }
        else
        {
            // 计算逆序对数量
            result += mid - i + 1;
            arr[k++] = temp[j++];
        }
    }
    // 处理剩余元素
    while (i <= mid) arr[k++] = temp[i++];
    while (j <= high) arr[k++] = temp[j++];
    return result;
}

// 归并排序
int MergeSort(vector<int>& arr,const int low,const int high, vector<int>& temp)
{

    /* 终止条件，就是一个元素 */
    if (low == high)
    {
        return 0;
    }

    int mid = (low + high) / 2;
    int result = 0;
    result += MergeSort(arr, low, mid, temp);
    result += MergeSort(arr, mid + 1, high, temp);
    result += Merge(arr, low, mid, high, temp);
    return result;
}

int main(int argc, char* argv[])
{
    int n = 0;

    while (cin >> n)
    {
        if (n <= 0)
        {
            return 0;
        }

        vector<int> arr(n);
        for (int i = 0; i < n; i++)
        {
            cin >> arr[i];
        }
        vector<int> temp(arr); // 预分配临时数组空间
        

        int result = MergeSort(arr, 0, n - 1, temp);
        cout << result << endl;
    }
    
}
