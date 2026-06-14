from collections import deque
import random
from constants import COLS, ROWS, UP, DOWN, LEFT, RIGHT
import state

# =====================================================================
# SILNIK WYSZUKIWANIA AI MINIMAX Z ODCIĘCIEM ALPHA-BETA
# =====================================================================

def get_legal_moves(pos, grid):
    """
    Zwraca listę dozwolonych ruchów dla węża z danej pozycji.
    Ruch jest dozwolony, gdy docelowe pole mieści się w granicach planszy
    oraz nie jest zajęte wartość w siatce grid jest 0.
    """
    moves = []
    x, y = pos
    # Iteracja po 4 podstawowych kierunkach ruchu: Góra, Dół, Lewo, Prawo
    for dx, dy in [UP, DOWN, LEFT, RIGHT]:
        nx, ny = x + dx, y + dy
        # Warunek: Czy pole mieści się na planszy i czy jest puste (0)
        if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
            moves.append((dx, dy))
    return moves

def evaluate_state(grid, ai_body, human_body):
    """
    Funkcja heurystyczna (oceny stanu gry).
    Zwraca punktową ocenę bieżącej sytuacji na planszy z perspektywy Bota AI.
    Im wyższa wartość czyli dodatnia, tym sytuacja jest lepsza dla AI.
    Im niższa wartość czyli ujemna, tym bardziej korzystna dla gracza ludzkiego.
    
    Ocena składa się z 4 głównych filarów:
    1. Podziału planszy metodą Voronoi kontrola przestrzeni
    2. Odległości do jedzenia z dynamiczną wagą długości
    3. Odległości do skrzynek z supermocami priorytet wolnego slotu
    4. Taktycznej agresji/defensywy w zależności od dystansu do gracza
    """
    ai_pos = ai_body[0]
    human_pos = human_body[0]
    
    # -----------------------------------------------------------------
    # Kontrola przestrzeni życiowej Algorytm typu Voronoi
    # -----------------------------------------------------------------

    # Tworzenie osobnej siatki odwiedzin. 
    # Wartość 1 oznacza obszar bliższy AI, a 2 obszar bliższy człowiekowi.
    visited = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    visited[ai_pos[1]][ai_pos[0]] = 1
    visited[human_pos[1]][human_pos[0]] = 2
    
    # Dwie kolejki do jednoczesnego przeszukiwania wszerz (BFS)
    q_ai = deque([ai_pos])
    q_hu = deque([human_pos])
    
    score_ai = 0 # Licznik pól, do których AI dotrze szybciej
    score_hu = 0 # Licznik pól, do których gracz dotrze szybciej
    
    # Przeszukiwanie BFS na zmianę krok po kroku
    while q_ai or q_hu:
        # Krok BFS dla AI
        next_q_ai = deque()
        while q_ai:
            cx, cy = q_ai.popleft()
            for dx, dy in [UP, DOWN, LEFT, RIGHT]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
                    if visited[ny][nx] == 0:
                        visited[ny][nx] = 1 # Oznaczenie pola jako terytorium AI
                        next_q_ai.append((nx, ny))
                        score_ai += 1
                        
        # Krok BFS dla Człowieka
        next_q_hu = deque()
        while q_hu:
            cx, cy = q_hu.popleft()
            for dx, dy in [UP, DOWN, LEFT, RIGHT]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
                    if visited[ny][nx] == 0:
                        visited[ny][nx] = 2 # Oznaczenie pola jako terytorium gracza
                        next_q_hu.append((nx, ny))
                        score_hu += 1
                        
        # Przejście do kolejnej fali przeszukiwania
        q_ai = next_q_ai
        q_hu = next_q_hu
        
    # Różnica w liczbie kontrolowanych pól planszy
    space_diff = score_ai - score_hu
    # Kontrola terytorium jest kluczowa dla unikania zapętlenia/zablokowania
    evaluation = 12.0 * space_diff
    
    # -----------------------------------------------------------------
    # Dążenie do jedzenia wzrost węża
    # -----------------------------------------------------------------
    food_score_ai = 0.0
    food_score_hu = 0.0
    if hasattr(state, 'food_list') and state.food_list:
        min_dist_food_ai = min(abs(ai_pos[0] - fx) + abs(ai_pos[1] - fy) for fx, fy in state.food_list)
        food_score_ai = 100.0 / (min_dist_food_ai + 1.0)
        
        min_dist_food_hu = min(abs(human_pos[0] - fx) + abs(human_pos[1] - fy) for fx, fy in state.food_list)
        food_score_hu = 100.0 / (min_dist_food_hu + 1.0)
        
    len_ai = len(ai_body)
    len_hu = len(human_body)
    weight_food_ai = 18.0 if len_ai <= len_hu else 6.0
    weight_food_hu = 18.0 if len_hu <= len_ai else 6.0
        
    evaluation += (weight_food_ai * food_score_ai) - (weight_food_hu * food_score_hu)
    
    # -----------------------------------------------------------------
    # Zbieranie supermocy Mystery Boxy
    # -----------------------------------------------------------------
    powerup_score_ai = 0.0
    powerup_score_hu = 0.0
    if hasattr(state, 'powerup_list') and state.powerup_list:
        min_dist_powerup_ai = min(abs(ai_pos[0] - px) + abs(ai_pos[1] - py) for px, py in state.powerup_list)
        powerup_score_ai = 100.0 / (min_dist_powerup_ai + 1.0)
        
        min_dist_powerup_hu = min(abs(human_pos[0] - px) + abs(human_pos[1] - py) for px, py in state.powerup_list)
        powerup_score_hu = 100.0 / (min_dist_powerup_hu + 1.0)
        
    weight_powerup = 300.0
    evaluation += weight_powerup * (powerup_score_ai - powerup_score_hu)
    
    # -----------------------------------------------------------------
    # Taktyka walki Agresja Defensywa
    # -----------------------------------------------------------------
    dist_to_human = abs(ai_pos[0] - human_pos[0]) + abs(ai_pos[1] - human_pos[1])
    
    if len_ai > len_hu:
        if dist_to_human <= 8:
            evaluation += 300.0 / (dist_to_human + 1.0)
        if dist_to_human <= 4:
            evaluation += 60.0 * (5.0 - dist_to_human)
    elif len_hu > len_ai:
        if dist_to_human <= 8:
            evaluation -= 300.0 / (dist_to_human + 1.0)
        if dist_to_human <= 4:
            evaluation -= 60.0 * (5.0 - dist_to_human)
            
    return evaluation

