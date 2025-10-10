/*2351136 –≈03 ¿Ó ¢≈Ù*/
#include <stdio.h>
int main()
{
	int a = 1, b = 1, c;
	for (b; b <=9;b++) {
		for (a=1; a<=b; a++) {
			c = a * b;
			printf("%dx%d=%-4d", a, b, c);
			if (a == b) {
				printf("\n");
			}
		}
	}
	printf("\n");
	return 0;
}