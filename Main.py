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
GRAY = (120, 120, 120)
CYAN = (0, 255, 255)
DARK_CYAN = (0, 150, 170)
YELLOW = (255, 230, 80)

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
            intensity = int(self.glow * 255)
            color = (intensity, intensity, intensity)
            pygame.draw.line(surface, color, (self.x1, self.y1), (self.x2, self.y2), 2)

# Einzelner Schallstrahl, der von Wänden abprallt
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

        next_x = self.x + self.vx
        next_y = self.y + self.vy

        hit = None
        closest_t = 1.0
        hit_wall = None
        hit_normal = None

        for wall in walls:
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
            hit_wall.glow = 1.0
            self.x, self.y = hit

            if self.bounces > 0:
                self.bounces -= 1
                dot = self.vx * hit_normal[0] + self.vy * hit_normal[1]
                self.vx = self.vx - 2 * dot * hit_normal[0]
                self.vy = self.vy - 2 * dot * hit_normal[1]
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
        alpha = self.life / self.max_life
        r = int(self.color[0] * alpha)
        g = int(self.color[1] * alpha)
        b = int(self.color[2] * alpha)
        pygame.draw.line(surface, (r, g, b), (int(self.prev_x), int(self.prev_y)), (int(self.x), int(self.y)), 2)

# Schnittpunkt zweier Strecken
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
        dx = p3_x - p2_x
        dy = p3_y - p2_y
        length = math.hypot(dx, dy)
        if length == 0:
            return None
        nx = -dy / length
        ny = dx / length
        if s1_x * nx + s1_y * ny > 0:
            nx = -nx
            ny = -ny
        return (t, ix, iy, nx, ny)
    return None

# Schallwelle erzeugen
def emit_sound_pulse(x, y, ray_count=48, speed=5.0, max_life=50, bounces=1, color=CYAN):
    new_rays = []
    for i in range(ray_count):
        angle = (2 * math.pi / ray_count) * i
        new_rays.append(SoundRay(x, y, angle, speed=speed, max_life=max_life, bounces=bounces, color=color))
    return new_rays

# Wände für Testlevel
walls = [
    Wall(50, 50, 750, 50),
    Wall(750, 50, 750, 550),
    Wall(750, 550, 50, 550),
    Wall(50, 550, 50, 50),
    Wall(250, 50, 250, 400),
    Wall(500, 200, 500, 550),
]

# Spieler-Attribute
player_x = 150.0
player_y = 300.0
player_normal_speed = 3.6
player_sneak_speed = 1.6
player_radius = 6

# Schrittgeräusche beim Gehen
walk_distance = 0.0
step_interval = 28.0

# Aufladen für Stampfen (Leertaste halten)
charging = False
charge_time = 0.0
max_charge = 1.0

rays = []

running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Leertaste drücken: Aufladen starten
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                charging = True
                charge_time = 0.0

        # Leertaste loslassen: Schall je nach Ladezeit aussenden
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and charging:
                charging = False
                charge_ratio = min(1.0, charge_time / max_charge)

                if charge_ratio < 0.2:
                    # Kurzes Klatschen
                    rays.extend(emit_sound_pulse(player_x, player_y, ray_count=36, speed=4.5, max_life=40, bounces=1, color=CYAN))
                else:
                    # Starkes Stampfen
                    ray_count = int(48 + charge_ratio * 40)
                    speed = 5.0 + charge_ratio * 2.5
                    life = int(50 + charge_ratio * 40)
                    bounces = 2 if charge_ratio < 0.7 else 3
                    rays.extend(emit_sound_pulse(player_x, player_y, ray_count=ray_count, speed=speed, max_life=life, bounces=bounces, color=WHITE))

    keys = pygame.key.get_pressed()

    # Schleichen mit Shift (halbe Geschwindigkeit, keine Schritte)
    is_sneaking = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
    current_speed = player_sneak_speed if is_sneaking else player_normal_speed

    move_x = 0
    move_y = 0
    if keys[pygame.K_w]: move_y -= 1
    if keys[pygame.K_s]: move_y += 1
    if keys[pygame.K_a]: move_x -= 1
    if keys[pygame.K_d]: move_x += 1

    # Diagonale Bewegung normalisieren
    if move_x != 0 or move_y != 0:
        length = math.hypot(move_x, move_y)
        dx = (move_x / length) * current_speed
        dy = (move_y / length) * current_speed

        player_x += dx
        player_y += dy

        # Nur Schritte erzeugen wenn nicht geschlichen wird
        if not is_sneaking:
            walk_distance += math.hypot(dx, dy)
            if walk_distance >= step_interval:
                walk_distance = 0.0
                # Kleine Schallwelle bei jedem Schritt
                rays.extend(emit_sound_pulse(player_x, player_y, ray_count=16, speed=3.0, max_life=22, bounces=0, color=DARK_CYAN))
    else:
        walk_distance = step_interval * 0.5

    # Stampfen aufladen
    if charging:
        charge_time += dt

    # Wände aktualisieren
    for wall in walls:
        wall.update()

    # Strahlen aktualisieren
    for ray in rays:
        ray.update(walls)
    rays = [r for r in rays if r.alive]

    # Zeichnen
    screen.fill(BLACK)

    # Wände zeichnen
    for wall in walls:
        wall.draw(screen)

    # Schallstrahlen zeichnen
    for ray in rays:
        ray.draw(screen)

    # Lade-Ring um den Spieler anzeigen
    if charging:
        charge_ratio = min(1.0, charge_time / max_charge)
        ring_radius = int(player_radius + 4 + charge_ratio * 16)
        ring_color = WHITE if charge_ratio > 0.8 else CYAN
        pygame.draw.circle(screen, ring_color, (int(player_x), int(player_y)), ring_radius, 1)

    # Spieler zeichnen (beim Schleichen dunkler)
    player_color = GRAY if is_sneaking else WHITE
    pygame.draw.circle(screen, player_color, (int(player_x), int(player_y)), player_radius)

    pygame.display.flip()

pygame.quit()
sys.exit()