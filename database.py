import sqlite3
import csv
import os
from datetime import datetime
from config import (
    DB_PATH,
    CSV_PATH,
    LEVELS_DIR,
    TILE_SIZE,
    TILE_WALL,
    TILE_STAR,
    TILE_PLAYER,
    TILE_EXIT,
    RECORDS_LIMIT,
)


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            level INTEGER,
            score INTEGER,
            stars_collected INTEGER,
            stars_total INTEGER,
            time_seconds REAL
        )"""
    )
    conn.commit()
    conn.close()


def save_result(level, score, stars_collected, stars_total, time_seconds):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO records (date, level, score, stars_collected, stars_total, time_seconds) VALUES (?,?,?,?,?,?)",
        (
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            level,
            score,
            stars_collected,
            stars_total,
            round(time_seconds, 1),
        ),
    )
    conn.commit()
    conn.close()

    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "level", "score", "stars_collected", "stars_total", "time_seconds"])
        writer.writerow(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                level,
                score,
                stars_collected,
                stars_total,
                round(time_seconds, 1),
            ]
        )


def get_top_records(limit=None):
    if limit is None:
        limit = RECORDS_LIMIT

    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """SELECT date, level, score, stars_collected, stars_total, time_seconds
           FROM records
           ORDER BY stars_collected DESC, time_seconds ASC
               LIMIT ?""",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def load_level(level_num):
    path = os.path.join(LEVELS_DIR, f"level_{level_num}.txt")
    walls = []
    stars = []
    player_pos = None
    exit_pos = None

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for row_idx, line in enumerate(lines):
        for col_idx, char in enumerate(line):
            x = col_idx * TILE_SIZE + TILE_SIZE // 2
            y = (len(lines) - row_idx - 1) * TILE_SIZE + TILE_SIZE // 2
            if char == TILE_WALL:
                walls.append((x, y))
            elif char == TILE_STAR:
                stars.append((x, y))
            elif char == TILE_PLAYER:
                player_pos = (x, y)
            elif char == TILE_EXIT:
                exit_pos = (x, y)

    level_width = max(len(line) for line in lines) * TILE_SIZE
    level_height = len(lines) * TILE_SIZE

    return walls, stars, player_pos, exit_pos, level_width, level_height
