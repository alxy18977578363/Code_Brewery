import pygame
import sys
import time
from Maze_class import load_maze, Maze, get_start_and_goal
from A_star import heuristic, reconstruct_path, A_star_search

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (169, 169, 169)  # 墙体颜色
LIGHT_GRAY = (211, 211, 211)  # 墙体的浅灰色
RED = (255, 0, 0)  # 终点
GREEN = (0, 255, 0)  # 起点
BLUE = (0, 0, 255)  # 路径
YELLOW = (255, 255, 0)  # 当前节点
PURPLE = (128, 0, 128)  # 已探索区域
LIGHT_BLUE = (173, 216, 230)  # 待探索区域

# 单元格大小
CELL_SIZE = 40
MARGIN = 2
ANIMATION_DELAY = 0.05  # 每步动画延迟(秒)

def visualize_maze_dynamic(maze_file):
    # 初始化pygame
    pygame.init()
    
    # 加载迷宫
    maze_data = load_maze(maze_file)
    maze = Maze(maze_data)
    start, goal = get_start_and_goal(maze)
    
    # 计算窗口大小
    width = maze.cols * (CELL_SIZE + MARGIN) + MARGIN
    height = maze.rows * (CELL_SIZE + MARGIN) + MARGIN + 100  # 额外空间给图例和状态
    
    # 设置显示
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("A* 算法动态可视化")
    
    # 字体
    font = pygame.font.SysFont('Arial', 16)
    large_font = pygame.font.SysFont('Arial', 20, bold=True)
    
    # 初始化A*搜索
    frontier = []
    frontier.append((0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    explored = set()
    path = []
    found = False
    current = None
    
    # 主循环
    running = True
    paused = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused  # 空格键暂停/继续
                elif event.key == pygame.K_r:
                    # R键重置
                    frontier = []
                    frontier.append((0, start))
                    came_from = {}
                    cost_so_far = {}
                    came_from[start] = None
                    cost_so_far[start] = 0
                    explored = set()
                    path = []
                    found = False
                    current = None
        
        if not paused and not found and frontier:
            # 执行一步A*搜索
            frontier.sort()  # 按优先级排序
            _, current = frontier.pop(0)
            
            if current == goal:
                found = True
                path = reconstruct_path(came_from, start, goal)
                continue
            
            explored.add(current)
            
            for next_node in maze.neighbors(current):
                new_cost = cost_so_far[current] + maze.cost(current, next_node)
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + heuristic(goal, next_node)
                    frontier.append((priority, next_node))
                    came_from[next_node] = current
            
            time.sleep(ANIMATION_DELAY)
        
        # 绘制
        screen.fill(BLACK)
        
        # 绘制迷宫
        for row in range(maze.rows):
            for col in range(maze.cols):
                cell_value = maze.get_attribute((row, col))
                color = WHITE  # 默认颜色
                
                # 确定单元格颜色
                if (row, col) == start:
                    color = GREEN  # 起点
                elif (row, col) == goal:
                    color = RED  # 终点
                elif cell_value == 1:  # 墙
                    color = DARK_GRAY
                elif (row, col) in explored:  # 已探索区域
                    color = PURPLE
                elif any((row, col) == node[1] for node in frontier):  # 待探索区域
                    color = LIGHT_BLUE
                
                # 如果是路径的一部分
                if (row, col) in path:
                    color = BLUE
                
                # 绘制单元格
                pygame.draw.rect(screen, color, 
                                [(MARGIN + CELL_SIZE) * col + MARGIN,
                                 (MARGIN + CELL_SIZE) * row + MARGIN,
                                 CELL_SIZE,
                                 CELL_SIZE])
        
        # 绘制当前节点
        if current:
            pygame.draw.rect(screen, YELLOW, 
                            [(MARGIN + CELL_SIZE) * current[1] + MARGIN,
                             (MARGIN + CELL_SIZE) * current[0] + MARGIN,
                             CELL_SIZE,
                             CELL_SIZE])
        
        # 绘制图例
        legend_y = maze.rows * (CELL_SIZE + MARGIN) + MARGIN + 10
        
        def draw_legend_item(color, text, x):
            pygame.draw.rect(screen, color, [x, legend_y, 20, 20])
            text_surface = font.render(text, True, WHITE)
            screen.blit(text_surface, (x + 25, legend_y))
            return x + 25 + text_surface.get_width() + 20
        
        x_pos = 10
        x_pos = draw_legend_item(GREEN, "起点", x_pos)
        x_pos = draw_legend_item(RED, "终点", x_pos)
        x_pos = draw_legend_item(DARK_GRAY, "墙", x_pos)
        x_pos = draw_legend_item(PURPLE, "已探索", x_pos)
        x_pos = draw_legend_item(LIGHT_BLUE, "待探索", x_pos)
        x_pos = draw_legend_item(BLUE, "路径", x_pos)
        x_pos = draw_legend_item(YELLOW, "当前", x_pos)
        
        # 显示状态
        status_text = "状态: "
        if found:
            status_text += f"找到路径! 总代价: {cost_so_far[goal]}"
        elif not frontier:
            status_text += "无可行路径!"
        else:
            status_text += "搜索中..."
        
        if paused:
            status_text += " (已暂停)"
        
        status_surface = large_font.render(status_text, True, WHITE)
        screen.blit(status_surface, (10, legend_y + 30))
        
        # 显示控制提示
        controls_surface = font.render("空格键: 暂停/继续 | R键: 重置", True, WHITE)
        screen.blit(controls_surface, (width - controls_surface.get_width() - 10, legend_y + 30))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        maze_file = sys.argv[1]
    else:
        maze_file = "Maze.txt"  # 默认迷宫文件
    
    visualize_maze_dynamic(maze_file)
