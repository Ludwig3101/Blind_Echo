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
DARK_CYAN = (0, 140, 160)
BLUE = (60, 160, 255)
DARK_BLUE = (20, 70, 140)
YELLOW = (255, 220, 70)

clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont("Arial", 22)
title_font = pygame.font.SysFont("Arial", 36, bold=True)

# Wand als Liniensegment
class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.glow = 0.0

    def update(self):
        if self.glow > 0:
            self.glow = max(0.0, self.glow - 0.02)

    def draw(self, surface):
        if self.glow > 0:
            intensity = int(self.glow * 255)
            color = (intensity, intensity, intensity)
            pygame.draw.line(surface, color, (self.x1, self.y1), (self.x2, self.y2), 2)

# Wasser-Pfütze (verlangsamt und erzeugt blaue Spritzer)
class WaterZone:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.glow = 0.0

    def contains(self, px, py):
        return self.rect.collidepoint(px, py)

    def update(self):
        if self.glow > 0:
            self.glow = max(0.0, self.glow - 0.015)

    def draw(self, surface):
        if self.glow > 0:
            # Wasserfläche zart blau schimmern lassen
            surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            alpha = int(self.glow * 70)
            surf.fill((20, 90, 180, alpha))
            surface.blit(surf, self.rect.topleft)
            # Umrandung zeichnen
            border_alpha = int(self.glow * 200)
            border_color = (min(255, int(BLUE[0] * self.glow)),
                            min(255, int(BLUE[1] * self.glow)),
                            min(255, int(BLUE[2] * self.glow)))
            pygame.draw.rect(surface, border_color, self.rect, 1)

# Ausgangs-Zone (Ziel des Levels)
class ExitZone:
    def __init__(self, x, y, radius=24):
        self.x = x
        self.y = y
        self.radius = radius
        self.glow = 0.0
        self.ping_timer = 0.0

    def update(self, dt):
        if self.glow > 0:
            self.glow = max(0.0, self.glow - 0.015)
        self.ping_timer += dt
        if self.ping_timer >= 3.5:
            self.ping_timer = 0.0
            self.glow = 0.8

    def draw(self, surface):
        if self.glow > 0:
            intensity = int(self.glow * 255)
            color = (intensity, int(intensity * 0.9), int(intensity * 0.3))
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius, 2)
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 4)

# Einzelner Schallstrahl
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

    def update(self, walls, water_zones, exit_zone=None):
        if not self.alive:
            return

        self.prev_x = self.x
        self.prev_y = self.y

        next_x = self.x + self.vx
        next_y = self.y + self.vy

        # Wasserzone zum Schimmern bringen
        for water in water_zones:
            if water.contains(self.x, self.y):
                water.glow = max(water.glow, 0.7)

        if exit_zone:
            dist_to_exit = math.hypot(self.x - exit_zone.x, self.y - exit_zone.y)
            if dist_to_exit < exit_zone.radius:
                exit_zone.glow = 1.0

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

def resolve_player_wall_collision(px, py, radius, wall):
    dx = wall.x2 - wall.x1
    dy = wall.y2 - wall.y1
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return px, py

    t = max(0.0, min(1.0, ((px - wall.x1) * dx + (py - wall.y1) * dy) / seg_len_sq))
    nearest_x = wall.x1 + t * dx
    nearest_y = wall.y1 + t * dy

    dist = math.hypot(px - nearest_x, py - nearest_y)
    if 0 < dist < radius:
        overlap = radius - dist
        push_x = (px - nearest_x) / dist * overlap
        push_y = (py - nearest_y) / dist * overlap
        return px + push_x, py + push_y
    return px, py

def emit_sound_pulse(x, y, ray_count=48, speed=5.0, max_life=50, bounces=1, color=CYAN):
    new_rays = []
    for i in range(ray_count):
        angle = (2 * math.pi / ray_count) * i
        new_rays.append(SoundRay(x, y, angle, speed=speed, max_life=max_life, bounces=bounces, color=color))
    return new_rays

# Level-Definitionen mit Wasserzonen
LEVELS = [
    {
        "name": "Level 1: Erwachen",
        "start": (120, 300),
        "exit": (680, 300),
        "walls": [
            Wall(60, 60, 740, 60),
            Wall(740, 60, 740, 540),
            Wall(740, 540, 60, 540),
            Wall(60, 540, 60, 60),
            Wall(250, 60, 250, 420),
            Wall(450, 180, 450, 540),
        ],
        "water": []
    },
    {
        "name": "Level 2: Kaltes Wasser",
        "start": (100, 100),
        "exit": (700, 500),
        "walls": [
            Wall(50, 50, 750, 50),
            Wall(750, 50, 750, 550),
            Wall(750, 550, 50, 550),
            Wall(50, 550, 50, 50),
            Wall(200, 50, 200, 350),
            Wall(350, 200, 350, 550),
            Wall(500, 50, 500, 350),
            Wall(620, 200, 620, 550),
        ],
        "water": [
            # Wasserabschnitte in den Gängen
            WaterZone(200, 350, 150, 200),
            WaterZone(500, 350, 120, 200)
        ]
    }
]

current_level_idx = 0

