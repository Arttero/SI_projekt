# Dokumentacja Projektowa: Cyberpunk Snake

Głównym celem projektu było stworzenie w pełni funkcjonalnego środowiska gry oraz implementacja autonomicznego bota podejmującego decyzje w oparciu o algorytmy teorii gier i przeszukiwania przestrzeni.

## 1. Wstęp i Wymagania Projektowe
Projekt to połączenie klasycznej gry "Snake'a" z elementami gry "Tron: Light Cycles", wzbogacona o rozbudowaną grafikę w trzech motywach oraz w pełni funkcjonalnego bota opierającego się na sztucznej inteligencji. 

**Główne Wymagania (zrealizowane w projekcie):**
* Tryb wieloosobowy (Gracz vs Bot AI - **PvE** oraz Bot AI vs Bot AI - **EvE**).
* Inteligentny przeciwnik oparty o algorytm **Minimax** z cięciami **Alpha-Beta**.
* Zaawansowana **funkcja heurystyczna** oceniająca bezpieczeństwo, przejęte terytorium, agresję oraz priorytetyzację pożywienia/supermocy.
* Zbieranie owoców (zwiększające punktację oraz długość węża).
* Zbieranie specjalnych Mocy (Mystery Box), dających graczom taktyczną przewagę (np. Teleportacja, Przyspieszenie, Zamrożenie wroga).
* Czytelny interfejs graficzny z wykorzystaniem biblioteki Pygame z efektami wizualnymi, cząsteczkami (particles) i wibracjami ekranu (screen shake).

---

## 2. Struktura Modularna Projektu i Spis Funkcji
Aplikacja została zaprojektowana w architekturze modułowej, co pozwala na pełną separację logiki gry, silnika renderowania, systemu cząsteczek oraz algorytmów decyzyjnych. Poniższa tabela przedstawia podział kodu:

| Plik źródłowy | Odpowiedzialność | Kluczowe klasy i funkcje |
| --- | --- | --- |
| `main.py` | Pętla główna programu, obsługa wejścia/klawiatury, kontroler maszyny stanów gry. | `main()` |
| `ai.py` | Silnik decyzyjny bota: algorytm Minimax z odcięciem Alpha-Beta oraz funkcja heurystyczna. | `get_legal_moves()`, `evaluate_state()`, `minimax()`, `get_best_move()` |
| `renderer.py` | Moduł graficzny: rysowanie planszy, animacje neonowe, panel dashboard, menu główne. | `draw_board()`, `draw_player()`, `draw_food()`, `draw_powerup()`, `draw_dashboard()`, `draw_menu()` |
| `game_logic.py` | Logika fizyczna: detekcja kolizji, zjadanie owoców/mocy, pozycjonowanie, reset stanu. | `spawn_new_food()`, `spawn_new_powerup()`, `check_collisions()`, `spawn_move_particles()`, `reset_game()` |
| `particles.py` | Efekty specjalne: generowanie iskier, wybuchów, śladów teleportacji i wstrząsów kamery. | Klasa `Particle`, `spawn_particles()`, `spawn_explosion()`, `spawn_jump_particles()`, `trigger_screen_shake()` |
| `player.py` | Klasa reprezentująca węża (gracza lub przeciwnika). | Klasa `Player` |
| `constants.py` | Parametry stałe konfiguracji (wymiary okna, kolory RGB, wektory ruchu, taktowanie FPS). | brak (zmienne stałe) |
| `state.py` | Centralna pamięć podręczna przechowująca stan gry w czasie rzeczywistym. | brak (zmienne stanu) |

### Opis implementacyjny funkcji i metod

**Plik `main.py`**
* `main()`: Główna pętla programu pracująca z częstotliwością 60 Hz. Obsługuje zdarzenia systemowe (Pygame events). Wykrywa wejście gracza (strzałki do zmiany kierunku, SPACJA do aktywacji mocy). Synchronizuje aktualizację cząsteczek z krokiem logicznym gry (wykonywanym co interwał `LOGIC_INTERVAL`). Odpowiada za podwójne buforowanie obrazu w celu uniknięcia migotania ekranu.

