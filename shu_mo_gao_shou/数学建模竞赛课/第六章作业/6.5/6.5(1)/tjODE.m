function dydx = tjODE(x,z)
    n = 1/2;        % 题目要求n=1/2
    dydx = [z(2);
            -z(2)/x - (x^2-n^2)*z(1)/x^2];
end