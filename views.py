import arcade
import os
import math
import random
import time

from entities import Player, Collectible, Obstacle, Nightmare, ExitSprite, STAR_POINTS
from particles import TrailEmitter, BurstEmitter
from database import load_level, save_result, get_top_records, get_last_uncompleted_level
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


def _center_hit(x, y, center_x, center_y, half_width, half_height):
    return abs(x - center_x) < half_width and abs(y - center_y) < half_height


def _draw_button(center_x, center_y, width, height, bg_color, border_color, text, text_color, text_size, text_y=None):
    arcade.draw_lbwh_rectangle_filled(center_x - width / 2, center_y - height / 2, width, height, bg_color)
    arcade.draw_lbwh_rectangle_outline(center_x - width / 2, center_y - height / 2, width, height, border_color, 2)
    arcade.draw_text(
        text,
        center_x,
        center_y if text_y is None else text_y,
        text_color,
        font_size=text_size,
        anchor_x="center",
        anchor_y="center",
    )


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self._timer = 0.0
        self._show_records = False
        self._records = []
        self._bg_stars = [(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT),
            random.uniform(0, 6.28),
        ) for _ in range(60)]
        self._bg_image = None
        self._load_background()

    def _load_background(self):
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
            arcade.draw_texture_rect(
                self._bg_image,
                arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            )
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
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH / 2 - 300, SCREEN_HEIGHT / 2 - 240, 600, 480, (40, 25, 65, 200))
        arcade.draw_lbwh_rectangle_outline(SCREEN_WIDTH / 2 - 300, SCREEN_HEIGHT / 2 - 240, 600, 480, (160, 120, 220), 2)

        title_y = SCREEN_HEIGHT / 2 + 180
        pulse = 1.0 + 0.04 * math.sin(self._timer * 2)
        arcade.draw_text(
            "Ловец снов",
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

        start_y = SCREEN_HEIGHT / 2 + 30
        cont_y = start_y - 60
        select_y = cont_y - 60
        rec_y = select_y - 60

        buttons = [
            (start_y, (100, 60, 180, 200), (200, 160, 255), "Начать заново", (255, 240, 255)),
            (cont_y, (80, 50, 150, 200), (180, 140, 235), "Продолжить", (240, 230, 255)),
            (select_y, (60, 40, 120, 200), (160, 120, 210), "Выбор уровня", (220, 210, 245)),
            (rec_y, (45, 30, 90, 180), (140, 100, 180), "Таблица снов", (200, 180, 240)),
        ]

        for y, bg_color, border_color, label, text_color in buttons:
            _draw_button(SCREEN_WIDTH / 2, y, 280, 45, bg_color, border_color, label, text_color, 16)

        arcade.draw_text("WASD / стрелки — управление", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 210, (140, 120, 180), font_size=13, anchor_x="center")

    def _draw_records(self):
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH / 2 - 350, SCREEN_HEIGHT / 2 - 250, 700, 500, (40, 25, 65, 220))
        arcade.draw_lbwh_rectangle_outline(SCREEN_WIDTH / 2 - 350, SCREEN_HEIGHT / 2 - 250, 700, 500, (160, 120, 220), 2)
        arcade.draw_text("Таблица снов", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 210, (220, 200, 255), font_size=26,
                         anchor_x="center", bold=True)

        if not self._records:
            arcade.draw_text("Нет записей", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, (180, 160, 220), font_size=18,
                             anchor_x="center")
        else:
            headers = ["Дата", "Ур.", "Очки", "Звёзды", "Время"]
            cols = [294, 394, 494, 594, 694]
            for i, h in enumerate(headers):
                arcade.draw_text(h, cols[i], SCREEN_HEIGHT / 2 + 165, (200, 180, 255), font_size=13, anchor_x="center",
                                 bold=True)
            for row_i, rec in enumerate(self._records[:10]):
                y = SCREEN_HEIGHT / 2 + 140 - row_i * 25
                color = (220, 210, 255) if row_i % 2 == 0 else (180, 165, 220)
                date, level, score, sc, st, t = rec
                values = [str(date), str(level), str(score), f"{sc}/{st}", f"{t}s"]
                for i, v in enumerate(values):
                    arcade.draw_text(v, cols[i], y, color, font_size=12, anchor_x="center")

        arcade.draw_text("Назад (Escape)", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 220, (160, 140, 200), font_size=14,
                         anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if self._show_records:
            return

        start_y = SCREEN_HEIGHT / 2 + 30
        cont_y = start_y - 60
        select_y = cont_y - 60
        rec_y = select_y - 60

        if _center_hit(x, y, SCREEN_WIDTH / 2, start_y, 140, 22):
            self.window.show_view(GameView(level=1))

        elif _center_hit(x, y, SCREEN_WIDTH / 2, cont_y, 140, 22):
            next_lvl = get_last_uncompleted_level(MAX_LEVELS)
            self.window.show_view(GameView(level=next_lvl))

        elif _center_hit(x, y, SCREEN_WIDTH / 2, select_y, 140, 22):
            self.window.show_view(LevelSelectView())

        elif _center_hit(x, y, SCREEN_WIDTH / 2, rec_y, 140, 22):
            self._records = get_top_records(limit=10)
            self._show_records = True

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE and self._show_records:
            self._show_records = False
        elif key == arcade.key.RETURN and not self._show_records:
            next_lvl = get_last_uncompleted_level(MAX_LEVELS)
            self.window.show_view(GameView(level=next_lvl))


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
        self._player_list = arcade.SpriteList()
        self._exit_list = arcade.SpriteList()
        self._exit_sprite = None
        self._player = None

        self._trail = TrailEmitter()
        self._burst = BurstEmitter()

        self._camera = arcade.Camera2D()

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
        bg_image_name = LEVEL_BG_IMAGES.get(self.level)
        if bg_image_name:
            bg_path = os.path.join(ASSETS_IMAGES_DIR, "bg", bg_image_name)
            if os.path.isfile(bg_path):
                self._bg_image = arcade.load_texture(bg_path)

    def on_show_view(self):
        self._load_level()
        self._start_time = time.time()
        if self._snd_ambient:
            self._ambient_player = arcade.play_sound(self._snd_ambient, loop=True)

    def _load_level(self):
        walls_pos, stars_pos, player_pos, exit_pos, lw, lh = load_level(self.level)
        self._level_width = lw
        self._level_height = lh

        self._player_list = arcade.SpriteList()
        self._exit_list = arcade.SpriteList()

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
        self._player_list.append(self._player)

        if exit_pos:
            self._exit_sprite = ExitSprite(*exit_pos)
            self._exit_list.append(self._exit_sprite)

        SAFE_RADIUS = 250.0

        patrol_range_base = NIGHTMARE_PATROL_BASE + self.level * NIGHTMARE_PATROL_LEVEL_MULT
        for i in range(NIGHTMARE_COUNT):
            while True:
                nx = random.randint(200, lw - 200)
                ny = random.randint(100, lh - 100)
                distance_to_player = math.hypot(nx - self._player.center_x, ny - self._player.center_y)
                if distance_to_player > SAFE_RADIUS:
                    break
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
                self._shake_timer = SHAKE_DURATION
                self._shake_intensity = SHAKE_INTENSITY
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
        target_x = self._player.center_x
        target_y = self._player.center_y
        target_x = max(SCREEN_WIDTH / 2, min(self._level_width - SCREEN_WIDTH / 2, target_x))
        target_y = max(SCREEN_HEIGHT / 2, min(self._level_height - SCREEN_HEIGHT / 2, target_y))

        if self._shake_timer > 0:
            target_x += random.uniform(-self._shake_intensity, self._shake_intensity)
            target_y += random.uniform(-self._shake_intensity, self._shake_intensity)
            self._shake_timer = max(0.0, self._shake_timer - delta_time)

        cur = self._camera.position
        lerp = CAMERA_LERP * delta_time
        new_x = cur[0] + (target_x - cur[0]) * lerp
        new_y = cur[1] + (target_y - cur[1]) * lerp
        self._camera.position = (new_x, new_y)

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
            was_won=1 if won else 0,
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
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, bg)

        self._camera.use()

        if self._bg_image:
            arcade.draw_texture_rect(
                self._bg_image,
                arcade.LBWH(0, 0, self._level_width, self._level_height),
            )

        self._trail.draw()
        self._walls.draw()
        self._stars_list.draw()
        self._nightmares.draw()
        if self._exit_sprite:
            self._exit_list.draw()

        if self._player.invincible_timer <= 0 or int(self._timer * 8) % 2 == 0:
            self._player_list.draw()

        self._burst.draw()

        self.window.default_camera.use()
        self._draw_hud()

    def _draw_hud(self):
        ratio = max(0, self._player.awareness / 100)
        bar_w = 200
        bar_x = 20
        bar_y = SCREEN_HEIGHT - 30
        arcade.draw_lbwh_rectangle_filled(bar_x, bar_y - 9, bar_w, 18, COLOR_AWARENESS_BG)
        arcade.draw_lbwh_rectangle_filled(bar_x, bar_y - 9, bar_w * ratio, 18, COLOR_AWARENESS_BAR)
        arcade.draw_lbwh_rectangle_outline(bar_x, bar_y - 9, bar_w, 18, COLOR_AWARENESS_BORDER)
        arcade.draw_text("Осознанность", bar_x, bar_y + 12, (200, 180, 255), font_size=11)

        arcade.draw_text(f"Очки: {self._player.score}", SCREEN_WIDTH - 20, SCREEN_HEIGHT - 30, (220, 200, 255), font_size=14, anchor_x="right")
        arcade.draw_text(f"{self._stars_collected}/{self._stars_total}", SCREEN_WIDTH - 20, SCREEN_HEIGHT - 55, (255, 220, 100), font_size=13, anchor_x="right")
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

        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH / 2 - 350, SCREEN_HEIGHT / 2 - 230, 700, 460, (35, 22, 55, 220))
        arcade.draw_lbwh_rectangle_outline(SCREEN_WIDTH / 2 - 350, SCREEN_HEIGHT / 2 - 230, 700, 460, (160, 120, 220), 2)

        if self.won:
            title = "Сон завершён"
            title_color = (220, 200, 255)
            sub = "Ловец снов поймал воспоминания"
        else:
            title = "Кошмар прервал сон"
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
            _draw_button(SCREEN_WIDTH / 2, btn_y, 280, 46, (100, 60, 180, 200), (200, 160, 255), "Следующий уровень", (255, 240, 255), 16)

        menu_y = SCREEN_HEIGHT / 2 - 170
        _draw_button(SCREEN_WIDTH / 2, menu_y, 220, 44, (60, 40, 100, 180), (160, 130, 200), "В главное меню", (200, 180, 240), 15)

    def on_mouse_press(self, x, y, button, modifiers):
        if self._next_level:
            btn_y = SCREEN_HEIGHT / 2 - 110
            if _center_hit(x, y, SCREEN_WIDTH / 2, btn_y, 140, 23):
                self.window.show_view(GameView(level=self._next_level))
                return
        menu_y = SCREEN_HEIGHT / 2 - 170
        if _center_hit(x, y, SCREEN_WIDTH / 2, menu_y, 110, 22):
            self.window.show_view(MenuView())

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE or key == arcade.key.M:
            self.window.show_view(MenuView())
        if key == arcade.key.RETURN and self._next_level:
            self.window.show_view(GameView(level=self._next_level))