def minimax(grid, ai_body, human_body, depth, alpha, beta, is_maximizing, my_id=2, enemy_id=1):
    """
    Algorytm Minimax z optymalizacją odcięcia Alpha-Beta.
    Rekurencyjnie symuluje przyszłe ruchy obu węży, zakładając, że:
    - Bot AI stara się maksymalizować wynik (is_maximizing = True)
    - Gracz ludzki stara się minimalizować wynik AI (is_maximizing = False)
    
    Alpha-Beta zapobiega sprawdzaniu gałęzi drzewa, które na pewno nie zostaną wybrane.
    """
    ai_pos = ai_body[0]
    human_pos = human_body[0]
    
    # Pobieranie możliwych kierunków ruchów dla obu stron
    ai_moves = get_legal_moves(ai_pos, grid)
    human_moves = get_legal_moves(human_pos, grid)
    
    # Warunki graniczne rekurencji Liście drzewa
    # Obaj gracze zablokowani remis
    if not ai_moves and not human_moves:
        return 0
    # AI nie ma ruchu śmierć bota zwracamy bardzo niską ocenę ujemną
    if not ai_moves:
        return -10000 + (10 - depth) # Kara preferuje dłuższą walkę o przetrwanie
    # Gracz nie ma ruchu śmierć człowieka bardzo wysoka ocena dodatnia
    if not human_moves:
        return 10000 - (10 - depth) # Nagroda premiuje szybsze pokonanie wroga
        
    # Osiągnięcie limitu przeszukiwania zwracamy ocenę heurystyczną stanu planszy
    if depth == 0:
        return evaluate_state(grid, ai_body, human_body)
        
    # RUCH MAKSYMALIZUJĄCY Tura Bota AI
    if is_maximizing:
        max_eval = -float('inf')
        for move in ai_moves:
            nx, ny = ai_pos[0] + move[0], ai_pos[1] + move[1]
            
            # Symulacja ruchu w przód
            ai_body.appendleft((nx, ny)) # Wydłużenie głowy na nowe pole
            grid[ny][nx] = my_id         # Zapisanie pola w siatce jako ciało AI
            
            tail_popped = False
            # Skracanie ogona ruch standardowy - chyba że wąż właśnie zjadł i ma urosnąć
            # W środowisku symulacji zakładamy ruch standardowy bez natychmiastowego wzrostu
            if len(ai_body) > 1:
                tail = ai_body.pop()
                grid[tail[1]][tail[0]] = 0 # Zwolnienie starego pola ogona
                tail_popped = True
                
            # Wywołanie rekurencyjne dla tury gracza (ruch minimalizujący)
            ev = minimax(grid, ai_body, human_body, depth - 1, alpha, beta, False, my_id, enemy_id)
            
            # Kara za potencjalne zderzenie czołowe (remis)
            if abs(nx - human_body[0][0]) + abs(ny - human_body[0][1]) == 1:
                ev -= 5000
                
            # Cofnięcie symulacji w tył
            if tail_popped:
                ai_body.append(tail)       # Przywrócenie segmentu ogona
                grid[tail[1]][tail[0]] = my_id # Zablokowanie go ponownie w siatce
            grid[ny][nx] = 0               # Zwolnienie pola symulowanej głowy
            ai_body.popleft()              # Usunięcie symulowanej głowy
            
            # Aktualizacja najlepszego wyniku i wskaźnika Alpha
            max_eval = max(max_eval, ev)
            alpha = max(alpha, ev)
            # Odcięcie Alpha-Beta: Jeśli ta ścieżka jest gorsza niż wybór gracza w innej gałęzi, przerywamy pętlę
            if beta <= alpha:
                break
        return max_eval
        
    # RUCH MINIMALIZUJĄCY Tura Gracza Ludzkiego
    else:
        min_eval = float('inf')
        for move in human_moves:
            nx, ny = human_pos[0] + move[0], human_pos[1] + move[1]
            
            # Symulacja ruchu gracza
            human_body.appendleft((nx, ny))
            grid[ny][nx] = enemy_id
            
            tail_popped = False
            if len(human_body) > 1:
                tail = human_body.pop()
                grid[tail[1]][tail[0]] = 0
                tail_popped = True
                
            # Wywołanie rekurencyjne dla tury Bota AI (ruch maksymalizujący)
            ev = minimax(grid, ai_body, human_body, depth - 1, alpha, beta, True, my_id, enemy_id)
            
            # Kara za potencjalne zderzenie czołowe z perspektywy gracza minimalizującego
            # Gracz minimalizujący chce unikać remisu, więc zwiększamy wynik (co zniechęca go do tego ruchu)
            if abs(nx - ai_body[0][0]) + abs(ny - ai_body[0][1]) == 1:
                ev += 5000
                
            # Cofnięcie symulacji gracza
            if tail_popped:
                human_body.append(tail)
                grid[tail[1]][tail[0]] = enemy_id
            grid[ny][nx] = 0
            human_body.popleft()
            
            # Aktualizacja najgorszego dla AI wyniku i wskaźnika Beta
            min_eval = min(min_eval, ev)
            beta = min(beta, ev)
            # Odcięcie Alpha-Beta
            if beta <= alpha:
                break
        return min_eval

