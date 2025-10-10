clc,clear
%% 定义数量
M = 10000;                % 市场饱和值
lamda = 0.1;            % 兰塔的值
beta = 0.01;            % 贝塔
a = 50;                 % 广告费用
limited_time = 10;     % 广告限时

%% 建立模型
dsdt = @(t,s) - lamda*s + beta*a*(M-s);
s0 = 0;
tspan = [0 20];

%% 求解模型
[t1,s1] = ode45(@(t,s)dsdt(t,s),[0,limited_time],s0);
[t2,s2] = ode45(@(t,s) -lamda*s,[limited_time,tspan(end)],s1(end));

%% 绘图
figure
plot(t1,s1);
hold on
plot(t2,s2);
hold on
grid on