clc,clear
% 样本data
data = [1050 1100 1120 1250 1280];
alpha = 0.10; % 置信水平为0.9
% 由于服从正态分布
[muhat,~,muci] = normfit(data,alpha);

% 最终结果
disp(['样本均值：',num2str(muhat),' 小时']);
disp(['样本均值的置信区间：[',num2str(muci(1)),',',num2str(muci(2)),']']);