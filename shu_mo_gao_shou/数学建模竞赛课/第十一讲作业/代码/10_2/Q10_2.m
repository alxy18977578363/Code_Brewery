clear; clc; close all;

% 1. 数据输入与预处理
years = 1984:2000;
investment_data = [
    0.71    0.49    0.41    0.51    0.46;
    0.40    0.49    0.44    0.57    0.50;
    0.55    0.56    0.48    0.53    0.49;
    0.62    0.93    0.38    0.53    0.47;
    0.45    0.42    0.41    0.54    0.47;
    0.36    0.37    0.46    0.54    0.48;
    0.55    0.68    0.42    0.54    0.46;
    0.62    0.90    0.38    0.56    0.46;
    0.61    0.99    0.33    0.57    0.43;
    0.71    0.93    0.35    0.66    0.44;
    0.59    0.69    0.36    0.57    0.48;
    0.41    0.47    0.40    0.54    0.48;
    0.26    0.29    0.43    0.57    0.48;
    0.14    0.16    0.43    0.55    0.47;
    0.12    0.13    0.45    0.59    0.54;
    0.22    0.25    0.44    0.58    0.52;
    0.71    0.49    0.41    0.51    0.46
];

% 2. 主成分分析
data_normalized = zscore(investment_data);
[coeff, score, latent, tsquared, explained] = pca(data_normalized);

% 3. 结果可视化
figure;
pareto(explained);
xlabel('主成分');
ylabel('解释方差比例 (%)');
title('主成分解释的方差比例');

figure;
biplot(coeff(:,1:2), 'scores', score(:,1:2), 'varlabels', ...
    {'无时滞','时滞一年','交付使用率','项目投产率','房屋竣工率'});
title('前两个主成分的载荷图');

% 4. 综合得分计算与排序
weighted_score = score(:,1)*explained(1)/100 + score(:,2)*explained(2)/100;
results = table(years', weighted_score, 'VariableNames', {'年份','综合得分'});
[~, sorted_idx] = sort(weighted_score, 'descend');
sorted_results = results(sorted_idx, :);

disp('投资效益综合得分排序:');
disp(sorted_results);

figure;
plot(years, weighted_score, 'o-', 'LineWidth', 2, 'MarkerSize', 8);
xlabel('年份');
ylabel('投资效益综合得分');
title('1984-2000年中国宏观投资效益趋势');
grid on;
xticks(years);
xtickangle(45);