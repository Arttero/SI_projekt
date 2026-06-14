# =====================================================================
# GLOBALNE STAŁE I KONFIGURACJA PARAMETRÓW GRY
# =====================================================================

# WYMIARY OKNA GRY (w pikselach)
# Całkowita szerokość okna to 850px, na co składa się:
# - 600px: Kwadratowy obszar planszy gry (arena 30x30 pól, każde po 20px)
# - 250px: Panel boczny (dashboard) z punktacją, legendą i slotami mocy
WIDTH = 950   
HEIGHT = 600

# ROZMIAR POJEDYNCZEGO POLA SIATKI (w pikselach)
# Każda komórka na planszy to kwadrat o boku 20px na 20px
GRID_SIZE = 20

# GEOMETRIA ARENY GRY
# Liczba wierszy i kolumn w siatce ( plansza ma rozmiar 30 x 30 = 900 pól )
ROWS = 30
COLS = 30

# PALETA KOLORÓW NEONOWYCH (Format RGB)
BLACK = (10, 10, 15)      # Głębokie tło planszy
WHITE = (255, 255, 255)    # Jasny biały (np. napisy, błyski)
BLUE = (0, 150, 255)       # Kolor Gracz 1 (Ty) - Cyberpunkowy Cyjan
RED = (255, 50, 50)        # Kolor Bota AI (Minimax) - Neonowa Czerwień
GOLD = (255, 215, 0)       # Kolor Skrzynek Mocy / Legendy
PURPLE = (255, 0, 255)     # Synthwave'owy Fiolet (Motyw 2)
GREEN = (50, 220, 80)      # Neonowa Acidowa Zieleń (Motyw 3)

# WEKTORY KIERUNKÓW RUCHU (Układ współrzędnych ekranu)
# W Pygame oś Y rośnie w dół, a oś X rośnie w prawo:
# - (0, -1)  -> Ruch w górę (Y maleje)
# - (0, 1)   -> Ruch w dół (Y rośnie)
# - (-1, 0)  -> Ruch w lewo (X maleje)
# - (1, 0)   -> Ruch w prawo (X rośnie)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# INTERWAŁ LOGIKI GRY (Prędkość rozgrywki)
# Definiuje co ile klatek renderowania (60 FPS) odbywa się jeden logiczny krok węży.
# Wartość 6 oznacza, że krok logiczny wykonuje się 10 razy na sekundę (60 / 6 = 10 Hz).
LOGIC_INTERVAL = 6  
