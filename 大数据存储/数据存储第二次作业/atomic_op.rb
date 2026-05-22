 # 第一步：先把状态设为 pending
  put 'car_sales', '北京_20240315_C1001', 'info:status', 'pending'
  puts "当前状态已设为 pending"

  # 第二步：成功场景 - 当前是 pending，改成 sold
  result = checkAndMutate('car_sales', '北京_20240315_C1001', 'info:status').isEqual('pending').thenPut('info:status',
  'sold')
  puts "成功场景（pending->sold）：#{result}"
  puts "验证当前状态："
  get 'car_sales', '北京_20240315_C1001', {COLUMN => 'info:status'}

  # 第三步：失败场景 - 当前是 sold，尝试再改成 pending
  result2 = checkAndMutate('car_sales', '北京_20240315_C1001', 'info:status').isEqual('pending').thenPut('info:status',
  'pending')
  puts "失败场景（sold->pending）：#{result2}"
  puts "验证当前状态："
  get 'car_sales', '北京_20240315_C1001', {COLUMN => 'info:status'}