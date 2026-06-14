import random
import state
from constants import COLS, ROWS, BLUE, RED, RIGHT, LEFT, GRID_SIZE, GOLD
from player import Player
from particles import spawn_particles, Particle

# =====================================================================
# MODUŁ KONTROLI LOGIKI ROZGRYWKI (SPAWNOWANIE, ROZGRYWKA I RESET)
# =====================================================================

def spawn_new_food(grid):
    """
    Losuje wolną pozycję na planszy i umieszcza tam nowe jedzenie (owoc).
    Zapewnia, że jedzenie nie pojawi się na polu zajętym przez gracza/bota (wartość != 0 w grid)
    oraz nie nałoży się na już istniejące jedzenie.
    """
    while True:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        # Pole w siatce musi być puste (0) i nie może zawierać jedzenia w state.food_list
        if grid[y][x] == 0 and (x, y) not in state.food_list:
            state.food_list.append((x, y))
            break

def spawn_new_powerup(grid):
    """
    Losuje wolną pozycję i spawnuje Mystery Box (skrzynkę z supermocą).
    Zapewnia brak kolizji z ciałami węży, jedzeniem oraz innymi skrzynkami.
    """
    while True:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        # Sprawdzamy czy pole w siatce jest wolne oraz czy nie ma na nim owocu bądź innej mocy
        if grid[y][x] == 0 and (x, y) not in state.food_list and (x, y) not in state.powerup_list:
            state.powerup_list.append((x, y))
            break

