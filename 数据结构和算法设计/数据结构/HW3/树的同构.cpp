#include <iostream>
#include <string>
#include <string.h>
using namespace std;

/* 数据结构定义 */
#define ERROR		-1
#define OK			0
#define SOVERFLOW	-1
#define FALSE		0
#define TRUE		1

typedef char ElemType;
typedef int  code;			// 编号
typedef int  Status;


// 定义二叉树节点结构体
struct TreeNode
{
	ElemType data;          // 节点数据
	TreeNode* ltree;       // 指向左子树的指针
	TreeNode* rtree;       // 指向右子树的指针
};

typedef struct TreeNode TreeNode, * Bitree;

/*==================================
根据输入的内容建造一棵树
Bitree T为一个树的指针，指向构造的树
===================================*/
Status BuildTree(Bitree &root)
{
	/* 读入一棵树的节点数 */
	int Node_num;
	cin >> Node_num;

	/* 错误处理 */
	if (Node_num <= 0)
	{
		return ERROR;
	}

	/* 申请T的空间 */
	Bitree T = new(nothrow)TreeNode[Node_num];
	if (!T)		exit(SOVERFLOW);

	/* vis的布尔类型数组是为了寻找根节点 */
	bool* vis = new(nothrow)bool[Node_num] {0};

	/* 将内容输入到树的结构体数组中 */
	for (int i = 0; i < Node_num; i++)
	{
		ElemType ch;
		string ltree, rtree;
		code lvalue, rvalue;
		
		cin >> ch >> ltree >> rtree;
		
		/* 先赋值再取指向 */
		if (ltree == "-")
		{
			lvalue = -1;
		}
		else
		{
			lvalue = stoi(ltree);
		}

		if (rtree == "-")
		{
			rvalue = -1;
		}
		else
		{
			rvalue = stoi(rtree);
		}
		T[i].data = ch;

		/* 取指向 */
		if (lvalue == -1)
		{
			T[i].ltree = NULL;
		}
		else
		{
			/* 第i个节点指向自己的左子树，标记为子树 */
			T[i].ltree = &(T[lvalue]);
			vis[lvalue] = true;
		}

		if (rvalue == -1)
		{
			T[i].rtree = NULL;
		}
		else
		{
			/* 第i个节点指向自己的左子树，标记为子树 */
			T[i].rtree = &(T[rvalue]);
			vis[rvalue] = true;
		}
	}

	/* 最终根据自己所得的树，将根的地址返回 */
	for (int i = 0; i < Node_num; i++)
	{
		/* 没有被标记过的，是根 */
		if (!vis[i])
		{
			root = &(T[i]);
			break;
		}
	}

	return OK;
}

/* 通过遍历两棵树来进行比较 */
Status visit(const Bitree root1,Bitree root2,Status(*compare)(const Bitree Node1, const Bitree Node2))
{
	/* 终止条件 */
	if (!root1 && !root2)
	{
		return TRUE;
	}

	/* 先比较根是否相等 */
	if (compare(root1, root2) == FALSE)
	{
		return FALSE;
	}

	/*  */
	return ((visit(root1->ltree, root2->ltree,compare) && visit(root1->rtree, root2->rtree,compare))
		|| (visit(root1->ltree, root2->rtree,compare) && visit(root1->rtree, root2->ltree,compare)));
	
}

/* 比较两个节点的data是否相等 */
Status Compare(const Bitree Node1, const Bitree Node2)
{
	/* 如果两个Node有一个不是NULL另一个是，说明不等 */
	if (Node1 == NULL && Node2 == NULL)
	{
		return TRUE;
	}
	else if ((Node1 == NULL && Node2 != NULL) || (Node1 != NULL && Node2 == NULL))
	{
		return FALSE;
	}
	

	if (Node1->data != Node2->data)
	{
		return FALSE;
	}

	return TRUE;
}

/* 取得深度 */
Status Get_depth(const Bitree root)
{
	int Ldepth, Rdepth;

	if (!root)
	{
		return 0;
	}
	else
	{
		Ldepth = Get_depth(root->ltree);
		Rdepth = Get_depth(root->rtree);
		return max(Ldepth, Rdepth) + 1;
	}
}


int main()
{
	/* 构建两棵树 */
	Bitree Tree1, Tree2;
	BuildTree(Tree1);
	BuildTree(Tree2);

	if (visit(Tree1, Tree2, Compare) == FALSE)
	{
		cout << "No" << endl;
	}
	else
	{
		cout << "Yes" << endl;

	}

	/* 求两个的深度 */
	int t1_depth = Get_depth(Tree1);
	int t2_depth = Get_depth(Tree2);

	cout << t1_depth << endl;
	cout << t2_depth << endl;


	return 0;
}
