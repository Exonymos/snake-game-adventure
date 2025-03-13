# game.py
import asyncio
import random
import time
from blessed import Terminal
from rich.console import Console
import audio

console = Console()

# Map snake speed to delay (seconds per move) from settings.
SPEED_MAP = {"1: Slow": 0.2, "2: Normal": 0.1, "3: Fast": 0.05}


class SnakeGame:
    """Main Snake game logic."""

    def __init__(self, settings, mode="classic"):
        self.term = Terminal()
        self.settings = settings  # Dictionary from SettingsManager.options
        self.mode = mode  # "classic", "time_attack", or "survival"
        self.board_width = 40
        self.board_height = 20
        # Appearance of game elements
        self.snake_char = "■"
        self.snake_head_char = "●"
        self.food_char = "♥"
        self.powerup_char = "♦"
        self.powerdown_char = "▲"
        self.reset_game()

    def reset_game(self):
        self.score = 0
        self.start_time = time.time()
        self.time_up = False  # Flag to indicate time ran out
        if self.mode == "time_attack":
            self.time_limit = 60  # seconds
        start_x = self.board_width // 2
        start_y = self.board_height // 2
        self.snake = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y),
        ]
        self.direction = (1, 0)
        self.food = self.spawn_item(exclude=self.snake)
        self.power_items = []
        self.delay = SPEED_MAP[self.settings["2"]["value"]]
        self.game_over = False

    def spawn_item(self, exclude):
        while True:
            x = random.randint(1, self.board_width - 2)
            y = random.randint(1, self.board_height - 2)
            if (x, y) not in exclude:
                return (x, y)

    def maybe_spawn_power_item(self):
        if len(self.power_items) < 1 and random.random() < 0.1:
            item_type = random.choice(["powerup", "powerdown"])
            pos = self.spawn_item(exclude=self.snake + [self.food])
            self.power_items.append({"pos": pos, "type": item_type})

    def process_input(self, key):
        # Fixed mapping for arrow keys and WASD
        mapping = {
            "KEY_UP": (0, -1),
            "KEY_DOWN": (0, 1),
            "KEY_LEFT": (-1, 0),
            "KEY_RIGHT": (1, 0),
            "w": (0, -1),
            "s": (0, 1),
            "a": (-1, 0),
            "d": (1, 0),
        }
        if key in mapping:
            candidate = mapping[key]
            # If invert controls is enabled, reverse the candidate direction.
            if self.settings["4"]["value"]:
                candidate = (-candidate[0], -candidate[1])
            # Prevent 180-degree turns
            if candidate == (-self.direction[0], -self.direction[1]):
                return
            self.direction = candidate

    def get_background(self):
        # Dynamic background: cycle through colors based on time and theme.
        t = time.time()
        theme = self.settings["3"]["value"]
        if theme == "Blue":
            colors = [self.term.on_blue, self.term.on_cyan]
        elif theme == "Red":
            colors = [self.term.on_red, self.term.on_light_red]
        elif theme == "Green":
            colors = [self.term.on_green, self.term.on_light_green]
        else:
            colors = [
                self.term.on_black,
                self.term.on_blue,
                self.term.on_magenta,
                self.term.on_cyan,
            ]
        index = int(t * 2) % len(colors)
        return colors[index]

    def update(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        # Check wall collisions.
        if (
            new_head[0] <= 0
            or new_head[0] >= self.board_width - 1
            or new_head[1] <= 0
            or new_head[1] >= self.board_height - 1
        ):
            self.game_over = True
            return
        # Check self-collision.
        if new_head in self.snake:
            self.game_over = True
            return
        self.snake.insert(0, new_head)
        # Check food collision with mode-specific scoring.
        if new_head == self.food:
            if self.mode == "classic":
                food_points = 10
            elif self.mode == "time_attack":
                food_points = 15
            elif self.mode == "survival":
                food_points = 20
            self.score += food_points
            audio.play_sound("assets/eat.wav")
            self.food = self.spawn_item(exclude=self.snake)
            if self.settings["1"]["value"]:
                factor = 0.97 if self.mode == "survival" else 0.98
                self.delay = max(0.02, self.delay * factor)
        else:
            self.snake.pop()
        # Check power items collision.
        for item in self.power_items:
            if new_head == item["pos"]:
                if item["type"] == "powerup":
                    if self.mode == "classic":
                        pu_points = 20
                    elif self.mode == "time_attack":
                        pu_points = 25
                    elif self.mode == "survival":
                        pu_points = 30
                    self.score += pu_points
                    audio.play_sound("assets/power-up.wav")
                elif item["type"] == "powerdown":
                    if self.mode == "classic":
                        pd_points = 5
                    elif self.mode == "time_attack":
                        pd_points = 7
                    elif self.mode == "survival":
                        pd_points = 10
                    self.score = max(0, self.score - pd_points)
                    audio.play_sound("assets/power-down.wav")
                    if len(self.snake) > 3:
                        self.snake.pop()
                self.power_items.remove(item)
                break
        self.maybe_spawn_power_item()
        # End the game in time_attack mode when time is up.
        if self.mode == "time_attack" and (
            time.time() - self.start_time >= self.time_limit
        ):
            self.time_up = True
            self.game_over = True

    def draw(self):
        bg_func = self.get_background()
        with self.term.location():
            print(self.term.home + self.term.clear, end="")
            # Top border
            print("+" + "-" * (self.board_width - 2) + "+")
            # Draw board rows
            for y in range(1, self.board_height - 1):
                line = "|"
                for x in range(1, self.board_width - 1):
                    pos = (x, y)
                    if pos == self.snake[0]:
                        line += self.term.green(self.snake_head_char)
                    elif pos in self.snake:
                        line += self.term.green(self.snake_char)
                    elif pos == self.food:
                        line += self.term.red(self.food_char)
                    elif any(item["pos"] == pos for item in self.power_items):
                        item = next(
                            item for item in self.power_items if item["pos"] == pos
                        )
                        if item["type"] == "powerup":
                            line += self.term.bright_yellow(self.powerup_char)
                        else:
                            line += self.term.bright_red(self.powerdown_char)
                    else:
                        line += bg_func(" ")
                line += "|"
                print(line)
            # Bottom border
            print("+" + "-" * (self.board_width - 2) + "+")
            if self.mode == "time_attack":
                remaining = max(
                    0, int(self.time_limit - (time.time() - self.start_time))
                )
                print(f"Score: {self.score} | Time Left: {remaining}s")
            else:
                print(f"Score: {self.score}")

    async def run(self):
        self.reset_game()
        loop = asyncio.get_event_loop()
        with self.term.cbreak(), self.term.hidden_cursor():
            while not self.game_over:
                start_time = loop.time()
                inp = await loop.run_in_executor(None, self.term.inkey, self.delay)
                if inp:
                    self.process_input(inp.name if inp.is_sequence else inp)
                self.update()
                self.draw()
                elapsed = loop.time() - start_time
                await asyncio.sleep(max(0, self.delay - elapsed))
        # In time_attack mode, add bonus points for remaining time.
        if self.mode == "time_attack" and self.time_up:
            print("Time's up!")
        else:
            print("Game Over!")
        audio.play_sound("assets/game-over.wav")
        return self.score
