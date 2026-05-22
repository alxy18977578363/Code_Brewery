 # 原子操作演示：incr（原子自增计数器）
  # 场景：待售车辆浏览次数，每次浏览原子+1，不会并发重复计数

  # 第一步：初始化 view_count 为 0
  put 'car_sales', '北京_20240315_C1001', 'sale:view_count', '0'
  puts "=== 初始化 view_count = 0 ==="
  get 'car_sales', '北京_20240315_C1001', {COLUMN => 'sale:view_count'}

  # 第二步：用户A浏览，原子+1
  incr 'car_sales', '北京_20240315_C1001', 'sale:view_count', 1
  puts "=== 用户A浏览后，view_count 应为 1 ==="
  get 'car_sales', '北京_20240315_C1001', {COLUMN => 'sale:view_count'}

  # 第三步：用户B浏览，原子+1
  incr 'car_sales', '北京_20240315_C1001', 'sale:view_count', 1
  puts "=== 用户B浏览后，view_count 应为 2 ==="
  get 'car_sales', '北京_20240315_C1001', {COLUMN => 'sale:view_count'}

  # 第四步：用户C批量浏览，原子+5
  incr 'car_sales', '北京_20240315_C1001', 'sale:view_count', 5
  puts "=== 用户C批量浏览后，view_count 应为 7 ==="
  get 'car_sales', '北京_20240315_C1001', {COLUMN => 'sale:view_count'}