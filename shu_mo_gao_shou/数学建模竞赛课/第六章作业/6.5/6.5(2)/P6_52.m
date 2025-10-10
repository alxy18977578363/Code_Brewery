clc,clear

% 输入初始值
z0 = [1;0];     % 也就是y(0) = 1,y'(0) =0
tspan = [0 10];
[x,z] = ode45(@myODE,tspan,z0);

% 将提取的结果绘图
y = z(:,1);         % 因为z(1) = y
plot(x,y);
xlabel('x');    ylabel('y(x)');
grid on
