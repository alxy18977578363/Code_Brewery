clc,clear
syms y(x)
y1 = diff(y,x);     % y的一阶导数

eqn = sqrt(1+y1^2) == 5*(1-x)*diff(y,x,2); % 微分方程
cond = [y(0)==0, y1(0)==0];
ySol = dsolve(eqn, cond);
disp(ySol);         % 这个解一共有两个分支，取决于你的船往y正负方向运动


% 为了满足题意，还应在微分方程结果后检查解的分支
ezplot(ySol(2),[0,0.9999]) % 符号求解时，得到两个分支，这里画出一个分支
y_limit=subs(ySol(2),x,1); % 求击中时乙舰行驶的距离
disp('最后的距离是')
y_limit=double(y_limit) % 把符号型数据化成浮点型数据
title('导弹攻击船只') % 不显示图形的标题