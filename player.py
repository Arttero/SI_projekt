from collections import deque

# =====================================================================
# MODEL OBIEKTU GRACZA (Klasa reprezentująca Węża)
# =====================================================================

class Player:
    def __init__(self, start_pos, color, direction, is_ai=False):
        """
        Inicjalizuje obiekt gracza (węża) ze wszystkimi właściwościami 
        sterującymi fizyką, punktacją oraz stanem posiadanych supermocy.
        """
        # Ciało węża reprezentowane przez kolejkę dwukierunkową (deque).
        # Umożliwia to błyskawiczne dodawanie segmentu z przodu (appendleft)
        # oraz usuwanie z samego końca (pop) z wydajnością O(1).
        # Zaczynamy od pojedynczego punktu start_pos np. (5, 5).
        self.body = deque([start_pos])
        
        # Kolor renderowania węża i powiązanych cząsteczek
        self.color = color
        
        # Bieżący wektor kierunku ruchu węża, np. (1, 0)
        self.direction = direction
        
        # Flaga określająca czy dany obiekt jest kontrolowany przez człowieka (False),
        # czy przez algorytm minimax AI (True)
        self.is_ai = is_ai
        
        # Licznik zebranych punktów (wynik gracza)
        self.score = 0
        
        # Aktualnie posiadana w magazynie supermoc (Mystery Box):
        # - None : Brak aktywnego ulepszenia w slocie
        # - 1    : Przyspieszenie (Turbo)
        # - 2    : Nagłe Zatrzymanie (Freeze)
        # - 3    : Teleportacja (Skok)
        self.superpower = None  
        
        # Licznik czasu działania przyspieszenia (w cyklach logicznych gry).
        # Gdy wartość > 0, wąż wykonuje 2 kroki na turę logiczną.
        self.speed_boost_timer = 0
        
        # Licznik czasu zamrożenia/zatrzymania w miejscu (w cyklach logicznych).
        # Gdy wartość > 0, wąż nie porusza się wcale (kroki = 0), co chroni go przed kraksą.
        self.stop_timer = 0
        
        # Docelowa długość ciała węża. 
        # Gdy wąż zjada jedzenie, rośnie jego target_length. Dopóki rzeczywista długość
        # ciała (len(body)) jest mniejsza niż target_length, ogon węża nie jest usuwany w danej turze.
        self.target_length = 5
        
        # Status życia gracza. Zmiana na False oznacza przegraną, wybuch cząsteczek i koniec rundy.
        self.alive = True