**Plik `ai.py`**
* `get_legal_moves(pos, grid)`: Zwraca listę bezpiecznych ruchów (wektorów) dla danej pozycji głowy węża. Wyklucza ruchy prowadzące do natychmiastowej kolizji ze ścianami i ciałami węży.
* `evaluate_state(grid, ai_body, human_body)`: Matematyczna funkcja oceny stanu gry (heurystyka). Wyznacza ocenę liczbową planszy na podstawie: terytorium Voronoi bota w stosunku do gracza, odległości Manhattan do jedzenia i Mystery Boxów oraz dystansu taktycznego między wężami.
* `minimax(grid, ai_body, human_body, depth, alpha, beta, is_maximizing)`: Rekurencyjna funkcja wyznaczania najlepszej ścieżki przeszukiwania w drzewie gry do zadanej głębokości. Wykorzystuje technikę odcięć Alpha-Beta dla eliminacji zbędnych obliczeniowo gałęzi.
* `get_best_move(grid, ai_body, human_body, depth)`: Funkcja startowa silnika decyzyjnego. Wykonuje symulacyjny krok w każdym dozwolonym kierunku i uruchamia algorytm Minimax w celu wytypowania optymalnego kierunku ruchu.

**Plik `renderer.py`**
* `draw_rotated_rect(surface, color, center, size, angle)`: Rysuje obrócony prostokąt (używany przy Mystery Boxach) na bazie transparentnego bufora Surface.
* `draw_rotated_rect_glow(surface, color, center, size, angle)`: Nakłada dwuwarstwowy, rozmyty prostokąt dający efekt neonowego świecenia (Glow).
* `draw_board(screen, style)`: Rysuje tło oraz siatki pomocnicze areny (dla stylów Cyberpunk, Synthwave i Klasycznego).
* `draw_player(screen, player, style)`: Odpowiada za wizualizację węża. W zależności od stylu rysuje wektorowy motocykl Tron ze smugą spalin, świecący neon z jądrem energetycznym lub organiczne łuski z głową i wysuwanym językiem.
* `draw_food(screen, fx, fy, style, frame_count)`: Renderuje jedzenie (ogniwo zasilające, neonową kulę lub jabłko z liściem) wraz z sinusowym pulsowaniem.
* `draw_powerup(screen, px, py, style, frame_count)`: Renderuje rotujące Mystery Boxy.
* `draw_dashboard(...)`, `draw_player_info(...)`, `draw_menu(...)`: Odpowiadają za wyświetlanie odpowiednich sekcji interfejsu (Dashboard, Gracz, Menu).

**Plik `game_logic.py`**
* `spawn_new_food(grid)` oraz `spawn_new_powerup(grid)`: Generator dynamicznych obiektów na planszy. Zapobiegają spawnowaniu przedmiotów na zablokowanych segmentach.
* `check_collisions(player, x, y, grid)`: Odpowiada za fizykę kolizji. Rejestruje zjedzenie owocu, przydziela losowe supermoce, uruchamia efekty cząsteczkowe i zarządza poprawnym obcinaniem ogona węży przy braku spożycia jedzenia.
* `spawn_move_particles(player, hx, hy)`: Tworzy smugi cząsteczek imitujące spaliny/pył za ogonem węża.
* `reset_game(style)`: Przywraca stan początkowy gry (tworzy nowe obiekty klasy Player, czyści siatki, generuje początkowe punkty).

**Plik `particles.py` i `player.py`**
* Klasa `Particle` (obiekty fizyczne), generatory wizualne zjawisk oraz Klasa `Player` modelująca wężyka ze zmiennymi logicznymi i timerami bonusów czasowych.

---

## 3. Omówienie Teoretyczne: Przeszukiwanie Wszerz (BFS) i Diagram Voronoia
Jednym z najważniejszych elementów projektu było zaprojektowanie efektywnego algorytmu oceny przestrzennej planszy. W grze typu Snake kluczowym czynnikiem decydującym o wygranej lub przegranej jest ilość bezpiecznego miejsca, jakim dysponuje dany wąż. Do precyzyjnego wyznaczenia stref wpływów zaimplementowano połączenie dwóch algorytmów: BFS oraz Podziału Voronoia.

