# achievements.py
import os
import json
import datetime
from rich.console import Console

console = Console()
ACHIEVEMENTS_FILE = "achievements.json"

DEFAULT_ACHIEVEMENTS = {
    "total_games": 0,
    "total_score": 0,
    "best_score": 0,
    "last_game_time": None,
}


class AchievementsManager:
    """Manage statistics and achievements."""

    def __init__(self, filename=ACHIEVEMENTS_FILE):
        self.filename = filename
        self.stats = DEFAULT_ACHIEVEMENTS.copy()
        self.load_stats()

    def load_stats(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.stats = json.load(f)
            except Exception as e:
                console.print(f"[red]Error loading achievements: {e}[/red]")
        else:
            self.save_stats()

    def save_stats(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.stats, f, indent=4)
        except Exception as e:
            console.print(f"[red]Error saving achievements: {e}[/red]")

    def update_stats(self, score):
        self.stats["total_games"] += 1
        self.stats["total_score"] += score
        if score > self.stats["best_score"]:
            self.stats["best_score"] = score
        self.stats["last_game_time"] = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.save_stats()

    def get_stats(self):
        return self.stats
