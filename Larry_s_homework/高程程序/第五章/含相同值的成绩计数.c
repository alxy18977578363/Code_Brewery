/* 2351136 李盛鹏 信03 */
#define _CRT_SECURE_NO_WARNINGS
#include<stdbool.h>
#include<stdio.h>
#define N 1000

int main()
{
	//完成对成绩的输入
	printf("请输入成绩（最多1000个），负数结束输入\n");
	int form[N], person = 0, person2, num=0;
	for (person = 0; person < N; person++) {
		int number = 0;
		int ret=scanf("%d", &number);

		if (number >= 0 && number <= 100) {
			num++;
			form[person] = number;
		}
		if (number < 0 || ret != 1) {
			break;
		}
		
		
	}


	//输出原数组
	printf("输入的数组为:\n");
	for (person = 0; person < num; person++) {
		int num10 = 0;
		for (person = 0; person < num; person++) {

			printf("%d ", form[person]);
			num10++;
			if (num10 % 10 == 0) {
				num10 = 0;
				printf("\n");
			}
		}
		printf("\n");
	}


	//调整次序
	for (person = 0; person < num; person++) {
		for (person2 = person; person2 < num; person2++) {
			if (form[person2] >= form[person]) {
				int tamp = form[person];
				form[person] = form[person2];
				form[person2] = tamp;
			}
		}
	}
	

	//分数及对应人的关系
	printf("分数与人数的对应关系为:\n");
	int i = 1;
	for (person = 0; person < num; person+=i) {
		i = 1;
		for (person2 = person+1; person2< num; person2++) {
			if (form[person2] == form[person]) {
				i++;
			}
		}
		printf("%d %d\n", form[person], i);
	}

	return 0;
}

