class Solution
{
public:
    vector<int> mySort(vector<int>& list)
    {
        int n=list.size();
        quickSort(list, 0, n - 1);
        return list;
    }

/* 快排 */
private:
    /* 快排函数 */
    void quickSort(vector<int>& arr, int low, int high)
    {
        if (low < high)
        {
            /* 分区本身，左右快排 */
            int pivot = partition(arr, low, high);
            quickSort(arr, low, pivot - 1);
            quickSort(arr, pivot + 1, high);
        }
    }

    /* 分区函数 */
    int partition(vector<int>& arr, int low, int high)
    {
        // 随机选择基准并交换到low位置（避免最坏情况）
        int randomIdx = low + rand() % (high - low + 1);
        swap(arr[low], arr[randomIdx]);
        int pivot = arr[low]; // 基准值


        int left = low + 1, right = high;
        while (true)
        {
            // 从左找第一个大于pivot的元素
            while (left <= right && arr[left] <= pivot) left++;
            // 从右找第一个小于等于pivot的元素
            while (left <= right && arr[right] > pivot) right--;

            if (left > right) break; // 指针交叉时退出
            swap(arr[left], arr[right]);
            left++;
            right--;
        }

        // 将基准放到正确位置（right是最后一个<=pivot的位置）
        swap(arr[low], arr[right]);
        return right; // 返回分界点
    }
};