import arcade
import math
import os
from config import (
    ASSETS_IMAGES_DIR,
    PLAYER_SPEED,
    PLAYER_ACCELERATION,
    PLAYER_FRICTION,
    MAX_AWARENESS,
    NIGHTMARE_DAMAGE,
    STAR_POINTS,
    PLAYER_WIDTH,
    PLAYER_HEIGHT,
    OBSTACLE_WIDTH,
    OBSTACLE_HEIGHT,
    EXIT_SIZE,
    COLLECTIBLE_SIZE,
    STAR_ANIM_SPEED,
    STAR_BLINK_AMP,
    COLOR_AWARENESS_BG,
    COLOR_AWARENESS_BAR,
    COLOR_AWARENESS_BORDER,
    NIGHTMARE_SPEED,
    NIGHTMARE_PATROL_BASE,
    NIGHTMARE_PATROL_LEVEL_MULT,
)


def _load_texture(filename):
    path = os.path.join(ASSETS_IMAGES_DIR, filename)
    return arcade.load_texture(path)


class BaseSprite(arcade.Sprite):
    def __init__(self, x, y, width=48, height=48):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height


class Player(BaseSprite):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.awareness = MAX_AWARENESS
        self.score = 0
        self.invincible_timer = 0.0
        self.anim_timer = 0.0
        self.anim_frame = 0
        self._build_textures()
        self.texture = self._idle_textures[0]
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

    def _build_textures(self):
        self._idle_textures = [_load_texture("player_idle.png")]
        self._fly_textures = [_load_texture("player_fly.png")]

    def update_movement(self, keys, delta_time):
        moving = False

        if keys.get(arcade.key.LEFT) or keys.get(arcade.key.A):
            self.vel_x -= PLAYER_ACCELERATION * delta_time
            moving = True
        if keys.get(arcade.key.RIGHT) or keys.get(arcade.key.D):
            self.vel_x += PLAYER_ACCELERATION * delta_time
            moving = True
        if keys.get(arcade.key.UP) or keys.get(arcade.key.W):
            self.vel_y += PLAYER_ACCELERATION * delta_time
            moving = True
        if keys.get(arcade.key.DOWN) or keys.get(arcade.key.S):
            self.vel_y -= PLAYER_ACCELERATION * delta_time
            moving = True

        self.vel_x = max(-PLAYER_SPEED, min(PLAYER_SPEED, self.vel_x))
        self.vel_y = max(-PLAYER_SPEED, min(PLAYER_SPEED, self.vel_y))

        if not moving:
            friction = max(0.0, 1 - PLAYER_FRICTION * delta_time)
            self.vel_x *= friction
            self.vel_y *= friction

        self.center_x += self.vel_x * delta_time
        self.center_y += self.vel_y * delta_time

        self.anim_timer += delta_time
        if self.anim_timer > 0.15:
            self.anim_timer = 0.0
            textures = self._fly_textures if moving else self._idle_textures
            self.anim_frame = (self.anim_frame + 1) % len(textures)
            self.texture = textures[self.anim_frame]

        if self.invincible_timer > 0:
            self.invincible_timer = max(0.0, self.invincible_timer - delta_time)

    def take_damage(self):
        if self.invincible_timer <= 0:
            self.awareness -= NIGHTMARE_DAMAGE
            self.invincible_timer = 1.5

    def is_dead(self):
        return self.awareness <= 0

    def draw_awareness_bar(self, cam_x, cam_y, screen_h):
        bar_x = cam_x + 20
        bar_y = cam_y + screen_h - 20
        bar_w = 200
        bar_h = 16
        ratio = max(0, self.awareness / MAX_AWARENESS)
        arcade.draw_lbwh_rectangle_filled(bar_x, bar_y - bar_h / 2, bar_w, bar_h, COLOR_AWARENESS_BG)
        arcade.draw_lbwh_rectangle_filled(bar_x, bar_y - bar_h / 2, bar_w * ratio, bar_h, COLOR_AWARENESS_BAR)
        arcade.draw_lbwh_rectangle_outline(bar_x, bar_y - bar_h / 2, bar_w, bar_h, COLOR_AWARENESS_BORDER)


class Collectible(BaseSprite):
    def __init__(self, x, y):
        super().__init__(x, y, COLLECTIBLE_SIZE, COLLECTIBLE_SIZE)
        self._timer = 0.0
        self._base_scale = 1.0
        self._angle = 0.0
        self._load_texture()
        self.width = COLLECTIBLE_SIZE
        self.height = COLLECTIBLE_SIZE
        self._base_scale = self.scale_x

    def _load_texture(self):
        self.texture = _load_texture("star.png")

    def update(self, delta_time):
        self._timer += delta_time
        self.scale = self._base_scale + STAR_BLINK_AMP * math.sin(self._timer * STAR_ANIM_SPEED)
        self._angle += 90 * delta_time
        self.angle = self._angle


class Obstacle(BaseSprite):
    def __init__(self, x, y):
        super().__init__(x, y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
        self._load_texture()
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT

    def _load_texture(self):
        self.texture = _load_texture("wall_cloud.png")


class Nightmare(BaseSprite):
    def __init__(self, x, y, patrol_range=80):
        super().__init__(x, y, 44, 44)
        self._origin_x = x
        self._patrol_range = patrol_range
        self._dir = 1
        self._speed = NIGHTMARE_SPEED
        self._load_texture()
        self.width = 44
        self.height = 44

    def _load_texture(self):
        self.texture = _load_texture("nightmare.png")

    def update(self, delta_time):
        self.center_x += self._dir * self._speed * delta_time
        if abs(self.center_x - self._origin_x) >= self._patrol_range:
            self._dir *= -1


class ExitSprite(BaseSprite):
    def __init__(self, x, y):
        super().__init__(x, y, EXIT_SIZE, EXIT_SIZE)
        self._timer = 0.0
        self._load_texture()
        self.width = EXIT_SIZE
        self.height = EXIT_SIZE

    def _load_texture(self):
        self.texture = _load_texture("dream_catcher.png")

    def update(self, delta_time):
        self._timer += delta_time
        self.scale = 1.0 + 0.08 * math.sin(self._timer * 2.5)
        self.angle = self._timer * 15
