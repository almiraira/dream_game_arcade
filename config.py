import os
from dotenv import load_dotenv

load_dotenv()

SCREEN_WIDTH = int(os.getenv("SCREEN_WIDTH", 1024))
SCREEN_HEIGHT = int(os.getenv("SCREEN_HEIGHT", 640))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, os.getenv("ASSETS_DIR", "assets"))
ASSETS_IMAGES_DIR = os.path.join(BASE_DIR, os.getenv("ASSETS_IMAGES_DIR", "assets/images"))
ASSETS_SOUNDS_DIR = os.path.join(BASE_DIR, os.getenv("ASSETS_SOUNDS_DIR", "assets/sounds"))
LEVELS_DIR = os.path.join(BASE_DIR, os.getenv("LEVELS_DIR", "levels"))
DATA_DIR = os.path.join(BASE_DIR, os.getenv("DATA_DIR", "data"))
DB_PATH = os.path.join(BASE_DIR, os.getenv("DB_PATH", "data/dream_history.db"))
CSV_PATH = os.path.join(BASE_DIR, os.getenv("CSV_PATH", "data/dream_history.csv"))

MAX_LEVELS = int(os.getenv("MAX_LEVELS", 3))

LEVEL_NAMES = {
    1: "Фаза 1: Лавандовый туман",
    2: "Фаза 2: Звёздный океан",
    3: "Фаза 3: Розовый рассвет",
}

LEVEL_BG_COLORS = {
    1: (60, 40, 90),
    2: (20, 20, 60),
    3: (90, 40, 60),
}

LEVEL_BG_IMAGES = {
    1: "background_1.png",
    2: "background_2.png",
    3: "background_3.png",
}

PLAYER_SPEED = 200
PLAYER_ACCELERATION = 400
PLAYER_FRICTION = 3.0
MAX_AWARENESS = 100
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 48

NIGHTMARE_DAMAGE = 25
NIGHTMARE_SPEED = 60
NIGHTMARE_PATROL_BASE = 60
NIGHTMARE_PATROL_LEVEL_MULT = 20
NIGHTMARE_COUNT = 3

STAR_POINTS = 10
STAR_SIZE = 28
STAR_ANIM_SPEED = 3
STAR_BLINK_AMP = 0.1

OBSTACLE_WIDTH = 60
OBSTACLE_HEIGHT = 44
EXIT_SIZE = 56
COLLECTIBLE_SIZE = 28

TRAIL_EMIT_RATE = 0.04
TRAIL_LIFETIME_MIN = 0.3
TRAIL_LIFETIME_MAX = 0.7
BURST_COUNT = 18
BURST_LIFETIME_MIN = 0.4
BURST_LIFETIME_MAX = 0.9

COLOR_PLAYER_IDLE = (200, 180, 255)
COLOR_PLAYER_FLY = (220, 200, 255)
COLOR_TRAIL = [(180, 160, 255), (220, 200, 255), (255, 240, 255)]
COLOR_BURST = [(255, 220, 100), (255, 180, 50), (255, 255, 150), (200, 255, 200)]
COLOR_AWARENESS_BG = (60, 40, 80, 180)
COLOR_AWARENESS_BAR = (160, 100, 255, 220)
COLOR_AWARENESS_BORDER = (200, 180, 255)
COLOR_TEXT_PRIMARY = (220, 200, 255)
COLOR_TEXT_SECONDARY = (180, 160, 220)
COLOR_MENU_BG = (30, 20, 50)

CAMERA_LERP = 5.0
SHAKE_DURATION = 0.4
SHAKE_INTENSITY = 8.0

RECORDS_LIMIT = 10

RANKS = [
    (90, "Осознанный сон"),
    (60, "Глубокий сон"),
    (30, "Беспокойный сон"),
    (0, "Разрушенный сон"),
]

TILE_SIZE = 64
TILE_WALL = "#"
TILE_STAR = "*"
TILE_PLAYER = "@"
TILE_EXIT = "E"

