import pygame
import random
import math
import state
from constants import GRID_SIZE, GOLD

# =====================================================================
# SYSTEM CZĄSTECZEK (EFEKTY SPECJALNE I NEONOWE ROZBŁYSKI)
# =====================================================================

class Particle:
    """
    Klasa reprezentująca pojedynczą cząsteczkę (iskierkę) na ekranie.
    Cząsteczka posiada pozycję, prędkość, kolor, rozmiar, grawitację
    oraz czas życia, po upływie którego samoistnie znika.
    """
    def __init__(self, x, y, dx, dy, color, size, lifetime, alpha_fade=True, gravity=0):
        self.x = x # Aktualna pozycja X na ekranie (w pikselach)
        self.y = y # Aktualna pozycja Y na ekranie (w pikselach)
        self.dx = dx # Prędkość pozioma cząsteczki (piksele na klatkę)
        self.dy = dy # Prędkość pionowa cząsteczki (piksele na klatkę)
        self.color = color # Kolor RGB cząsteczki
        self.size = size # Początkowy rozmiar (promień) cząsteczki
        self.max_lifetime = lifetime # Początkowy czas życia cząsteczki
        self.lifetime = lifetime # Pozostały czas życia (odliczany do 0)
        self.alpha_fade = alpha_fade # Czy cząsteczka ma stopniowo stawać się przezroczysta
        self.gravity = gravity # Przyspieszenie pionowe (grawitacja ściągająca w dół)

    def update(self):
        """
        Aktualizuje fizykę cząsteczki: przesuwa ją o wektor prędkości,
        aplikuje grawitację oraz zmniejsza czas życia o 1 klatkę.
        """
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity # Grawitacja wpływa bezpośrednio na pionową prędkość Y
        self.lifetime -= 1

    def draw(self, surface):
        """
        Rysuje cząsteczkę na podanej powierzchni.
        Rozmiar i przezroczystość płynnie maleją wraz z upływem czasu życia.
        """
        if self.lifetime <= 0:
            return
            
        # Wyliczenie poziomu przezroczystości (alfa) od 255 (pełny rozbłysk) do 0 (całkowity zanik)
        alpha = int((self.lifetime / self.max_lifetime) * 255) if self.alpha_fade else 255
        
        # Płynne zmniejszanie promienia cząsteczki w miarę jej starzenia się
        radius = int((self.lifetime / self.max_lifetime) * self.size)
        if radius < 1:
            radius = 1
            
        # Renderowanie koła z przezroczystością na docelowej powierzchni
        draw_transparent_circle(surface, self.color, (int(self.x), int(self.y)), radius, alpha)

def draw_transparent_circle(surface, color, center, radius, alpha):
    """
    Rysuje koło z obsługą przezroczystości (kanał alfa).
    Pygame standardowo nie wspiera rysowania przezroczystych figur geometrycznych 
    bezpośrednio na ekranie, dlatego tworzona jest tymczasowa przezroczysta powierzchnia (Surface).
    """
    # Tworzenie tymczasowego kwadratu z obsługą przezroczystości SRCALPHA o boku równym średnicy koła
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    # Rysowanie koła na tymczasowej powierzchni (kolor RGB + wartość alfa krycia)
    pygame.draw.circle(s, (*color, alpha), (radius, radius), radius)
    # Naniesienie tymczasowej powierzchni na główną planszę (z centrowaniem pozycji)
    surface.blit(s, (center[0] - radius, center[1] - radius))

def spawn_particles(x, y, color, count=10):
    """
    Generuje chmurę małych cząsteczek rozchodzących się we wszystkich kierunkach.
    Stosowane przy aktywacji dopalacza, zamrożenia czy błędach teleportacji.
    """
    for _ in range(count):
        dx = random.uniform(-2, 2)
        dy = random.uniform(-2, 2)
        size = random.randint(3, 6)
        lifetime = random.randint(15, 30)
        # Dodanie nowo utworzonej cząsteczki do globalnej listy w state.py
        state.particles.append(Particle(x, y, dx, dy, color, size, lifetime))

def spawn_explosion(x, y, color):
    """
    Tworzy efektowną, gęstą eksplozję cząsteczek z efektem grawitacji.
    Wywoływane w momencie zderzenia węża ze ścianą lub przeciwnikiem (śmierć węża).
    """
    for _ in range(50): # Duża liczba cząsteczek (50 sztuk) dla efektu eksplozji
        angle = random.uniform(0, 2 * math.pi) # Losowy kąt rozbłysku (0 do 360 stopni)
        speed = random.uniform(2, 6)           # Losowa prędkość początkowa wylotu
        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed
        size = random.randint(4, 9)
        lifetime = random.randint(20, 45)
        # Cząsteczki wybuchu opadają lekko w dół dzięki grawitacji (gravity=0.15)
        state.particles.append(Particle(x + GRID_SIZE//2, y + GRID_SIZE//2, dx, dy, color, size, lifetime, gravity=0.15))

def spawn_jump_particles(start_pos, end_pos, color):
    """
    Generuje ścieżkę (smugę neonową) łączącą punkt startowy i docelowy skoku teleportacji.
    Tworzy to wrażenie błyskawicznego przelotu energetycznego przez planszę.
    """
    # Koordynaty środka pola startowego
    sx = start_pos[0] * GRID_SIZE + GRID_SIZE//2
    sy = start_pos[1] * GRID_SIZE + GRID_SIZE//2
    # Koordynaty środka pola docelowego
    ex = end_pos[0] * GRID_SIZE + GRID_SIZE//2
    ey = end_pos[1] * GRID_SIZE + GRID_SIZE//2
    
    # Rozmieszczenie 25 cząsteczek w równej linii prostej (interpolacja liniowa LERP)
    for i in range(25):
        t = i / 25.0 # Współczynnik proporcji (od 0.0 do 1.0)
        px = sx + (ex - sx) * t
        py = sy + (ey - sy) * t
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        state.particles.append(Particle(px, py, dx, dy, color, size=5, lifetime=20))
        
def spawn_style_shift_particles(color):
    """
    Tworzy rozbłysk cząsteczek na całym obszarze planszy.
    Wywoływane przy zmianie motywu graficznego w locie, dając świetny efekt przejścia.
    """
    for _ in range(40):
        x = random.randint(0, 600)
        y = random.randint(0, 600)
        state.particles.append(Particle(x, y, random.uniform(-2, 2), random.uniform(-2, 2), color, size=5, lifetime=25))

def trigger_screen_shake(duration=12):
    """
    Uruchamia efekt wstrząsu ekranu (Screen Shake) na określony czas.
    Używane przy wybuchach i najmocniejszych supermocach dla zwiększenia dynamiki.
    """
    state.screen_shake_timer = duration
