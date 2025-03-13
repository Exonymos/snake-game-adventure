# settings.py
import os
import json
from rich.console import Console

console = Console()

SETTINGS_FILE = "settings.json"
SCORE_FILE = "score.json"

DEFAULT_SETTINGS = {
    "1": {
        "name": "Gradually speed up snake",
        "type": "toggle",
        "save": True,
        "default": True,
        "value": True,
    },
    "2": {
        "name": "Snake speed",
        "type": "choice",
        "choices": ["1: Slow", "2: Normal", "3: Fast"],
        "save": True,
        "default": "2: Normal",
        "value": "2: Normal",
    },
    "3": {
        "name": "Theme",
        "type": "choice",
        "choices": ["Default", "Blue", "Red", "Green"],
        "save": True,
        "default": "Default",
        "value": "Default",
    },
    "4": {
        "name": "Custom Controls",
        "type": "mapping",
        "save": True,
        "default": {
            "up": "KEY_UP",
            "down": "KEY_DOWN",
            "left": "KEY_LEFT",
            "right": "KEY_RIGHT",
        },
        "value": {
            "up": "KEY_UP",
            "down": "KEY_DOWN",
            "left": "KEY_LEFT",
            "right": "KEY_RIGHT",
        },
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


class ScoreManager:
    """Manage and persist scores: high score and last score."""

    def __init__(self, filename=SCORE_FILE):
        self.filename = filename
        self.scores = {"high_score": 0, "last_score": 0, "high_score_time": None}
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

    def update_score(self, score):
        self.scores["last_score"] = score
        if score > self.scores.get("high_score", 0):
            self.scores["high_score"] = score
            from datetime import datetime

            self.scores["high_score_time"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        self.save_scores()
