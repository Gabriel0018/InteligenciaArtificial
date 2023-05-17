#Autores: Gabriel Prisco e Krisley Almeida
#Disciplina: IC817 - INTELIGÊNCIA ARTIFICIAL - T01 (2023.1 - 46M45)

import pygame
import math
from queue import PriorityQueue
import random
from collections import deque

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))

#Setar Cores
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

print('\nManual do programa:')
print('1 - o primeiro clique do mouse indica a posição inicial do robo, marcado como azul claro')
print('2 - o segundo clique do mouse indica a posição final do robo (destino), marcado como laranja')
print('3 - blocos em azul escuro indicam obstaculos que nao podem ser atravessados pelo robo')
print('4 - blocos em verde mostra todos os caminhos percorridos pelo robo')
print('5 - blocos em roxo mostra o melhor caminho possivel que o algoritmo poderia ter escolhido (pathing)')

class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows
		self.prev = None

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == GREEN

	#def is_open(self):
	#	return self.color == GREEN

	def is_barrier(self):
		return self.color == BLUE

	def is_start(self):
		return self.color == TURQUOISE

	def is_end(self):
		return self.color == ORANGE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = TURQUOISE

	def make_closed(self):
		self.color = GREEN

	#def make_open(self):
	#	self.color = GREEN

	def make_barrier(self):
		self.color = BLUE

	def make_end(self):
		self.color = ORANGE

	def make_path(self):
		if not self.is_start():
			self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])


		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

		if self.row < self.total_rows - 1 and self.col < self.total_rows - 1 and not grid[self.row + 1][self.col + 1].is_barrier(): # DOWN-RIGHT
			self.neighbors.append(grid[self.row + 1][self.col + 1])

		if self.row < self.total_rows - 1 and self.col > 0 and not grid[self.row + 1][self.col - 1].is_barrier(): # DOWN-LEFT
			self.neighbors.append(grid[self.row + 1][self.col - 1])

		if self.row > 0 and self.col < self.total_rows - 1 and not grid[self.row - 1][self.col + 1].is_barrier(): # UP-RIGHT
			self.neighbors.append(grid[self.row - 1][self.col + 1])

		if self.row > 0 and self.col > 0 and not grid[self.row - 1][self.col - 1].is_barrier(): # UP-LEFT
			self.neighbors.append(grid[self.row - 1][self.col - 1])

	def __lt__(self, other):
		return False


def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def algorithm_AStar(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    # Define o custo de cada ação
    action_cost = {
        "stay": 1000,
        "turn": 1,
        "collision": 1000,
        "move": 0
    }

    while not open_set.empty():

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
		
        for neighbor in current.neighbors:
            # Calcula o custo de cada movimento com base na ação realizada
            if neighbor.row == current.row and neighbor.col == current.col:
                # Ficar parado
                action = "stay"
		
            elif neighbor.row != current.row and neighbor.col != current.col:
                # Girar 45 graus
                action = "turn"
		
            elif neighbor.is_barrier():
                # Colisão com um obstáculo
                action = "collision"
            else:
                # Seguir na direção atual
                action = "move"
	
            temp_g_score = g_score[current] + action_cost[action]

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    #neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False
    
def algorithm_BFS(draw, grid, start, end):
    queue = deque([start])
    came_from = {}
    visited = {spot: False for row in grid for spot in row}
    visited[start] = True

    # Define o custo de cada ação
    action_cost = {
        "stay": 1000,
        "turn": 1,
        "collision": 1000,
        "move": 1,
    }

    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = queue.popleft()

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            # Calcula o custo de cada movimento com base na ação realizada
            if neighbor.row == current.row and neighbor.col == current.col:
                # Ficar parado
                action = "stay"
            elif neighbor.row != current.row and neighbor.col != current.col:
                # Girar 45 graus
                action = "turn"
            elif neighbor.is_barrier():
                # Colisão com um obstáculo
                action = "collision"
            else:
                # Seguir na direção atual
                action = "move"

            if not visited[neighbor]:
                queue.append(neighbor)
                visited[neighbor] = True
                came_from[neighbor] = current

        draw()

        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)
	

	num_blocks = random.randint(10, 25)

	barriers = rows ** 2 * num_blocks / 100 
	count = 0
	while count < barriers:
		row = random.randrange(rows)
		col = random.randrange(rows)
		spot = grid[row][col]
		if spot.is_barrier() or spot.is_start() or spot.is_end():
			continue
		spot.make_barrier()
		count += 1

	return grid


def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def main(win, width):
	print('\nSelecione o numero correspondente do algoritmo')
	print('(1) Algoritmo A*')
	print('(2) Algoritmo busca em largura')

	option = int(input('Opcao: '))

	while option != 1 and option != 2:
		option = int(input('Opcao: '))

	if option == 1:
		pygame.display.set_caption("Algoritmo A* (A Star)")
		print("\nAbra a aba gráfica do pygame")

	if option == 2:
		pygame.display.set_caption("Algoritmo de busca em largura")
		print("\nAbra a aba gráfica do pygame")

	ROWS = 40
	grid = make_grid(ROWS, width)

	start = None
	end = None
	started = False # variável adicionada para verificar se o algoritmo foi iniciado

	run = True
	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				if not start and spot != end:
					start = spot
					start.make_start()

				elif not end and spot != start:
					end = spot
					end.make_end()

			if start and end and not started: # verifica se o start e o end foram definidos e se o algoritmo ainda não foi iniciado
				for row in grid:
					for spot in row:
						spot.update_neighbors(grid)

				if option == 1:
					algorithm_AStar(lambda: draw(win, grid, ROWS, width), grid, start, end)

				if option == 2:
					algorithm_BFS(lambda: draw(win, grid, ROWS, width), grid, start, end)

				started = True # define que o algoritmo foi iniciado

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)
					started = False # redefine a variável para falso, para permitir que o algoritmo seja iniciado novamente

	pygame.quit()

main(WIN, WIDTH)