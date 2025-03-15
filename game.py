# game.py
import asyncio
import random
import time
from blessed import Terminal
from rich.console import Console
import audio

console = Console()

SPEED_MAP = {"Slow": 0.2, "Normal": 0.1, "Fast": 0.05}


class SnakeGame:
    """Main Snake game logic."""

    def __init__(self, settings, mode="classic", achievements_manager=None):
        self.term = Terminal()
        self.settings = settings
        self.mode = mode  # "classic", "time_attack", "survival"
        self.achievements_manager = achievements_manager
        self.board_width = 40
        self.board_height = 20
        # Appearance of game elements
        self.snake_char = "■"
        self.snake_head_char = "●"
        self.food_char = "♥"
        self.powerup_char = "♦"
        self.powerdown_char = "▲"
        self.consecutive_food = 0
        self.achievements_unlocked = set()
        if self.mode == "classic":
            self.lives = 3
            self.cumulative_score = 0
        self.reset_game(initial=True)

    def reset_game(self, initial=False):
        if self.mode == "classic" and not initial:
            self.score = self.cumulative_score  # Preserve score after losing a life.
        else:
            self.score = 0
            if self.mode == "classic":
                self.cumulative_score = 0
        self.start_time = time.time()
        self.time_up = False
        if self.mode == "time_attack":
            self.time_limit = 60
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
        # Additional stats
        self.food_eaten = 0
        self.powerups_collected = 0
        self.powerdowns_collected = 0
        self.max_length = len(self.snake)
        self.collisions = 0
        difficulty = self.settings.get("7", {"value": "Normal"})["value"]
        factor = {"Easy": 1.2, "Normal": 1.0, "Hard": 0.8}.get(difficulty, 1.0)
        self.delay = SPEED_MAP[self.settings["2"]["value"]] * factor
        self.game_over = False
        self.consecutive_food = 0

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
            if self.settings["4"]["value"]:
                candidate = (-candidate[0], -candidate[1])
            if candidate == (-self.direction[0], -self.direction[1]):
                return
            self.direction = candidate

    def get_background(self):
        theme = self.settings["3"]["value"]
        if theme == "Default":
            return lambda text: text  # no background color
        elif theme == "Rainbow":
            rainbow_colors = [
                self.term.on_red,
                self.term.on_yellow,
                self.term.on_green,
                self.term.on_cyan,
                self.term.on_blue,
                self.term.on_magenta,
            ]
            index = int(time.time() * 2) % len(rainbow_colors)
            return rainbow_colors[index]
        elif theme == "Dark":
            dark_colors = [
                self.term.on_grey15,
                self.term.on_grey19,
                self.term.on_grey23,
            ]
            index = int(time.time() * 2) % len(dark_colors)
            return dark_colors[index]
        else:
            return lambda text: text

    def check_achievements(self):
        if (
            self.consecutive_food >= 10
            and "Food Frenzy" not in self.achievements_unlocked
        ):
            self.achievements_unlocked.add("Food Frenzy")
            if self.achievements_manager:
                self.achievements_manager.add_achievement("Food Frenzy")
        if len(self.snake) >= 15 and "Long Snake" not in self.achievements_unlocked:
            self.achievements_unlocked.add("Long Snake")
            if self.achievements_manager:
                self.achievements_manager.add_achievement("Long Snake")
        if (
            self.mode == "survival"
            and (time.time() - self.start_time) >= 300
            and "Marathon" not in self.achievements_unlocked
        ):
            self.achievements_unlocked.add("Marathon")
            if self.achievements_manager:
                self.achievements_manager.add_achievement("Marathon")
        if (
            self.mode == "time_attack"
            and self.score >= 500
            and "Combo Master" not in self.achievements_unlocked
        ):
            self.achievements_unlocked.add("Combo Master")
            if self.achievements_manager:
                self.achievements_manager.add_achievement("Combo Master")
        difficulty = self.settings.get("7", {"value": "Normal"})["value"]
        if (
            self.mode == "classic"
            and difficulty == "Hard"
            and self.score >= 200
            and "Speed Demon" not in self.achievements_unlocked
        ):
            self.achievements_unlocked.add("Speed Demon")
            if self.achievements_manager:
                self.achievements_manager.add_achievement("Speed Demon")

    def update(self):
        try:
            head_x, head_y = self.snake[0]
            dx, dy = self.direction
            new_head = (head_x + dx, head_y + dy)
            if self.mode == "classic":
                if self.settings.get("5", {"value": False})["value"]:
                    new_head = (
                        (new_head[0] - 1) % (self.board_width - 2) + 1,
                        (new_head[1] - 1) % (self.board_height - 2) + 1,
                    )
                else:
                    if (
                        new_head[0] <= 0
                        or new_head[0] >= self.board_width - 1
                        or new_head[1] <= 0
                        or new_head[1] >= self.board_height - 1
                    ):
                        self.collisions += 1
                        if self.lives > 1:
                            self.lives -= 1
                            self.cumulative_score = self.score
                            console.print(
                                f"[yellow]Life lost! Lives remaining: {self.lives}[/yellow]"
                            )
                            time.sleep(1)
                            self.reset_game()
                            return
                        else:
                            self.game_over = True
                            return
            else:
                if (
                    new_head[0] <= 0
                    or new_head[0] >= self.board_width - 1
                    or new_head[1] <= 0
                    or new_head[1] >= self.board_height - 1
                ):
                    self.game_over = True
                    return

            if new_head in self.snake:
                if self.mode == "classic":
                    self.collisions += 1
                    if self.lives > 1:
                        self.lives -= 1
                        self.cumulative_score = self.score
                        console.print(
                            f"[yellow]Life lost! Lives remaining: {self.lives}[/yellow]"
                        )
                        time.sleep(1)
                        self.reset_game()
                        return
                    else:
                        self.game_over = True
                        return
                else:
                    self.game_over = True
                    return

            self.snake.insert(0, new_head)
            if new_head == self.food:
                food_points = (
                    10
                    if self.mode == "classic"
                    else (15 if self.mode == "time_attack" else 20)
                )
                self.score += food_points
                if self.mode == "classic":
                    self.cumulative_score = self.score
                self.food_eaten += 1
                self.consecutive_food += 1
                audio.play_sound("assets/eat.wav")
                self.food = self.spawn_item(exclude=self.snake)
                if self.settings["1"]["value"]:
                    factor = 0.97 if self.mode == "survival" else 0.98
                    self.delay = max(0.02, self.delay * factor)
            else:
                self.consecutive_food = 0
                self.snake.pop()

            for item in self.power_items:
                if new_head == item["pos"]:
                    if item["type"] == "powerup":
                        pu_points = (
                            20
                            if self.mode == "classic"
                            else (25 if self.mode == "time_attack" else 30)
                        )
                        self.score += pu_points
                        if self.mode == "classic":
                            self.cumulative_score = self.score
                        self.powerups_collected += 1
                        audio.play_sound("assets/power-up.wav")
                    elif item["type"] == "powerdown":
                        pd_points = (
                            5
                            if self.mode == "classic"
                            else (7 if self.mode == "time_attack" else 10)
                        )
                        self.score = max(0, self.score - pd_points)
                        self.powerdowns_collected += 1
                        audio.play_sound("assets/power-down.wav")
                        if len(self.snake) > 3:
                            self.snake.pop()
                    self.power_items.remove(item)
                    break

            self.maybe_spawn_power_item()
            self.check_achievements()
            self.max_length = max(self.max_length, len(self.snake))
            if self.mode == "time_attack" and (
                time.time() - self.start_time >= self.time_limit
            ):
                self.time_up = True
                self.game_over = True
        except Exception as e:
            console.print(f"[red]Error during game update: {e}[/red]")
            self.game_over = True

    def draw(self):
        try:
            bg_color = self.get_background()
            elapsed = time.time() - self.start_time
            with self.term.location():
                print(self.term.home + self.term.clear, end="")
                print("+" + "-" * (self.board_width - 2) + "+")
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
                            line += (
                                self.term.bright_yellow(self.powerup_char)
                                if item["type"] == "powerup"
                                else self.term.bright_red(self.powerdown_char)
                            )
                        else:
                            line += bg_color(" ")
                    line += "|"
                    print(line)
                print("+" + "-" * (self.board_width - 2) + "+")
                if self.mode == "classic":
                    print(
                        f"Score: {self.score} | Lives: {self.lives} | Time: {elapsed:.1f}s"
                    )
                elif self.mode == "time_attack":
                    remaining = max(0, int(self.time_limit - elapsed))
                    print(f"Score: {self.score} | Time Left: {remaining}s")
                else:
                    print(f"Score: {self.score} | Time: {elapsed:.1f}s")
        except Exception as e:
            console.print(f"[red]Error during drawing: {e}[/red]")

    async def run(self):
        self.reset_game(initial=True)
        loop = asyncio.get_event_loop()
        try:
            with self.term.cbreak(), self.term.hidden_cursor():
                while not self.game_over:
                    start_loop = loop.time()
                    inp = await loop.run_in_executor(None, self.term.inkey, self.delay)
                    if inp:
                        self.process_input(inp.name if inp.is_sequence else inp)
                    self.update()
                    self.draw()
                    elapsed_loop = loop.time() - start_loop
                    await asyncio.sleep(max(0, self.delay - elapsed_loop))
        except Exception as e:
            console.print(f"[red]Error during game run: {e}[/red]")
        if self.mode == "time_attack" and self.time_up:
            print("Time's up!")
            win_flag = True
        elif self.mode == "time_attack":
            win_flag = False
        elif self.mode == "classic":
            win_flag = self.lives > 0
        else:
            win_flag = False
        print("Game Over!")
        audio.play_sound("assets/game-over.wav")
        # Return a dictionary of game stats.
        game_duration = time.time() - self.start_time
        stats = {
            "score": self.score,
            "duration": game_duration,
            "max_length": self.max_length,
            "collisions": self.collisions,
            "food_eaten": self.food_eaten,
            "powerups": self.powerups_collected,
            "powerdowns": self.powerdowns_collected,
            "lives_remaining": self.lives if self.mode == "classic" else None,
            "won": win_flag,
        }
        return stats
