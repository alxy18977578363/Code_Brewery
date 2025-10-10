% 目标函数，输入变化的角度delta，求其平方和
function f = fun1(delta);
    f = sum(delta.^2);
end