class LevelSelectView(arcade.View):
    def __init__(self):
        super().__init__()
        self._timer = 0.0
        self._max_available_level = get_last_uncompleted_level(MAX_LEVELS)

        self._buttons = []
        buttons_per_row = 4
        start_x = SCREEN_WIDTH / 2 - 150
        start_y = SCREEN_HEIGHT / 2 + 60
        spacing_x = 100
        spacing_y = 80

        for i in range(MAX_LEVELS):
            row = i // buttons_per_row
            col = i % buttons_per_row
            bx = start_x + col * spacing_x
            by = start_y - row * spacing_y
            lvl_num = i + 1
            is_unlocked = lvl_num <= self._max_available_level
            self._buttons.append({
                "level": lvl_num,
                "x": bx,
                "y": by,
                "unlocked": is_unlocked,
                "w": 70,
                "h": 55,
            })

    def on_update(self, delta_time):
        self._timer += delta_time

    def on_draw(self):
        self.clear()

        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH / 2 - 300, SCREEN_HEIGHT / 2 - 220, 600, 440, (30, 20, 50, 230))
        arcade.draw_lbwh_rectangle_outline(SCREEN_WIDTH / 2 - 300, SCREEN_HEIGHT / 2 - 220, 600, 440, (150, 110, 200), 2)

        arcade.draw_text("Выбор уровня", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 160, (220, 200, 255), font_size=24,
                         anchor_x="center", bold=True)

        for btn in self._buttons:
            self._draw_level_button(btn)

            if btn["unlocked"]:
                lvl_name = LEVEL_NAMES.get(btn["level"], f"Сон {btn['level']}")
                if len(lvl_name) > 12:
                    lvl_name = lvl_name[:10] + ".."
                arcade.draw_text(lvl_name, btn["x"], btn["y"] - 40, (160, 140, 190), font_size=9, anchor_x="center")

        back_y = SCREEN_HEIGHT / 2 - 160
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH / 2 - 90, back_y - 20, 180, 40, (50, 35, 75))
        arcade.draw_lbwh_rectangle_outline(SCREEN_WIDTH / 2 - 90, back_y - 20, 180, 40, (130, 100, 160), 1)
        arcade.draw_text("Назад в меню", SCREEN_WIDTH / 2, back_y, (190, 170, 210), font_size=14, anchor_x="center",
                         anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self._buttons:
            if abs(x - btn["x"]) < 35 and abs(y - btn["y"]) < 27:
                if btn["unlocked"]:
                    self.window.show_view(GameView(level=btn["level"]))
                    return

        back_y = SCREEN_HEIGHT / 2 - 160
        if abs(x - SCREEN_WIDTH / 2) < 90 and abs(y - back_y) < 20:
            self.window.show_view(MenuView())

    def _draw_level_button(self, btn):
        if btn["unlocked"]:
            bg_color = (90, 50, 160)
            border_color = (190, 150, 240)
            text_color = (255, 255, 255)
            text = str(btn["level"])
            text_size = 18
            text_y = btn["y"]
        else:
            bg_color = (45, 35, 55)
            border_color = (80, 70, 90)
            text_color = (110, 100, 120)
            text = "🔒"
            text_size = 14
            text_y = btn["y"] - 2

        _draw_button(btn["x"], btn["y"], btn["w"], btn["h"], bg_color, border_color, text, text_color, text_size, text_y=text_y)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())
