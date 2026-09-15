import pygame
import sys
import math

# Pygame initialisieren
pygame.init()

# Fenster und Konstanten einrichten
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blind Echo")

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
DARK_CYAN = (0, 140, 160)

clock = pygame.time.Clock()
FPS = 60

# Wand als Liniensegment
class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.glow = 0.0  # 0.0 bis 1.0, leuchtet wenn Schall auftrifft

    def update(self):
        # Leuchten verblasst mit der Zeit
        if self.glow > 0:
            self.glow = max(0.0, self.glow - 0.02)

    def draw(self, surface):
        if self.glow > 0:
            # Helligkeit der Wand berechnen
            intensity = int(self.glow * 255)
            color = (intensity, intensity, intensity)
            pygame.draw.line(surface, color, (self.x1, self.y1), (self.x2, self.y2), 2)

# Einzelner Schallstrahl, der von Wänden abprallen kann
class SoundRay:
    def __init__(self, x, y, angle, speed=5.0, max_life=45, bounces=1, color=CYAN):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.speed = speed
        self.life = max_life
        self.max_life = max_life
        self.bounces = bounces
        self.color = color
        self.alive = True
        self.prev_x = x
        self.prev_y = y

    def update(self, walls):
        if not self.alive:
            return

        self.prev_x = self.x
        self.prev_y = self.y

        # Nächste Position
        next_x = self.x + self.vx
        next_y = self.y + self.vy

        # Kollision mit Wänden prüfen
        hit = None
        closest_t = 1.0
        hit_wall = None
        hit_normal = None

        for wall in walls:
            # Schnittpunkt zwischen Strahlenschritt und Wandlinie
            res = line_intersection(self.prev_x, self.prev_y, next_x, next_y,
                                    wall.x1, wall.y1, wall.x2, wall.y2)
            if res:
                t, ix, iy, nx, ny = res
                if t < closest_t:
                    closest_t = t
                    hit = (ix, iy)
                    hit_wall = wall
                    hit_normal = (nx, ny)

        if hit and hit_wall:
            # Wand zum Leuchten bringen
            hit_wall.glow = 1.0
            self.x, self.y = hit

            # Abprallen wenn noch Bounces übrig sind
            if self.bounces > 0:
                self.bounces -= 1
                # Reflektionsvektor: v' = v - 2*(v.n)*n
                dot = self.vx * hit_normal[0] + self.vy * hit_normal[1]
                self.vx = self.vx - 2 * dot * hit_normal[0]
                self.vy = self.vy - 2 * dot * hit_normal[1]
                # Leicht von der Wand wegschieben um Steckenbleiben zu verhindern
                self.x += self.vx * 0.2
                self.y += self.vy * 0.2
            else:
                self.alive = False
        else:
            self.x = next_x
            self.y = next_y

        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        # Strahl verblasst mit abnehmender Lebenszeit
        alpha = self.life / self.max_life
        r = int(self.color[0] * alpha)
        g = int(self.color[1] * alpha)
        b = int(self.color[2] * alpha)
        pygame.draw.line(surface, (r, g, b), (int(self.prev_x), int(self.prev_y)), (int(self.x), int(self.y)), 2)

# Hilfsfunktion für Linienkollision & Normalenvektor
def line_intersection(p0_x, p0_y, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):
    s1_x = p1_x - p0_x
    s1_y = p1_y - p0_y
    s2_x = p3_x - p2_x
    s2_y = p3_y - p2_y

    denom = (-s2_x * s1_y + s1_x * s2_y)
    if abs(denom) < 1e-6:
        return None

    s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / denom
    t = ( s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / denom

    if 0 <= s <= 1 and 0 <= t <= 1:
        ix = p0_x + (t * s1_x)
        iy = p0_y + (t * s1_y)
        # Normale der Wand
        dx = p3_x - p2_x
        dy = p3_y - p2_y
        length = math.hypot(dx, dy)
        if length == 0:
            return None
        nx = -dy / length
        ny = dx / length
        # Normale Richtung Strahl ausrichten
        if s1_x * nx + s1_y * ny > 0:
            nx = -nx
            ny = -ny
        return (t, ix, iy, nx, ny)
    return None

# Schallimpuls erzeugen (viele Strahlen im Kreis)
def emit_sound_pulse(x, y, ray_count=48, speed=5.0, max_life=50, bounces=1, color=CYAN):
    new_rays = []
    for i in range(ray_count):
        angle = (2 * math.pi / ray_count) * i
        new_rays.append(SoundRay(x, y, angle, speed=speed, max_life=max_life, bounces=bounces, color=color))
    return new_rays

# Ein paar Testwände um das Zimmer
walls = [
    # Außenwände
    Wall(50, 50, 750, 50),
    Wall(750, 50, 750, 550),
    Wall(750, 550, 50, 550),
    Wall(50, 550, 50, 50),
    # Innenwände / Flure
    Wall(250, 50, 250, 400),
    Wall(500, 200, 500, 550),
]

# Spieler
player_x = 150
player_y = 300
player_speed = 4
player_radius = 6

rays = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Schallwelle aussenden
                rays.extend(emit_sound_pulse(player_x, player_y, ray_count=60, speed=6.0, max_life=60, bounces=2))

    # Bewegung WASD
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player_y -= player_speed
    if keys[pygame.K_s]: player_y += player_speed
    if keys[pygame.K_a]: player_x -= player_speed
    if keys[pygame.K_d]: player_x += player_speed

    # Wände aktualisieren
    for wall in walls:
        wall.update()

    # Strahlen aktualisieren
    for ray in rays:
        ray.update(walls)
    rays = [r for r in rays if r.alive]

    # Zeichnen
    screen.fill(BLACK)

    # Wände zeichnen (nur sichtbar wenn von Schall getroffen)
    for wall in walls:
        wall.draw(screen)

    # Schallstrahlen zeichnen
    for ray in rays:
        ray.draw(screen)

    # Spieler (in der Dunkelheit als kleiner Punkt sichtbar)
    pygame.draw.circle(screen, WHITE, (int(player_x), int(player_y)), player_radius)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()