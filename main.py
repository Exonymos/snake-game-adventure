# main.py
import asyncio
import sys
import time
from settings import SettingsManager, ScoreManager
from achievements import AchievementsManager
from ui import (
    entrance_menu,
    start_game_menu,
    instructions_menu,
    about_menu,
    settings_menu,
    achievements_stats_menu,
    safe_input,
)
from game import SnakeGame
import audio


async def main():
    settings_manager = SettingsManager()
    # Initialize music only if enabled.
    if settings_manager.options["6"]["value"]:
        audio.init_audio()
    score_manager = ScoreManager()
    achievements_manager = AchievementsManager()

    while True:
        choice = entrance_menu()
        if choice == "1":
            mode = start_game_menu()
            if mode is None:
                continue
            game = SnakeGame(
                settings_manager.options,
                mode=mode,
                achievements_manager=achievements_manager,
            )
            score = await game.run()
            score_manager.update_score(mode, score)
            achievements_manager.update_stats(score)
            safe_input("Press ENTER to return to the main menu...")
        elif choice == "2":
            instructions_menu()
        elif choice == "3":
            about_menu()
        elif choice == "4":
            settings_menu(settings_manager)
        elif choice == "5":
            achievements_stats_menu(score_manager, achievements_manager)
        elif choice in ["6", "q", "Q"]:
            print("Goodbye and thanks for playing!")
            time.sleep(2)
            sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting the game. Bye!")
