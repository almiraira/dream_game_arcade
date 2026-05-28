import arcade
import random
import math
from config import (
    COLOR_TRAIL,
    COLOR_BURST,
    TRAIL_EMIT_RATE,
    TRAIL_LIFETIME_MIN,
    TRAIL_LIFETIME_MAX,
    BURST_COUNT,
    BURST_LIFETIME_MIN,
    BURST_LIFETIME_MAX,
)


class Particle:
    def __init__(self, x, y, color, vx, vy, lifetime, size=4):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True

    def update(self, delta_time):
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.alive = False

    def draw(self):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        r, g, b = self.color[0], self.color[1], self.color[2]
        arcade.draw_circle_filled(self.x, self.y, self.size, (r, g, b, alpha))


class TrailEmitter:
    def __init__(self):
        self.particles = []
        self.timer = 0.0
        self.emit_rate = TRAIL_EMIT_RATE

    def emit(self, x, y):
        self.timer = 0.0
        color = random.choice(COLOR_TRAIL)
        vx = random.uniform(-20, 20)
        vy = random.uniform(-20, 20)
        size = random.uniform(2, 5)
        p = Particle(x, y, color, vx, vy, random.uniform(TRAIL_LIFETIME_MIN, TRAIL_LIFETIME_MAX), size)
        self.particles.append(p)

    def update(self, x, y, delta_time):
        self.timer += delta_time
        if self.timer >= self.emit_rate:
            self.emit(x, y)
            self.timer = 0.0
        for p in self.particles:
            p.update(delta_time)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self):
        for p in self.particles:
            p.draw()


class BurstEmitter:
    def __init__(self):
        self.particles = []

    def burst(self, x, y, count=None):
        if count is None:
            count = BURST_COUNT
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(60, 180)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice(COLOR_BURST)
            size = random.uniform(3, 7)
            p = Particle(x, y, color, vx, vy, random.uniform(BURST_LIFETIME_MIN, BURST_LIFETIME_MAX), size)
            self.particles.append(p)

    def update(self, delta_time):
        for p in self.particles:
            p.update(delta_time)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self):
        for p in self.particles:
            p.draw()
