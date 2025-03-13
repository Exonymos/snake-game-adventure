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
        self.settings = settings  # This is a dict from SettingsManager.options
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
        # Use custom controls from settings "4"
        controls = self.settings["4"]["value"]
        mapping = {
            controls.get("up", "KEY_UP"): (0, -1),
            controls.get("down", "KEY_DOWN"): (0, 1),
            controls.get("left", "KEY_LEFT"): (-1, 0),
            controls.get("right", "KEY_RIGHT"): (1, 0),
            # Also allow default WASD as fallback
            "w": (0, -1),
            "s": (0, 1),
            "a": (-1, 0),
            "d": (1, 0),
        }
        if key in mapping:
            new_dir = mapping[key]
            if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
                self.direction = new_dir

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
        # Check wall collisions
        if (
            new_head[0] <= 0
            or new_head[0] >= self.board_width - 1
            or new_head[1] <= 0
            or new_head[1] >= self.board_height - 1
        ):
            self.game_over = True
            return
        # Check self-collision
        if new_head in self.snake:
            self.game_over = True
            return
        self.snake.insert(0, new_head)
        # Check food
        if new_head == self.food:
            self.score += 10
            audio.play_sound("assets/eat.wav")
            self.food = self.spawn_item(exclude=self.snake)
            if self.settings["1"]["value"]:
                factor = 0.97 if self.mode == "survival" else 0.98
                self.delay = max(0.02, self.delay * factor)
        else:
            self.snake.pop()
        # Check power items
        for item in self.power_items:
            if new_head == item["pos"]:
                if item["type"] == "powerup":
                    self.score += 20
                    audio.play_sound("assets/power-up.wav")
                elif item["type"] == "powerdown":
                    self.score = max(0, self.score - 5)
                    audio.play_sound("assets/power-down.wav")
                    if len(self.snake) > 3:
                        self.snake.pop()
                self.power_items.remove(item)
                break
        self.maybe_spawn_power_item()
        if self.mode == "time_attack":
            if time.time() - self.start_time >= self.time_limit:
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
        # Removed term.noecho() since it's not a context manager.
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
        audio.play_sound("assets/game-over.wav")
        return self.score
