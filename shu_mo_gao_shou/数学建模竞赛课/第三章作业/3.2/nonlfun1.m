% 下面是非线性约束
function [c,ceq] = nonlfun1(delta)  % 决策变量是六个飞机的变化角度
    % 输入参数
    x = [150,85,150,145,130,0]';     % 起始的x坐标
    y = [140,85,155,50,150,0]';      % 起始的y坐标
    theta0 = [243,236,220.5,159,230,52]';    % 初始的角度
    theta = theta0 + delta;
    v = 800;        % 速度800km\h
    
    k = 1;
    % 循环，将各个判别式写出来
    for i = 1:5
        for j = i+1:6
            % 计算A_ij, B_ij, C_ij
            A = 4*v^2 * (sind((theta(i)-theta(j))/2))^2; % 根据theta计算A
            B = 2*v *( (x(i)-x(j))*(cosd(theta(i))-cosd(theta(j))) + (y(i)-y(j))*(sind(theta(i))-sind(theta(j))) ); % 根据theta计算B
            C = (x(i)-x(j))^2 + (y(i)-y(j))^2 - 64; % 根据theta计算C
            
            c(k) = B^2 -4*A*C;
            k = k + 1;
     
        end
    end

    ceq = [];       % 这题没有非线性等式约束
end