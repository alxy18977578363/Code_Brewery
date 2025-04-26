#include<iostream>
#include<queue>
using namespace std;

#define MEMORY_ALLOCATION_FAILED -1;
#define OK		1
#define MAX_VEXNUM 20			// 假设最多顶点数，留着，不一定用

typedef int InfoType;

typedef struct ArcNode		// 表的结点
{
	int		adjvex;		//存储顶点对应的下标   存储的是一个位置，而非具体元素，为了以后改变数据方便操作 
	ArcNode* nextarc;	// 链域指向下一个邻接点 
	int   weight;      //权值（问题中有权值再用）
}ArcNode;

typedef struct VNode	// 顶点表结点
{
	InfoType  data;		// 顶点信息
	ArcNode* firstarc;  // 指向边表中第一个结点 
}VNode;

typedef struct Graph_Adjlist
{
	VNode adjlist[MAX_VEXNUM];		// 顶点表，但是我不这么用因为我用的是申请内存
	int vexnum;			// 顶点数
	int arcnum;			// 弧数
}Graph_Adjlist;//声明图的邻接表类型

/* 创建一个邻接表 */
int create_graph(VNode Graph[],const int arcnum,const int vexnum)
{
	/* 为每个头结点带上数据 */
	for (int i = 0; i < vexnum; i++)
	{
		Graph[i].data = i;
		Graph[i].firstarc = NULL;
	}


	for (int i = 0; i < arcnum; i++)
	{
		InfoType  value1;		// 头结点的信息值
		InfoType  value2;		// 边结点的信息值
		cin >> value1 >> value2;

		ArcNode* p = Graph[value1].firstarc;
		ArcNode* q = new(nothrow) ArcNode{value2,NULL};
		if (!q)
			exit(-1);

		if (p)
		{
			while (p->nextarc)
				p = p->nextarc;
			p->nextarc = q;
		}
		else
			Graph[value1].firstarc = q;

		/* 反过来同样需要 */
		p = Graph[value2].firstarc;
		q = new(nothrow) ArcNode{ value1,NULL };
		if (!q)
			exit(-1);

		if (p)
		{
			while (p->nextarc)
				p = p->nextarc;
			p->nextarc = q;
		}
		else
			Graph[value2].firstarc = q;
	}
	
	return OK;
}

/* DFS读出相邻组合 */
int DFS(VNode *Graph, const int i, bool *visited)
{
	// 用于不断地向深处探索
	ArcNode* p = Graph[i].firstarc;		// 取得i下标对应的第一邻边	
	if (!p)
	{
		return 0;
	}

	for (; p; p = p->nextarc)
	{
		if (visited[p->adjvex] == 0)
		{
			cout << " " << p->adjvex;
			visited[p->adjvex] = true;
			DFS(Graph, p->adjvex,visited);
		}
	}
	
	return OK;
}

/* 通过DFS遍历整个表 */
int DFSTraverse(VNode *Graph, const int vexnum)
{
	/* 申请visited数组记录遍历情况 */
	bool* visited = new bool[vexnum] {0};
	if (!visited)	return MEMORY_ALLOCATION_FAILED;

	for (int i = 0; i < vexnum; i++)
	{
		if (visited[i] == 0)
		{
			cout << "{" << i;
			visited[i] = true;
			DFS(Graph, i, visited);
			cout << "}";
		}		// 若没有经历过，则进行DFS,内部输出了相应数值
	}

	cout << endl;
	delete[]visited;		// 记得释放内存
	return OK;
}

/* BFS读出邻接表 */
int BFS(VNode* Graph, const int i, bool* visited, bool first)
{
	ArcNode* p = Graph[i].firstarc;
	queue<InfoType> vexlist;
	vexlist.push(i);

	while (!vexlist.empty())
	{
		int cur = vexlist.front();
		vexlist.pop();
		ArcNode* p = Graph[cur].firstarc;
		for (; p; p = p->nextarc)
		{
			if (!visited[p->adjvex])
			{
				cout << " " << p->adjvex;
				visited[p->adjvex] = true;
				vexlist.push(p->adjvex);
			}
		}
	}

	return 0;
}

/* 通过BFS遍历整个表 */
int BFSTraverse(VNode* Graph, const int vexnum)
{
	/* 申请visited数组记录遍历情况 */
	bool* visited = new bool[vexnum] {0};
	if (!visited)	return MEMORY_ALLOCATION_FAILED;

	for (int i = 0; i < vexnum; i++)
	{
		if (visited[i] == 0)
		{
			cout << "{" << i;
			visited[i] = true;
			BFS(Graph, i, visited, true);
			cout << "}";
		}		// 若没有经历过，则进行DFS,内部输出了相应数值
	}

	cout << endl;
	delete[]visited;		// 记得释放内存
	return OK;
}

int main()
{
	Graph_Adjlist G;	
	cin >> G.vexnum >> G.arcnum;	// 顶点数和弧数

	VNode* Graph = new VNode[G.vexnum];		// 申请这个表
	if (Graph == NULL)
	{
		cout << "申请空间失败" << endl;
		return -1;
	}


	// 错误处理已经在函数调用中了
	if (create_graph(Graph, G.arcnum,G.vexnum) != OK)
	{
		return -1;
	}

	DFSTraverse(Graph, G.vexnum);
	BFSTraverse(Graph, G.vexnum);

	return 0;
}