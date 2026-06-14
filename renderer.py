import pygame
import math
import random
import state
from constants import (GRID_SIZE, WHITE, BLACK, BLUE, RED, GREEN, PURPLE, GOLD)
from particles import draw_transparent_circle

# =====================================================================
# MODUŁ RENDEROWANIA GRAFIKI I EFEKTÓW WIZUALNYCH (SILNIK GRAFICZNY)
# =====================================================================

def draw_rotated_rect(surface, color, center, size, angle):
    """
    Rysuje obrócony prostokąt o zadany kąt wokół jego środka.
    Wykorzystuje tymczasową przezroczystą powierzchnię (Surface), 
    dokonuje obrotu metodą pygame.transform.rotate, a następnie
    nakłada obrócony kształt na docelowy obraz (blit).
    """
    # Tworzenie tymczasowego obrazu kwadratowego o wymiarach size z obsługą kanału alfa (przezroczystości)
    s = pygame.Surface(size, pygame.SRCALPHA)
    # Narysowanie prostokąta o zaokrąglonych rogach (border_radius=4)
    pygame.draw.rect(s, color, (0, 0, *size), border_radius=4)
    # Obrót powierzchni o kąt (w stopniach)
    rotated = pygame.transform.rotate(s, angle)
    # Pobranie kontenera (rect) obróconej grafiki i wyśrodkowanie na pozycji center
    rect = rotated.get_rect(center=center)
    # Naniesienie obróconej grafiki na planszę główną
    surface.blit(rotated, rect.topleft)

