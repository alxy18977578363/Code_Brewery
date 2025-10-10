/*2351136 ÐÅ03 ÀîÊ¢Åô*/
#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
int main()
{
	printf("ÇëÊäÈë[0-100ÒÚ)Ö®¼äµÄÊý×Ö:\n");
	double a, b;
	scanf("%lf", &a);
	printf("´óÐ´½á¹ûÊÇ:\n");
	int  c, d, e, f, g, h, i, j, k, l, m, n;
	b = a / 10 - (int)(a / 10);
	c = ((int)(a / 1000000000) % 10);
	d = ((int)(a / 100000000) % 10);
	e = ((int)(a / 10000000) % 10);
	f = ((int)(a / 1000000) % 10);
	g = ((int)(a / 100000) % 10);
	h = ((int)(a / 10000) % 10);
	i = ((int)(a / 1000) % 10);
	j = ((int)(a / 100) % 10);
	k = ((int)(a / 10) % 10);
	l = ((int)(b * 10 + 0.001) % 10);
	m = ((int)(b * 100 + 0.001) % 10);
	n = ((int)(b * 1000 + 0.001) % 10);//·ÖÀëÃ¿Ò»Î»Êý×Ö

	if (c != 0) {
		switch (c) {
			case 1:
				printf("Ò¼Ê°");
				break;
			case 2:
				printf("·¡Ê°");
				break;
			case 3:
				printf("ÈþÊ°");
				break;
			case 4:
				printf("ËÁÊ°");
				break;
			case 5:
				printf("ÎéÊ°");
				break;
			case 6:
				printf("Â½Ê°");
				break;
			case 7:
				printf("ÆâÊ°");
				break;
			case 8:
				printf("°ÆÊ°");
				break;
			case 9:
				printf("¾ÁÊ°");
				break;
		}
	}
	if (d != 0) {
		switch (d) {
			case 1:
				printf("Ò¼");
				break;
			case 2:
				printf("·¡");
				break;
			case 3:
				printf("Èþ");
				break;
			case 4:
				printf("ËÁ");
				break;
			case 5:
				printf("Îé");
				break;
			case 6:
				printf("Â½");
				break;
			case 7:
				printf("Æâ");
				break;
			case 8:
				printf("°Æ");
				break;
			case 9:
				printf("¾Á");
				break;
		}
	}
	if (c != 0 || d != 0) {
		printf("ÒÚ");
	}//ÒÚÎ»µÄÅÐ¶¨


	if (e != 0) {
		switch (e) {
			case 1:
				printf("Ò¼Çª");
				break;
			case 2:
				printf("·¡Çª");
				break;
			case 3:
				printf("ÈþÇª");
				break;
			case 4:
				printf("ËÁÇª");
				break;
			case 5:
				printf("ÎéÇª");
				break;
			case 6:
				printf("Â½Çª");
				break;
			case 7:
				printf("ÆâÇª");
				break;
			case 8:
				printf("°ÆÇª");
				break;
			case 9:
				printf("¾ÁÇª");
				break;
		}
	}
	if (a > 10000000 && e == 0) {
		if (f == 0 || g == 0 || h == 0) {
			if (f == 0 && g == 0 && h == 0) {

			}
			else {
				printf("Áã");
			}
		}
	}
	if (f != 0) {
		switch (f) {
			case 1:
				printf("Ò¼°Û");
				break;
			case 2:
				printf("·¡°Û");
				break;
			case 3:
				printf("Èþ°Û");
				break;
			case 4:
				printf("ËÁ°Û");
				break;
			case 5:
				printf("Îé°Û");
				break;
			case 6:
				printf("Â½°Û");
				break;
			case 7:
				printf("Æâ°Û");
				break;
			case 8:
				printf("°Æ°Û");
				break;
			case 9:
				printf("¾Á°Û");
				break;
		}
	}
	if (e != 0 && f == 0) {
		if (g == 0 && h == 0) {

		}
		else {
			printf("Áã");
		}
	}
	if (g != 0) {
		switch (g) {
			case 1:
				printf("Ò¼Ê°");
				break;
			case 2:
				printf("·¡Ê°");
				break;
			case 3:
				printf("ÈþÊ°");
				break;
			case 4:
				printf("ËÁÊ°");
				break;
			case 5:
				printf("ÎéÊ°");
				break;
			case 6:
				printf("Â½Ê°");
				break;
			case 7:
				printf("ÆâÊ°");
				break;
			case 8:
				printf("°ÆÊ°");
				break;
			case 9:
				printf("¾ÁÊ°");
				break;
		}
	}
	if (f != 0 && g == 0 && h != 0) {
		printf("Áã");
	}
	if (h != 0) {
		switch (h) {
			case 1:
				printf("Ò¼");
				break;
			case 2:
				printf("·¡");
				break;
			case 3:
				printf("Èþ");
				break;
			case 4:
				printf("ËÁ");
				break;
			case 5:
				printf("Îé");
				break;
			case 6:
				printf("Â½");
				break;
			case 7:
				printf("Æâ");
				break;
			case 8:
				printf("°Æ");
				break;
			case 9:
				printf("¾Á");
				break;
		}
	}
	if (e != 0 || f != 0 || g != 0 || h != 0) {
		printf("Íò");
	}//ÍòµÄÅÐ¶Ï

	if (i != 0) {
		switch (i) {
			case 1:
				printf("Ò¼Çª");
				break;
			case 2:
				printf("·¡Çª");
				break;
			case 3:
				printf("ÈþÇª");
				break;
			case 4:
				printf("ËÁÇª");
				break;
			case 5:
				printf("ÎéÇª");
				break;
			case 6:
				printf("Â½Çª");
				break;
			case 7:
				printf("ÆâÇª");
				break;
			case 8:
				printf("°ÆÇª");
				break;
			case 9:
				printf("¾ÁÇª");
				break;
		}
	}
	if (a > 1000 && i == 0) {
		if (j == 0 || k == 0 || l == 0) {
			if (j == 0 && k == 0 && l == 0) {

			}
			else {
				printf("Áã");
			}
		}
	}
	if (j != 0) {
		switch (j) {
			case 1:
				printf("Ò¼°Û");
				break;
			case 2:
				printf("·¡°Û");
				break;
			case 3:
				printf("Èþ°Û");
				break;
			case 4:
				printf("ËÁ°Û");
				break;
			case 5:
				printf("Îé°Û");
				break;
			case 6:
				printf("Â½°Û");
				break;
			case 7:
				printf("Æâ°Û");
				break;
			case 8:
				printf("°Æ°Û");
				break;
			case 9:
				printf("¾Á°Û");
				break;
		}
	}
	if (i != 0 && j == 0) {
		if (k == 0 && l == 0) {

		}
		else {
			printf("Áã");
		}
	}
	if (k != 0) {
		switch (k) {
			case 1:
				printf("Ò¼Ê°");
				break;
			case 2:
				printf("·¡Ê°");
				break;
			case 3:
				printf("ÈþÊ°");
				break;
			case 4:
				printf("ËÁÊ°");
				break;
			case 5:
				printf("ÎéÊ°");
				break;
			case 6:
				printf("Â½Ê°");
				break;
			case 7:
				printf("ÆâÊ°");
				break;
			case 8:
				printf("°ÆÊ°");
				break;
			case 9:
				printf("¾ÁÊ°");
				break;
		}
	}
	if (j != 0 && k == 0 && l != 0) {
		printf("Áã");
	}
	if (l != 0) {
		switch (l) {
			case 1:
				printf("Ò¼");
				break;
			case 2:
				printf("·¡");
				break;
			case 3:
				printf("Èþ");
				break;
			case 4:
				printf("ËÁ");
				break;
			case 5:
				printf("Îé");
				break;
			case 6:
				printf("Â½");
				break;
			case 7:
				printf("Æâ");
				break;
			case 8:
				printf("°Æ");
				break;
			case 9:
				printf("¾Á");
				break;
		}
	}
	if (a == 0) {
		printf("ÁãÔ²");
	}
	if (a >= 1) {
		printf("Ô²");
	}
	if (m == 0 && n == 0) {
		printf("Õû\n");
	}//Ô²µÄÅÐ¶Ï

	if (m != 0) {
		switch (m) {
			case 1:
				printf("Ò¼½Ç");
				break;
			case 2:
				printf("·¡½Ç");
				break;
			case 3:
				printf("Èþ½Ç");
				break;
			case 4:
				printf("ËÁ½Ç");
				break;
			case 5:
				printf("Îé½Ç");
				break;
			case 6:
				printf("Â½½Ç");
				break;
			case 7:
				printf("Æâ½Ç");
				break;
			case 8:
				printf("°Æ½Ç");
				break;
			case 9:
				printf("¾Á½Ç");
				break;
		}
	}
	if (m != 0 && n == 0) {
		printf("Õû\n");
	}
	if (a > 0.1 && m == 0 && n != 0) {
		printf("Áã");//½ÇµÄÅÐ¶Ï
	}
	if (n != 0) {
		switch (n) {
			case 1:
				printf("Ò¼·Ö\n");
				break;
			case 2:
				printf("·¡·Ö\n");
				break;
			case 3:
				printf("Èþ·Ö\n");
				break;
			case 4:
				printf("ËÁ·Ö\n");
				break;
			case 5:
				printf("Îé·Ö\n");
				break;
			case 6:
				printf("Â½·Ö\n");
				break;
			case 7:
				printf("Æâ·Ö\n");
				break;
			case 8:
				printf("°Æ·Ö\n");
				break;
			case 9:
				printf("¾Á·Ö\n");
				break;
		}
	}//·ÖµÄÅÐ¶Ï
	return 0;
}