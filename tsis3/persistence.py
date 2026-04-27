import json
import os

SETTINGS_FILE   = os.path.join(os.path.dirname(__file__), "settings.json")
LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")

DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  [50, 120, 220],
    "difficulty": "Normal",
}

# ── Settings ──────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    """Load settings from JSON, filling any missing keys with defaults."""
    try:
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
    except Exception:
        data = {}
    # Merge: keep saved values, add any missing defaults
    for key, val in DEFAULT_SETTINGS.items():
        if key not in data:
            data[key] = val
    return data


def save_settings(settings: dict) -> None:
    """Persist settings dict to JSON."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


# ── Leaderboard ───────────────────────────────────────────────────────────────

def load_leaderboard() -> list:
    """Return list of leaderboard entries (dicts with name/score/distance)."""
    try:
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def save_leaderboard(entries: list) -> None:
    """Save leaderboard, keeping only top 50 entries sorted by score."""
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(entries[:50], f, indent=2)


def add_leaderboard_entry(name: str, score: int, distance: int, coins: int) -> None:
    """Append a new run to the leaderboard and save."""
    entries = load_leaderboard()
    entries.append({"name": name, "score": score,
                    "distance": distance, "coins": coins})
    save_leaderboard(entries)