### A. Algorytm BFS (Breadth-First Search)
BFS (przeszukiwanie wszerz) to deterministyczny algorytm grafowy, który przechodzi siatkę planszy warstwowo (poziom po poziomie), gwarantując odnalezienie najkrótszej geometrycznie drogi w układzie współrzędnych do każdego osiągalnego pola.

Algorytm działa w oparciu o kolejkę FIFO (First-In, First-Out):
1. Pozycja startowa (głowa węża) jest umieszczana w kolejce jako węzeł początkowy.
2. W każdym kroku pobierany jest element z początku kolejki, a jego sąsiednie wolne pola (góra, dół, lewo, prawo) są analizowane.
3. Wolne, nieodwiedzone dotąd pola są oznaczane w strukturze pomocniczej jako zbadane i dodawane na koniec kolejki.
4. Proces kończy się w momencie opróżnienia kolejki (brak dalszych wolnych pól).

### B. Podział Terytorialny metodą Voronoia
Diagram Voronoia to metoda dekompozycji przestrzeni metrycznej na komórki (terytoria) przypisane do najbliższych im punktów (tzw. generatorów). W kontekście naszej gry dwuosobowej na planszy występują dwa generatory:
1. Głowa węża sterowanego komputerowo (AI)
2. Głowa węża gracza

Chcemy sprawdzić, do których pól planszy dany wąż jest w stanie dotrzeć szybciej niż jego przeciwnik.

**Implementacja w kodzie projektu (`bfs_area` w `ai.py`):**
1. Inicjalizowana jest pomocnicza dwuwymiarowa tablica odwiedzin `visited` wypełniona wartością 0.
2. Do pierwszej kolejki `q_ai` dodawana jest pozycja głowy bota, a do drugiej kolejki `q_hu` pozycja gracza. W tablicy `visited` pola te otrzymują odpowiednio wartości 1 oraz 2.
3. W głównej pętli algorytmu, naprzemiennie i krok po kroku, wykonujemy jedną falę ekspansji BFS dla bota, a następnie jedną falę dla gracza.
4. Każde nowo odwiedzone wolne pole siatki zostaje przypisane do tego węża, którego fala dotarła tam pierwsza. Przypisanie pola do bota zwiększa licznik `score_ai`, a do gracza – `score_hu`.
5. Ponieważ fale rozchodzą się z taką samą prędkością (1 pole na iterację), plansza zostaje idealnie i sprawiedliwie podzielona na dwie strefy wpływów geometrycznych.

*Przykład działania dekompozycji na uproszczonej planszy 5x5:*
```text
Pozycje wejściowe (A = Bot, H = Gracz, . = wolne):
[A]  .   .   .  [H]
 .   .   .   .   .
 .   .   .   .   .

Wynik podziału Voronoi (1 = terytorium bota, 2 = terytorium gracza):
[1] [1] [1] [2] [2]
[1] [1] [1] [2] [2]
[1] [1] [1] [2] [2]
[1] [1] [2] [2] [2]
[1] [2] [2] [2] [2]
```

**Rola algorytmu w heurystyce decyzyjnej:**
Wyliczona różnica terytorialna `space_diff = score_ai - score_hu` stanowi fundament oceny heurystycznej i jest mnożona przez stałą wagową `12.0`.

Dzięki temu silnik decyzyjny zyskuje następujące cechy:
* **Unikanie pułapek:** Bot natychmiast odrzuci ruchy prowadzące w korytarze o małej pojemności Voronoia (gdzie grozi mu zapętlenie i śmierć).
* **Strategiczne odcinanie:** Jeżeli bot wykryje ruch, który fizycznie zablokuje rozchodzenie się fali przeciwnika (np. zajechanie drogi i przejęcie dużej części planszy), otrzyma on bardzo wysoką ocenę i zostanie wykonany. Pozwala to botowi na niezwykle inteligentną grę pozycyjną.

---

