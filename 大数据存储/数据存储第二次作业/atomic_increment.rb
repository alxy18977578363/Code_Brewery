# 原子操作演示：atomicIncrement
  # 场景：模拟一个待售车辆的浏览次数计数器，每次浏览原子自增，不会出现并发重复计数

  # 第一步：初始化 view_count 为 0
  put 'car_sales', '北京_20240315_C1001', 'sale:view_count', '0'
  puts "初始化 view_count = 0"

  # 第二步：用户A浏览，原子自增1
  atomicIncrement 'car_sales', '北京_20240315_C1001', 'sale:view_count', 1
  puts "用户A浏览后："
  get 'car_sales', '北京_20240315_C1001', {COLUMN => 'sale:view_count'}

  # 第三步：用户B浏览，原子自增1
  atomicIncrement 'car_sales', '北京_20240315_C1001', 'sale:view_count', 1
  puts "用户B浏览后："
  get 'car_sales', '北京_20240315_C1001', {COLUMN => 'sale:view_count'}

  # 第四步：用户C浏览，原子自增5
  atomicIncrement 'car_sales', '北京_20240315_C1001', 'sale:view_count', 5
  puts "用户C批量浏览后："
  get 'car_sales', '北京_20240315_C1001', {COLUMN => 'sale:view_count'}