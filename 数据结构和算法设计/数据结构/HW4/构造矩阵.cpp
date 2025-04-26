#include<iostream>
#include<vector>
#include <unordered_map>
#include<queue>
using namespace std;

/* 拓扑系列图 */
vector<int> topo_logical_Sort(int k, const vector<pair<int, int>>& conditions)
{
    /* 用于创建一个哈希表 */
    unordered_map<int, vector<int>> graph;
    vector<int> in_degree(k + 1, 0);            // 每个的入度都是0

    for (const auto& conditions : conditions)
    {
        /* 取得每次的前后驱 */
        int first = conditions.first;
        int last = conditions.second;

        graph[first].push_back(last);       // 压入栈
        in_degree[last]++;
    }

    /* 取得目前表中无入度的点 */
    queue<int> q;
    for (int i = 1; i <= k; i++)
    {
        if (in_degree[i] == 0)
        {
            q.push(i);
        }
    }

    /* 进行拓扑排序 */
    vector<int> order;
    while (!q.empty())
    {
        int node = q.front();
        q.pop();
        order.push_back(node);      // 取出一个放入order，然后遍历该入度

        for (int neighbor : graph[node])        // 图中的所有邻居都要减一
        {
            in_degree[neighbor]--;
            if (in_degree[neighbor] == 0)
            {
                q.push(neighbor);
            }
        }
    }

    if (order.size() != k)
    {
        return {};
    }

    return order;
}

/* 建立这个矩阵 */
vector<vector<int>> buildMatrix(int k, const vector<pair<int, int>>& rowConditions, const vector<pair<int, int>>& colConditions)
{
    vector<int> rowOrder = topo_logical_Sort(k, rowConditions);
    vector<int> colOrder = topo_logical_Sort(k, colConditions);

    if (rowOrder.empty() || colOrder.empty())
    {
        return {};
    }

    /* 其实就是k*k的矩阵 */
    vector<vector<int>> matrix(k, vector<int>(k, 0));
    for (int i = 0; i < k; i++)
    {
        /* 寻找到j */
        int j = 0;
        for (j = 0; j < k; j++)
        {
            if (colOrder[j] == rowOrder[i])
            {
                break;
            }
        }

        matrix[i][j] = rowOrder[i];
    }

    return matrix;
}


int main()
{
	/* 1.读入k阶矩，n行row，m行col */
	int k, n, m;
	cin >> k >> n >> m;

    /* 2.读入 */
    vector<pair<int, int>>rowConditions(n);
    for (int i = 0; i < n; i++)
    {
        cin >> rowConditions[i].first >> rowConditions[i].second;
    }

    vector<pair<int, int>> colConditions(m);
    for (int i = 0; i < m; i++)
    {
        cin >> colConditions[i].first >> colConditions[i].second;
    }

    vector<vector<int>>result = buildMatrix(k, rowConditions, colConditions);

    if (result.empty())
    {
        cout << -1 << endl;
    }
    else
    {
        for (const auto& row : result)
        {
            for (const auto& value : row)
            {
                cout << value << " ";
            }
            cout << endl;
        }
    }

    return 0;
}