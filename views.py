import arcade
import os
import math
import time

from entities import Player, Collectible, Obstacle, Nightmare, ExitSprite, STAR_POINTS
from particles import TrailEmitter, BurstEmitter
from database import load_level, save_result, get_top_records
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ASSETS_IMAGES_DIR,
    ASSETS_SOUNDS_DIR,
    LEVEL_NAMES,
    LEVEL_BG_COLORS,
    LEVEL_BG_IMAGES,
    RANKS,
    MAX_LEVELS,
    NIGHTMARE_PATROL_BASE,
    NIGHTMARE_PATROL_LEVEL_MULT,
    NIGHTMARE_COUNT,
    CAMERA_LERP,
    SHAKE_DURATION,
    SHAKE_INTENSITY,
    COLOR_MENU_BG,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_AWARENESS_BG,
    COLOR_AWARENESS_BAR,
    COLOR_AWARENESS_BORDER,
)


def _sound(filename):
    path = os.path.join(ASSETS_SOUNDS_DIR, filename)
    if os.path.isfile(path):
        return arcade.load_sound(path)
    return None


def _play(sound):
    if sound:
        arcade.play_sound(sound)


def get_rank(percent):
    for threshold, name in RANKS:
        if percent >= threshold:
            return name
    return RANKS[-1][1]


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self._timer = 0.0
        self._show_records = False
        self._records = []
        self._bg_stars = [(
            __import__("random").randint(0, SCREEN_WIDTH),
            __import__("random").randint(0, SCREEN_HEIGHT),
            __import__("random").uniform(0, 6.28),
        ) for _ in range(60)]
        self._bg_image = None
        self._load_background()

    def _load_background(self):
        """Загружаем фоновое изображение меню"""
        bg_path = os.path.join(ASSETS_IMAGES_DIR, "bg", "menu_bg.png")
        if os.path.isfile(bg_path):
            self._bg_image = arcade.load_texture(bg_path)

    def on_show_view(self):
        arcade.set_background_color(COLOR_MENU_BG)

    def on_update(self, delta_time):
        self._timer += delta_time

    def on_draw(self):
        self.clear()
        if self._bg_image:
            arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self._bg_image)
        self._draw_bg()
        if self._show_records:
            self._draw_records()
        else:
            self._draw_menu()

    def _draw_bg(self):
        for i, (sx, sy, phase) in enumerate(self._bg_stars):
            alpha = int(100 + 100 * math.sin(self._timer * 1.5 + phase))
            size = 1.5 if i % 3 == 0 else 1.0
            arcade.draw_circle_filled(sx, sy, size, (200, 180, 255, alpha))

    def _draw_menu(self):
        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 600, 420, (40, 25, 65, 200))
        arcade.draw_rectangle_outline(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 600, 420, (160, 120, 220), 2)

        title_y = SCREEN_HEIGHT / 2 + 150
        pulse = 1.0 + 0.04 * math.sin(self._timer * 2)
        arcade.draw_text(
            "✦ Ловец Снов ✦",
            SCREEN_WIDTH / 2,
            title_y,
            (220, 200, 255),
            font_size=int(38 * pulse),
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        arcade.draw_text(
            "Путешествие сквозь ночные сны",
            SCREEN_WIDTH / 2,
            title_y - 50,
            (180, 160, 220),
            font_size=16,
            anchor_x="center",
        )

        btn_y = SCREEN_HEIGHT / 2 - 20
        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, btn_y, 280, 50, (100, 60, 180, 200))
        arcade.draw_rectangle_outline(SCREEN_WIDTH / 2, btn_y, 280, 50, (200, 160, 255), 2)
        arcade.draw_text("▶  Начать путешествие", SCREEN_WIDTH / 2, btn_y, (255, 240, 255), font_size=18, anchor_x="center", anchor_y="center")

        rec_y = btn_y - 70
        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, rec_y, 280, 50, (60, 40, 100, 180))
        arcade.draw_rectangle_outline(SCREEN_WIDTH / 2, rec_y, 280, 50, (160, 130, 200), 2)
        arcade.draw_text("★  Таблица снов", SCREEN_WIDTH / 2, rec_y, (200, 180, 240), font_size=18, anchor_x="center", anchor_y="center")

        arcade.draw_text("WASD / стрелки — управление", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 180, (140, 120, 180), font_size=13, anchor_x="center")

    def _draw_records(self):
        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 700, 500, (40, 25, 65, 220))
        arcade.draw_rectangle_outline(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 700, 500, (160, 120, 220), 2)
        arcade.draw_text("★ Таблица снов ★", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 210, (220, 200, 255), font_size=26, anchor_x="center", bold=True)

        if not self._records:
            arcade.draw_text("Нет записей", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, (180, 160, 220), font_size=18, anchor_x="center")
        else:
            headers = ["Дата", "Ур.", "Очки", "Звёзды", "Время"]
            cols = [214, 314, 414, 514, 614]
            for i, h in enumerate(headers):
                arcade.draw_text(h, cols[i], SCREEN_HEIGHT / 2 + 165, (200, 180, 255), font_size=13, anchor_x="center", bold=True)
            for row_i, rec in enumerate(self._records[:8]):
                y = SCREEN_HEIGHT / 2 + 140 - row_i * 30
                color = (220, 210, 255) if row_i % 2 == 0 else (180, 165, 220)
                date, level, score, sc, st, t = rec
                values = [str(date), str(level), str(score), f"{sc}/{st}", f"{t}s"]
                for i, v in enumerate(values):
                    arcade.draw_text(v, cols[i], y, color, font_size=12, anchor_x="center")

        arcade.draw_text("← Назад (Escape)", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 220, (160, 140, 200), font_size=14, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if self._show_records:
            return
        btn_y = SCREEN_HEIGHT / 2 - 20
        rec_y = btn_y - 70
        if abs(x - SCREEN_WIDTH / 2) < 140 and abs(y - btn_y) < 25:
            game_view = GameView(level=1)
            self.window.show_view(game_view)
        elif abs(x - SCREEN_WIDTH / 2) < 140 and abs(y - rec_y) < 25:
            self._records = get_top_records()
            self._show_records = True

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE and self._show_records:
            self._show_records = False
        elif key == arcade.key.RETURN and not self._show_records:
            game_view = GameView(level=1)
            self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self, level=1):
        super().__init__()
        self.level = level
        self.keys = {}
        self._timer = 0.0
        self._start_time = None

        self._walls = arcade.SpriteList()
        self._stars_list = arcade.SpriteList()
        self._nightmares = arcade.SpriteList()
        self._exit_sprite = None
        self._player = None

        self._trail = TrailEmitter()
        self._burst = BurstEmitter()

        self._camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self._gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        self._stars_total = 0
        self._stars_collected = 0

        self._shake_timer = 0.0
        self._shake_intensity = 0.0

        self._snd_ambient = _sound("ambient.wav") or _sound("ambient.ogg")
        self._snd_collect = _sound("collect.wav")
        self._snd_hit = _sound("hit.wav")
        self._snd_complete = _sound("level_complete.wav")
        self._snd_gameover = _sound("game_over.wav")
        self._ambient_player = None

        self._level_width = SCREEN_WIDTH
        self._level_height = SCREEN_HEIGHT

        self._bg_image = None
        self._load_background()

    def _load_background(self):
        """Загружаем фоновое изображение для уровня"""
        bg_image_name = LEVEL_BG_IMAGES.get(self.level)
        if bg_image_name:
            bg_path = os.path.join(ASSETS_IMAGES_DIR, "bg", bg_image_name)
            if os.path.isfile(bg_path):
                self._bg_image = arcade.load_texture(bg_path)

    def on_show_view(self):
        self._load_level()
        self._start_time = time.time()
        if self._snd_ambient:
            self._ambient_player = arcade.play_sound(self._snd_ambient, looping=True)

    def _load_level(self):
        walls_pos, stars_pos, player_pos, exit_pos, lw, lh = load_level(self.level)
        self._level_width = lw
        self._level_height = lh

        for x, y in walls_pos:
            w = Obstacle(x, y)
            self._walls.append(w)

        for x, y in stars_pos:
            s = Collectible(x, y)
            self._stars_list.append(s)
        self._stars_total = len(self._stars_list)

        if player_pos:
            self._player = Player(*player_pos)
        else:
            self._player = Player(100, self._level_height // 2)

        if exit_pos:
            self._exit_sprite = ExitSprite(*exit_pos)

        import random
        patrol_range_base = NIGHTMARE_PATROL_BASE + self.level * NIGHTMARE_PATROL_LEVEL_MULT
        for i in range(NIGHTMARE_COUNT):
            nx = random.randint(200, lw - 200)
            ny = random.randint(100, lh - 100)
            nm = Nightmare(nx, ny, patrol_range=patrol_range_base)
            self._nightmares.append(nm)

    def on_hide_view(self):
        if self._ambient_player:
            arcade.stop_sound(self._ambient_player)

    def on_update(self, delta_time):
        self._timer += delta_time

        self._player.update_movement(self.keys, delta_time)
        self._player.center_x = max(20, min(self._level_width - 20, self._player.center_x))
        self._player.center_y = max(20, min(self._level_height - 20, self._player.center_y))

        wall_hits = arcade.check_for_collision_with_list(self._player, self._walls)
        for wall in wall_hits:
            dx = self._player.center_x - wall.center_x
            dy = self._player.center_y - wall.center_y
            if abs(dx) > abs(dy):
                self._player.center_x += dx * 0.3
                self._player.vel_x *= -0.5
            else:
                self._player.center_y += dy * 0.3
                self._player.vel_y *= -0.5

        star_hits = arcade.check_for_collision_with_list(self._player, self._stars_list)
        for star in star_hits:
            self._burst.burst(star.center_x, star.center_y)
            self._player.score += STAR_POINTS
            self._stars_collected += 1
            star.remove_from_sprite_lists()
            _play(self._snd_collect)

        nm_hits = arcade.check_for_collision_with_list(self._player, self._nightmares)
        if nm_hits:
            self._player.take_damage()
            if self._player.invincible_timer > 1.4:
                self._shake_timer = 0.4
                self._shake_intensity = 8.0
                _play(self._snd_hit)

        if self._exit_sprite:
            self._exit_sprite.update(delta_time)
            if arcade.check_for_collision(self._player, self._exit_sprite):
                self._finish(won=True)
                return

        if self._player.is_dead():
            self._finish(won=False)
            return

        for nm in self._nightmares:
            nm.update(delta_time)

        for star in self._stars_list:
            star.update(delta_time)

        self._trail.update(self._player.center_x, self._player.center_y, delta_time)
        self._burst.update(delta_time)

        self._update_camera(delta_time)

    def _update_camera(self, delta_time):
        target_x = self._player.center_x - SCREEN_WIDTH / 2
        target_y = self._player.center_y - SCREEN_HEIGHT / 2
        target_x = max(0, min(self._level_width - SCREEN_WIDTH, target_x))
        target_y = max(0, min(self._level_height - SCREEN_HEIGHT, target_y))

        if self._shake_timer > 0:
            import random
            target_x += random.uniform(-self._shake_intensity, self._shake_intensity)
            target_y += random.uniform(-self._shake_intensity, self._shake_intensity)
            self._shake_timer -= delta_time

        cur = self._camera.position
        lerp = CAMERA_LERP * delta_time
        new_x = cur[0] + (target_x - cur[0]) * lerp
        new_y = cur[1] + (target_y - cur[1]) * lerp
        self._camera.move_to((new_x, new_y))

    def _finish(self, won):
        if won:
            _play(self._snd_complete)
        else:
            _play(self._snd_gameover)

        elapsed = time.time() - self._start_time
        save_result(
            self.level,
            self._player.score,
            self._stars_collected,
            self._stars_total,
            elapsed,
        )
        view = GameOverView(
            won=won,
            level=self.level,
            score=self._player.score,
            stars_collected=self._stars_collected,
            stars_total=self._stars_total,
            elapsed=elapsed,
        )
        self.window.show_view(view)

    def on_draw(self):
        self.clear()
        bg = LEVEL_BG_COLORS.get(self.level, (30, 20, 50))
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, bg
        )

        # Рисуем фоновое изображение, если оно загружено
        if self._bg_image:
            self._camera.use()
            arcade.draw_lrwh_rectangle_textured(0, 0, self._level_width, self._level_height, self._bg_image)

        self._camera.use()

        self._trail.draw()
        self._walls.draw()
        self._stars_list.draw()
        self._nightmares.draw()
        if self._exit_sprite:
            self._exit_sprite.draw()

        if self._player.invincible_timer <= 0 or int(self._timer * 8) % 2 == 0:
            self._player.draw()

        self._burst.draw()

        self._gui_camera.use()
        self._draw_hud()

    def _draw_hud(self):
        ratio = max(0, self._player.awareness / 100)
        bar_w = 200
        bar_x = 20
        bar_y = SCREEN_HEIGHT - 30
        arcade.draw_rectangle_filled(bar_x + bar_w / 2, bar_y, bar_w, 18, COLOR_AWARENESS_BG)
        arcade.draw_rectangle_filled(bar_x + bar_w * ratio / 2, bar_y, bar_w * ratio, 18, COLOR_AWARENESS_BAR)
        arcade.draw_rectangle_outline(bar_x + bar_w / 2, bar_y, bar_w, 18, COLOR_AWARENESS_BORDER)
        arcade.draw_text("Осознанность", bar_x, bar_y + 12, (200, 180, 255), font_size=11)

        arcade.draw_text(f"Очки: {self._player.score}", SCREEN_WIDTH - 20, SCREEN_HEIGHT - 30, (220, 200, 255), font_size=14, anchor_x="right")
        arcade.draw_text(f"★ {self._stars_collected}/{self._stars_total}", SCREEN_WIDTH - 20, SCREEN_HEIGHT - 55, (255, 220, 100), font_size=13, anchor_x="right")
        arcade.draw_text(LEVEL_NAMES.get(self.level, ""), SCREEN_WIDTH / 2, SCREEN_HEIGHT - 25, (180, 160, 220), font_size=13, anchor_x="center")
        arcade.draw_text("Escape — меню", 10, 12, (120, 100, 160), font_size=11)

    def on_key_press(self, key, modifiers):
        self.keys[key] = True
        if key == arcade.key.ESCAPE:
            menu = MenuView()
            self.window.show_view(menu)

    def on_key_release(self, key, modifiers):
        self.keys[key] = False


