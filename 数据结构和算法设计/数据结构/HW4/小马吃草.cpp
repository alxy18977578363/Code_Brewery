#include<iostream>
#include<vector>
#include <unordered_map>
#include<queue>
#include <limits>
using namespace std;

const int INF = numeric_limits<int>::max();
typedef int InfoType;

typedef struct Edge
{
	int next;		// 下一个点的顶点下标
	InfoType power;		// 权重

}Edge;

/* 马的起点和目标 */
typedef struct Start_End
{
	int start;
	int end;
}Start_End;

void dijkstra(int start, const vector<vector<Edge>>& graph, vector<int>& dist)
{
	/* 一个队列 */
	priority_queue<pair<int, int>> pq;
	dist[start] = 0;
	pq.push({ 0, start });

	while (!pq.empty())
	{
		int current_dist = pq.top().first;
		int current_node = pq.top().second;
		pq.pop();

		if (current_dist > dist[current_node]) continue;

		/* 迭代取得取出元素的所有临边，如果该邻边的长度和到该元素的长度之和比start到该元素小，那就更新 */
		for (const Edge& edge : graph[current_node])
		{
			int next_node = edge.next;
			int weight = edge.power;

			if (dist[current_node] + weight < dist[next_node])
			{
				dist[next_node] = dist[current_node] + weight;
				pq.push({ dist[next_node], next_node });
			}
		}
	}
}

int main()
{
	int N, M;				// 点的数量和边的数量
	cin >> N >> M;

	/* 二维矩阵图表 */
	vector<vector<Edge>>graph(N + 1);		// 因为下标从1开始，所以浪费一个空间
	for (int i = 0; i < M; i++)
	{
		int first, last, power;			// 前驱、后继和权重
		cin >> first >> last >> power;

		graph[first].push_back({ last,power });
		graph[last].push_back({ first,power });
	}

	int H, R;			// H是牧草点的数量，R是马的数量
	cin >> H >> R;

	/* 牧草点的下标 */
	vector<int> grass_points(H);
	for (int i = 0; i < H; ++i)
	{
		cin >> grass_points[i];
	}

	/* R匹马的起点和终点 */
	vector<Start_End> horses(R);
	for (int i = 0; i < R; ++i)
	{
		cin >> horses[i].start >> horses[i].end;
	}

	/* 计算每个草到终点的最短距离 */
	vector<vector<int>> grass_dist(H, vector<int>(N + 1, INF));
	for (int i = 0; i < H; ++i)
	{
		dijkstra(grass_points[i], graph, grass_dist[i]);
	}

	for (const auto& horse : horses)
	{
		/* 马到任何一草的距离：start_dist */
		vector<int> start_dist(N + 1, INF);
		dijkstra(horse.start, graph, start_dist);

		int min_distance = INF;
		for (int i = 0; i < H; ++i)
		{
			int grass_point = grass_points[i];
			if (start_dist[grass_point] != INF)
			{
				min_distance = min(min_distance, start_dist[grass_point] + grass_dist[i][horse.end]);
			}
		}

		cout << min_distance << endl;
	}

	return 0;
}