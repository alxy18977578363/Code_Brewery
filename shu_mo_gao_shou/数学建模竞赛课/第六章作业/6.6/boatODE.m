function dydx = boatODE(t,y,v1,v2,d)
% 构造d[x;y]/dt = [dx/dt,dy/dt],y是状态
    x = y(1);
    y_pos = y(2);
    fun = sqrt(x^2 + (d - y_pos)^2);
    dxdt = v1 - v2*x/fun;
    dydt = v2 * (d - y_pos) / fun;
    dydx = [dxdt;dydt];
end