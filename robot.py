import pygame
import heapq
import random
import string

# Configuración
WIDTH, HEIGHT = 700, 600
ROWS, COLS = 15, 15
CELL_SIZE = 40

# Colores
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
ORANGE = (255, 165, 0)
DARKGRAY = (100, 100, 100)

# Tipos de celda
EMPTY, OBSTACLE, ROBOT, PACKAGE, TARGET = 0, 1, 2, 3, 4

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot con letras identificadoras")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)

def create_base_map():
    grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    for _ in range(60):
        x, y = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
        grid[y][x] = OBSTACLE
    return grid

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, goal):
    neighbors = [(0, 1), (1, 0), (-1, 0), (0, -1)]
    queue = [(0, start)]
    came_from = {}
    cost_so_far = {start: 0}

    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            break
        for dx, dy in neighbors:
            nx, ny = current[0] + dx, current[1] + dy
            next_pos = (nx, ny)
            if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] != OBSTACLE:
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(goal, next_pos)
                    heapq.heappush(queue, (priority, next_pos))
                    came_from[next_pos] = current

    if goal not in came_from:
        return []
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def draw_grid(win, grid, robot_pos, labels):
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            tipo = grid[y][x]
            color = WHITE
            if tipo == OBSTACLE:
                color = BLACK
            elif tipo == PACKAGE:
                color = ORANGE
            elif tipo == TARGET:
                color = GREEN
            pygame.draw.rect(win, color, rect)
            pygame.draw.rect(win, DARKGRAY, rect, 1)

    # Letras
    for letter, (pkg_pos, dest_pos) in labels.items():
        pkg_text = font.render(letter, True, BLACK)
        dest_text = font.render(letter, True, BLACK)
        win.blit(pkg_text, (pkg_pos[0] * CELL_SIZE + 10, pkg_pos[1] * CELL_SIZE + 10))
        win.blit(dest_text, (dest_pos[0] * CELL_SIZE + 10, dest_pos[1] * CELL_SIZE + 10))

    # Dibujar robot encima
    rx, ry = robot_pos
    pygame.draw.rect(win, BLUE, (rx * CELL_SIZE, ry * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_buttons():
    pygame.draw.rect(win, GRAY, (610, 50, 80, 30))
    pygame.draw.rect(win, GRAY, (610, 100, 80, 30))
    win.blit(font.render("+1 Paquete", True, BLACK), (615, 55))
    win.blit(font.render("Buscar", True, BLACK), (625, 105))

def random_empty_cell(grid):
    while True:
        x, y = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
        if grid[y][x] == EMPTY:
            return (x, y)

# Inicialización
grid = create_base_map()
robot_pos = (0, 0)
tasks = []  # Lista de (paquete_pos, destino_pos)
labels = {}  # letra: (paquete, destino) //
letter_index = 0

path = []
phase = "idle"
step_index = 0
current_pair = None
current_letter = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if 610 <= mx <= 690 and 50 <= my <= 80:
                if letter_index < len(string.ascii_uppercase):
                    letra = string.ascii_uppercase[letter_index]
                    paquete = random_empty_cell(grid)
                    destino = random_empty_cell(grid)
                    tasks.append((paquete, destino, letra))
                    labels[letra] = (paquete, destino)
                    grid[paquete[1]][paquete[0]] = PACKAGE
                    grid[destino[1]][destino[0]] = TARGET
                    letter_index += 1

            if 610 <= mx <= 690 and 100 <= my <= 130:
                if phase == "idle" and tasks:
                    paquete, destino, letra = tasks.pop(0)
                    current_pair = (paquete, destino)
                    current_letter = letra
                    path = astar(grid, robot_pos, paquete)
                    phase = "to_package"
                    step_index = 0

    if phase in ["to_package", "to_target"] and step_index < len(path):
        robot_pos = path[step_index]
        step_index += 1
    elif phase == "to_package" and step_index >= len(path):
        px, py = current_pair[0]
        if grid[py][px] == PACKAGE:
            grid[py][px] = EMPTY
        path = astar(grid, robot_pos, current_pair[1])
        phase = "to_target"
        step_index = 0
    elif phase == "to_target" and step_index >= len(path):
        dx, dy = current_pair[1]
        if grid[dy][dx] == TARGET:
            grid[dy][dx] = EMPTY
        labels.pop(current_letter, None)
        phase = "idle"
        current_pair = None
        current_letter = None

    win.fill(WHITE)
    draw_grid(win, grid, robot_pos, labels)
    draw_buttons()
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
