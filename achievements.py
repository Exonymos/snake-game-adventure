# achievements.py
import os
import json
import datetime
from rich.console import Console

console = Console()
ACHIEVEMENTS_FILE = "achievements.json"

# Predefined possible achievements and their details.
POSSIBLE_ACHIEVEMENTS = {
    "Food Frenzy": "Eat 10 food items consecutively without missing.",
    "Long Snake": "Grow your snake to 15 segments.",
    "Marathon": "Survive 5 minutes in Survival mode.",
    "Combo Master": "Score at least 500 points in Time Attack mode.",
    "Speed Demon": "Complete a Classic game on Hard difficulty with a score of at least 200.",
    "Persistence": "Play 10 or more games in total.",
}

DEFAULT_ACHIEVEMENTS = {
    "total_games": 0,
    "total_score": 0,
    "best_score": 0,
    "last_game_time": None,
    "achievements": [],
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
        # Check Persistence achievement
        if self.stats["total_games"] >= 10:
            self.add_achievement("Persistence")
        self.save_stats()

    def add_achievement(self, achievement_key):
        # Use the possible achievements dictionary to get full name/description.
        if not any(a["name"] == achievement_key for a in self.stats["achievements"]):
            unlock_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.stats["achievements"].append(
                {"name": achievement_key, "unlock_time": unlock_time}
            )
            console.print(
                f"[bold green]Achievement Unlocked: {achievement_key} at {unlock_time}![/bold green]"
            )
            self.save_stats()

    def get_stats(self):
        return self.stats

    def get_unlocked(self):
        return self.stats.get("achievements", [])

    def get_locked(self):
        unlocked = {a["name"] for a in self.get_unlocked()}
        return [
            {"name": key, "detail": POSSIBLE_ACHIEVEMENTS[key]}
            for key in POSSIBLE_ACHIEVEMENTS
            if key not in unlocked
        ]

    def clear_achievements(self):
        self.stats["achievements"] = []
        self.save_stats()
