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

# 60 FPS
clock = pygame.time.Clock()
FPS = 60

# Spielereigenschaften, Startposition in der Mitte
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 4
player_radius = 8

# Der Game Loop
running = True
while running:
    # Events verarbeiten (Eingaben abfragen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spiellogik (Bewegung berechnen) WASD
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_w]: # Oben
        player_y -= player_speed
    if keys[pygame.K_s]: # Unten
        player_y += player_speed
    if keys[pygame.K_a]: # Links
        player_x -= player_speed
    if keys[pygame.K_d]: # Rechts
        player_x += player_speed

    # Rendering
    # Zuerst den alten Frame mit Schwarz übermalen
    screen.fill(BLACK)
    
    # den Spieler an seiner neuen Position zeichnen
    pygame.draw.circle(screen, WHITE, (player_x, player_y), player_radius)

    # Das fertige Bild auf den Monitor schicken
    pygame.display.flip()

    # Das Spiel auf 60 Bilder pro Sekunde drosseln
    clock.tick(FPS)

# Spiel beenden
pygame.quit()
sys.exit()