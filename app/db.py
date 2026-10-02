import sqlite3
from pathlib import Path


class Store:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                create table if not exists jobs (
                    id integer primary key autoincrement,
                    telegram_id integer not null,
                    input_path text not null,
                    output_path text not null,
                    created_at text not null default current_timestamp
                );
                """
            )

    def save_job(self, telegram_id: int, input_path: str, output_path: str) -> None:
        with self.connect() as db:
            db.execute(
                "insert into jobs (telegram_id, input_path, output_path) values (?, ?, ?)",
                (telegram_id, input_path, output_path),
            )

    def stats(self) -> dict[str, int]:
        with self.connect() as db:
            jobs = db.execute("select count(*) as c from jobs").fetchone()["c"]
            users = db.execute("select count(distinct telegram_id) as c from jobs").fetchone()["c"]
        return {"jobs": jobs, "users": users}
