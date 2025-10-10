clc,clear
data = importdata('data.txt');
data = data(:);
mu = mean(data);
sig = std(data);
[h, p, stats] = chi2gof(data, 'CDF', @(z)normcdf(z, mean(data), std(data)), 'NParams', 2);
disp(['p值: ', num2str(p)]);
if h == 0
    disp('数据服从正态分布');
else
    disp('数据不服从正态分布');
end