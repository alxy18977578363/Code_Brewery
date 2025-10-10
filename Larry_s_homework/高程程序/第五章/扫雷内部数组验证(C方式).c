/* 2351136 李盛鹏 信03 */
/* 2351134 吕奎辰  2351135 钟康华 2352036 雷达 2351120 韦森尹 2351446 刘昱辰 2353606 王瀚威 2353125 郑凯博 */
#define _CRT_SECURE_NO_WARNINGS
#include<stdbool.h>
#include<stdio.h>
#define ROW 10
#define COL 26
#define mine_num 50

//检验雷函数
bool mine_inspection(char map[][COL])
{
	int count = 0;
	bool mine_enough = false;
	//历遍整个数组，找出的*不够mine_num则输出错误1
	for (int y = 0; y < ROW; y++) {
		for (int x = 0; x < COL; x++) {
			if (map[y][x] == '*') {
				count++;
			}	
		}
	}

	//如果不够雷，输出错误。够雷，返回真。
	if(count==mine_num){
		mine_enough = true;
	}
	return mine_enough;
}

bool map_compare(char map[][COL], int x, int y,int count)
{
	//比较一下是否和给的一样
	if (count == map[y][x])
		return true;
	else
		return false;
}

//9方格排雷
bool judge_nine(char map[][COL], int x, int y)
{
	int count = 0;//用count来数雷

	//数一下有多少雷
	for (int i=y-1; i<=y + 1; i++) {
		for (int j = x - 1; j <= x + 1; j++) {
			if (map[i][j] == '*')
				count++;
		}
	}
	
	return map_compare(map, x, y, count);
}


//6方格排雷(上下左右银边)
bool judge_six(char map[][COL], int x, int y)
{
	int count = 0;//用count来数雷

	if (x == 0) {
		for (int i = y- 1; i <= y+1; i++) {
			for (int j = x; j <= x + 1; j++) {
				if (map[i][j] == '*')
					count++;
			}
		}
	}
	else if (x == COL - 1) {
		for (int i = y - 1; i<= y + 1; i++) {
			for (int j = x - 1; j <= x; j++) {
				if (map[i][j] == '*')
					count++;
			}
		}
	}
	else if (y == 0) {
		for (int i = y; i <= y + 1; i++) {
			for (int j = x - 1; j <=x + 1; j++) {
				if (map[i][j] == '*')
					count++;
			}
		}
	}
	else if (y == ROW - 1) {
		for (int i = y - 1;i <= y; i++) {
			for (int j = x - 1; j <= x + 1; j++) {
				if (map[i][j] == '*')
					count++;
			}
		}
	}
	return map_compare(map, x, y, count);
}

//4方格排雷（四个金角）
bool judge_four(char map[][COL], int x, int y)
{
	int count = 0;// 用count来数雷

	if (x == 0 && y == 0) {
		for (int i =y; i <=y + 1; i++) {
			for (int j = x; j <= x + 1; j++) {
				if (map[i][j] == '*')
					count++;
			}
		}
	}//左上角
	else if (x == COL - 1 && y == 0) {
		for (int i = y; i <= y + 1; i++) {
			for (int j = x - 1; j <= x; j++) {
				if (map[i][j] == '*')
					count++;
			}
		}
	}//右上角
	else if (x == 0 && y == ROW - 1) {
		for (int i = y - 1; i <= y; i++) {
			for (int j = x; j <= x + 1; j++) {
				if (map[i][j] == '*')
					count++;
			}
		}
	}//左下角
	else if (x == COL - 1 && y == ROW - 1) {
		for (int i = y - 1; i<= y; i++) {
			for (int j = x - 1; j <= x; j++) {
				if (map[i][j] == '*')
					count++;
			}
		}
	}//右下角
	return map_compare(map, x, y, count);
}


//检验周围雷数量准不准的函数
bool mine_num_true(char map[][COL])
{
	bool my_accuracy = true;

	//历遍每一个不是雷的位置，按照位置特性带入不同的judge函数，一旦找到一个不对的就停止循环
	for (int y = 0; y < ROW - 1&& my_accuracy; y++) {
		for (int x = 0; x < COL - 1&& my_accuracy; x++) {
			if (map[y][x] != '*') {
				//为四个金角判断
				if ((x == 0 && y == 0) || (x == COL - 1 && y == 0) || (x == 0 && y == ROW - 1) || (x == COL - 1 && y == ROW - 1)) {
					my_accuracy = judge_four(map, x, y);
				}
				else if ((x == 0) || (x == COL - 1) || (y == 0) || (y == ROW - 1)) {
					my_accuracy = judge_six(map, x, y);
				}
				else {
					my_accuracy = judge_nine(map, x, y);
				}
			}
		}
	}

	return my_accuracy;
}


//main 函数,处理文本并且为数组赋值
int main()
{
	char map[ROW][COL] = {'0'};
	for (int y = 0; y < ROW; y++) {
		for (int x = 0; x < COL; x++) {
			map[y][x] = getchar();

			//排除掉空格和回车
			while(map[y][x] == ' ' || map[y][x] == '\n') {
				map[y][x] = getchar();
			}
		}
	}

	//将每个不是雷的地方都减去字符0，后面转int输出保证其正确
	for (int y = 0; y < ROW; y++) {
		for (int x = 0; x < COL; x++) {
			if (map[y][x] != '*') {
				map[y][x] -= '0';
			}
		}
	}

	//进行内部数组检查
	if (!mine_inspection(map)) {
		printf("错误1\n");
	}
	else if (!mine_num_true(map)) {
		printf("错误2\n");
	}
	if (mine_inspection(map) && mine_num_true(map)) {
		printf("正确\n");
	}


	return 0;
}