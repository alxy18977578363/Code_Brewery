#include<iostream>
#include<vector>
using namespace std;

// 求和
int sum_value(const vector<int>& cards)
{
	int n = cards.size();		// 数量
	int res = 0;				// 求和
	for (int i = 0; i < n; i++)
	{
		res += cards[i];
	}

	return res;
}


// 背包问题
pair<int, vector<int>> package(vector<int>& cards)
{
	int n = cards.size();		// 背包物品数
	int total_value = sum_value(cards);

	int half_value = total_value / 2;			// 一半价值，观察所能凑出的最大价值
	vector<vector<bool>>dp(n + 1, vector<bool>(half_value + 1, false));
	vector<vector<int>> parent(n + 1, vector<int>(half_value + 1, -1));		// 用于回溯的父指针表

	// 初始化：0个物品可以凑出价值0
	for (int i = 0; i <= n; i++)
	{
		dp[i][0] = true;
	}

	// 动态规划填表
	for (int i = 1; i <= n; i++)
	{
		for (int j = 0; j <= half_value; j++)
		{
			// 不选当前物品
			if (dp[i - 1][j])
			{
				dp[i][j] = true;
				parent[i][j] = j;
			}

			// 选当前物品（注意cards的索引是0-based）
			if (j >= cards[i - 1] && dp[i - 1][j - cards[i - 1]])
			{
				dp[i][j] = true;
				parent[i][j] = j - cards[i - 1];
			}
		}
	}


	// 找到最大的可凑值
	int max_value = 0;
	for (int j = half_value; j >= 0; j--)
	{
		if (dp[n][j])
		{
			max_value = j;
			break;
		}
	}

	// 回溯找出选了哪些物品
	vector<int> selected;
	int current_value = max_value;
	for (int i = n; i > 0 && current_value > 0; i--)
	{
		if (current_value != parent[i][current_value])
		{  // 说明选了第i个物品
			selected.push_back(i);  // 记录物品索引（1-based）
			current_value = parent[i][current_value];
		}
	}

	return { max_value, selected };
}

int main()
{
	// 示例数据（卡片价值）
	vector<int> cards = { 2,1,3,1,5,2,3,4 };

	auto result = package(cards);
	int max_value = result.first;
	vector<int> selected = result.second;

	// 输出结果
	int n = cards.size();
	vector<bool> choice(n + 1, false);

	cout << max_value << endl;
	for (int idx : selected)
	{
		choice[idx] = true;
		cout << idx << " ";
	}
	cout << endl;
	cout << sum_value(cards) - max_value << endl;
	for (int i = 1; i <= n; i++)
	{
		if (choice[i] == false)		cout << i << " ";
	}
	cout << endl;

	return 0;
}