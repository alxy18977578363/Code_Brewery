#include<iostream>
#include<vector>
#include<queue>
using namespace std;

typedef int InfoType;

typedef struct ArcNode
{
	int adjvex;				//该弧的终点
	ArcNode* nextarc;		//后继的弧
	//本题中边无权重
}ArcNode;
	
/* 顶点 */
typedef struct VNode
{
	int time;                // 课程所需学时
	vector<int> next;		// 后置结点(可能多个相同)
	vector<int>pre;			// 前置结点
}VNode;

/* topo排序 */
void topo(const int&n,vector<VNode>&course_graph,vector<int>&in_degree,vector<int>&max_Time)
{
	// 拓扑排序计算最早完成时间
	queue<int> q;
	for (int i = 0; i < n; ++i)
	{
		if (in_degree[i] == 0)
		{
			q.push(i);
			max_Time[i] = course_graph[i].time;  // 没有前置课程的课程最早完成时间就是其自身时间
		}
	}

	while (!q.empty())
	{
		int current = q.front();
		q.pop();

		for (const auto& next_course : course_graph[current].next)
		{
			max_Time[next_course] = max(max_Time[next_course], max_Time[current] + course_graph[next_course].time);
			in_degree[next_course]--;		// 入度减少

			/* 入度为0则入栈 */
			if (in_degree[next_course] == 0)
			{
				q.push(next_course);
			}
		}

	}
}

int main()
{
	int n;		// 课程数量
	cin >> n;

	/* 图表 */
	vector<VNode>course_graph(n);
	vector<int>in_degree(n, 0);			// 入度，用于计算
	vector<int> max_Time(n, 0); // 计算每个课程的最早完成时间

	for (int i = 0; i < n; i++)
	{
		cin >> course_graph[i].time >> in_degree[i];		// 读入该课程时间和入度

		for (int j = 0; j < in_degree[i]; j++)
		{
			int course_index;
			cin >> course_index;

			course_graph[course_index - 1].next.push_back(i);
			course_graph[i].pre.push_back(course_index - 1);
		}
	}

	// 复制一份数据，避免修改原数据
	vector<int> temp_in_degree = in_degree;

	topo(n, course_graph, temp_in_degree, max_Time);

	// 计算最短毕业时间，即所有课程最早完成时间的最大值
	int graduation_time = 0;
	for (int i = 0; i < n; i++)
	{
		graduation_time = max(graduation_time, max_Time[i]);
	}

	for (int i = 0; i < n; i++)
	{
		course_graph[i].time+=1;

		/* 复制一份入度 */
		vector<int> temp_in_degree = in_degree;
		vector<int>temp_max_Time(n, 0);

		topo(n, course_graph, temp_in_degree, temp_max_Time);

		int new_graduation_time = 0;
		for (int i = 0; i < n; i++)
		{
			new_graduation_time = max(new_graduation_time, temp_max_Time[i]);
		}

		cout << max_Time[i] << " " << (new_graduation_time > graduation_time) << endl;

		course_graph[i].time -= 1;
	}

	return 0;
}