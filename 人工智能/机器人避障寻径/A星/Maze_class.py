# 地图信息
start_info = -1        # 开始的位置
way_info = 0           # 路径
wall_info = 1          # 墙
goal_info = 2          # 目标

class Maze:
    def __init__(self, maze):
        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0])

    def update_maze(self, maze):
        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0])

    # 判断是否出界
    def is_out_of_bounds(self, node):
        row, col = node
        return row < 0 or row >= self.rows or col < 0 or col >= self.cols
    
    # 取得某点的属性
    def get_attribute(self, node):
        return self.maze[node[0]][node[1]]

    def neighbors(self, current):
        row, col = current
        results = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for direction in directions:
            new_row = row + direction[0]
            new_col = col + direction[1]
            new_node = (new_row, new_col)

            if not self.is_out_of_bounds(new_node) and self.get_attribute(new_node) != wall_info:
                results.append(new_node)

        return results

    def cost(self, current, neighbor):
        return 1
    
def load_maze(filename):
    with open(filename, "r") as f:
        maze = [[int(num) for num in line.strip().split()] for line in f]
    return maze

def get_start_and_goal(maze):
    rows = maze.rows
    cols = maze.cols
    for i in range(rows):
        for j in range(cols):
            if maze.get_attribute((i,j)) == start_info:
                start = (i,j)
            elif maze.get_attribute((i,j)) == goal_info:
                goal = (i,j)

    if start is None or goal is None:
        raise ValueError("Start or goal not found in the maze")
    
    return start,goal