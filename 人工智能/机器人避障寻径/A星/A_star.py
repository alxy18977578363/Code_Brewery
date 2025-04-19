import pandas as pd
from queue import PriorityQueue

# 计算到终点的启发函数
def heuristic(goal, node):
    return abs(goal[0] - node[0]) + abs(goal[1] - node[1])

# 重建路线
def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)  # 可选：是否包含起点
    path.reverse()      # 从起点到终点
    return path


def A_star_search(maze, start, goal):
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = dict()
    cost_so_far = dict()
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        _, current = frontier.get()     # 第一个是优先级

        if current == goal:
            break
        
        for next in maze.neighbors(current):
            new_cost = cost_so_far[current] + maze.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put((priority, next))
                came_from[next] = current
    
    return came_from, cost_so_far
