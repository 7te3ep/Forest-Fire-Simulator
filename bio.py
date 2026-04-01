import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import copy
import random 

# CONST
grid = []
SIZE = 10
REPRODUCT_PROBABILITY = 0.1
FIRE_DIE_PROBABILITY = [0.5,0.7,0.7]
COLORS = ['#3B8A3E', '#D07A18', '#3A6DB5']
PLANT_NAMES = ['Plante A', 'Plante B', 'Plante C']
MIN_BIOMASS_FOR_FIRE = 40
FIRE_PROPAGATION = 0.8
WIND = [1,1]
FIRE_START = [5,5]
neighbors = [[1,0],[0,1],[1,1],[-1,-1],[-1,0],[0,-1],[1,-1],[-1,1]]
# INIT
# datagram cell [fire : boolean, plants [A,B,C], biomass : Int]
for i in range(10):
    grid.append([])
    for j in range(10):
        grid[i].append([0,[random.randint(0,33),random.randint(0,33),random.randint(0,33)],30])

grid[5][5][0] = 1

def checkBoundaries(i,j):
    return i >= 0 and i < SIZE and j >= 0 and j < SIZE

def reproducePlant(plantIndex,i,j,qty,grid):
    neighbors = [[1,0],[0,1],[1,1],[-1,-1],[-1,0],[0,-1],[1,-1],[-1,1]]
    for coords in neighbors:
        target_i = i + coords[0]
        target_j = j + coords[1]
        if not checkBoundaries(target_i,target_j):
            continue
        current_population_overflow = 1 - (((grid[target_i][target_j][2] + (qty * REPRODUCT_PROBABILITY)))/100)
        if (current_population_overflow < 0):
            current_population_overflow = 0
        reproduce_qty = round(qty * REPRODUCT_PROBABILITY * current_population_overflow)
        print(reproduce_qty)
        grid[target_i][target_j][1][plantIndex] += reproduce_qty

    current_population_overflow = 1 - (((qty + (qty * REPRODUCT_PROBABILITY)))/100)
    if (current_population_overflow < 0):
        current_population_overflow = 0
    reproduce_qty = round(qty * REPRODUCT_PROBABILITY * current_population_overflow)
    grid[i][j][1][plantIndex] += reproduce_qty

def step(grid):
    oldGrid = copy.deepcopy(grid)

    for i in range(SIZE):
        for j in range(SIZE):
            reproducePlant(0, i, j, oldGrid[i][j][1][0], grid)
            reproducePlant(1, i, j, oldGrid[i][j][1][1], grid)
            reproducePlant(2, i, j, oldGrid[i][j][1][2], grid)

    for i in range(SIZE):
        for j in range(SIZE):
            cell = grid[i][j]
            oldCell = oldGrid[i][j]
            if oldCell[0] == 1:
                cell[1][0] = round(cell[1][0] - cell[1][0] * FIRE_DIE_PROBABILITY[0])
                cell[1][1] = round(cell[1][1] - cell[1][1] * FIRE_DIE_PROBABILITY[1])
                cell[1][2] = round(cell[1][2] - cell[1][2] * FIRE_DIE_PROBABILITY[2])

                # ✅ recalcul immédiat avant de tester l'extinction
                current_biomass = cell[1][0] + cell[1][1] + cell[1][2]
                cell[2] = current_biomass
                if current_biomass < MIN_BIOMASS_FOR_FIRE:
                    cell[0] = 0

                # ✅ copie locale pour ne pas muter la liste globale
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

def display_grid(grid, title="État de la grille"):
    fig, axes = plt.subplots(SIZE, SIZE, figsize=(14, 14))
    fig.suptitle(title, fontsize=14)
    fig.patch.set_facecolor('#f0f0f0')

    for i in range(SIZE):
        for j in range(SIZE):
            ax = axes[i][j]
            cell = grid[i][j]
            plants = cell[1]
            biomass = cell[2]
            on_fire = cell[0] == 1

            if on_fire:
                ax.set_facecolor('#ffdddd')

            # Barres sur seulement 60% de la hauteur pour laisser place au texte
            if biomass > 0:
                for p in range(3):
                    qty = max(0, plants[p])
                    height = (qty / biomass) * 0.6
                    bottom = sum(max(0, plants[k]) / biomass for k in range(p)) * 0.6
                    ax.bar(0, height, bottom=bottom + 0.35, color=COLORS[p], width=0.8)

            # Biomasse en grand en bas
            ax.text(0.5, 0.18, str(biomass), ha='center', va='center',
                    fontsize=9, fontweight='bold', color='#222222',
                    transform=ax.transAxes)

            if on_fire:
                ax.text(0.85, 0.85, '🔥', ha='center', va='center',
                        fontsize=8, transform=ax.transAxes)

            ax.set_xlim(-0.5, 0.5)
            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_edgecolor('#ff4444' if on_fire else '#aaaaaa')
                spine.set_linewidth(1.5 if on_fire else 0.8)

    # Ligne de séparation visuelle entre barres et biomasse
    for i in range(SIZE):
        for j in range(SIZE):
            axes[i][j].axhline(y=0.3, color='#cccccc', linewidth=0.5)

    patches = [mpatches.Patch(color=COLORS[p], label=PLANT_NAMES[p]) for p in range(3)]
    fig.legend(handles=patches, loc='lower left', ncol=3, fontsize=10)

    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    plt.subplots_adjust(wspace=0, hspace=0)
    plt.show()

step(grid)
display_grid(grid)
step(grid)
step(grid)
display_grid(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
display_grid(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
step(grid)
display_grid(grid)