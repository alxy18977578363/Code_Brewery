/* 信03 2351136 李盛鹏 */
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include<stdbool.h>
#include<string.h>

//可按需增加需要的头文件

const char chnstr[] = "零壹贰叁肆伍陆柒捌玖"; /* 所有输出大写 "零" ~ "玖" 的地方，只允许从这个数组中取值 */
char result[256];  /* 除result外，不再允许定义任何形式的全局变量 */

/* --允许添加需要的函数 --*/
void Change(int num)
{
	if (num >= 0 && num <= 9) {
		result[strlen(result)] = chnstr[2*num];
		result[strlen(result)] = chnstr[2 * num+1];
	}
	return;
}

/***************************************************************************
  函数名称：main
  功    能：判断输入是否错误，分解数字
  输入参数：
  返 回 值：int
  说    明：
***************************************************************************/
int main()
{
    /* --允许添加需要的内容 --*/
	double x, y;
	char connection[] = "仟佰拾万亿圆角分整";
	while (1) {
		printf("请输入[0-100亿)之间的数字:\n");
		int ret=scanf("%lf", &x);
		y = x / 10 - (int)(x / 10);

		if (ret==0) {
			while (getchar() != '\n')
				;
			continue;
		}
		else if (x >= 10000000000 || x < 0) {
			continue;
		}
		else {
			break;
		}

	}//输入错误的处理

	printf("大写结果是:\n");
	int  shiyi, yi, qianwan, baiwan, shiwan, wan, qian, bai, shi, yuan, jiao, fen;
	shiyi = ((int)(x / 1000000000) % 10);
	yi = ((int)(x / 100000000) % 10);
	qianwan = ((int)(x / 10000000) % 10);
	baiwan = ((int)(x / 1000000) % 10);
	shiwan = ((int)(x / 100000) % 10);
	wan = ((int)(x / 10000) % 10);
	qian = ((int)(x / 1000) % 10);
	bai = ((int)(x / 100) % 10);
	shi = ((int)(x / 10) % 10);
	yuan = ((int)(y * 10 + 0.001) % 10);
	jiao = ((int)(y * 100 + 0.001) % 10);
	fen = ((int)(y * 1000 + 0.001) % 10);//分离每一位数字

	//在可能出现零的地方判断是否读0。
	bool _qianwan = (shiyi + yi) != 0 && baiwan != 0;
	bool _baiwan= (shiyi + yi+qianwan) != 0 && shiwan != 0;
	bool _shiwan = (shiyi + yi + qianwan + baiwan) != 0 && wan != 0;
	bool _qian = (shiyi + yi + qianwan + baiwan + shiwan + wan) != 0 && bai != 0;
	bool _bai= (shiyi + yi + qianwan + baiwan + shiwan + wan+qian) != 0 && shi != 0;
	bool _shi= (shiyi + yi + qianwan + baiwan + shiwan + wan+qian+bai) != 0 && yuan != 0;
	bool _jiao = (shiyi + yi + qianwan + baiwan + shiwan + wan + qian + bai+shi+yuan) != 0 && fen != 0;
	
	
	//往里面赋值

	
	
	//十亿
	if (shiyi) {
		Change(shiyi);
		result[strlen(result)] = connection[2*2];
		result[strlen(result)] = connection[2 * 2+1];
	}

	//亿
	if (yi) {
		Change(yi);
	}
	if (yi + shiyi != 0) {
		result[strlen(result)] = connection[4 * 2];
		result[strlen(result)] = connection[4 * 2 + 1];
	}
	
	//千万
	if (!qianwan&&_qianwan) {
		Change(qianwan);
	}
	else if(qianwan){
		Change(qianwan);
		result[strlen(result)] = connection[0*2];
		result[strlen(result)] = connection[0 * 2+1];
	}
	
	//百万
	if (!baiwan && _baiwan) {
		Change(baiwan);
	}
	else if(baiwan){
		Change(baiwan);
		result[strlen(result)] = connection[1*2];
		result[strlen(result)] = connection[1*2+1];
	}

	//十万
	if (!shiwan && _shiwan) {
		Change(shiwan);
	}
	else if(shiwan){
		Change(shiwan);
		result[strlen(result)] = connection[2*2];
		result[strlen(result)] = connection[2*2+1];
	}

	//万
	if (wan) {
		Change(wan);
	}
	if (qianwan + baiwan + shiwan + wan != 0) {
		result[strlen(result)] = connection[3 * 2];
		result[strlen(result)] = connection[3 * 2 + 1];
	}

	//仟
	if (!qian && _qian) {
		Change(qian);
	}
	else if(qian){
		Change(qian);
		result[strlen(result)] = connection[0*2];
		result[strlen(result)] = connection[0*2+1];
	}

	//佰
	if (!bai && _bai) {
		Change(bai);
	}
	else if(bai){
		Change(bai);
		result[strlen(result)] = connection[1*2];
		result[strlen(result)] = connection[1*2+1];
	}

	//拾
	if (!shi && _shi) {
		Change(shi);
	}
	else if(shi){
		Change(shi);
		result[strlen(result)] = connection[2*2];
		result[strlen(result)] = connection[2*2+1];
	}

	//圆
	if (x == 0) {
		Change(yuan);
	}
	if (yuan) {
		Change(yuan);
	}
	if (shiyi + yi + qianwan + baiwan + shiwan + wan + qian + bai + shi + yuan!=0||x==0) {
		result[strlen(result)] = connection[5 * 2];
		result[strlen(result)] = connection[5 * 2 + 1];
	}

	//角
	if (!jiao && _jiao) {
		Change(jiao);
	}
	if (jiao) {
		Change(jiao);
		result[strlen(result)] = connection[6*2];
		result[strlen(result)] = connection[6 * 2+1];
	}
	//整
	if (fen == 0) {
		result[strlen(result)] = connection[8*2];
		result[strlen(result)] = connection[8*2+1];
	}

	//分
	if (fen) {
		Change(fen);
		result[strlen(result)] = connection[7*2];
		result[strlen(result)] = connection[7*2+1];
	}


    printf("%s\n", result);  /* 转换得到的大写结果，只允许用本语句输出，其它地方不允许以任何形式对大写结果进行全部/部分输出 */
    return 0;
}