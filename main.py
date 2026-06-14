import pygame
import sys
import random
from constants import (WIDTH, HEIGHT, GRID_SIZE, ROWS, COLS, BLACK, WHITE, BLUE, RED, GOLD, PURPLE, GREEN, UP, DOWN, LEFT, RIGHT, LOGIC_INTERVAL)
import state
from player import Player
from ai import get_best_move
from game_logic import spawn_new_food, spawn_new_powerup, check_collisions, spawn_move_particles, reset_game
from renderer import draw_board, draw_player, draw_food, draw_powerup, draw_dashboard, draw_menu
from particles import spawn_particles, spawn_explosion, spawn_jump_particles, spawn_style_shift_particles, trigger_screen_shake

# =====================================================================
# GŁÓWNA PĘTLA I SILNIK GRY
# =====================================================================

def main():
    # Inicjalizacja biblioteki Pygame 
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cyberpunk Snake: Minimax Multiplayer AI")
    clock = pygame.time.Clock() # Służy do kontrolowania liczby klatek na sekundę (FPS)
    
    # KONTROLA STANU GRY
    # Dostępne stany: 
    # - "MENU": Wybór motywu i oczekiwanie na start
    # - "PLAYING": Aktywna rozgrywka (gracz vs bot)
    # - "GAME_OVER": Ekran końcowy z wynikiem i opcją restartu
    game_state = "MENU"  
    selected_style_menu = 1 # Domyślnie wybrany motyw: 1 (Cyberpunk)
    winner = None # Przechowuje informację o zwycięzcy ("Wygrałeś!", "Wygrał Bot AI!", "Remis!")
    frame_count = 0 # Licznik klatek renderowania, używany do animacji i synchronizacji kroków gry
    
    running = True
    # Główna pętla gry - działa nieprzerwanie do zamknięcia okna
    while running:
        frame_count += 1
        
        # -------------------------------------------------------------
        # OBSŁUGA ZDARZEŃ (WEJŚCIE UŻYTKOWNIKA)
        # -------------------------------------------------------------
        for event in pygame.event.get():
            # Kliknięcie "X" na pasku okna powoduje bezpieczne wyłączenie gry
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # OBSŁUGA KLIKNIĘĆ MYSZY (Głównie nawigacja w Menu)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "MENU":
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Sprawdzanie kliknięcia w karty wyboru motywów wizualnych
                    # Na ekranie są 3 karty ustawione obok siebie w poziomie
                    for idx in range(3):
                        card_rect = pygame.Rect(70 + idx * 250, 200, 205, 220)
                        if card_rect.collidepoint(mouse_pos):
                            selected_style_menu = idx + 1 # Ustawia styl 1, 2 lub 3
                            
                    # Sprawdzanie kliknięcia w przycisk startowy "ROZPOCZNIJ GRĘ"
                    start_rect = pygame.Rect(425 - 250, 450, 500, 30)
                    if start_rect.collidepoint(mouse_pos):
                        reset_game(selected_style_menu) # Przygotowanie nowej planszy w wybranym stylu
                        game_state = "PLAYING" # Zmiana stanu na start gry
                        frame_count = 1  # Reset licznika zapobiega usterkom z pustym ekranem przy starcie
                        
            # OBSŁUGA KLAWISZY (Ruch, Aktywacja Mocy, Skróty w Menu i GameOver)
            elif event.type == pygame.KEYDOWN:
                
                # Sterowanie w obszarze MENU
                if game_state == "MENU":
                    # Klawisze 1, 2, 3 do szybkiego wyboru motywu
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        selected_style_menu = 1
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        selected_style_menu = 2
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        selected_style_menu = 3
                    # Klawisz G do przełączania trybu gry
                    elif event.key == pygame.K_g:
                        state.game_mode = "EvE" if state.game_mode == "PvE" else "PvE"
                    # Klawisz Enter uruchamia grę
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        reset_game(selected_style_menu)
                        game_state = "PLAYING"
                        frame_count = 1  # Wymuszenie odrysowania pierwszego kadru przed kalkulacją ruchu AI
                        
                # Sterowanie w trakcie rozgrywki
                elif game_state == "PLAYING":
                    # ZMIANA KIERUNKU RUCHU WĘŻA GRACZA strzałki na klawiaturze
                    # Blokowanie możliwości ruchu w przeciwnym kierunku np. w dół gdy idziemy w górę
                    if state.game_mode == "PvE" and event.key == pygame.K_UP and state.human.direction != DOWN:
                        state.human.direction = UP
                    elif state.game_mode == "PvE" and event.key == pygame.K_DOWN and state.human.direction != UP:
                        state.human.direction = DOWN
                    elif state.game_mode == "PvE" and event.key == pygame.K_LEFT and state.human.direction != RIGHT:
                        state.human.direction = LEFT
                    elif state.game_mode == "PvE" and event.key == pygame.K_RIGHT and state.human.direction != LEFT:
                        state.human.direction = RIGHT
                        
                    # AKTYWACJA SUPERMOCY klawisz spacji
                    # Gracz musi najpierw zdobyć skrzynkę z mocą, aby móc ją odpalić
                    elif state.game_mode == "PvE" and event.key == pygame.K_SPACE:
                        # SUPERMOC 1 TURBO Przyspieszenie tempa ruchu węża
                        if state.human.superpower == 1:
                            state.human.speed_boost_timer = 15 # Działa przez 15 cykli gry
                            state.human.superpower = None      # Zużycie supermocy
                            # Efekt cząsteczek przy aktywacji turbo
                            spawn_particles(state.human.body[0][0]*GRID_SIZE + 10, state.human.body[0][1]*GRID_SIZE + 10, (0, 255, 255), count=15)
                            
                        # SUPERMOC 2 ZAMROŻENIE Zatrzymuje model gracza w miejscu na 10 cykli
                        elif state.human.superpower == 2:
                            state.human.stop_timer = 10 # Zatrzymuje model gracza na 10 cykli gry
                            state.human.superpower = None
                            trigger_screen_shake(10) # Trzęsienie ekranem przy uderzeniu fali zamrażającej
                            # Cząsteczki rozchodzące się od głowy
                            spawn_particles(state.human.body[0][0]*GRID_SIZE + 10, state.human.body[0][1]*GRID_SIZE + 10, (255, 100, 100), count=25)
                            
                        # SUPERMOC 3 TELEPORTACJA Skok o 6 pól wprzód
                        elif state.human.superpower == 3:
                            # Wyliczanie współrzędnych docelowych (6 pól przed głową, w aktualnym kierunku ruchu)
                            lx = state.human.body[0][0] + state.human.direction[0] * 6
                            ly = state.human.body[0][1] + state.human.direction[1] * 6
                            
                            # Teleportacja jest efektywna tylko wtedy, gdy cel znajduje się na planszy i pole docelowe jest wolne (wartość 0 w siatce)
                            if 0 <= lx < COLS and 0 <= ly < ROWS and state.grid[ly][lx] == 0:
                                old_head = state.human.body[0]
                                state.human.body.appendleft((lx, ly)) # Wstawienie nowej głowy na pozycję docelową
                                state.grid[ly][lx] = 1 # Oznaczenie pola w siatce jako zajęte przez gracza
                                check_collisions(state.human, lx, ly, state.grid) # Sprawdzanie kolizji z jedzeniem/mocą
                                spawn_jump_particles(old_head, (lx, ly), state.human.color) # Powstawanie cząsteczek tworzących ślad między punktem startu a punktem skoku
                                trigger_screen_shake(10)
                                state.human.superpower = None
                            else:
                                # Teleportacja zablokowana (przeszkoda na drodze) - krótki czerwony rozbłysk cząsteczek błędu
                                spawn_particles(state.human.body[0][0]*GRID_SIZE + 10, state.human.body[0][1]*GRID_SIZE + 10, (255, 0, 0), count=5)
                                
                    # ZMIANA MOTYWU GRY W TRAKCIE ROZGRYWKI (zmiana wizualna planszy)
                    # Pozwala zmienić dynamicznie całą oprawę wizualną areny za pomocą klawiszy 1, 2, 3
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        state.current_style = 1 # Zmiana stylu na 1 (Cyberpunk / Niebieski)
                        spawn_style_shift_particles(BLUE) # Rozbłysk niebieskich cząsteczek na całej planszy
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        state.current_style = 2 # Zmiana stylu na 2 (Synthwave / Fioletowy)
                        spawn_style_shift_particles(PURPLE) # Rozbłysk fioletowych cząsteczek
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        state.current_style = 3 # Zmiana stylu na 3 (Acid / Zielony)
                        spawn_style_shift_particles(GREEN) # Rozbłysk zielonych cząsteczek
                        
                # Sterowanie po przegranej / wygranej
                elif game_state == "GAME_OVER":
                    # Klawisz R - natychmiastowy restart w wybranym przed chwilą motywie
                    if event.key == pygame.K_r:
                        reset_game(state.current_style)
                        game_state = "PLAYING"
                        frame_count = 1
                    # Klawisz M - powrót do głównego menu gry
                    elif event.key == pygame.K_m:
                        game_state = "MENU"
                        
        # -------------------------------------------------------------
        # 2. SILNIK FIZYKI CZĄSTECZEK
        # -------------------------------------------------------------
        # Aktualizacja pozycji, prędkości oraz czasu trwania wszystkich efektów cząsteczkowych
        for p in state.particles[:]:
            p.update()
            if p.lifetime <= 0:
                state.particles.remove(p) # Usunięcie cząsteczek, które zgasły
                
        # -------------------------------------------------------------
        # 3. PĘTLA LOGIKI ROZGRYWKI 
        # -------------------------------------------------------------
        # Ta sekcja decyduje o fizycznym przesunięciu węży. Dzięki LOGIC_INTERVAL ruch
        # nie następuje co klatkę 60 FPS, lecz w kontrolowanym tempie.
        if game_state == "PLAYING":
            if frame_count % LOGIC_INTERVAL == 0:
                
                # INTELIGENTNE UŻYCIE SUPERMOCY PRZEZ BOTA AI
                # Jeśli bot posiada supermoc TURBO (1), nie jest aktualnie przyspieszony i jest blisko gracza:
                if state.ai.superpower == 1 and state.ai.speed_boost_timer == 0 and state.ai.alive:
                    dist = abs(state.ai.body[0][0] - state.human.body[0][0]) + abs(state.ai.body[0][1] - state.human.body[0][1])
                    if dist < 12: # Aktywacja, gdy dystans manhattan wynosi poniżej 12 pól
                        state.ai.speed_boost_timer = 15
                        state.ai.superpower = None
                        spawn_particles(state.ai.body[0][0]*GRID_SIZE + 10, state.ai.body[0][1]*GRID_SIZE + 10, (0, 255, 255), count=15)
                
                if state.game_mode == "EvE" and state.human.superpower == 1 and state.human.speed_boost_timer == 0 and state.human.alive:
                    dist = abs(state.human.body[0][0] - state.ai.body[0][0]) + abs(state.human.body[0][1] - state.ai.body[0][1])
                    if dist < 12:
                        state.human.speed_boost_timer = 15
                        state.human.superpower = None
                        spawn_particles(state.human.body[0][0]*GRID_SIZE + 10, state.human.body[0][1]*GRID_SIZE + 10, (0, 255, 255), count=15)
                
                # OBLICZANIE KROKÓW RUCHU W TURE
                # Standardowy ruch to 1 pole na turę.
                # Turbo daje 2 pola na turę.
                # Zamrożenie daje 0 pól na turę.
                human_steps = 2 if state.human.speed_boost_timer > 0 else (0 if state.human.stop_timer > 0 else 1)
                ai_steps = 2 if state.ai.speed_boost_timer > 0 else (0 if state.ai.stop_timer > 0 else 1)
                
                # Zmniejszanie liczników aktywnych efektów czasowych
                if state.human.speed_boost_timer > 0:
                    state.human.speed_boost_timer -= 1
                if state.ai.speed_boost_timer > 0:
                    state.ai.speed_boost_timer -= 1
                    
                if state.human.stop_timer > 0:
                    state.human.stop_timer -= 1
                if state.ai.stop_timer > 0:
                    state.ai.stop_timer -= 1
                    
                # WYKONANIE KROKÓW RUCHU W SIATCE GRY
                # Pętla wykonuje się tyle razy, ile wynosi największa liczba kroków któregoś z węży (np. 2, jeśli ktoś ma turbo)
                max_steps = max(human_steps, ai_steps)
                for step in range(max_steps):
                    h_moves = (step < human_steps) and state.human.alive
                    a_moves = (step < ai_steps) and state.ai.alive
                    
                    if not h_moves and not a_moves:
                        continue
                        
                    h_dir = state.human.direction
                    
                    if state.game_mode == "EvE" and h_moves:
                        best_move_h = get_best_move(state.grid, state.ai.body, state.human.body, depth=1, my_id=2, enemy_id=1, is_maximizing=False)
                        if best_move_h:
                            h_dir = best_move_h
                            state.human.direction = best_move_h
                        else:
                            if state.human.superpower == 2:
                                state.human.stop_timer = 15
                                state.human.superpower = None
                                trigger_screen_shake(12)
                                spawn_particles(state.human.body[0][0]*GRID_SIZE + 10, state.human.body[0][1]*GRID_SIZE + 10, state.human.color, count=25)
                                h_moves = False
                            elif state.human.superpower == 3:
                                lx = state.human.body[0][0] + state.human.direction[0] * 6
                                ly = state.human.body[0][1] + state.human.direction[1] * 6
                                if 0 <= lx < COLS and 0 <= ly < ROWS and state.grid[ly][lx] == 0:
                                    old_head = state.human.body[0]
                                    state.human.body.appendleft((lx, ly))
                                    state.grid[ly][lx] = 1
                                    check_collisions(state.human, lx, ly, state.grid)
                                    spawn_jump_particles(old_head, (lx, ly), state.human.color)
                                    trigger_screen_shake(12)
                                    state.human.superpower = None
                                    h_moves = False
                                else:
                                    jumped = False
                                    for d in [UP, DOWN, LEFT, RIGHT]:
                                        lx = state.human.body[0][0] + d[0] * 6
                                        ly = state.human.body[0][1] + d[1] * 6
                                        if 0 <= lx < COLS and 0 <= ly < ROWS and state.grid[ly][lx] == 0:
                                            state.human.direction = d
                                            old_head = state.human.body[0]
                                            state.human.body.appendleft((lx, ly))
                                            state.grid[ly][lx] = 1
                                            check_collisions(state.human, lx, ly, state.grid)
                                            spawn_jump_particles(old_head, (lx, ly), state.human.color)
                                            trigger_screen_shake(12)
                                            state.human.superpower = None
                                            h_moves = False
                                            jumped = True
                                            break
                                    if not jumped:
                                        h_dir = state.human.direction
                            else:
                                h_dir = state.human.direction
                                
                    a_dir = None
                    
                    # LOGIKA BOTA AI (ALGORYTM MINIMAX)
                    if a_moves:
                        # Algorytm przeszukuje drzewo ruchów do głębokości 3 co eliminuje lagi.
                        best_move = get_best_move(state.grid, state.ai.body, state.human.body, depth=1)
                        if best_move:
                            a_dir = best_move
                            state.ai.direction = best_move
                        else:
                            # Awaryjne użycie supermocy przez bota gdy algorytm nie widzi bezpiecznych pól
                            if state.ai.superpower == 2:  # Zamrożenie modelu w miejscu w celu uniknięcia kolizji
                                state.ai.stop_timer = 15
                                state.ai.superpower = None
                                trigger_screen_shake(12)
                                spawn_particles(state.ai.body[0][0]*GRID_SIZE + 10, state.ai.body[0][1]*GRID_SIZE + 10, state.ai.color, count=25)
                                a_moves = False
                            elif state.ai.superpower == 3:  # Awaryjny teleport ratunkowy o 6 pól
                                # Próba teleportacji prosto przed siebie
                                lx = state.ai.body[0][0] + state.ai.direction[0] * 6
                                ly = state.ai.body[0][1] + state.ai.direction[1] * 6
                                if 0 <= lx < COLS and 0 <= ly < ROWS and state.grid[ly][lx] == 0:
                                    old_head = state.ai.body[0]
                                    state.ai.body.appendleft((lx, ly))
                                    state.grid[ly][lx] = 2
                                    check_collisions(state.ai, lx, ly, state.grid)
                                    spawn_jump_particles(old_head, (lx, ly), state.ai.color)
                                    trigger_screen_shake(12)
                                    state.ai.superpower = None
                                    a_moves = False
                                else:
                                    # Próba teleportacji w jakimkolwiek innym, wolnym kierunku
                                    jumped = False
                                    for d in [UP, DOWN, LEFT, RIGHT]:
                                        lx = state.ai.body[0][0] + d[0] * 6
                                        ly = state.ai.body[0][1] + d[1] * 6
                                        if 0 <= lx < COLS and 0 <= ly < ROWS and state.grid[ly][lx] == 0:
                                            state.ai.direction = d
                                            old_head = state.ai.body[0]
                                            state.ai.body.appendleft((lx, ly))
                                            state.grid[ly][lx] = 2
                                            check_collisions(state.ai, lx, ly, state.grid)
                                            spawn_jump_particles(old_head, (lx, ly), state.ai.color)
                                            trigger_screen_shake(12)
                                            state.ai.superpower = None
                                            a_moves = False
                                            jumped = True
                                            break
                                    if not jumped:
                                        a_dir = state.ai.direction # Ruch w dotychczasową stronę i zderzenie o ile nie nastąpił wcześniej wybór innego kierunku
                            else:
                                a_dir = state.ai.direction
                                
                    # Obliczenie kolejnych koordynatów głowy gracza i AI na planszy
                    next_h = (state.human.body[0][0] + h_dir[0], state.human.body[0][1] + h_dir[1]) if h_moves else None
                    next_a = (state.ai.body[0][0] + a_dir[0], state.ai.body[0][1] + a_dir[1]) if (a_moves and a_dir) else None
                    
                    # KOLIZJA CZOŁOWA
                    if h_moves and a_moves and next_h == next_a:
                        state.human.alive = False
                        state.ai.alive = False
                        spawn_explosion(next_h[0]*GRID_SIZE, next_h[1]*GRID_SIZE, state.human.color)
                        spawn_explosion(next_a[0]*GRID_SIZE, next_a[1]*GRID_SIZE, state.ai.color)
                        trigger_screen_shake(16)
                        break
                        
                    # AKCEPTACJA I ZATWIERDZENIE RUCHU GRACZA
                    if h_moves:
                        hx, hy = next_h
                        # Sprawdzenie czy gracz nie uderzy w ścianę lub inny segment węża wartość != 0 w siatce
                        if 0 <= hx < COLS and 0 <= hy < ROWS and state.grid[hy][hx] == 0:
                            state.human.body.appendleft((hx, hy)) # Dodanie segmentu z przodu
                            state.grid[hy][hx] = 1 # Oznaczenie w pamięci siatki planszy jako "Gracz 1"
                            check_collisions(state.human, hx, hy, state.grid) # Sprawdzenie czy zjedzono owoc/moc
                            spawn_move_particles(state.human, hx, hy) # Mały ślad cząsteczek za ogonem
                        else:
                            # Kolizja i śmierć gracza
                            state.human.alive = False
                            spawn_explosion(state.human.body[0][0]*GRID_SIZE, state.human.body[0][1]*GRID_SIZE, state.human.color)
                            trigger_screen_shake(16)
                            
                    # AKCEPTACJA I ZATWIERDZENIE RUCHU BOTA AI
                    if a_moves and a_dir:
                        ax, ay = next_a
                        # Sprawdzenie wolnego miejsca dla AI
                        if 0 <= ax < COLS and 0 <= ay < ROWS and state.grid[ay][ax] == 0:
                            state.ai.body.appendleft((ax, ay)) # Dodanie segmentu z przodu AI
                            state.grid[ay][ax] = 2 # Oznaczenie w pamięci siatki planszy jako "AI"
                            check_collisions(state.ai, ax, ay, state.grid) # Sprawdzenie czy zjedzono owoc/moc
                            spawn_move_particles(state.ai, ax, ay) # Mały ślad cząsteczek za ogonem
                        else:
                            # Kolizja i śmierć AI
                            state.ai.alive = False
                            spawn_explosion(state.ai.body[0][0]*GRID_SIZE, state.ai.body[0][1]*GRID_SIZE, state.ai.color)
                            trigger_screen_shake(16)
                            
                # KONTROLA KOŃCA ROZGRYWKI
                if not state.human.alive or not state.ai.alive:
                    game_state = "GAME_OVER"
                    if not state.human.alive and not state.ai.alive:
                        winner = "Remis!"
                    elif not state.human.alive:
                        winner = "Wygrał Bot MAKSYMALIZUJĄCY!" if state.game_mode == "EvE" else "Wygrał Bot AI!"
                    else:
                        winner = "Wygrał Bot MINIMALIZUJĄCY!" if state.game_mode == "EvE" else "Wygrałeś!"
                        
        # -------------------------------------------------------------
        # 4. RENDEROWANIE GRAFIKI
        # -------------------------------------------------------------
        # Użycie pomocniczej powierzchni primary_surface z obsługą przezroczystości (alfa)
        # dla uzyskania neonowych przejść i poświaty
        primary_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Ekran A: RENDEROWANIE MENU GŁÓWNEGO
        if game_state == "MENU":
            draw_menu(primary_surface, selected_style_menu, frame_count)
            
        # Ekran B: RENDEROWANIE GRY (PLAYING / GAME_OVER)
        elif game_state == "PLAYING" or game_state == "GAME_OVER":
            # Rysowanie tła areny, siatki neonowej dopasowanej do motywu
            draw_board(primary_surface, state.current_style)
            
            # Rysowanie animowanych cząstek jedzenia (owoce)
            for fx, fy in state.food_list:
                draw_food(primary_surface, fx, fy, state.current_style, frame_count)
                
            # Rysowanie skrzynek z supermocami
            for px, py in state.powerup_list:
                draw_powerup(primary_surface, px, py, state.current_style, frame_count)
                
            # Rysowanie obu węży (Węża Gracza oraz Węża AI)
            draw_player(primary_surface, state.human, state.current_style)
            draw_player(primary_surface, state.ai, state.current_style)
            
            # Rysowanie aktywnych cząsteczek wybuchów, skoków i ruchu
            for p in state.particles:
                p.draw(primary_surface)
                
            # Rysowanie bocznego panelu z punktacją, legendą klawiszy i stanem mocy
            draw_dashboard(primary_surface, state.human, state.ai, state.current_style, frame_count)
            
            # Nakładka przyciemniająca w tle ekranu Game Over
            if game_state == "GAME_OVER":
                overlay = pygame.Surface((600, 600), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 190)) 
                primary_surface.blit(overlay, (0, 0))
                
                font_large = pygame.font.SysFont("Impact", 44)
                font_med = pygame.font.SysFont("Consolas", 18)
                
                # Dobór koloru tekstu w zależności od tego, kto wygrał
                text_win = font_large.render(winner, True, GOLD if winner == "Wygrałeś!" else (RED if winner == "Wygrał Bot AI!" else (190, 190, 190)))
                text_win_rect = text_win.get_rect(center=(300, 240))
                
                # Dodatkowy efekt trójwymiarowego cienia pod głównym napisem
                text_win_shadow = font_large.render(winner, True, BLACK)
                primary_surface.blit(text_win_shadow, text_win_rect.move(2, 2))
                primary_surface.blit(text_win, text_win_rect)
                
                # Wyświetlenie instrukcji dla ekranu porażki/zwycięstwa
                text_restart = font_med.render("Naciśnij [R] aby Zagrać Ponownie", True, (255, 255, 255))
                primary_surface.blit(text_restart, text_restart.get_rect(center=(300, 310)))
                
                text_menu = font_med.render("Naciśnij [M] aby powrócić do Menu", True, (170, 170, 185))
                primary_surface.blit(text_menu, text_menu.get_rect(center=(300, 340)))
                
        # -------------------------------------------------------------
        # 5. EFEKT WSTRZĄSU EKRANEM
        # -------------------------------------------------------------
        # Gdy wąż uderzy w przeszkodę lub aktywuje moc zamrażania/teleportu,
        # obraz jest lekko przesunięty o losową wartość pikseli shake_x/shake_y.
        shake_x = 0
        shake_y = 0
        if state.screen_shake_timer > 0:
            state.screen_shake_timer -= 1
            shake_x = random.randint(-4, 4)
            shake_y = random.randint(-4, 4)
            
        # Naniesienie wyrenderowanego obrazu na główne okno programu
        screen.blit(primary_surface, (shake_x, shake_y))
        pygame.display.flip() # Przełączenie buforów ekranu co zapobiega migotaniu
        clock.tick(60) # Stałe tempo 60 klatek na sekundę

if __name__ == "__main__":
    main()
