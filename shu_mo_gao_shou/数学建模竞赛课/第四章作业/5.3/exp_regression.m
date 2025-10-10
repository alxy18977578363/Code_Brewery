% 根据题意将数据输入
x = [1 2 3 4 5 6 7 8];
yi = [15.3 20.5 27.4 36.6 49.1 65.6 87.87 117.6];

%% 为了使用最小二乘法，应该先将其化作线性形式
% 根据建模内容,Y = A + Bx。因此A的列向量为全1，B的列向量为x取值
Y = log(yi);
M = [ones(length(x),1),x'];

% 反斜杠用于求解线性最小二乘法
solution = M\Y';
A = solution(1);
B = solution(2);

%% 由 y = ae^bx可得
a = exp(A);
b = B;

% 生成拟合曲线
x_fit = 1:0.1:8;
y_fit = a*exp(b*x_fit);

%% 绘制结果
figure
scatter(x, yi, 'o', 'MarkerFaceColor', 'b');  % 绘制原始数据点
hold on
plot(x_fit,y_fit,'r-','LineWidth',2)
xlabel('x'),ylabel('y')
legend('原始数据','拟合曲线','Location','northwest')
title('最小二乘法指数拟合')
grid on