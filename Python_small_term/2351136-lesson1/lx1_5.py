import datetime

#该函数用来判定是周几
def get_weekday(weekday):
    weekdays=["星期天","星期一","星期二","星期三","星期四","星期五","星期六"]
    return weekdays[weekday]

def get_current_time():
    #调用系统函数，获取日期
    today=datetime.datetime.now()
    year=today.year
    month=today.month
    day=today.day
    weekday=today.weekday()

    chinese_weekday=get_weekday(weekday)

# 格式化输出
    print(f"今天是 {year}年{month}月{day}日，{chinese_weekday}")

if __name__ == "__main__":
    get_current_time()
