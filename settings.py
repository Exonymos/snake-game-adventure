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
        "name": "Invert Controls",
        "type": "toggle",
        "save": True,
        "default": False,
        "value": False,
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
                            # Ensure toggles are booleans.
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
    """Manage and persist scores for different game modes and combined scores."""

    def __init__(self, filename=SCORE_FILE):
        self.filename = filename
        self.scores = {
            "classic": {"last": 0, "high": 0},
            "time_attack": {"last": 0, "high": 0},
            "survival": {"last": 0, "high": 0},
            "combined": {"last": 0, "high": 0},
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

    def update_score(self, mode, score):
        self.scores[mode]["last"] = score
        if score > self.scores[mode]["high"]:
            self.scores[mode]["high"] = score
        # Combined scores are now the sum of all three modes.
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
        self.save_scores()