def check_collisions(player, x, y, grid):
    """
    Obsługuje zdarzenie wejścia głowy węża (player) na współrzędne (x, y).
    Sprawdza kolizje z:
    1. Jedzeniem (owoce): Wąż rośnie o 2 segmenty, dostaje +10 pkt, spawnuje cząsteczki i nowe jedzenie.
    2. Skrzynkami Mocy (Mystery Box): Gracz dostaje losową moc (1, 2 lub 3), +5 pkt i spawnuje nową skrzynkę.
    3. Jeśli nie zjedzono owocu: Usuwany jest najstarszy segment ogona węża w celu utrzymania właściwego tempa i długości.
    """
    ate_food = False
    
    # 1. SPRAWDZANIE KOLIZJI Z JEDZENIEM
    for fx, fy in state.food_list[:]:
        if (x, y) == (fx, fy):
            state.food_list.remove((fx, fy)) # Usunięcie zjedzonego owocu
            player.target_length += 2        # Zwiększenie limitu długości węża o 2 segmenty
            player.score += 10               # Dodanie 10 punktów do wyniku
            ate_food = True
            # Rozbłysk 15 neonowych cząsteczek o kolorze węża w miejscu zjedzenia
            spawn_particles(x * GRID_SIZE + GRID_SIZE//2, y * GRID_SIZE + GRID_SIZE//2, player.color, count=15)
            spawn_new_food(grid) # Natychmiastowe utworzenie nowego owocu na planszy
            break
            
    # 2. SPRAWDZANIE KOLIZJI Z MYSTERY BOXEM (SUPERMOCĄ)
    for px, py in state.powerup_list[:]:
        if (x, y) == (px, py):
            state.powerup_list.remove((px, py)) # Usunięcie skrzynki z planszy
            # Losowanie supermocy: 1=Przyspieszenie, 2=Zamrożenie, 3=Teleport
            player.superpower = random.choice([1, 2, 3])
            player.score += 5
            # Złote cząsteczki sukcesu (GOLD) przy zebraniu ulepszenia
            spawn_particles(x * GRID_SIZE + GRID_SIZE//2, y * GRID_SIZE + GRID_SIZE//2, GOLD, count=20)
            spawn_new_powerup(grid) # Spawnowanie nowej skrzynki w innym wolnym miejscu
            break
            
    # 3. ZARZĄDZANIE DŁUGOŚCIĄ WĘŻA (PORUSZANIE)
    # Jeśli wąż nie zjadł owocu w tej turze, jego długość w siatce powinna pozostać stała.
    # W związku z tym usuwamy ostatni segment ogona (pop) i oznaczamy pole w siatce jako puste (0).
    if not ate_food:
        if len(player.body) > player.target_length:
            tail = player.body.pop()
            grid[tail[1]][tail[0]] = 0

def spawn_move_particles(player, hx, hy):
    """
    Tworzy mikro-animacje cząsteczkowe wydobywające się z tyłu głowy węża przy ruchu.
    Wygląd i dynamika spalin zależą w pełni od wybranego motywu wizualnego.
    """
    cx = hx * GRID_SIZE + GRID_SIZE//2
    cy = hy * GRID_SIZE + GRID_SIZE//2
    # Wyliczamy punkt wylotu (tył głowy węża, przeciwny do kierunku poruszania)
    back_x = cx - player.direction[0] * (GRID_SIZE // 2)
    back_y = cy - player.direction[1] * (GRID_SIZE // 2)
    
    # MOTYW 1: Motocykle ( Tron Grid )
    # Gęsty, gasnący ślad spalin imitujący film science-fiction.
    if state.current_style == 1:
        for _ in range(3):
            # Prędkość wylotu skierowana wstecz z lekkim losowym rozrzutem
            dx = -player.direction[0] * random.uniform(0.5, 1.5) + random.uniform(-0.5, 0.5)
            dy = -player.direction[1] * random.uniform(0.5, 1.5) + random.uniform(-0.5, 0.5)
            state.particles.append(Particle(back_x, back_y, dx, dy, player.color, size=6, lifetime=20))
            
    # MOTYW 2: Neonowy Synthwave
    # Drobne, bardzo jasne i szybkie iskierki sypiące się z tyłu.
    elif state.current_style == 2:
        for _ in range(2):
            dx = -player.direction[0] * random.uniform(1.0, 2.5) + random.uniform(-1.0, 1.0)
            dy = -player.direction[1] * random.uniform(1.0, 2.5) + random.uniform(-1.0, 1.0)
            state.particles.append(Particle(back_x, back_y, dx, dy, player.color, size=3, lifetime=15))
            
    # MOTYW 3: Organiczny Wąż
    # Rzadki, unoszący się szary pył ziemny/organiczny pod wężem (40% szans na spawn)
    elif state.current_style == 3:
        if random.random() < 0.4:
            dx = random.uniform(-0.6, 0.6)
            dy = random.uniform(-0.6, 0.6)
            state.particles.append(Particle(back_x, back_y, dx, dy, (110, 95, 75), size=3, lifetime=12))

def reset_game(style):
    """
    Przywraca grę do stanu początkowego (uruchomienie nowej rozgrywki).
    - Czyści siatkę zderzeń.
    - Tworzy obiekty gracza (w lewej części) i bota AI (w prawej części).
    - Ustawia wartości siatki planszy (1 = Gracz, 2 = AI).
    - Resetuje listy owoców, skrzynek mocy oraz cząsteczek.
    - Generuje startowe 3 owoce oraz 1 Mystery Box.
    """
    state.current_style = style
    # Nowa, czysta siatka planszy 30x30 wypełniona zerami (puste pola)
    state.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    
    # KREOWANIE WĘŻY
    # Gracz startuje po lewej stronie, poruszając się w prawo (RIGHT)
    state.human = Player((COLS // 4, ROWS // 2), BLUE, RIGHT, is_ai=False)
    # Bot AI startuje po prawej stronie, poruszając się w lewo (LEFT)
    state.ai = Player((3 * COLS // 4, ROWS // 2), RED, LEFT, is_ai=True)
    
    # Umieszczenie głów startowych na siatce zderzeń
    state.grid[state.human.body[0][1]][state.human.body[0][0]] = 1
    state.grid[state.ai.body[0][1]][state.ai.body[0][0]] = 2
    
    # Czyszczenie list dynamicznych obiektów
    state.food_list = []
    state.powerup_list = []
    state.particles = []
    
    # GENEROWANIE STARTOWYCH OBIEKTÓW
    # Generowanie pierwszych 3 owoców w losowych wolnych miejscach planszy
    for _ in range(3):
        spawn_new_food(state.grid)
    # Generowanie pierwszego Mystery Boxa z supermocami
    spawn_new_powerup(state.grid)
