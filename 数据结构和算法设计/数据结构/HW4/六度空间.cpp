#include<iostream>
#include<queue>
#include<iomanip>
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
		Graph[i].data = i + 1;
		Graph[i].firstarc = NULL;
	}

	for (int i = 0; i < arcnum; i++)
	{
		InfoType  value1;		// 头结点的信息值
		InfoType  value2;		// 边结点的信息值
		cin >> value1 >> value2;

		ArcNode* p = Graph[value1 - 1].firstarc;
		ArcNode* q = new(nothrow) ArcNode{value2 - 1,NULL};
		if (!q)
			exit(-1);

		if (p)
		{
			while (p->nextarc)
				p = p->nextarc;
			p->nextarc = q;
		}
		else
			Graph[value1 - 1].firstarc = q;

		/* 反过来同样需要 */
		p = Graph[value2 - 1].firstarc;
		q = new(nothrow) ArcNode{ value1 - 1,NULL };
		if (!q)
			exit(-1);

		if (p)
		{
			while (p->nextarc)
				p = p->nextarc;
			p->nextarc = q;
		}
		else
			Graph[value2 - 1].firstarc = q;
	}
	
	return OK;
}

/* BFS读出邻接表 */
int BFS(VNode* Graph, const int i, bool* visited)
{
	InfoType last = 0;		// 记录下一圈的关系图中最后一个元素的下标
	InfoType tail = i;	// 记录下某一层的最后一个结点真正的下标
	int num = 1;		// 数量
	int depth = 0;		// 深度

	queue<InfoType> vexlist;
	vexlist.push(i);

	while (!vexlist.empty())
	{
		InfoType temp = vexlist.front();		// 暂时记录取出来的是什么
		vexlist.pop();			// 取出队伍顶端

		ArcNode* p = Graph[temp].firstarc;		// 取第一个邻元
		for (; p; p = p->nextarc)
		{
			if (visited[p->adjvex] == 0)
			{
				visited[p->adjvex] = 1;
				num++;
				last = p->adjvex;			// 记录好下一圈的最后一个元素
				vexlist.push(p->adjvex);
			}
		}

		if (tail == temp)
		{
			depth++;
			tail = last;		// 更新为下一圈的最后一个数的下标
		}

		if (depth == 6)
		{
			break;				// 比如说一的时候，你刚处理完放进去就是一了，直接不用算了
		}
	}

	return num;
}

template<typename T>
void clear_matrix(T* matrix,size_t N)
{
	for (size_t i = 0; i < N; i++)
	{
		matrix[i] = 0;
	}
}

/* 通过BFS遍历整个表 */
int BFSTraverse(VNode* Graph, const int vexnum)
{
	/* 申请visited数组记录遍历情况 */
	bool* visited = new bool[vexnum] {0};
	if (!visited)	return MEMORY_ALLOCATION_FAILED;

	for (int i = 0; i < vexnum; i++)
	{
		visited[i] = true;
		cout << i + 1 << ": " << setprecision(2)<< fixed <<((double)BFS(Graph, i, visited) /(double) vexnum)*100 << "%" << endl;

		/* 更新visit */
		clear_matrix(visited, vexnum);
	}

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

	BFSTraverse(Graph, G.vexnum);

	return 0;
}