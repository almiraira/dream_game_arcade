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


def _connect_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = _connect_db()
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                level INTEGER,
                score INTEGER,
                stars_collected INTEGER,
                stars_total INTEGER,
                time_seconds REAL,
                was_won INTEGER DEFAULT 1
            )"""
        )
        conn.commit()
    finally:
        conn.close()


def save_result(level, score, stars_collected, stars_total, time_seconds, was_won=1):
    conn = _connect_db()
    try:
        conn.execute(
            "INSERT INTO records (date, level, score, stars_collected, stars_total, time_seconds, was_won) VALUES (?,?,?,?,?,?,?)",
            (
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                level,
                score,
                stars_collected,
                stars_total,
                round(time_seconds, 1),
                was_won,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "level", "score", "stars_collected", "stars_total", "time_seconds", "was_won"])
        writer.writerow(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                level,
                score,
                stars_collected,
                stars_total,
                round(time_seconds, 1),
                was_won,
            ]
        )


def get_top_records(limit=None):
    if limit is None:
        limit = RECORDS_LIMIT

    conn = _connect_db()
    try:
        cur = conn.execute(
            """SELECT date, level, score, stars_collected, stars_total, time_seconds
               FROM records
               ORDER BY stars_collected DESC, time_seconds ASC
                   LIMIT ?""",
            (limit,),
        )
        return cur.fetchall()
    finally:
        conn.close()


def load_level(level_num):
    path = os.path.join(LEVELS_DIR, f"level_{level_num}.txt")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Level file not found: {path}")

    walls = []
    stars = []
    player_pos = None
    exit_pos = None

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    if not lines:
        raise ValueError(f"Level file is empty: {path}")

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

    if player_pos is None:
        raise ValueError(f"Level is missing player spawn: {path}")
    if exit_pos is None:
        raise ValueError(f"Level is missing exit: {path}")

    return walls, stars, player_pos, exit_pos, level_width, level_height


def get_last_uncompleted_level(max_levels):
    conn = _connect_db()
    try:
        row = conn.execute("SELECT MAX(level) FROM records WHERE was_won = 1").fetchone()
    finally:
        conn.close()

    if row and row[0] is not None:
        max_id_in_db = row[0]
        if max_id_in_db < max_levels:
            return max_id_in_db + 1
        return max_levels

    return 1


init_db()