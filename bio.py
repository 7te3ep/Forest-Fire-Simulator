import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import copy
import random 
import pygame

# CONST
grid = []
SIZE = 10
REPRODUCT_PROBABILITY = 0.6
DEATH_PROBABILITY = 0.2
FIRE_DIE_PROBABILITY = [0.6,0.6,0.6]
COLORS = ['#3B8A3E', '#D07A18', '#3A6DB5']
PLANT_NAMES = ['Plante A', 'Plante B', 'Plante C']
MIN_BIOMASS_FOR_FIRE = 10
FIRE_PROPAGATION = 0.8
WIND = [1,1]
FIRE_START = [5,5]
neighbors = [[1,0],[0,1],[1,1],[-1,-1],[-1,0],[0,-1],[1,-1],[-1,1]]
# INIT
# datagram cell [fire : boolean, plants [A,B,C], biomass : Int]

for i in range(SIZE):
    grid.append([])
    for j in range(SIZE):
        plant1 = random.randint(0,33)
        plant2 = random.randint(0,33)
        plant3 = random.randint(0,33)
        grid[i].append([0,[plant1,plant2,plant3],plant1+plant2+plant3])

grid[5][5][0] = 1

def checkBoundaries(i,j):
    return i >= 0 and i < SIZE and j >= 0 and j < SIZE

def reproducePlant(plantIndex,i,j,qty,grid):
    neighbors = [[1,0,0],[0,1,0],[1,1,0],[-1,-1,0],[-1,0,0],[0,-1,0],[1,-1,0],[-1,1,0],[0,0,0]]

    for i in range(qty):
        if (random.random() < REPRODUCT_PROBABILITY):
            seed_location = random.randint(0,len(neighbors)-1)
            neighbors[seed_location][2] += 1

    for n in neighbors:
        target_i = i + n[0]
        target_j = j + n[1]
        if not checkBoundaries(target_i,target_j):
            continue

        grid[target_i][target_j][1][plantIndex] += n[2]

def killPlant(plantIndex,i,j,qty,grid,probability):
    for k in range(qty):
        if (random.random() < probability):
            grid[i][j][1][plantIndex] -= 1


def step(grid):
    oldGrid = copy.deepcopy(grid)

    for i in range(SIZE):
        for j in range(SIZE):
            reproducePlant(0, i, j, oldGrid[i][j][1][0], grid)
            reproducePlant(1, i, j, oldGrid[i][j][1][1], grid)
            reproducePlant(2, i, j, oldGrid[i][j][1][2], grid)

    for i in range(SIZE):
        for j in range(SIZE):
            killPlant(0, i, j, oldGrid[i][j][1][0], grid,DEATH_PROBABILITY)
            killPlant(1, i, j, oldGrid[i][j][1][1], grid,DEATH_PROBABILITY)
            killPlant(2, i, j, oldGrid[i][j][1][2], grid,DEATH_PROBABILITY)

    for i in range(SIZE):
        for j in range(SIZE):
            cell = grid[i][j]
            oldCell = oldGrid[i][j]
            if oldCell[0] == 1:
                killPlant(0, i, j, oldGrid[i][j][1][0], grid,FIRE_DIE_PROBABILITY[0])
                killPlant(1, i, j, oldGrid[i][j][1][1], grid,FIRE_DIE_PROBABILITY[1])
                killPlant(2, i, j, oldGrid[i][j][1][2], grid,FIRE_DIE_PROBABILITY[2])

                current_biomass = cell[1][0] + cell[1][1] + cell[1][2]
                cell[2] = current_biomass
                if current_biomass < MIN_BIOMASS_FOR_FIRE:
                    cell[0] = 0

                local_neighbors = [n[:] for n in neighbors]
                propagation_arr = []

                for n in local_neighbors:
                    dx = n[0] - WIND[0]
                    dy = n[1] - WIND[1]
                    if n[0] == WIND[0] and n[1] == WIND[1]:
                        n.append(FIRE_PROPAGATION)
                        propagation_arr.append(n)
                    elif abs(dx) <= 1 and abs(dy) <= 1:
                        n.append(FIRE_PROPAGATION / 2)
                        propagation_arr.append(n)

                for propagation in propagation_arr:
                    fire_cell = [propagation[0] + i, propagation[1] + j]
                    if not checkBoundaries(fire_cell[0], fire_cell[1]):
                        continue
                    if random.random() < propagation[2]:
                        grid[fire_cell[0]][fire_cell[1]][0] = 1

    for i in range(SIZE):
        for j in range(SIZE):
            cell = grid[i][j]
            cell[2] = cell[1][0] + cell[1][1] + cell[1][2]



def update(grid):
    screen.fill(WHITE)
    for i in range(SIZE):
        pygame.draw.line(screen, BLACK, (i * space, 0), (i * space, DISPLAY_SIZE), 1)
        pygame.draw.line(screen, BLACK, (0, i * space), (DISPLAY_SIZE,i * space), 1)

    for i in range(SIZE):
        for j in range(SIZE):
            cell = grid[i][j]
            x = i * space
            y = j * space
            if (cell[0]):
                pygame.draw.rect(screen, "orange", (x+1,y+1,space-2,space-2))
            
            biomass_text = font.render(str(cell[2]), True, BLACK)
            print(str(cell[2]))
            screen.blit(biomass_text, (x+space/20, y+space/20))  

    pygame.display.flip()


pygame.init()
DISPLAY_SIZE = 800
screen = pygame.display.set_mode((DISPLAY_SIZE, DISPLAY_SIZE))
pygame.display.set_caption("Forest")
font = pygame.font.SysFont("Arial", 12)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
space = DISPLAY_SIZE / SIZE
update(grid)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                step(grid)
                update(grid)
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
