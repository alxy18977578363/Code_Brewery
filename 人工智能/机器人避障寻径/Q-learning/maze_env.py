import numpy as np
import tkinter as tk
import time

UNIT = 40   # 每个格子大小
# 地图信息
start_info = -1        # 开始的位置
way_info = 0           # 路径
wall_info = 1          # 墙
goal_info = 2          # 目标

class Maze(tk.Tk, object):
    def __init__(self, map_file):
        super(Maze, self).__init__()
        self.action_space = ['u', 'd', 'l', 'r']
        self.n_actions = len(self.action_space)
        self.title('maze')
        
        # 从文件加载地图
        self.load_map(map_file)
        
        self.geometry('{0}x{1}'.format(self.MAZE_W * UNIT, self.MAZE_H * UNIT))
        self._build_maze()

    def load_map(self, map_file):
        """从txt文件加载地图"""
        with open(map_file, 'r') as f:
            lines = f.readlines()
        
        # 去除空行和注释行（以#开头的行）
        lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
        
        self.MAZE_H = len(lines)
        self.MAZE_W = len(lines[0].split()) if self.MAZE_H > 0 else 0
        
        self.map_data = []
        self.start_pos = None
        self.paradise_pos = None
        
        for i in range(self.MAZE_H):
            row = lines[i].split()
            map_row = []
            for j in range(self.MAZE_W):
                cell = int(row[j])
                map_row.append(cell)
                
                # 记录起点位置（假设用3表示起点）
                if cell == start_info:
                    self.start_pos = (j, i)
                # 记录奖励区位置（2表示奖励区）
                elif cell == goal_info:
                    self.paradise_pos = (j, i)
            
            self.map_data.append(map_row)
        
        # 如果没有指定起点，默认使用(0,0)
        if self.start_pos is None:
            self.start_pos = (0, 0)

    def _build_maze(self):
        self.canvas = tk.Canvas(self, bg='white',
                           height=self.MAZE_H * UNIT,
                           width=self.MAZE_W * UNIT)

        # 创建格子
        for c in range(0, self.MAZE_W * UNIT, UNIT):
            x0, y0, x1, y1 = c, 0, c, self.MAZE_H * UNIT
            self.canvas.create_line(x0, y0, x1, y1)
        for r in range(0, self.MAZE_H * UNIT, UNIT):
            x0, y0, x1, y1 = 0, r, self.MAZE_W * UNIT, r
            self.canvas.create_line(x0, y0, x1, y1)

        # 根据地图数据创建元素
        self.hells = []
        self.paradise = []
        
        for i in range(self.MAZE_H):
            for j in range(self.MAZE_W):
                center = np.array([j * UNIT + 20, i * UNIT + 20])
                
                if self.map_data[i][j] == wall_info:  # 障碍物
                    self.hells.append(self.create_hell(center))
                elif self.map_data[i][j] == goal_info:  # 奖励区
                    self.paradise.append(self.create_paradise(center))

        # 创建起点
        start_position = np.array([self.start_pos[0] * UNIT + 20, self.start_pos[1] * UNIT + 20])
        self.rect = self.canvas.create_rectangle(
            start_position[0] - 15, start_position[1] - 15,
            start_position[0] + 15, start_position[1] + 15,
            fill='red')

        self.canvas.pack()

    def create_hell(self, center):
        """创建一个障碍物"""
        return self.canvas.create_rectangle(
            center[0] - 15, center[1] - 15,
            center[0] + 15, center[1] + 15,
            fill='black')

    def create_paradise(self, center):
        """创建一个奖励区"""
        return self.canvas.create_oval(
            center[0] - 15, center[1] - 15,
            center[0] + 15, center[1] + 15,
            fill='yellow')

    def reset(self):
        """重置迷宫"""
        self.update()

        self.canvas.delete(self.rect)
        
        start_position = np.array([self.start_pos[0] * UNIT + 20, self.start_pos[1] * UNIT + 20])
        self.rect = self.canvas.create_rectangle(
            start_position[0] - 15, start_position[1] - 15,
            start_position[0] + 15, start_position[1] + 15,
            fill='red')

        return self.canvas.coords(self.rect)

    def step(self, action):
        """执行一步操作"""
        s = self.canvas.coords(self.rect)
        base_action = np.array([0, 0])
        if action == 0:   # up
            if s[1] > UNIT:
                base_action[1] -= UNIT
        elif action == 1:   # down
            if s[1] < (self.MAZE_H - 1) * UNIT:
                base_action[1] += UNIT
        elif action == 2:   # right
            if s[0] < (self.MAZE_W - 1) * UNIT:
                base_action[0] += UNIT
        elif action == 3:   # left
            if s[0] > UNIT:
                base_action[0] -= UNIT

        self.canvas.move(self.rect, base_action[0], base_action[1])  # 移动探索者
        s_ = self.canvas.coords(self.rect)  # 下一状态

        # 奖励函数
        if s_ in [self.canvas.coords(p) for p in self.paradise]:
            reward = 1
            done = True
            s_ = 'terminal'
        elif s_ in [self.canvas.coords(h) for h in self.hells]:
            reward = -1
            done = True
            s_ = 'terminal'
        else:
            reward = 0
            done = False

        return s_, reward, done

    def render(self):
        """渲染当前的状态"""
        time.sleep(0.1)
        self.update()

def update():
    for t in range(10):
        s = env.reset()
        while True:
            env.render()
            a = 1  # 随便选择一个动作
            s, r, done = env.step(a)
            if done:
                break

if __name__ == '__main__':
    
    map_file = 'Maze.txt'  # 替换为你的地图文件路径
    env = Maze(map_file)
    env.after(100, update)
    env.mainloop()