def get_best_move(grid, ai_body, human_body, depth, my_id=2, enemy_id=1, is_maximizing=True):
    """
    Funkcja wywoływana z głównej pętli gry.
    Ocenia każdy możliwy bezpośredni ruch dla głowy AI
    za pomocą rekurencyjnej analizy Minimax o zadanej głębokości depth.
    Zwraca wektor optymalnego ruchu np (0 -1) dla ruchu w górę.
    """
    best_move = None
    alpha = -float('inf')
    beta = float('inf')
    
    if is_maximizing:
        max_eval = -float('inf')
        moves = get_legal_moves(ai_body[0], grid)
        if not moves: return None
        for move in moves:
            nx, ny = ai_body[0][0] + move[0], ai_body[0][1] + move[1]
            ai_body.appendleft((nx, ny))
            grid[ny][nx] = my_id
            tail_popped = False
            if len(ai_body) > 1:
                tail = ai_body.pop()
                grid[tail[1]][tail[0]] = 0
                tail_popped = True
                
            ev = minimax(grid, ai_body, human_body, depth - 1, alpha, beta, False, my_id, enemy_id)
            
            if abs(nx - human_body[0][0]) + abs(ny - human_body[0][1]) == 1:
                ev -= 5000
                
            if tail_popped:
                ai_body.append(tail)
                grid[tail[1]][tail[0]] = my_id
            grid[ny][nx] = 0
            ai_body.popleft()
            
            if ev > max_eval:
                max_eval = ev
                best_move = move
            alpha = max(alpha, ev)
    else:
        min_eval = float('inf')
        moves = get_legal_moves(human_body[0], grid)
        if not moves: return None
        for move in moves:
            nx, ny = human_body[0][0] + move[0], human_body[0][1] + move[1]
            human_body.appendleft((nx, ny))
            grid[ny][nx] = enemy_id
            tail_popped = False
            if len(human_body) > 1:
                tail = human_body.pop()
                grid[tail[1]][tail[0]] = 0
                tail_popped = True
                
            ev = minimax(grid, ai_body, human_body, depth - 1, alpha, beta, True, my_id, enemy_id)
            
            if abs(nx - ai_body[0][0]) + abs(ny - ai_body[0][1]) == 1:
                ev += 5000
                
            if tail_popped:
                human_body.append(tail)
                grid[tail[1]][tail[0]] = enemy_id
            grid[ny][nx] = 0
            human_body.popleft()
            
            if ev < min_eval:
                min_eval = ev
                best_move = move
            beta = min(beta, ev)
            
    if best_move is None:
        best_move = random.choice(moves) if moves else None
        
    return best_move