## 4. Wyjaśnienie Heurystyki i Zjawisk Emergentnych
Podstawą bystrości bota nie jest to jak daleko widzi, lecz to **jak ocenia to, co widzi**. Za to odpowiada funkcja `evaluate_state`, która przyznaje planszy ocenę liczbową.

**Elementy brane pod uwagę w heurystyce:**
* **Wygrana/Przegrana (+/- 10000):** Śmierć któregokolwiek z węży kończy ocenę. Bezpieczeństwo jest najwyższym priorytetem.
* **Terytorium i Przestrzeń (+/- 12.0 za kratkę):** Opisane wyżej algorytmy zapewniają długoterminowe przetrwanie.
* **Supermoce (Waga 800.0):** Ogromny nacisk na odległość (Dystans Manhattan) węża od skrzynki. Bot priorytetowo traktuje zebranie potężnego buffa.
* **Jedzenie (Waga 6.0 do 18.0):** Apetyt węża na owoce zależy od tego, czy jest krótszy od wroga. Jeżeli przegrywa długością – bardzo chce zjeść. Jeżeli jest dłuższy – priorytet jedzenia maleje.
* **Unikanie remisów (Kary -5000):** Bezpośrednie uderzenie "głowa w głowę" jest ekstremalnie karane przed wysłaniem ruchu, aby maszyna unikała bezpiecznych dla niej, lecz frustrujących zderzeń czołowych.

**Zjawisko Emergentne (Maksymalizator vs Minimalizator w trybie EvE):**
Zamiast kodować dwie osobne sztuczne inteligencje (jedną do agresji, drugą do ucieczki), obydwa boty posiadają **jeden, współdzielony matematyczny wzorzec**. Jeden bot szuka w nim wyników na absolutny "plus" (Maksymalizator), a drugi na absolutny "minus" (Minimalizator).
* **Jeśli jeden wąż staje się dłuższy**, kod przyznaje mu nagrodę za bliskość do przeciwnika. Powoduje to, że dłuższy wąż od razu zmienia się w agresywnego drapieżcę.
* **Krótszy wąż**, reagując na te same zasady matematyczne (dla niego jest to ogromna kara), desperacko rzuca się do ucieczki oraz zbierania owoców, by wyrównać długość.

Dzięki matematycznej opozycji algorytmu Minimax z jednej funkcji zrodziły się naturalne instynkty polowania, ucieczki i walki o przetrwanie.

---

## 5. Mechaniki Rozgrywki i Supermoce
Rozgrywka została wzbogacona o Mystery Boxy, które zmieniają losy na mapie:
1. **Przyspieszenie:** Wykonanie kilku szybkich kroków po wciśnięciu Spacji (wąż wykonuje je niezależnie od siatki interwałów, wymuszając szybką ucieczkę lub szybki atak).
2. **Nagłe Zatrzymanie (Zamrożenie):** Umiejętność awaryjna wbudowana w AI; jeżeli bot znajdzie się w tragicznej sytuacji bez drogi ucieczki, a posiada tę moc – zatrzymuje się na 15 klatek by pozwolić wrogowi się przesunąć i otworzyć mu przejście.
3. **Teleportacja (6 Pól):** Bot w ostateczności teleportuje się w powietrzu o 6 pól z miejsca zagrożenia.

---

## 6. Sterowanie i Obsługa
* **Start programu:** Uruchom w konsoli komendę `python main.py`
* **Menu Główne:** Naciskając klawisze `1`, `2` lub `3`, przełączasz się między trzema stylami graficznymi (Klasyczny Cyberpunk Tron, Neonowy Synthwave, Biologiczny Wąż). Wybierz klawisz `[P]` by grać przeciwko komputerowi lub klawisz `[G]` by obserwować walkę dwóch algorytmów (Bot vs Bot).
* **W Grze (Tryb PvE):**
  * `Strzałki` – Zmiana kierunku ruchu gracza.
  * `Spacja` – Aktywacja zebranej supermocy.
  * Klawisze `1, 2, 3` w dowolnej chwili na żywo zmieniają filtry na ekranie.
* **Game Over:** Klawisz `[R]` pozwala zagrać ponownie, a `[M]` przywraca menu.
