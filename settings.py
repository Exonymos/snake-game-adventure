# settings.py
import os
import json
from rich.console import Console

console = Console()

SETTINGS_FILE = "settings.json"
SCORE_FILE = "score.json"

DEFAULT_SETTINGS = {
    "1": {
        "name": "Gradually Speed Up Snake",
        "type": "toggle",
        "save": True,
        "default": True,
        "value": True,
    },
    "2": {
        "name": "Snake Speed",
        "type": "choice",
        "choices": ["Slow", "Normal", "Fast"],
        "save": True,
        "default": "Normal",
        "value": "Normal",
    },
    "3": {
        "name": "Theme",
        "type": "choice",
        "choices": ["Default", "Rainbow", "Dark"],
        "save": True,
        "default": "Default",
        "value": "Default",
    },
    "4": {
        "name": "Invert Controls",
        "type": "toggle",
        "save": True,
        "default": False,
        "value": False,
    },
    "5": {
        "name": "Allow Wall Wrapping (Classic Mode)",
        "type": "toggle",
        "save": True,
        "default": False,
        "value": False,
    },
    "6": {
        "name": "Music On/Off",
        "type": "toggle",
        "save": True,
        "default": True,
        "value": True,
    },
    "7": {
        "name": "Difficulty",
        "type": "choice",
        "choices": ["Easy", "Normal", "Hard"],
        "save": True,
        "default": "Normal",
        "value": "Normal",
    },
    "8": {
        "name": "Start Screen Art",
        "type": "choice",
        "choices": ["Art 1", "Art 2", "Art 3"],
        "save": True,
        "default": "Art 1",
        "value": "Art 1",
    },
}


class SettingsManager:
    """Manage game settings: load, update, and save."""

    def __init__(self, filename=SETTINGS_FILE):
        self.filename = filename
        self.options = DEFAULT_SETTINGS.copy()
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
                    for key, option in self.options.items():
                        if key in data:
                            if option["type"] == "toggle":
                                option["value"] = bool(data[key])
                            else:
                                option["value"] = data[key]
            except Exception as e:
                console.print(f"[red]Error loading settings: {e}[/red]")
        else:
            self.save_settings()

    def save_settings(self):
        data = {
            key: option["value"]
            for key, option in self.options.items()
            if option.get("save", False)
        }
        try:
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            console.print(f"[red]Error saving settings: {e}[/red]")

    def update_setting(self, key, value):
        if key in self.options:
            self.options[key]["value"] = value
            self.save_settings()

    def reset_settings(self):
        for key, option in self.options.items():
            option["value"] = option["default"]
        self.save_settings()


class ScoreManager:
    """Manage and persist scores and additional game stats."""

    def __init__(self, filename=SCORE_FILE):
        self.filename = filename
        self.scores = {
            "classic": {"last": 0, "high": 0},
            "time_attack": {"last": 0, "high": 0},
            "survival": {"last": 0, "high": 0},
            "combined": {"last": 0, "high": 0},
            "statistics": {
                "total_games": 0,
                "total_playtime": 0,
                "longest_game": 0,
                "total_max_length": 0,
                "total_collisions": 0,
                "total_lives_lost": 0,
                "games_won": 0,
                "time_attack_games": 0,
                "time_attack_wins": 0,
                "total_food_eaten": 0,
                "total_powerups": 0,
                "total_powerdowns": 0,
            },
        }
        self.load_scores()

    def load_scores(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.scores = json.load(f)
            except Exception as e:
                console.print(f"[red]Error loading scores: {e}[/red]")
        else:
            self.save_scores()

    def save_scores(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.scores, f, indent=4)
        except Exception as e:
            console.print(f"[red]Error saving scores: {e}[/red]")

    def update_score(self, mode, game_stats):
        # Update per-mode scores.
        self.scores[mode]["last"] = game_stats["score"]
        if game_stats["score"] > self.scores[mode]["high"]:
            self.scores[mode]["high"] = game_stats["score"]
        # Update combined scores.
        self.scores["combined"]["last"] = (
            self.scores["classic"]["last"]
            + self.scores["time_attack"]["last"]
            + self.scores["survival"]["last"]
        )
        self.scores["combined"]["high"] = (
            self.scores["classic"]["high"]
            + self.scores["time_attack"]["high"]
            + self.scores["survival"]["high"]
        )
        # Update additional statistics.
        stats = self.scores["statistics"]
        stats["total_games"] += 1
        stats["total_playtime"] += game_stats["duration"]
        if game_stats["duration"] > stats["longest_game"]:
            stats["longest_game"] = game_stats["duration"]
        stats["total_max_length"] += game_stats["max_length"]
        stats["total_collisions"] += game_stats["collisions"]
        stats["total_food_eaten"] += game_stats["food_eaten"]
        stats["total_powerups"] += game_stats["powerups"]
        stats["total_powerdowns"] += game_stats["powerdowns"]
        if mode == "classic":
            lives_lost = 3 - game_stats["lives_remaining"]
            stats["total_lives_lost"] += lives_lost
            if game_stats["won"]:
                stats["games_won"] += 1
        if mode == "time_attack":
            stats["time_attack_games"] = stats.get("time_attack_games", 0) + 1
            if game_stats["won"]:
                stats["time_attack_wins"] = stats.get("time_attack_wins", 0) + 1
        self.save_scores()

    def clear_scores(self):
        self.scores = {
            "classic": {"last": 0, "high": 0},
            "time_attack": {"last": 0, "high": 0},
            "survival": {"last": 0, "high": 0},
            "combined": {"last": 0, "high": 0},
            "statistics": {
                "total_games": 0,
                "total_playtime": 0,
                "longest_game": 0,
                "total_max_length": 0,
                "total_collisions": 0,
                "total_lives_lost": 0,
                "games_won": 0,
                "time_attack_games": 0,
                "time_attack_wins": 0,
                "total_food_eaten": 0,
                "total_powerups": 0,
                "total_powerdowns": 0,
            },
        }
        self.save_scores()