def load_level(idx):
    lvl = LEVELS[idx]
    px, py = lvl["start"]
    exit_x, exit_y = lvl["exit"]
    walls = [Wall(w.x1, w.y1, w.x2, w.y2) for w in lvl["walls"]]
    water_zones = [WaterZone(w.rect.x, w.rect.y, w.rect.w, w.rect.h) for w in lvl.get("water", [])]
    exit_zone = ExitZone(exit_x, exit_y)
    return px, py, walls, water_zones, exit_zone

player_x, player_y, walls, water_zones, exit_zone = load_level(current_level_idx)

# Spieler-Attribute
player_normal_speed = 3.6
player_sneak_speed = 1.6
player_radius = 7

walk_distance = 0.0
step_interval = 28.0

charging = False
charge_time = 0.0
max_charge = 1.0

rays = []
game_state = "PLAYING"

running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    charging = True
                    charge_time = 0.0

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and charging:
                    charging = False
                    charge_ratio = min(1.0, charge_time / max_charge)

                    # Prüfen ob Spieler im Wasser steht
                    in_water = any(w.contains(player_x, player_y) for w in water_zones)
                    pulse_color = BLUE if in_water else (CYAN if charge_ratio < 0.2 else WHITE)

                    if charge_ratio < 0.2:
                        rays.extend(emit_sound_pulse(player_x, player_y, ray_count=36, speed=4.5, max_life=40, bounces=1, color=pulse_color))
                    else:
                        ray_count = int(48 + charge_ratio * 40)
                        speed = 5.0 + charge_ratio * 2.5
                        life = int(50 + charge_ratio * 40)
                        bounces = 2 if charge_ratio < 0.7 else 3
                        rays.extend(emit_sound_pulse(player_x, player_y, ray_count=ray_count, speed=speed, max_life=life, bounces=bounces, color=pulse_color))

        elif game_state == "LEVEL_CLEAR":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                current_level_idx = (current_level_idx + 1) % len(LEVELS)
                player_x, player_y, walls, water_zones, exit_zone = load_level(current_level_idx)
                rays.clear()
                game_state = "PLAYING"

    if game_state == "PLAYING":
        keys = pygame.key.get_pressed()
        is_sneaking = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Im Wasser bewegt man sich langsamer
        in_water = any(w.contains(player_x, player_y) for w in water_zones)
        speed_mult = 0.65 if in_water else 1.0

        current_speed = (player_sneak_speed if is_sneaking else player_normal_speed) * speed_mult

        move_x = 0
        move_y = 0
        if keys[pygame.K_w]: move_y -= 1
        if keys[pygame.K_s]: move_y += 1
        if keys[pygame.K_a]: move_x -= 1
        if keys[pygame.K_d]: move_x += 1

        if move_x != 0 or move_y != 0:
            length = math.hypot(move_x, move_y)
            dx = (move_x / length) * current_speed
            dy = (move_y / length) * current_speed

            player_x += dx
            player_y += dy

            for wall in walls:
                player_x, player_y = resolve_player_wall_collision(player_x, player_y, player_radius, wall)

            # Im Wasser macht jeder Schritt Plätschern (auch beim Schleichen etwas)
            effective_interval = 18.0 if in_water else step_interval
            step_allowed = in_water or (not is_sneaking)

            if step_allowed:
                walk_distance += math.hypot(dx, dy)
                if walk_distance >= effective_interval:
                    walk_distance = 0.0
                    if in_water:
                        # Wasser-Plätschern (blau)
                        rays.extend(emit_sound_pulse(player_x, player_y, ray_count=22, speed=3.2, max_life=30, bounces=1, color=BLUE))
                    else:
                        rays.extend(emit_sound_pulse(player_x, player_y, ray_count=16, speed=3.0, max_life=22, bounces=0, color=DARK_CYAN))
        else:
            walk_distance = step_interval * 0.5

        if charging:
            charge_time += dt

        exit_dist = math.hypot(player_x - exit_zone.x, player_y - exit_zone.y)
        if exit_dist < exit_zone.radius:
            game_state = "LEVEL_CLEAR"

        for wall in walls:
            wall.update()
        for water in water_zones:
            water.update()
        exit_zone.update(dt)

        for ray in rays:
            ray.update(walls, water_zones, exit_zone)
        rays = [r for r in rays if r.alive]

    # Zeichnen
    screen.fill(BLACK)

    if game_state == "PLAYING":
        # Zuerst Wasserzonen (unter Wänden)
        for water in water_zones:
            water.draw(screen)

        for wall in walls:
            wall.draw(screen)

        exit_zone.draw(screen)

        for ray in rays:
            ray.draw(screen)

        if charging:
            charge_ratio = min(1.0, charge_time / max_charge)
            ring_radius = int(player_radius + 4 + charge_ratio * 16)
            ring_color = BLUE if in_water else (WHITE if charge_ratio > 0.8 else CYAN)
            pygame.draw.circle(screen, ring_color, (int(player_x), int(player_y)), ring_radius, 1)

        player_color = BLUE if in_water else (GRAY if is_sneaking else WHITE)
        pygame.draw.circle(screen, player_color, (int(player_x), int(player_y)), player_radius)

    elif game_state == "LEVEL_CLEAR":
        txt = title_font.render("AUSGANG ERREICHT!", True, YELLOW)
        sub = font.render("Drücke LEERTASTE für das nächste Level", True, WHITE)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))

    pygame.display.flip()

pygame.quit()
sys.exit()