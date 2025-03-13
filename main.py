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
    high_scores_menu,
    achievements_menu,
)
from game import SnakeGame
import audio


async def main():
    audio.init_audio()  # Initialize pygame mixer and start background music
    settings_manager = SettingsManager()
    score_manager = ScoreManager()
    achievements_manager = AchievementsManager()

    while True:
        choice = entrance_menu()
        if choice == "1":
            mode = start_game_menu()
            game = SnakeGame(settings_manager.options, mode=mode)
            score = await game.run()
            score_manager.update_score(mode, score)
            achievements_manager.update_stats(score)
            input("Press ENTER to return to the main menu...")
        elif choice == "2":
            instructions_menu()
        elif choice == "3":
            about_menu()
        elif choice == "4":
            settings_menu(settings_manager)
        elif choice == "5":
            high_scores_menu(score_manager)
        elif choice == "6":
            achievements_menu(achievements_manager)
        elif choice in ["7", "q", "Q"]:
            print("Thank you for playing Snake Game! Goodbye!")
            time.sleep(1)
            sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting the game. Bye!")
