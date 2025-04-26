#include <iostream>
#include <vector>
#include <queue>
#include <functional> // for greater

using namespace std;

int find_kth_smallest_element(vector<int>& arr, int k)
{
	// 错误处理
	int n = arr.size();
	if (k > n)
	{
		cout << "错误，结果不可信" << endl;
		return -1;
	}

	// 创建一个最大堆
	priority_queue<int> maxHeap;		// 优先队列,队首位置是最大的

	// 插入前k个数
	for (int i = 0; i < k; i++)
	{
		maxHeap.push(arr[i]);
	}

	// 继续遍历剩余的元素
	for (int i = k; i < arr.size(); ++i)
	{
		if (arr[i] < maxHeap.top())
		{
			maxHeap.pop();
			maxHeap.push(arr[i]);
		}
	}

	// 返回堆顶元素即为第 k 小的元素
	return maxHeap.top();
}

int main()
{
	vector<int> arr = { 12, 3, 5, 7, 19, 4, 1 };
	int k = 4;

	cout << "The " << k << "th smallest element is: " << find_kth_smallest_element(arr, k) << endl;

	return 0;
}