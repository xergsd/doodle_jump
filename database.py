"""SQLite persistence for scores and game history."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "doodle_jump.db"


class Database:
    def __init__(self, path: Path | str = DB_PATH) -> None:
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def save_game(self, score: int) -> None:
        now = datetime.now()
        self.conn.execute(
            "INSERT INTO games (score, date, time) VALUES (?, ?, ?)",
            (int(score), now.strftime("%Y-%m-%d"), now.strftime("%H:%M")),
        )
        self.conn.commit()

    def get_history(self, limit: int = 50) -> list[sqlite3.Row]:
        cursor = self.conn.execute(
            "SELECT id, score, date, time FROM games ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return list(cursor.fetchall())

    def get_best_score(self) -> int:
        row = self.conn.execute("SELECT MAX(score) AS best FROM games").fetchone()
        if row is None or row["best"] is None:
            return 0
        return int(row["best"])

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None