def draw_rotated_rect_glow(surface, color, center, size, angle):
    """
    Rysuje zaawansowany obrócony prostokąt z efektem świecącego neonu (Glow).
    Nakłada dwie warstwy:
    1. Zewnętrzną warstwę rozmytej, półprzezroczystej poświaty neonowej (alfa 45).
    2. Wewnętrzny, jasny i ostry rdzeń neonu.
    """
    # WARSTWA 1: Rozmyta poświata (Glow)
    # Tworzymy dwukrotnie większą tymczasową powierzchnię, by zmieścić cień/poświatę
    s_glow = pygame.Surface((size[0]*2, size[1]*2), pygame.SRCALPHA)
    # Rysowanie poświaty z niskim współczynnikiem krycia (alfa = 45/255)
    pygame.draw.rect(s_glow, (*color, 45), (size[0]//2, size[1]//2, *size), border_radius=6)
    rotated_glow = pygame.transform.rotate(s_glow, angle)
    rect_glow = rotated_glow.get_rect(center=center)
    surface.blit(rotated_glow, rect_glow.topleft)
    
    # WARSTWA 2: Jasny rdzeń (rdzeń z obwódką)
    s = pygame.Surface(size, pygame.SRCALPHA)
    # Rysowanie białego jądra w środku dla efektu neonu
    pygame.draw.rect(s, (255, 255, 255), (0, 0, *size), border_radius=4)
    # Nakładamy na to kolorową obwódkę
    pygame.draw.rect(s, color, (2, 2, size[0]-4, size[1]-4), border_radius=3, width=2)
    rotated = pygame.transform.rotate(s, angle)
    rect = rotated.get_rect(center=center)
    surface.blit(rotated, rect.topleft)

def draw_board(screen, style):
    """
    Rysuje siatkę i tło areny gry w zależności od wybranego motywu graficznego.
    """
    # MOTYW 1: Styl Motocykli / Tron Grid (Cyberpunk)
    if style == 1:  
        screen.fill((16, 16, 26)) # Ciemne granatowe tło
        # Pionowe linie siatki o kolorze ciemnego fioletu
        for x in range(0, 600, GRID_SIZE):
            pygame.draw.line(screen, (32, 32, 48), (x, 0), (x, 600))
        # Poziome linie siatki
        for y in range(0, 600, GRID_SIZE):
            pygame.draw.line(screen, (32, 32, 48), (0, y), (600, y))
            
    # MOTYW 2: Świecący Styl Neonowy (Synthwave)
    elif style == 2:  
        screen.fill((6, 6, 12)) # Bardzo głęboka czerń kosmiczna
        # Ciemnoniebieskie linie siatki
        for x in range(0, 600, GRID_SIZE):
            pygame.draw.line(screen, (15, 30, 65), (x, 0), (x, 600))
        for y in range(0, 600, GRID_SIZE):
            pygame.draw.line(screen, (15, 30, 65), (0, y), (600, y))
            
    # MOTYW 3: Klasyczny Wąż (Organic Arena)
    elif style == 3:  
        screen.fill((22, 38, 22)) # Ciemnozielona trawiasta plansza
        # Delikatne leśne zielone linie siatki
        for x in range(0, 600, GRID_SIZE):
            pygame.draw.line(screen, (30, 48, 30), (x, 0), (x, 600))
        for y in range(0, 600, GRID_SIZE):
            pygame.draw.line(screen, (30, 48, 30), (0, y), (600, y))

def draw_player(screen, player, style):
    """
    Rysuje węża (gracza lub bota) na planszy.
    Wygląd ciała, głowy i efektów ogona różni się w zależności od aktywnego motywu.
    """
    if not player.alive:
        return # Martwy wąż nie jest rysowany (wybucha wcześniej)
        
    color = player.color
    head_pos = player.body[0]
    hx, hy = head_pos[0] * GRID_SIZE, head_pos[1] * GRID_SIZE
    cx, cy = hx + GRID_SIZE//2, hy + GRID_SIZE//2 # Środek głowy węża
    
    # Klawisze stałe kierunku dla rotacji postaci
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    
    # -----------------------------------------------------------------
    # STYL 1: ŚCIGACZE TRON (Wektorowe Motocykle)
    # -----------------------------------------------------------------
    if style == 1:
        # A. Rysowanie zanikającego spalinowego śladu (ogona)
        for idx, pos in enumerate(reversed(list(player.body)[1:])):
            real_idx = len(player.body) - 1 - idx
            # Współczynnik wieku segmentu (od 0.0 na końcu ogona do 1.0 przy głowie)
            age_pct = 1.0 - (real_idx / len(player.body))
            alpha = int(age_pct * 190) # Ślad staje się przezroczysty na końcu ogona
            radius = int(GRID_SIZE * 0.45 * (0.3 + 0.7 * age_pct)) # Ogon zwęża się na końcu
            cx_tail = pos[0] * GRID_SIZE + GRID_SIZE//2
            cy_tail = pos[1] * GRID_SIZE + GRID_SIZE//2
            draw_transparent_circle(screen, color, (cx_tail, cy_tail), radius, alpha)
            
        # B. Rysowanie motocykla (jako głowy węża)
        bike_width, bike_height = int(GRID_SIZE * 0.8), int(GRID_SIZE * 0.45)
        bike_surf = pygame.Surface((bike_width, bike_height), pygame.SRCALPHA)
        # Narysowanie kół motocykla
        pygame.draw.ellipse(bike_surf, (45, 45, 45), (2, 1, int(bike_width*0.25), int(bike_height*0.8)))
        pygame.draw.ellipse(bike_surf, (45, 45, 45), (bike_width - int(bike_width*0.25) - 2, 1, int(bike_width*0.25), int(bike_height*0.8)))
        # Narysowanie korpusu/karoserii
        pygame.draw.rect(bike_surf, color, (int(bike_width*0.2), 0, int(bike_width*0.6), bike_height), border_radius=3)
        # Szyba przednia kierowcy
        pygame.draw.rect(bike_surf, (255, 255, 255), (int(bike_width*0.45), 2, int(bike_width*0.25), bike_height - 4), border_radius=1)
        
        # Obliczanie kąta obrotu motocykla na podstawie kierunku ruchu
        angle = 0
        if player.direction == UP: angle = 90
        elif player.direction == DOWN: angle = 270
        elif player.direction == LEFT: angle = 180
        else: angle = 0 # W PRAWO
        
        rotated_bike = pygame.transform.rotate(bike_surf, angle)
        bike_rect = rotated_bike.get_rect(center=(cx, cy))
        screen.blit(rotated_bike, bike_rect)
        
        # C. Reflektor przedni (stożek światła przed motocyklem)
        glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        # Rysowanie trójkątnego strumienia światła
        pygame.draw.polygon(glow_surf, (*color, 45), [(0, 30), (60, 10), (60, 50)])
        rotated_glow = pygame.transform.rotate(glow_surf, angle)
        glow_rect = rotated_glow.get_rect(center=(cx + player.direction[0]*16, cy + player.direction[1]*16))
        screen.blit(rotated_glow, glow_rect)

    # -----------------------------------------------------------------
    # STYL 2: MOTYW NEONOWY (Świecący wąż z poświatą)
    # -----------------------------------------------------------------
    elif style == 2:
        # A. Rysowanie świecącego neonowego śladu ciała
        for idx, pos in enumerate(reversed(list(player.body)[1:])):
            cx_tail = pos[0] * GRID_SIZE + GRID_SIZE//2
            cy_tail = pos[1] * GRID_SIZE + GRID_SIZE//2
            # Poświata składa się z trzech warstw o różnej przezroczystości i rozmiarze:
            draw_transparent_circle(screen, color, (cx_tail, cy_tail), int(GRID_SIZE * 0.55), 45)  # Szerokie halo
            draw_transparent_circle(screen, color, (cx_tail, cy_tail), int(GRID_SIZE * 0.35), 110) # Średni neon
            draw_transparent_circle(screen, (255, 255, 255), (cx_tail, cy_tail), int(GRID_SIZE * 0.15), 255) # Super jasny środek
            
        # B. Rysowanie świecącej głowy
        draw_transparent_circle(screen, color, (cx, cy), int(GRID_SIZE * 0.85), 65)  # Bardzo szerokie rozmycie głowy
        draw_transparent_circle(screen, color, (cx, cy), int(GRID_SIZE * 0.55), 160) # Neon głowy
        draw_transparent_circle(screen, (255, 255, 255), (cx, cy), int(GRID_SIZE * 0.3), 255) # Białe jądro energetyczne

    # -----------------------------------------------------------------
    # STYL 3: KLASYCZNY WĄŻ (Styl organiczny / retro)
    # -----------------------------------------------------------------
    elif style == 3:
        # A. Rysowanie zachodzących na siebie łusek
        for idx, pos in enumerate(reversed(list(player.body)[1:])):
            real_idx = len(player.body) - 1 - idx
            age_pct = 1.0 - (real_idx / len(player.body))
            # Łuski stają się mniejsze pod koniec ogona
            radius = int(GRID_SIZE * 0.46 * (0.45 + 0.55 * age_pct))
            cx_tail = pos[0] * GRID_SIZE + GRID_SIZE//2
            cy_tail = pos[1] * GRID_SIZE + GRID_SIZE//2
            
            # Wąż ma naprzemienne barwy łusek (główny kolor oraz ciemniejszy odcień) dla efektu trójwymiaru
            seg_color = color if real_idx % 2 == 0 else tuple(max(0, c - 45) for c in color)
            pygame.draw.circle(screen, seg_color, (cx_tail, cy_tail), radius)
            pygame.draw.circle(screen, (10, 10, 10), (cx_tail, cy_tail), radius, 1) # Ciemny kontur łuski
            
        # B. Rysowanie okrągłej głowy węża
        pygame.draw.circle(screen, color, (cx, cy), int(GRID_SIZE * 0.52))
        pygame.draw.circle(screen, (10, 10, 10), (cx, cy), int(GRID_SIZE * 0.52), 1)
        
        # C. Rysowanie oczu węża reagujących na kierunek patrzenia
        eye_rad = 3
        pupil_rad = 1
        if player.direction == UP:
            eye1 = (cx - 4, cy - 3)
            eye2 = (cx + 4, cy - 3)
        elif player.direction == DOWN:
            eye1 = (cx - 4, cy + 3)
            eye2 = (cx + 4, cy + 3)
        elif player.direction == LEFT:
            eye1 = (cx - 3, cy - 4)
            eye2 = (cx - 3, cy + 4)
        else: # W PRAWO
            eye1 = (cx + 3, cy - 4)
            eye2 = (cx + 3, cy + 4)
            
        pygame.draw.circle(screen, WHITE, eye1, eye_rad)
        pygame.draw.circle(screen, WHITE, eye2, eye_rad)
        pygame.draw.circle(screen, BLACK, eye1, pupil_rad)
        pygame.draw.circle(screen, BLACK, eye2, pupil_rad)
        
        # D. Wysuwający się czerwony język węża
        tongue_x = cx + player.direction[0] * 12
        tongue_y = cy + player.direction[1] * 12
        pygame.draw.line(screen, (240, 40, 40), (cx, cy), (tongue_x, tongue_y), 2)

def draw_food(screen, fx, fy, style, frame_count):
    """
    Rysuje jedzenie na arenie.
    Wygląd i pulsacja dopasowują się do wybranego motywu.
    """
    cx = fx * GRID_SIZE + GRID_SIZE//2
    cy = fy * GRID_SIZE + GRID_SIZE//2
    # Efekt pulsowania promienia (wykorzystuje sinus czasu klatek)
    pulse = math.sin(frame_count * 0.15) * 2
    
    # MOTYW 1: Ogniwo baterii (dla ścigaczy)
    if style == 1:  
        radius = int(GRID_SIZE * 0.35 + pulse)
        # Zielony rdzeń baterii
        pygame.draw.rect(screen, (0, 255, 100), (cx - 5, cy - 7, 10, 14), border_radius=2)
        # Biała nasadka baterii
        pygame.draw.rect(screen, WHITE, (cx - 3, cy - 9, 6, 2))
        # Półprzezroczysta neonowa poświata wokół baterii
        draw_transparent_circle(screen, (0, 255, 100), (cx, cy), radius + 4, 55)
        
    # MOTYW 2: Świecąca neonowa kula
    elif style == 2:  
        radius = int(GRID_SIZE * 0.38 + pulse)
        draw_transparent_circle(screen, PURPLE, (cx, cy), radius + 7, 45) # Fioletowa poświata zewnętrzna
        draw_transparent_circle(screen, PURPLE, (cx, cy), radius + 2, 130) # Wewnętrzna poświata fioletowa
        draw_transparent_circle(screen, WHITE, (cx, cy), radius - 1, 255)  # Biały jasny środek
        
    # MOTYW 3: Czerwone jabłuszko
    elif style == 3:  
        radius = int(GRID_SIZE * 0.4 + pulse)
        # Czerwony owoc
        pygame.draw.circle(screen, (225, 30, 30), (cx, cy + 2), radius)
        # Brązowy ogonek
        pygame.draw.line(screen, (100, 60, 30), (cx, cy - 2), (cx + 2, cy - 8), 2)
        # Zielony listek
        pygame.draw.ellipse(screen, (30, 180, 50), (cx + 1, cy - 9, 6, 3))

def draw_powerup(screen, px, py, style, frame_count):
    """
    Rysuje Mystery Box (skrzynkę z supermocą).
    Skrzynki obracają się wokół własnej osi z efektem pulsowania rozmiaru.
    """
    cx = px * GRID_SIZE + GRID_SIZE//2
    cy = py * GRID_SIZE + GRID_SIZE//2
    # Prędkość kątowa obracania w czasie
    angle = (frame_count * 4.5) % 360
    pulse = math.sin(frame_count * 0.12) * 2.5
    
    # MOTYW 1 i 3: Złota obracająca się skrzynka z pytajnikiem
    if style == 1 or style == 3:  
        size = int(GRID_SIZE * 0.72 + pulse)
        draw_rotated_rect(screen, GOLD, (cx, cy), (size, size), angle)
        # Rysowanie znaku zapytania na środku skrzynki
        font = pygame.font.SysFont("Consolas", 14, bold=True)
        text = font.render("?", True, BLACK)
        text_rect = text.get_rect(center=(cx, cy))
        screen.blit(text, text_rect)
        
    # MOTYW 2: Błyszczący, wirujący diament z poświatą neonową
    elif style == 2:  
        size = int(GRID_SIZE * 0.76 + pulse)
        draw_rotated_rect_glow(screen, GOLD, (cx, cy), (size, size), angle)

# =====================================================================
# INTERFEJS - PANEL BOCZNY (STATYSTYKI, STAN MOCY, STEROWANIE)
# =====================================================================

def draw_dashboard(surface, human, ai, style_index, frame_count):
    """
    Rysuje prawy boczny panel interfejsu (Dashboard).
    Pokazuje aktualny motyw planszy, wyniki i ulepszenia graczy oraz legendę klawiszy.
    """
    # 1. Podkład / tło panelu
    panel_rect = pygame.Rect(600, 0, 350, 600)
    pygame.draw.rect(surface, (22, 22, 32), panel_rect)
    # Linia odgradzająca arenę gry od panelu bocznego
    pygame.draw.line(surface, (60, 60, 85), (600, 0), (600, 600), 2)
    
    # 2. Główny tytuł gry "CYBER SNAKE" z neonowym pulsowaniem koloru
    font_title = pygame.font.SysFont("Impact", 24)
    pulse = int(140 + 115 * math.sin(frame_count * 0.08))
    title_color = (0, pulse, 255) # Pulsowanie w odcieniach błękitu i cyjanu
    title_text = font_title.render("CYBER SNAKE", True, title_color)
    surface.blit(title_text, (620, 20))
    
    # 3. Informacja o aktywnym motywie graficznym planszy
    font_style = pygame.font.SysFont("Consolas", 13)
    style_names = {1: "MOTOCYKLE", 2: "MOTYW NEONOWY", 3: "MOTYW WĘŻA"}
    style_text = font_style.render(f"MOTYW [1-3]: {style_names[style_index]}", True, (190, 190, 190))
    surface.blit(style_text, (620, 55))
    
    # Linia podziału
    pygame.draw.line(surface, (45, 45, 65), (610, 80), (940, 80), 1)
    
    # 4. Sekcja Gracza 1
    player1_name = "BOT MINIMALIZUJĄCY" if state.game_mode == "EvE" else "GRACZ 1 (TY)"
    draw_player_info(surface, 620, 95, player1_name, human, BLUE, frame_count)
    
    pygame.draw.line(surface, (45, 45, 65), (610, 290), (940, 290), 1)
    
    # 5. Sekcja Bota AI (Minimax)
    player2_name = "BOT MAKSYMALIZUJĄCY" if state.game_mode == "EvE" else "BOT AI MINIMAX"
    draw_player_info(surface, 620, 305, player2_name, ai, RED, frame_count)
    
    pygame.draw.line(surface, (45, 45, 65), (610, 500), (940, 500), 1)
    
    # 6. Legenda klawiszologii sterowania
    font_small = pygame.font.SysFont("Consolas", 12)
    controls = [
        "STEROWANIE:",
        " Strzałki    - Sterowanie",
        " SPACJA      - Aktywacja Mocy",
        " Klawisze 1-3 - Zmiana Motywu",
        " Klawisz [R]  - Graj Ponownie / Restart"
    ]
    for idx, line in enumerate(controls):
        # Nagłówek sekcji jest złoty, reszta linii szara
        color = GOLD if idx == 0 else (145, 145, 155)
        c_text = font_small.render(line, True, color)
        surface.blit(c_text, (620, 510 + idx * 16))

def draw_player_info(surface, x, y, name, player, color, frame_count):
    """
    Rysuje szczegółowe statystyki jednego z węży (wynik, długość ciała, 
    aktywne efekty czasowe oraz zawartość slotu na supermoc).
    """
    font_bold = pygame.font.SysFont("Arial", 16, bold=True)
    font_norm = pygame.font.SysFont("Consolas", 14)
    
    # Nazwa gracza
    name_text = font_bold.render(name, True, color)
    surface.blit(name_text, (x, y))
    
    # Informacja o przeżyciu węża (czy zderzył się ze ścianą)
    if not player.alive:
        status_text = font_bold.render("KRAKSA!", True, RED)
        surface.blit(status_text, (x + 235, y))
    else:
        status_text = font_bold.render("AKTYWNY", True, GREEN)
        surface.blit(status_text, (x + 235, y))
        
    # Wyświetlanie aktualnego wyniku punktowego
    score_text = font_norm.render(f"Wynik: {player.score}", True, (230, 230, 230))
    surface.blit(score_text, (x, y + 25))
    
    # Wyświetlanie długości węża w stosunku do jego docelowego wymiaru
    tail_text = font_norm.render(f"Długość: {len(player.body)}/{player.target_length}", True, (200, 200, 200))
    surface.blit(tail_text, (x, y + 45))
    
    # Sekcja aktywnych liczników (czasowych bonusów / kar)
    timer_offset = 0
    # 1. Przyspieszenie (dopalacz)
    if player.speed_boost_timer > 0:
        boost_text = font_norm.render(f"PRZYSPIESZENIE: {player.speed_boost_timer}s", True, (0, 255, 255))
        surface.blit(boost_text, (x, y + 65))
        timer_offset += 20
    # 2. Zamrożenie w miejscu
    elif player.stop_timer > 0:
        stop_text = font_norm.render(f"ZAMROŻENIE: {player.stop_timer}s", True, (255, 110, 110))
        surface.blit(stop_text, (x, y + 65))
        timer_offset += 20
        
    # 3. Graficzna wizualizacja slotu posiadanej supermocy (Mystery Boxa)
    slot_y = y + 70 + timer_offset
    # Szara ramka slotu
    pygame.draw.rect(surface, (14, 14, 20), (x, slot_y, 210, 45), border_radius=5)
    pygame.draw.rect(surface, (45, 45, 65), (x, slot_y, 210, 45), width=1, border_radius=5)
    
    slot_lbl = font_norm.render("SLOT NA MOC:", True, (110, 110, 140))
    surface.blit(slot_lbl, (x + 10, slot_y + 5))
    
    power_names = {
        1: "PRZYSPIESZENIE",
        2: "NAGŁE ZATRZYMANIE",
        3: "TELEPORTACJA (6 PÓL)"
    }
    power_colors = {
        1: (0, 255, 255),
        2: (255, 100, 100),
        3: GOLD
    }
    
    # Wyświetlanie nazwy supermocy w slocie z neonowym pulsowaniem koloru
    if player.superpower:
        p_name = power_names[player.superpower]
        p_color = power_colors[player.superpower]
        
        # Płynne miganie tekstu ułatwia szybką identyfikację posiadanej mocy w trakcie gry
        pulse = int(185 + 70 * math.sin(frame_count * 0.18))
        p_text = font_bold.render(p_name, True, tuple(min(255, int(c * (pulse/255))) for c in p_color))
        surface.blit(p_text, (x + 10, slot_y + 22))
    else:
        p_text = font_norm.render("PUSTY", True, (75, 75, 75))
        surface.blit(p_text, (x + 10, slot_y + 22))

# =====================================================================
# RENDEROWANIE MENU GŁÓWNEGO I SYSTEM EFEKTÓW TŁA
# =====================================================================

# Globalna lista cząsteczek unoszących się tylko w tle Menu Głównego
menu_particles = []

def update_and_draw_menu_particles(screen):
    """
    Tworzy i aktualizuje unoszące się w tle bąbelki energetyczne w Menu.
    Cząsteczki płynnie lecą z dołu ekranu w górę i powoli zanikają.
    """
    # Spawnowanie cząsteczek w tempie losowym (maksymalnie 35 cząsteczek na raz)
    if len(menu_particles) < 35 and random.random() < 0.12:
        x = random.uniform(0, 850)
        y = 600
        dy = -random.uniform(0.6, 1.6) # Unoszenie w górę (prędkość ujemna)
        dx = random.uniform(-0.3, 0.3)
        size = random.randint(2, 6)
        color = random.choice([BLUE, PURPLE, GREEN]) # Kolory dobrane do trzech motywów gry
        menu_particles.append({
            "x": x, "y": y, "dx": dx, "dy": dy, 
            "size": size, "color": color, 
            "alpha": random.randint(100, 210)
        })
        
    # Aktualizacja fizyki i rysowanie cząsteczek menu
    for p in menu_particles[:]:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        # Usunięcie, gdy wyleci poza górną krawędź
        if p["y"] < -10:
            menu_particles.remove(p)
        else:
            draw_transparent_circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["size"], p["alpha"])

def draw_menu(screen, selected_style, frame_count):
    """
    Rysuje kompletne główne menu gry.
    Zawiera:
    - Unoszące się w tle bąbelki
    - Trójwymiarowy, podświetlany napis "CYBERPUNK SNAKE"
    - Trzy interaktywne karty wyboru motywów z podglądem animowanym
    - Legendę działania zbieranych supermocy
    """
    # Ciemno-fioletowe tło menu
    screen.fill((9, 9, 16))
    
    # Rysowanie unoszących się w tle bąbelków energetycznych
    update_and_draw_menu_particles(screen)
    
    # 1. Główny neonowy nagłówek gry
    font_large = pygame.font.SysFont("Impact", 48)
    pulse = int(170 + 85 * math.sin(frame_count * 0.12))
    title_color = (0, pulse, 255)
    title_text = font_large.render("CYBERPUNK SNAKE", True, title_color)
    title_rect = title_text.get_rect(center=(425, 80))
    
    # Renderowanie cienia napisu (przesunięty o 3px) dla trójwymiarowego efektu głębi
    shadow_text = font_large.render("CYBERPUNK SNAKE", True, (0, int(pulse * 0.35), int(pulse * 0.7)))
    screen.blit(shadow_text, title_rect.move(3, 3))
    screen.blit(title_text, title_rect)
    
    # Podtytuł
    font_sub = pygame.font.SysFont("Consolas", 16)
    sub_text = font_sub.render("Edycja AI Minimax - Gra Wieloosobowa", True, (140, 140, 175))
    screen.blit(sub_text, sub_text.get_rect(center=(425, 130)))
    
    # Tryb gry
    mode_text_str = "TRYB: BOT VS BOT" if state.game_mode == "EvE" else "TRYB: GRACZ VS BOT"
    mode_color = RED if state.game_mode == "EvE" else GREEN
    mode_text = font_sub.render(f"{mode_text_str} (Naciśnij [G] by zmienić)", True, mode_color)
    screen.blit(mode_text, mode_text.get_rect(center=(425, 160)))
    
    # 2. Rysowanie trzech interaktywnych kart motywów gry
    card_width, card_height = 205, 220
    card_y = 200
    styles_info = [
        {"id": 1, "name": "MOTOCYKLE", "desc": ["Wielobarwne ścigacze", "Gęste ślady spalin", "Klasyczna siatka Tron"], "color": BLUE},
        {"id": 2, "name": "MOTYW NEONOWY", "desc": ["Świecące neony", "Energetyczne iskry", "Wysoki kontrast gry"], "color": PURPLE},
        {"id": 3, "name": "MOTYW WĘŻA", "desc": ["Klasyczny, organiczny", "Zachodzące na siebie łuski", "Spokojne, naturalne tło"], "color": GREEN}
    ]
    
    for idx, info in enumerate(styles_info):
        card_x = 70 + idx * 250
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        is_selected = (selected_style == info["id"])
        
        # Podświetlenie krawędzi aktualnie wybranego motywu z płynnym pulsowaniem obramowania
        if is_selected:
            bg_color = (25, 25, 45) # Jaśniejsze fioletowe tło karty
            border_color = info["color"]
            border_width = 3
            # Lekkie pulsowanie grubości ramki
            offset = int(2 + math.sin(frame_count * 0.22) * 2)
            pygame.draw.rect(screen, border_color, card_rect.inflate(offset, offset), border_radius=8, width=2)
        else:
            bg_color = (14, 14, 21) # Ciemne tło karty niewybranej
            border_color = (60, 60, 75)
            border_width = 1
            
        # Narysowanie tła i ramki karty
        pygame.draw.rect(screen, bg_color, card_rect, border_radius=6)
        pygame.draw.rect(screen, border_color, card_rect, border_width, border_radius=6)
        
        # Tytuł karty motywu
        font_card_title = pygame.font.SysFont("Arial", 16, bold=True)
        title_text = font_card_title.render(info["name"], True, info["color"])
        screen.blit(title_text, title_text.get_rect(center=(card_x + card_width//2, card_y + 25)))
        
        # INTERAKTYWNY PODGLĄD GRAFICZNY MOTYWU (Rysowany dynamicznie w środku każdej karty)
        preview_y = card_y + 70
        if info["id"] == 1:
            # Rysowanie imitacji małego ścigacza Tron
            pygame.draw.rect(screen, (30, 30, 42), (card_x + 30, preview_y - 15, 145, 30), border_radius=3)
            for k in range(5):
                draw_transparent_circle(screen, info["color"], (card_x + 50 + k * 18, preview_y), 6, 80 - k*12)
            pygame.draw.rect(screen, info["color"], (card_x + 130, preview_y - 6, 20, 12), border_radius=2)
        elif info["id"] == 2:
            # Rysowanie neonowej linii z sypiącymi się w locie iskierkami
            pygame.draw.line(screen, info["color"], (card_x + 30, preview_y), (card_x + 175, preview_y), 4)
            for k in range(8):
                draw_transparent_circle(screen, info["color"], (card_x + 65 + k * 13, preview_y + random.randint(-3, 3)), 3, 145)
        elif info["id"] == 3:
            # Rysowanie falującego wężyka organicznego
            for k in range(7):
                seg_col = info["color"] if k % 2 == 0 else (30, 150, 50)
                pygame.draw.circle(screen, seg_col, (card_x + 50 + k * 17, preview_y + int(math.sin(k + frame_count*0.18)*6)), 7)
                
        # Opis tekstowy cech i zalet danego stylu
        font_card_desc = pygame.font.SysFont("Consolas", 11)
        for line_idx, line in enumerate(info["desc"]):
            desc_text = font_card_desc.render(line, True, (170, 170, 185))
            screen.blit(desc_text, desc_text.get_rect(center=(card_x + card_width//2, card_y + 125 + line_idx * 16)))
            
        # Sygnalizacja klawisza skrótu pod kartą
        hotkey_font = pygame.font.SysFont("Consolas", 14, bold=True)
        hotkey_text = hotkey_font.render(f"KLIKNIJ LUB [{info['id']}]", True, info["color"] if is_selected else (115, 115, 115))
        screen.blit(hotkey_text, hotkey_text.get_rect(center=(card_x + card_width//2, card_y + 190)))
        
    # 3. Pulsujący tekst zaproszenia "NACIŚNIJ ENTER ABY ZAGRAĆ"
    font_start = pygame.font.SysFont("Consolas", 18, bold=True)
    pulse_start = int(140 + 115 * math.sin(frame_count * 0.16))
    start_text = font_start.render("KLIKNIJ TUTAJ LUB NACIŚNIJ [ENTER] ABY ZAGRAĆ", True, (255, pulse_start, 0))
    screen.blit(start_text, start_text.get_rect(center=(425, 465)))
    
    # 4. Legenda i opis kart supermocy na samym dole ekranu
    font_legend = pygame.font.SysFont("Consolas", 12)
    legends = [
        "SPECYFIKACJA KART SUPERMOCY ZBIERANYCH W TRAKCIE GRY:",
        "1. PRZYSPIESZENIE      [SPACJA] - Podwaja prędkość ruchu węża na 15 ruchów",
        "2. NAGŁE ZATRZYMANIE   [SPACJA] - Zamraża węża w miejscu, chroniąc przed kolizją",
        "3. TELEPORTACJA (SKOK) [SPACJA] - Przeskakuje o 6 pól wprzód w wybranym kierunku"
    ]
    for line_idx, line in enumerate(legends):
        color = GOLD if line_idx == 0 else (150, 150, 165)
        leg_text = font_legend.render(line, True, color)
        screen.blit(leg_text, leg_text.get_rect(center=(425, 510 + line_idx * 16)))
