# ️Importing Libraries
import pygame
from collections import deque

# Grid size------------------------
CELL_SIZE = 20
ROWS = 20
COLS = 30
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

# Cell types--------------------------
EMPTY = 0
WALL = 1
START = 2
END = 3
VISITED = 4
PATH = 5

# Colors (simple)---------------------------------
COLORS = {
    EMPTY: (255, 255, 255), #white
    WALL: (0, 0, 0), #black
    START: (0, 255, 0), #green
    END: (255, 0, 0), #red
    VISITED: (200, 200, 200), #lightGray
    PATH: (0, 0, 255) # blue
}

# Create a simple maze-------------------------------------
maze = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

# Add borders----------------------------------
for r in range(ROWS):
    maze[r][0] = WALL
    maze[r][COLS-1] = WALL
for c in range(COLS):
    maze[0][c] = WALL
    maze[ROWS-1][c] = WALL

# Add some walls--------------------------------------
for r in range(2, ROWS-2, 3):
    for c in range(2, COLS-2, 4):
        maze[r][c] = WALL

# Start and End---------------------------------------
start = (1, 1)
end = (ROWS-2, COLS-2)
maze[start[0]][start[1]] = START
maze[end[0]][end[1]] = END

# Pygame setup---------------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Maze Solver / KEY PRESS-B=BFS,D=DFS")

def draw():
    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen, COLORS[maze[r][c]],
                             (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (100,100,100), (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
    pygame.display.flip()

def get_neighbors(pos):
    r, c = pos
    neighbors = []
    for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] != WALL:
            neighbors.append((nr, nc))
    return neighbors
#BFS-------------------------------------------------------
def bfs():
    queue = deque([(start, [start])])
    visited = set([start])
    while queue:
        pos, path = queue.popleft()
        if pos == end:
            return path
        for n in get_neighbors(pos):
            if n not in visited:
                visited.add(n)
                queue.append((n, path+[n]))
                if n != end:
                    maze[n[0]][n[1]] = VISITED
        draw()
        pygame.time.delay(35)
    return None

#DFS--------------------------------------------
def dfs():
    stack = [(start, [start])]
    visited = set([start])
    while stack:
        pos, path = stack.pop()
        if pos == end:
            return path
        for n in get_neighbors(pos):
            if n not in visited:
                visited.add(n)
                stack.append((n, path+[n]))
                if n != end:
                    maze[n[0]][n[1]] = VISITED
        draw()
        pygame.time.delay(35)
    return None

# Main loop----------------------------------
running = True
solving = False
algorithm = "BFS"  # default

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                algorithm = "BFS"
                solving = True
            elif event.key == pygame.K_d:
                algorithm = "DFS"
                solving = True

    if solving:
        if algorithm == "BFS":
            path = bfs()
        else:
            path = dfs()
        if path:
            for r,c in path:
                if (r,c) != start and (r,c) != end:
                    maze[r][c] = PATH
        draw()
        solving = False

    draw()
pygame.quit()
