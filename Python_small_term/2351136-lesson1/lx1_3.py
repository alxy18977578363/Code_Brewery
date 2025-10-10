import turtle
import random

# 创建画布
screen = turtle.Screen()
screen.bgcolor("white")


while True:
    # 创建海龟
    t = turtle.Turtle()

    # 确定海龟的初始位置
    t.penup()
    x = random.randint(-300, 300)
    y = random.randint(-200, 200)
    t.goto(x, y)
    t.pendown()

    # 随机移动距离和角度
    distance = random.randint(50, 150)  # 移动距离在50到150像素之间随机选择
    angle = random.randint(15, 60)      # 移动角度在15到360度之间随机选择

    # 设置笔的颜色和大小
    color = (random.random(), random.random(), random.random())
    t.color(color)
    pensize = random.randint(1, 10)
    t.pensize(pensize)

    # 绘画速度设置为5
    t.speed(5)

    # 绘制线条
    for _ in range(360 // angle + 1):
        t.forward(distance)
        t.back(distance)
        t.right(angle)

# 隐藏海龟并保持窗口显示
turtle.done()