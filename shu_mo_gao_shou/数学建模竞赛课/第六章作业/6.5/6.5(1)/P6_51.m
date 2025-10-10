clc,clear

% 先定义初值
x0 = pi/2;      % 初始点
xspan = [x0 10];    % 上下区间
z0 = [2;-2/pi];     % y(pai/2) = 2,y'(pai/2)=-2/pi

% 利用ode45求解
[x,z] = ode45(@tjODE,xspan,z0);
y_numerical = z(:,1); % 由于y=z(1);

% 计算解析解
y_analytical = besselj(1/2, x);

figure;
plot(x, y_numerical, 'b-'); % 数值解（蓝色实线）
hold on;
plot(x, y_analytical, 'r--'); % 解析解（红色虚线）
xlabel('x'); ylabel('y(x)');
title('Comparison of Numerical and Analytical Solutions');
legend('Numerical (ode45)', 'Analytical (BesselJ_{1/2})');
grid on;
hold off;