clc,clear
% 基础数值
d = 100;    % 河宽 (m)
v1 = 1;     % 水流速度 (m/s)
v2 = 2;     % 船速 (m/s)
k = v1 / v2;

%% 小船渡河问题数值解
% 初始条件
y0 = [0;0];

% 时间跨度
tspan = [0 100];

% 求解微分方程
[t,y] = ode45(@(t,y)boatODE(t,y,v1,v2,d),tspan,y0);

% 提取x(t)和y(t)
xt = y(:,1);
yt = y(:,2);

%% 求解解析解
x_analytic = linspace(1e-6, max(xt), 100); % 避免x=0
y_analytic = (d/2) * ( (x_analytic/d).^(1-k) - (x_analytic/d).^(1+k) );

%% 绘制最后的图
figure
plot(xt, yt, 'b-', 'LineWidth', 2); % 数值解
hold on
plot(x_analytic, y_analytic, 'r--', 'LineWidth', 2);
hold on
xlabel('x');
ylabel('y');
title('小船过河');
legend('数值解','解析解')
grid on

%% 求解
crossing_index = find(yt >= d,1);
if ~isempty(crossing_index)
    crossing_time = t(crossing_index)
else
    crossing_time = NaN
end

disp('最后的渡河时间为')
disp(crossing_time)