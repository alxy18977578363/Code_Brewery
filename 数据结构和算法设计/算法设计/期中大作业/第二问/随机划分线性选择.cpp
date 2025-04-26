#include <iostream>
#include <cstdlib>
#include <ctime>
#include<vector>

using namespace std;


// 分区函数
int partition(vector<int>& arr, int low, int high)
{
	int random_index = rand() % (high - low + 1) + low;
	swap(arr[random_index], arr[high]);  // 将随机的 pivot 放到数组的末尾
	int pivot = arr[high];							// 由于最后一位是基准，所以应该最后是跟比它大的数交换，所以应该先让左边踏足不喜欢的区域

	int i = low;  // i 表示 <= pivot 的区域的右边界
	for (int j = low; j < high; j++)
	{
		if (arr[j] <= pivot)
		{
			swap(arr[i], arr[j]);  // 把 <= pivot 的元素交换到左边
			i++;
		}
	}
	swap(arr[i], arr[high]);  // 把 pivot 放到正确的位置
	return i;
}


// 快速选择函数
int quickSelect(vector<int>& arr,int low,int high,int k)
{
	// k 是从 1 开始的，转化为从 0 开始的索引
	int need_index = k - 1;

	while (low <= high)
	{
		int pivot_index = partition(arr, low, high);

		if (pivot_index == need_index)
		{
			return arr[pivot_index];  // 找到第 k 小的元素
		}
		else if (pivot_index < need_index)
		{
			low = pivot_index + 1;  // 查找右边部分
		}
		else
		{
			high = pivot_index - 1;  // 查找左边部分
		}
	}

	return -1;  // 不应该执行到这里
}

int main()
{
	std::srand(std::time(nullptr));
	vector<int> arr = { 12, 3, 5, 7, 19, 4, 1 };
	int k = 4;

	cout << "The " << k << "th smallest element is: " << quickSelect(arr, 0,6,k) << endl;

	return 0;
}