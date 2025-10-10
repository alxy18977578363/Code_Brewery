/* 信03 2351136 李盛鹏 */
#include <iostream>
#include<windows.h>
#include<time.h>

#define ROW 10
#define COL 26
#define mine_num 50
using namespace std;

//形成雷的函数
void mine_set(char map[][COL])
{
	int rand_x, rand_y;

	srand(time(NULL)); //使用srand()函数设置随机数种子

	for (int count = 0; count < mine_num; count++) {
		int rand_x = rand() % COL;
		int rand_y = rand() % ROW;

		//如果这个位置有地雷，那就回头再放雷
		if (map[rand_y][rand_x] == '*') {
			count--;
			continue;
		}
		else
		map[rand_y][rand_x] = '*'; // 假设 '*' 表示地雷

	}


		
}

//描述扫雷空间
void map_show(char map[][COL])
{
	for (int y = 0; y < ROW; y++) {
		for (int x = 0; x < COL; x++) {
			if (map[y][x] == '*')
				cout << map[y][x] << " ";
			else
				cout << (int)(map[y][x]) << " ";

		}
		cout << endl;
	}
}

//9方格排雷
int search_nine(char map[][COL],int x,int y)
{
	int count = 0, tamp_x = x, tamp_y = y;//用暂时的变量记录进来的x，y值，用count来数雷

	for (y=tamp_y-1; y <= tamp_y + 1; y++) {
		for (x=tamp_x-1; x <= tamp_x + 1; x++) {
			if (map[y][x] == '*') 
				count++;
		}
	}
	return count;
}

//6方格排雷(上下左右银边)
int search_six(char map[][COL], int x, int y)
{
	int count = 0, tamp_x = x, tamp_y = y;//用暂时的变量记录进来的x，y值，用count来数雷

	if (x == 0) {
		for (y=tamp_y-1; y <= tamp_y + 1; y++) {
			for (x=tamp_x; x <= tamp_x + 1; x++) {
				if (map[y][x] == '*')
					count++;
			}
		}
	}
	else if (x == COL - 1) {
		for (y = tamp_y - 1; y <= tamp_y + 1; y++) {
			for (x = tamp_x-1; x <= tamp_x; x++) {
				if (map[y][x] == '*')
					count++;
			}
		}
	}
	else if (y == 0) {
		for (y = tamp_y; y <= tamp_y+1; y++) {
			for (x = tamp_x - 1; x <= tamp_x+1; x++) {
				if (map[y][x] =='*')
					count++;
			}
		}
	}
	else if (y == ROW - 1) {
		for (y = tamp_y-1; y <= tamp_y; y++) {
			for (x = tamp_x - 1; x <= tamp_x + 1; x++) {
				if (map[y][x] == '*')
					count++;
			}
		}
	}
	return count;
}

//4方格排雷（四个金角）
int search_four(char map[][COL], int x, int y)
{
	int count = 0, tamp_x = x, tamp_y = y;//用暂时的变量记录进来的x，y值，用count来数雷

	if (x == 0 && y == 0) {
		for (y = tamp_y; y <= tamp_y + 1; y++) {
			for (x = tamp_x; x <= tamp_x + 1; x++) {
				if (map[y][x] == '*')
					count++;
			}
		}
	}//左上角
	else if (x == COL - 1 && y == 0) {
		for (y = tamp_y; y <= tamp_y + 1; y++) {
			for (x = tamp_x - 1; x <= tamp_x; x++) {
				if (map[y][x] == '*')
					count++;
			}
		}
	}//右上角
	else if (x == 0 && y == ROW - 1) {
		for (y = tamp_y - 1; y <= tamp_y; y++) {
			for (x = tamp_x; x <= tamp_x + 1; x++) {
				if (map[y][x] == '*')
					count++;
			}
		}
	}//左下角
	else if (x == COL - 1&&y==ROW-1) {
		for (y = tamp_y - 1; y <= tamp_y; y++) {
			for (x = tamp_x - 1; x <= tamp_x; x++) {
				if (map[y][x] == '*')
					count++;
			}
		}
	}//右下角
	return count;
}

//为雷周围区域赋值
void num_input(char map[][COL])
{
	for (int x = 0; x < COL; x++) {
		for (int y = 0; y < ROW; y++) {
			if (map[y][x] != '*') {

				//为四个金角赋值
				if ((x == 0 && y == 0) || (x == COL - 1 && y == 0) || (x == 0 && y == ROW - 1) || (x == COL - 1 && y == ROW - 1)) {
					map[y][x] = search_four(map, x, y);
				}
				else if ((x == 0) || (x == COL - 1) || (y == 0) || (y == ROW - 1)) {
					map[y][x] = search_six(map, x, y);
				}
				else {
					map[y][x] = search_nine(map, x, y);
				}
			}
		}
	}
}

int main()
{
	//定义一个字符数组作为该扫雷空间
	char map[ROW][COL] = {0};

	//先形成雷阵
	mine_set(map);

	//为周围有雷的区域赋值
	num_input(map);

	//输出这个扫雷盘
	map_show(map);
	
	return 0;
}