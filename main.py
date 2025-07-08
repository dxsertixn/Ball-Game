import pygame
import math
import random
import time

pygame.init()

WIDTH, HEIGHT = 1080, 2400
CENTER = (WIDTH // 2, HEIGHT // 2)
CIRCLE_RADIUS = 400
CIRCLE_THICKNESS = 3
CUTOUT_ANGLE_WIDTH = math.radians(60)
BALL_RADIUS = 20
GRAVITY = 0.8
ROTATION_SPEED = 0.01
FONT_SIZE = 48
FPS_LIMIT = 60
TEXT_COLOR = (200, 200, 200)
MAX_BALLS = 1200

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Game - By Xerous.js")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, FONT_SIZE)

rotation_angle = 0
start_time = time.time()

last_overlay_values = ("", "", "")
last_overlay_surfaces = []

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = 0
        self.color = [random.randint(120, 255) for _ in range(3)]

    def update(self):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

    def draw(self):
        outer_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.circle(screen, outer_color, (int(self.x), int(self.y)), BALL_RADIUS)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), BALL_RADIUS - 5)

    def get_polar(self):
        dx = self.x - CENTER[0]
        dy = self.y - CENTER[1]
        norm = math.hypot(dx, dy)
        angle = math.atan2(dy, dx) % (2 * math.pi)
        return dx, dy, norm, angle

    def is_through_cutout(self, rotation_angle, angle, dist):
        start = rotation_angle % (2 * math.pi)
        end = (start + CUTOUT_ANGLE_WIDTH) % (2 * math.pi)
        if start < end:
            in_cutout = start <= angle <= end
        else:
            in_cutout = angle >= start or angle <= end
        return dist >= (CIRCLE_RADIUS - BALL_RADIUS) and in_cutout

    def check_collision_with_circle(self, rotation_angle):
        dx, dy, dist, angle = self.get_polar()
        if dist <= (CIRCLE_RADIUS - BALL_RADIUS):
            return
        if self.is_through_cutout(rotation_angle, angle, dist):
            return
        norm = dist
        if norm == 0:
            return
        overlap = dist - (CIRCLE_RADIUS - BALL_RADIUS)
        self.x -= (dx / norm) * overlap
        self.y -= (dy / norm) * overlap
        nx, ny = dx / norm, dy / norm
        dot = self.vx * nx + self.vy * ny
        self.vx -= 2 * dot * nx
        self.vy -= 2 * dot * ny
        bounce_energy = 1.0
        self.vx *= bounce_energy
        self.vy *= bounce_energy
        if abs(self.vy) < 2:
            self.vy = -random.uniform(2, 5)

def draw_circle_with_cutout(rotation_angle):
    pygame.draw.circle(screen, WHITE, CENTER, CIRCLE_RADIUS, CIRCLE_THICKNESS)
    points = [CENTER]
    steps = 30
    for i in range(steps + 1):
        angle = rotation_angle + (i / steps) * CUTOUT_ANGLE_WIDTH
        x = CENTER[0] + CIRCLE_RADIUS * math.cos(angle)
        y = CENTER[1] + CIRCLE_RADIUS * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(screen, BLACK, points)

def draw_overlay(ball_count, fps, elapsed):
    global last_overlay_values, last_overlay_surfaces
    values = (f"Balls: {ball_count}", f"FPS: {int(fps)}", f"Time: {int(elapsed)}s")
    if values != last_overlay_values:
        last_overlay_surfaces = [font.render(t, True, TEXT_COLOR) for t in values]
        last_overlay_values = values
    for i, surf in enumerate(last_overlay_surfaces):
        screen.blit(surf, (20, 20 + i * 50))

balls = [Ball(CENTER[0], CENTER[1] - CIRCLE_RADIUS + 40)]
running = True

while running:
    screen.fill(BLACK)
    rotation_angle += ROTATION_SPEED
    draw_circle_with_cutout(rotation_angle)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for ball in balls:
        ball.update()

    new_balls = []
    for ball in balls[:]:
        dx, dy, dist, angle = ball.get_polar()
        if ball.is_through_cutout(rotation_angle, angle, dist):
            balls.remove(ball)
            if len(balls) + 3 <= MAX_BALLS:
                for _ in range(3):
                    offset = random.randint(-30, 30)
                    new_balls.append(Ball(CENTER[0] + offset, CENTER[1] - CIRCLE_RADIUS + 40))
            continue
        ball.check_collision_with_circle(rotation_angle)
        ball.draw()

    if len(balls) < MAX_BALLS:
        balls.extend(new_balls[:MAX_BALLS - len(balls)])

    if not balls:
        balls.append(Ball(CENTER[0], CENTER[1] - CIRCLE_RADIUS + 40))

    fps = clock.get_fps()
    elapsed_time = time.time() - start_time
    draw_overlay(len(balls), fps, elapsed_time)

    pygame.display.flip()
    clock.tick(FPS_LIMIT)

pygame.quit()
