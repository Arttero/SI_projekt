# =====================================================================
# SYSTEM CENTRALNEJ PAMIĘCI / GLOBALNY WSPÓŁDZIELONY STAN ROZGRYWKI
# =====================================================================

# Moduł ten działa jako globalny kontener przechowujący aktualny stan gry.
# Dzięki zaimportowaniu go w innych plikach (np. main.py, game_logic.py, ai.py),
# różne moduły mogą bezpiecznie odczytywać i modyfikować te same obiekty w czasie rzeczywistym.

# Główna dwuwymiarowa macierz (siatka zderzeń planszy) o rozmiarze 30x30 pól.
# Zawiera cyfry:
# - 0: Pole puste (wolna strefa)
# - 1: Pole zajęte przez ciało węża Gracza 1
# - 2: Pole zajęte przez ciało węża Bota AI
grid = []

# Referencja do obiektu Player (wąż gracza ludzkiego)
human = None

# Referencja do obiektu Player (wąż bota AI minimax)
ai = None

# Lista koordynatów (x, y) aktywnego jedzenia (owoców) znajdującego się na planszy
food_list = []

# Lista koordynatów (x, y) aktywnych skrzynek z supermocami (Mystery Boxów)
powerup_list = []

# Dynamiczna lista zawierająca wszystkie aktywne na planszy cząsteczki (Particle).
# Obiekty cząsteczek są tu stale dodawane i usuwane po wygaśnięciu ich czasu życia.
particles = []

# Identyfikator aktualnego motywu wizualnego na planszy:
# - 1: Cyberpunk / Motocykle (Tron)
# - 2: Neonowy Synthwave
# - 3: Organiczny / Klasyczny Wąż
current_style = 1

# Tryb gry: "PvE" (Gracz vs Bot) lub "EvE" (Bot vs Bot)
game_mode = "PvE"

# Licznik czasu trwania efektu trzęsienia ekranu (Screen Shake) wyrażony w klatkach.
# Gdy licznik jest dodatni (> 0), przy renderowaniu obraz planszy ulega losowemu przesunięciu.
screen_shake_timer = 0