class GameOverView(arcade.View):
    def __init__(self, won, level, score, stars_collected, stars_total, elapsed):
        super().__init__()
        self.won = won
        self.level = level
        self.score = score
        self.stars_collected = stars_collected
        self.stars_total = stars_total
        self.elapsed = elapsed
        self._timer = 0.0
        percent = int(stars_collected / stars_total * 100) if stars_total > 0 else 0
        self.percent = percent
        self.rank = get_rank(percent)
        self._next_level = level + 1 if won and level < MAX_LEVELS else None

    def on_show_view(self):
        arcade.set_background_color((20, 15, 35))

    def on_update(self, delta_time):
        self._timer += delta_time

    def on_draw(self):
        self.clear()

        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 700, 460, (35, 22, 55, 220))
        arcade.draw_rectangle_outline(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 700, 460, (160, 120, 220), 2)

        if self.won:
            title = "✦ Сон завершён ✦"
            title_color = (220, 200, 255)
            sub = "Ловец Снов поймал все воспоминания"
        else:
            title = "☁ Кошмар прервал сон ☁"
            title_color = (200, 140, 180)
            sub = "Осознанность упала до нуля"

        arcade.draw_text(title, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 180, title_color, font_size=30, anchor_x="center", bold=True)
        arcade.draw_text(sub, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 140, (170, 150, 200), font_size=15, anchor_x="center")

        arcade.draw_text(f"Уровень: {LEVEL_NAMES.get(self.level, str(self.level))}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 90, (200, 180, 240), font_size=14, anchor_x="center")
        arcade.draw_text(f"Очки: {self.score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60, (220, 200, 255), font_size=16, anchor_x="center")
        arcade.draw_text(f"Собрано воспоминаний: {self.stars_collected} / {self.stars_total}  ({self.percent}%)", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 28, (255, 220, 100), font_size=14, anchor_x="center")
        arcade.draw_text(f"Время в полёте: {self.elapsed:.1f} сек.", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, (180, 200, 220), font_size=14, anchor_x="center")

        rank_pulse = 1.0 + 0.05 * math.sin(self._timer * 2)
        arcade.draw_text(f"Ранг сна: «{self.rank}»", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40, (240, 200, 100), font_size=int(18 * rank_pulse), anchor_x="center", bold=True)

        if self._next_level:
            btn_y = SCREEN_HEIGHT / 2 - 110
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, btn_y, 280, 46, (100, 60, 180, 200))
            arcade.draw_rectangle_outline(SCREEN_WIDTH / 2, btn_y, 280, 46, (200, 160, 255), 2)
            arcade.draw_text("▶  Следующий уровень", SCREEN_WIDTH / 2, btn_y, (255, 240, 255), font_size=16, anchor_x="center", anchor_y="center")

        menu_y = SCREEN_HEIGHT / 2 - 170
        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, menu_y, 220, 44, (60, 40, 100, 180))
        arcade.draw_rectangle_outline(SCREEN_WIDTH / 2, menu_y, 220, 44, (160, 130, 200), 2)
        arcade.draw_text("↩  В главное меню", SCREEN_WIDTH / 2, menu_y, (200, 180, 240), font_size=15, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if self._next_level:
            btn_y = SCREEN_HEIGHT / 2 - 110
            if abs(x - SCREEN_WIDTH / 2) < 140 and abs(y - btn_y) < 23:
                self.window.show_view(GameView(level=self._next_level))
                return
        menu_y = SCREEN_HEIGHT / 2 - 170
        if abs(x - SCREEN_WIDTH / 2) < 110 and abs(y - menu_y) < 22:
            self.window.show_view(MenuView())

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE or key == arcade.key.M:
            self.window.show_view(MenuView())
        if key == arcade.key.RETURN and self._next_level:
            self.window.show_view(GameView(level=self._next_level))
