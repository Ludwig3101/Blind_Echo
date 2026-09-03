import pygame
import sys

# Pygame initialisieren
pygame.init()

# Fenster und Konstanten einrichten
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blind Echo - Schritt 1")

# Farben werden in RGB definieren
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255) # Echo Farbe

# 60 FPS
clock = pygame.time.Clock()
FPS = 60

# Die Soundwellen Klasse
class SoundWave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 2          
        self.speed = 5           
        self.max_radius = 250    
        self.alive = True

    def update(self):
        # Radius vergrößern
        self.radius += self.speed
        # Wenn maximale Reichweite erreicht ist, aufhören
        if self.radius >= self.max_radius:
            self.alive = False

    def draw(self, surface):
        # Umriss 2
        pygame.draw.circle(surface, CYAN, (self.x, self.y), int(self.radius), width=2)

# Spielereigenschaften, Startposition in der Mitte
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 4
player_radius = 8

# Liste für alle aktuell sichtbaren Soundwellen
waves = []

# Der Game Loop
running = True
while running:
    # Events verarbeiten (Eingaben abfragen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Einzeltastendruck Leertaste
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Neue Welle an aktueller Spielerposition erzeugen
                waves.append(SoundWave(player_x, player_y))


    # Spiellogik (Bewegung berechnen) WASD
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_w]: player_y -= player_speed # Oben
    if keys[pygame.K_s]: player_y += player_speed # Unten 
    if keys[pygame.K_a]: player_x -= player_speed # Links
    if keys[pygame.K_d]: player_x += player_speed # Rechts

    # Alle Wellen aktualisieren
    for wave in waves:
        wave.update()

    # Nur die Wellen behalten, die nicht zu groß sind
    waves = [wave for wave in waves if wave.alive]

    # Rendering
    # Zuerst den alten Frame mit Schwarz übermalen
    screen.fill(BLACK)

    # alle Wellen zeichnen
    for wave in waves:
        wave.draw(screen)
    
    # den Spieler an seiner neuen Position zeichnen
    pygame.draw.circle(screen, WHITE, (player_x, player_y), player_radius)

    # Das fertige Bild auf den Monitor schicken
    pygame.display.flip()

    # Das Spiel auf 60 Bilder pro Sekunde drosseln
    clock.tick(FPS)

# Spiel beenden
pygame.quit()
sys.exit()