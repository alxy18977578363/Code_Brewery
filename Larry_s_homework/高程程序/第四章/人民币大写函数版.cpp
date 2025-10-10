/* 2351136 李盛鹏 信03 */
#include <iostream>
using namespace std;

/* 可根据需要添加相应的内容 */

/***************************************************************************
  函数名称：daxie
  功    能：输出大写的0~9
  输入参数：num，flag_of_zero
  返 回 值：void
  说    明：除本函数外，不允许任何函数中输出“零”-“玖”!!!!!!
***************************************************************************/
void daxie(int num, int flag_of_zero)
{
	/* 不允许对本函数做任何修改 */
	switch (num) {
		case 0:
			if (flag_of_zero)	//此标记什么意思请自行思考
				cout << "零";
			break;
		case 1:
			cout << "壹";
			break;
		case 2:
			cout << "贰";
			break;
		case 3:
			cout << "叁";
			break;
		case 4:
			cout << "肆";
			break;
		case 5:
			cout << "伍";
			break;
		case 6:
			cout << "陆";
			break;
		case 7:
			cout << "柒";
			break;
		case 8:
			cout << "捌";
			break;
		case 9:
			cout << "玖";
			break;
		default:
			cout << "error";
			break;
	}
}

/* 可根据需要自定义其它函数(也可以不定义) */

/***************************************************************************
  函数名称：judge1 ,judge2,judge3
  功    能：分别是千位，百位，十位的读零判断
  输入参数：a，b，c，d
  返 回 值：bool
  说    明：
***************************************************************************/

bool judge2(int a, int b, int c, int d)
{
	if (b == 0 && a != 0 && c + d != 0) {
		return 1;
	}
	else {
		return 0;
	}
}//百位读零

bool judge3(int a, int b, int c, int d)
{
	if (b != 0 && c == 0 && d != 0) {
		return 1;
	}
	else {
		return 0;
	}
}//十位读零




int main()
{
	/* 按需完成 */
	double x, y;
	while (1) {
		cout << "请输入[0-100亿)之间的数字:" << endl;
		cin >> x;
		y= x / 10 - int(x / 10);
		if (cin.good() == 0) {
			cin.clear();
			cin.ignore(1025, '\n');
			continue;
		}
		if (x >= 10000000000 || x < 0) {
			continue;
		}
		if (x >= 0 && x < 10000000000&&cin.good()) {
			break;
		}
		
	}//输入错误的处理

	cout << "大写结果是:" << endl;
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
	
	daxie(shiyi, 0);
	if (shiyi != 0) {
		cout << "拾";
	}

	daxie(yi, 0);
	if (shiyi + yi != 0) {
		cout << "亿";
	}
	//亿的变中文

	if (x > 10000000 && qianwan == 0&&baiwan+shiwan+wan!=0) {
		daxie(qianwan, 1);
	}
	if (x < 10000000 && qianwan == 0) {
		daxie(qianwan, 0);
	}
	if (qianwan != 0) {
		daxie(qianwan, 0);
	}
	if (qianwan != 0) {
		cout << "仟";
	}

    bool flag_of_zero = judge2(qianwan, baiwan, shiwan, wan);
	daxie(baiwan, flag_of_zero);
	if (baiwan != 0) {
		cout << "佰";
	}

	flag_of_zero = judge3(qianwan, baiwan, shiwan, wan);
	daxie(shiwan, flag_of_zero);
	if (shiwan != 0) {
		cout << "拾";
	}

	daxie(wan, 0);
	if (qianwan + baiwan+shiwan+wan != 0) {
		cout << "万";
	}
	//万变中文

	if (x > 1000 && qian == 0 && bai + shi + yuan != 0) {
		daxie(qian, 1);
	}
	if (x < 1000 && qian == 0) {
		daxie(qian, 0);
	}
	if (qian != 0) {
		daxie(qian, 0);
	}
	if (qian != 0) {
		cout << "仟";
	}


	flag_of_zero = judge2(qian, bai, shi, yuan);
	daxie(bai, flag_of_zero);
	if (bai != 0) {
		cout << "佰";
	}

	flag_of_zero = judge3(qian, bai, shi, yuan);
	daxie(shi, flag_of_zero);
	if (shi != 0) {
		cout << "拾";
	}

	if (x == 0) {
		daxie(yuan, 1);
	}

	daxie(yuan, 0);
	if (x >= 1||x==0) {
		cout << "圆";
	}
	//圆的读数

	if (jiao > 0) {
		daxie(jiao, 0);
		cout << "角";
	}
	if (jiao == 0&&fen!=0&&x>1) {
		daxie(jiao, 1);
	}
	//角的读数


	if (fen == 0 || (fen + jiao == 0)) {
		cout << "整" << endl;
	}

	if (fen != 0) {
		daxie(fen, 0);
		cout << "分" << endl;
	}
	

	return 0;
}