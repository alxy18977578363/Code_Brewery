/* 信03 2351136 李盛鹏 */
#pragma once

/* ------------------------------------------------------------------------------------------------------

	 本文件功能：
	1、为了保证 hanoi_main.cpp/hanoi_menu.cpp/hanoi_multiple_solutions.cpp 能相互访问函数的函数声明
	2、一个以上的cpp中用到的宏定义（#define）或全局只读（const）变量，个数不限
	3、可以参考 cmd_console_tools.h 的写法（认真阅读并体会）
   ------------------------------------------------------------------------------------------------------ */
#include <iostream>
#include <iomanip>
#include <ctime>
#include <cmath>
#include <cstdio>
#include <conio.h>
#include <Windows.h>

#define base_x 30
#define base_y 15
#define min_y 1
#define min_x 1
extern const int N;


extern int A[];
extern int B[];
extern int C[];
extern int i;
extern int topA;
extern int topB;
extern int topC;
extern int i_speed;

int my_menu();
void my_pause();
int Selection(int i_speed);
void my_tower(int choice);
void initial(int n, char src, char tmp, char dst, int choice);
void initial_tower(int choice);
void printshow(int A[], int B[], int C[], char src, char dst, char n);
void my_move(char src, char dst);
void hanoi(int n, char src, char tmp, char dst,int choice);
void hanoicase(int n, char src, char tmp, char dst, int choice);
void wait_for_enter();
int input_n();
char input_src();
char input_dst(char src);
char input_tmp(char src, char dst);
int input_i_speed();
void tower_setup();
void ring_setup(int n, char src);
void main_case(int choice);
void ring_move_up(int n, char src,int choice);
void ring_move_parallel(int n, char src, char dst,int choice);
void ring_move_down(int n, char dst,int choice);
void hanoi_game(int choice, char game_dst, int n);
bool ring_exist(char src);
void game_move(char src, char dst);
bool ring_can_move(char src, char dst);
void ring_move(int n, char src, char dst,int choice);