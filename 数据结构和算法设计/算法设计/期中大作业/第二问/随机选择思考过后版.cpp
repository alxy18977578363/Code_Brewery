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

	int l = low, r = high - 1;
	while (l <= r)
	{  // 注意这里是 <= 而不是 <
		// 从左找第一个 >= pivot 的元素
		while (l <= r && arr[l] < pivot) l++;
		// 从右找第一个 <= pivot 的元素
		while (l <= r && arr[r] > pivot) r--;

		if (l <= r)
		{
			swap(arr[l], arr[r]);
			l++;  // 关键：交换后必须移动指针
			r--;
		}
	}

	// 将 pivot 放到正确位置
	swap(arr[l], arr[high]);
	return l;
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