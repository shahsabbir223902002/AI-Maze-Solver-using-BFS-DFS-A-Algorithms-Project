import pygame
import heapq
import time
import random
from collections import deque
from enum import Enum


class CellType(Enum):
    EMPTY = 0
    WALL = 1
    START = 2
    END = 3
    PATH = 4
    VISITED = 5


class Algorithm(Enum):
    BFS = 1
    DFS = 2
    A_STAR = 3


class MazeSolver:
    def __init__(self, width=850, height=650, cell_size=25):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = width // cell_size
        self.rows = height // cell_size

        # Colors
        self.colors = {
            CellType.EMPTY: (173, 216, 230),  # Light blue
            CellType.WALL: (0, 0, 0),  # Black
            CellType.START: (0, 255, 0),  # Green
            CellType.END: (255, 0, 0),  # Red
            CellType.PATH: (0, 0, 255),  # Blue
            CellType.VISITED: (255, 165, 0)  # Orange
        }

        # Maze data
        self.maze = [[CellType.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.start_pos = None
        self.end_pos = None
        self.solving = False
        self.solution_path = []
        self.visited_cells = set()

        # Speed presets (delay in seconds)
        # fast -- smallest delay, slow -- largest delay
        self.speed_presets = {
            "fast": 0.01,
            "medium": 0.03,
            "slow": 0.12
        }
        self.current_speed = "medium"  # default
        self.delay = self.speed_presets[self.current_speed]

        # Time measurement
        self.last_solve_time = None  # seconds (float)

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AI Maze Solver - BFS/DFS/A* (SHAH_SABBIR & ROBIUL)")
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 32)

        # Create a sample maze with random start/end
        self.create_sample_maze(randomize_start_end=True)

    def create_sample_maze(self, randomize_start_end=True):
        #Create a sample maze with walls. Optionally randomize start/end.
        # Clear maze
        self.maze = [[CellType.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]

        # Add border walls
        for i in range(self.rows):
            self.maze[i][0] = CellType.WALL
            self.maze[i][self.cols - 1] = CellType.WALL
        for j in range(self.cols):
            self.maze[0][j] = CellType.WALL
            self.maze[self.rows - 1][j] = CellType.WALL

        # Add some internal walls (same pattern as before)
        for i in range(2, self.rows - 2):
            if i % 4 == 0:
                for j in range(2, self.cols - 2):
                    if j % 3 != 0:
                        self.maze[i][j] = CellType.WALL

        # Choose start and end positions
        if randomize_start_end:
            self.randomize_start_end()
        else:
            self.start_pos = (2, 2)
            self.end_pos = (self.rows - 3, self.cols - 3)
            self.maze[self.start_pos[0]][self.start_pos[1]] = CellType.START
            self.maze[self.end_pos[0]][self.end_pos[1]] = CellType.END

        # Reset time display
        self.last_solve_time = None

    def randomize_start_end(self):
        #Pick random start and end on empty (non-wall) cells and set them.
        empty_cells = []
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if self.maze[r][c] == CellType.EMPTY:
                    empty_cells.append((r, c))

        if len(empty_cells) < 2:
            # fallback to defaults
            self.start_pos = (2, 2)
            self.end_pos = (self.rows - 3, self.cols - 3)
        else:
            self.start_pos = random.choice(empty_cells)
            # ensure different end
            end_candidate = random.choice(empty_cells)
            attempts = 0
            while end_candidate == self.start_pos and attempts < 50:
                end_candidate = random.choice(empty_cells)
                attempts += 1
            if end_candidate == self.start_pos:
                # final fallback: pick opposite corner
                end_candidate = (self.rows - 3, self.cols - 3)
            self.end_pos = end_candidate

        # Mark start and end in the maze
        self.maze[self.start_pos[0]][self.start_pos[1]] = CellType.START
        self.maze[self.end_pos[0]][self.end_pos[1]] = CellType.END

    def get_neighbors(self, pos):
        #Get valid neighboring cells (up, down, left, right)
        row, col = pos
        neighbors = []

        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.rows and
                    0 <= new_col < self.cols and
                    self.maze[new_row][new_col] != CellType.WALL):
                neighbors.append((new_row, new_col))

        return neighbors

    def heuristic(self, pos):
        #Manhattan distance heuristic for A* algorithm
        return abs(pos[0] - self.end_pos[0]) + abs(pos[1] - self.end_pos[1])

    def bfs(self):
        #Breadth-First Search algorithm (generator
        queue = deque([(self.start_pos, [self.start_pos])])
        visited = set([self.start_pos])

        while queue:
            current_pos, path = queue.popleft()

            if current_pos != self.start_pos and current_pos != self.end_pos:
                self.maze[current_pos[0]][current_pos[1]] = CellType.VISITED

            yield current_pos, path

            if current_pos == self.end_pos:
                return path

            for neighbor in self.get_neighbors(current_pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def dfs(self):
        #Depth-First Search algorithm (generator)
        stack = [(self.start_pos, [self.start_pos])]
        visited = set([self.start_pos])

        while stack:
            current_pos, path = stack.pop()

            if current_pos != self.start_pos and current_pos != self.end_pos:
                self.maze[current_pos[0]][current_pos[1]] = CellType.VISITED

            yield current_pos, path

            if current_pos == self.end_pos:
                return path

            for neighbor in self.get_neighbors(current_pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, path + [neighbor]))

        return None

    def a_star(self):
        #A* Search algorithm (generator)
        open_set = []
        heapq.heappush(open_set, (0, self.start_pos, [self.start_pos]))
        g_score = {self.start_pos: 0}
        visited = set()

        while open_set:
            _, current_pos, path = heapq.heappop(open_set)

            if current_pos in visited:
                continue

            visited.add(current_pos)

            if current_pos != self.start_pos and current_pos != self.end_pos:
                self.maze[current_pos[0]][current_pos[1]] = CellType.VISITED

            yield current_pos, path

            if current_pos == self.end_pos:
                return path

            for neighbor in self.get_neighbors(current_pos):
                if neighbor in visited:
                    continue

                tentative_g = g_score[current_pos] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor)
                    heapq.heappush(open_set, (f_score, neighbor, path + [neighbor]))

        return None

    def set_speed(self, preset_name):
        #Set speed preset by name ('fast','medium','slow')
        if preset_name in self.speed_presets:
            self.current_speed = preset_name
            self.delay = self.speed_presets[preset_name]

    def solve_maze(self, algorithm):
        #Solve the maze using the specified algorithm; measure time and allow UI events while solving.
        self.solving = True
        self.solution_path = []
        self.visited_cells = set()
        self.last_solve_time = None

        # Reset visited/path cells
        for i in range(self.rows):
            for j in range(self.cols):
                if self.maze[i][j] in (CellType.VISITED, CellType.PATH):
                    self.maze[i][j] = CellType.EMPTY

        # Re-mark start and end (in case they were overwritten)
        self.maze[self.start_pos[0]][self.start_pos[1]] = CellType.START
        self.maze[self.end_pos[0]][self.end_pos[1]] = CellType.END

        # Choose solver generator
        if algorithm == Algorithm.BFS:
            solver = self.bfs()
        elif algorithm == Algorithm.DFS:
            solver = self.dfs()
        elif algorithm == Algorithm.A_STAR:
            solver = self.a_star()
        else:
            return

        # Start measuring time
        t0 = time.perf_counter()

        try:
            while True:
                # Process pygame events so UI remains responsive
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        raise StopIteration
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        # speed buttons or other buttons are handled if clicked
                        self.handle_static_click((mx, my), inside_solver=True)
                    elif event.type == pygame.KEYDOWN:
                        # allow quick speed toggles with keys F/M/S
                        if event.key == pygame.K_a:
                            self.set_speed("fast")
                        elif event.key == pygame.K_s:
                            self.set_speed("medium")
                        elif event.key == pygame.K_d:
                            self.set_speed("slow")

                current_pos, path = next(solver)
                self.solution_path = path
                self.draw()
                # Respect the current delay (speed) while solving
                if self.delay > 0:
                    time.sleep(self.delay)
        except StopIteration:
            # solver finished (either found path or generator ended)
            t1 = time.perf_counter()
            self.last_solve_time = t1 - t0
            self.solving = False

            # Mark final path visually
            for pos in self.solution_path:
                if pos != self.start_pos and pos != self.end_pos:
                    self.maze[pos[0]][pos[1]] = CellType.PATH

    def draw(self):
        #Draw maze, UI, buttons and time info
        self.screen.fill((255, 255, 255))

        # Draw maze cells
        for i in range(self.rows):
            for j in range(self.cols):
                color = self.colors[self.maze[i][j]]
                rect = pygame.Rect(j * self.cell_size, i * self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

        # Draw algorithm buttons (bottom-left)
        button_width = 85
        button_height = 25
        margin = 5
        y_buttons = self.height - button_height - margin

        self.bfs_button = pygame.Rect(margin, y_buttons, button_width, button_height)
        self.dfs_button = pygame.Rect(margin * 2 + button_width, y_buttons, button_width, button_height)
        self.astar_button = pygame.Rect(margin * 3 + button_width * 2, y_buttons, button_width, button_height)
        self.reset_button = pygame.Rect(margin * 4 + button_width * 3, y_buttons, button_width, button_height)

        pygame.draw.rect(self.screen, (100, 100, 255), self.bfs_button)
        pygame.draw.rect(self.screen, (255, 100, 100), self.dfs_button)
        pygame.draw.rect(self.screen, (100, 255, 100), self.astar_button)
        pygame.draw.rect(self.screen, (255, 255, 100), self.reset_button)

        bfs_text = self.large_font.render("BFS", True, (0, 0, 0))
        dfs_text = self.large_font.render("DFS", True, (0, 0, 0))
        astar_text = self.large_font.render("A*", True, (0, 0, 0))
        reset_text = self.large_font.render("Reset", True, (0, 0, 0))

        self.screen.blit(bfs_text, (self.bfs_button.x + 30, self.bfs_button.y + 4))
        self.screen.blit(dfs_text, (self.dfs_button.x + 30, self.dfs_button.y + 4))
        self.screen.blit(astar_text, (self.astar_button.x + 30, self.astar_button.y + 4))
        self.screen.blit(reset_text, (self.reset_button.x + 18, self.reset_button.y + 4))

        # Draw speed buttons (bottom-right)
        speed_button_w = 80
        speed_margin = 8
        sx_base = self.width - (speed_button_w + speed_margin) * 3 - 20
        sy = y_buttons

        self.fast_button = pygame.Rect(sx_base, sy, speed_button_w, button_height)
        self.medium_button = pygame.Rect(sx_base + (speed_button_w + speed_margin), sy, speed_button_w, button_height)
        self.slow_button = pygame.Rect(sx_base + 2 * (speed_button_w + speed_margin), sy, speed_button_w, button_height)

        # highlight the current preset
        def draw_speed_button(rect, label, preset_name):
            color = (160, 220, 160) if self.current_speed == preset_name else (200, 200, 200)
            pygame.draw.rect(self.screen, color, rect)
            text_surf = self.font.render(label, True, (0, 0, 0))
            self.screen.blit(text_surf, (rect.x + 12, rect.y + 8))

        draw_speed_button(self.fast_button, "Fast", "fast")
        draw_speed_button(self.medium_button, "Medium", "medium")
        draw_speed_button(self.slow_button, "Slow", "slow")

        # Randomize start/end button (to the left of speed buttons)
        rand_button_w = 100
        self.rand_button = pygame.Rect(sx_base - rand_button_w - 12, sy, rand_button_w, button_height)
        pygame.draw.rect(self.screen, (180, 180, 255), self.rand_button)
        rand_text = self.font.render("Random", True, (0, 0, 0))
        self.screen.blit(rand_text, (self.rand_button.x + 6, self.rand_button.y + 8))

        # Instructions (top-left)

        instructions = [
            "Press a/s/d keys for quick speed change."
        ]


        time_y = 8 + len(instructions) * 20 + 6
        if self.last_solve_time is None:
            time_text = "   Solver Time: "
        else:
            time_text = f"Time: {self.last_solve_time:.3f} s"
        time_surf = self.large_font.render(time_text, True, (0, 0, 0))
        self.screen.blit(time_surf, (10, time_y))

        # Display Start/End coordinates for clarity (top-left, to the right of time)
        se_text = f"    Start: {self.start_pos}  End: {self.end_pos} "
        se_surf = self.font.render(se_text, True, (0, 0, 0))
        self.screen.blit(se_surf, (10, time_y + 36))

        pygame.display.flip()

    def handle_static_click(self, pos, inside_solver=False):
        #Handle clicks on buttons. If inside_solver True, this was called while solving (so avoid starting nested solvers).
        x, y = pos

        # Check algorithm buttons
        if hasattr(self, "bfs_button") and self.bfs_button.collidepoint(x, y):
            if not inside_solver:
                self.solve_maze(Algorithm.BFS)
            return
        if hasattr(self, "dfs_button") and self.dfs_button.collidepoint(x, y):
            if not inside_solver:
                self.solve_maze(Algorithm.DFS)
            return
        if hasattr(self, "astar_button") and self.astar_button.collidepoint(x, y):
            if not inside_solver:
                self.solve_maze(Algorithm.A_STAR)
            return
        if hasattr(self, "reset_button") and self.reset_button.collidepoint(x, y):
            # Reset maze (randomize start/end)
            self.create_sample_maze(randomize_start_end=True)
            return

        # Speed buttons
        if hasattr(self, "fast_button") and self.fast_button.collidepoint(x, y):
            self.set_speed("fast")
            return
        if hasattr(self, "medium_button") and self.medium_button.collidepoint(x, y):
            self.set_speed("medium")
            return
        if hasattr(self, "slow_button") and self.slow_button.collidepoint(x, y):
            self.set_speed("slow")
            return

        # Randomize button
        if hasattr(self, "rand_button") and self.rand_button.collidepoint(x, y):
            # Randomize start and end on current maze
            # First clear previous start/end marks
            if self.start_pos:
                r, c = self.start_pos
                if self.maze[r][c] == CellType.START:
                    self.maze[r][c] = CellType.EMPTY
            if self.end_pos:
                r, c = self.end_pos
                if self.maze[r][c] == CellType.END:
                    self.maze[r][c] = CellType.EMPTY

            self.randomize_start_end()
            return

    def run(self):
        #Main loop
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_static_click(event.pos, inside_solver=False)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.set_speed("fast")
                    elif event.key == pygame.K_m:
                        self.set_speed("medium")
                    elif event.key == pygame.K_s:
                        self.set_speed("slow")

            self.draw()
            clock.tick(60)

        pygame.quit()


def main():
    print("AI Maze Solver Project by sabbir223902002 & Robiul223902043")
    print("Controls:")
    print("- Click BFS / DFS / A* to run algorithms.")
    print("- Click Reset to create a new maze with random Start/End.")
    print("- Click 'Randomize Start/End' to randomly place start and goal on the current maze.")
    print("- Click Fast / Medium / Slow to change visualization speed (works while solving).")
    print("- Shortcut keys: a = Fast, s = Medium, d = Slow.")
    print("\n Let's go .....")

    solver = MazeSolver()
    solver.run()


if __name__ == "__main__":
    main()
