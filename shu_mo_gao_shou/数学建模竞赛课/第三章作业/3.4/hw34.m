clc
clear all
% 定义目标函数为fun1，非线性不等式/等式约束为fun2
A = [-1,-2,0];
b = [-1];

% 变量约束
lb = [0,-Inf , -Inf];

% 求解
x0 = [0,0,0];
[x_opt, fval] = fmincon(@fun1, x0, A, b, [], [], lb, [], @fun2);

disp('本题的x取值为：')
disp(x_opt);
disp('本题的最优解为:');
disp(-fval);