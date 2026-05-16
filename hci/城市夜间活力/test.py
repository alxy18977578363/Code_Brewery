from graphviz import Digraph

# 1. 订单主表
dot1 = Digraph('订单主表', format='png', node_attr={'shape': 'record', 'fontname':'Microsoft YaHei'}, edge_attr={'fontname':'Microsoft YaHei'})
dot1.attr(rankdir='TB', size='8,8')

dot1.node('order_main', '''{
订单主表（业务核心表）|
{<id>订单标识信息|
  order_id：订单唯一编号\n
  poi_id：商家/门店唯一编号
}|
{<base>商家基础信息|
  poi_name：商家名称\n
  category_lv1：一级品类\n
  category_lv2：二级品类
}|
{<geo>地理空间信息|
  city：城市\n
  district：区县\n
  lng：经度\n
  lat：纬度
}|
{<trade>订单交易信息|
  order_time：下单时间\n
  order_amount：订单金额(元)\n
  payment_type：支付方式
}|
{<rate>用户评价|
  rating：1-5星评分
}
}''')

dot1.render('订单主表_结构图', cleanup=True)
print("已生成：订单主表_结构图.png")