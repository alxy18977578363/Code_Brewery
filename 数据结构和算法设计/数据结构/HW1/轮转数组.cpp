#include<iostream>
using namespace std;

void rotate(int b[100000], int num, int times)
{
    if (num == 0 || times == 0)        return;
    int dst[100000];
    int distance = times % num;

    for (int i = 0; i < num; i++)
    {
        dst[(distance + i) % num] = b[i];
    }
    for (int i = 0; i < num; i++)
    {
        b[i] = dst[i];
    }
}

int main()
{
    int num = 0, times = 0;
    int a[100000] = { 0 };
    cin >> num >> times;
    for (int i = 0; i < num; i++)
    {
        cin >> a[i];
    }
    rotate(a, num, times);


    for (int i = 0; i < num; i++)
    {
        cout << a[i] << " ";
    }
}
