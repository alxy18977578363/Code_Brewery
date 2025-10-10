% 定义微分方程
function dydx = myODE(x,z)      % 用z代替y进行求导结果
    dydx = [z(2); -z(1)*cos(x)];
end