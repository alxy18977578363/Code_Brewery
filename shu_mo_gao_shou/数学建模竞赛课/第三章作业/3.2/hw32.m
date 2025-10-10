clc
clear all 

%% 求解非线性规划问题
delta = [0 0 0 0 0 0];  % 初始值
lb = -30*ones(6,1);   % 下限
ub = 30*ones(6,1);    % 上限
[x,fval] = fmincon(@fun1,rand(6,1),[],[],[],[],lb,ub,@nonlfun1);

disp(x);
disp(fval);     % 这里是角度制的平方和