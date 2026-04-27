import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Any # Добавили импорты для совместимости

# ── Connection parameters ─────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "snake_game",
    "user":     "postgres",
    "password": "postgres",
}

_conn = None   # module-level connection (lazy)


def _get_conn():
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(**DB_CONFIG)
        _conn.autocommit = True
    return _conn


def init_db() -> bool:
    """
    Create tables if they don't exist.
    Returns True on success, False if the DB is unreachable.
    """
    sql_players = """
        CREATE TABLE IF NOT EXISTS players (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """
    sql_sessions = """
        CREATE TABLE IF NOT EXISTS game_sessions (
            id            SERIAL PRIMARY KEY,
            player_id     INTEGER REFERENCES players(id),
            score         INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at     TIMESTAMP DEFAULT NOW()
        );
    """
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute(sql_players)
            cur.execute(sql_sessions)
        return True
    except Exception as e:
        print(f"[DB] init_db failed: {e}")
        return False


# ИСПРАВЛЕНО: заменено int | None на Optional[int] для Python 3.9
def get_or_create_player(username: str) -> Optional[int]:
    """Return existing player_id or insert and return new one."""
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s)"
                " ON CONFLICT (username) DO NOTHING;",
                (username,)
            )
            cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
            row = cur.fetchone()
            return row[0] if row else None
    except Exception as e:
        print(f"[DB] get_or_create_player failed: {e}")
        return None


def save_session(player_id: int, score: int, level_reached: int) -> None:
    """Insert one game_sessions row."""
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO game_sessions (player_id, score, level_reached)"
                " VALUES (%s, %s, %s);",
                (player_id, score, level_reached)
            )
    except Exception as e:
        print(f"[DB] save_session failed: {e}")


# ИСПРАВЛЕНО: заменено list[dict] на List[dict] для старых версий
def get_top10() -> List[dict]:
    """
    Return the top-10 all-time scores.
    Each entry: {rank, username, score, level_reached, played_at}
    """
    sql = """
        SELECT p.username,
               gs.score,
               gs.level_reached,
               gs.played_at
        FROM   game_sessions gs
        JOIN   players p ON p.id = gs.player_id
        ORDER  BY gs.score DESC
        LIMIT  10;
    """
    try:
        conn = _get_conn()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB] get_top10 failed: {e}")
        return []


def get_personal_best(player_id: int) -> int:
    """Return the player's highest score ever (0 if no sessions)."""
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(score), 0)"
                " FROM game_sessions WHERE player_id = %s;",
                (player_id,)
            )
            row = cur.fetchone()
            return row[0] if row else 0
    except Exception as e:
        print(f"[DB] get_personal_best failed: {e}")
        return 0