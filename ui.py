# ui.py
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()


def safe_prompt(message, **kwargs):
    """Wrapper around Prompt.ask that catches KeyboardInterrupt."""
    try:
        return Prompt.ask(message, **kwargs)
    except KeyboardInterrupt:
        print("\nExiting the game. Bye!")
        sys.exit(0)


def safe_input(prompt=""):
    """Wrapper around input() that catches KeyboardInterrupt."""
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\nExiting the game. Bye!")
        sys.exit(0)


def entrance_menu():
    console.clear()
    snake_ascii = r"""
        _            _             _                   _              _      
       / /\         /\ \     _    / /\                /\_\           /\ \    
      / /  \       /  \ \   /\_\ / /  \              / / /  _       /  \ \   
     / / /\ \__   / /\ \ \_/ / // / /\ \            / / /  /\_\    / /\ \ \  
    / / /\ \___\ / / /\ \___/ // / /\ \ \          / / /__/ / /   / / /\ \_\ 
    \ \ \ \/___// / /  \/____// / /  \ \ \        / /\_____/ /   / /_/_ \/_/ 
     \ \ \     / / /    / / // / /___/ /\ \      / /\_______/   / /____/\    
 _    \ \ \   / / /    / / // / /_____/ /\ \    / / /\ \ \     / /\____\/    
/_/\__/ / /  / / /    / / // /_________/\ \ \  / / /  \ \ \   / / /______    
\ \/___/ /  / / /    / / // / /_       __\ \_\/ / /    \ \ \ / / /_______\   
 \_____\/   \/_/     \/_/ \_\___\     /____/_/\/_/      \_\_\\/__________/   
    """
    console.print(
        Panel(
            snake_ascii,
            title="[bold green]SNAKE GAME[/bold green]",
            subtitle="Slither into Action!",
            border_style="bright_magenta",
        )
    )
    table = Table(show_header=False, box=None)
    table.add_row("[bold yellow]1.[/bold yellow]", "Start Game")
    table.add_row("[bold yellow]2.[/bold yellow]", "Instructions")
    table.add_row("[bold yellow]3.[/bold yellow]", "About")
    table.add_row("[bold yellow]4.[/bold yellow]", "Settings")
    table.add_row("[bold yellow]5.[/bold yellow]", "High Scores")
    table.add_row("[bold yellow]6.[/bold yellow]", "Achievements")
    table.add_row("[bold yellow]7.[/bold yellow]", "Quit")
    console.print(table)
    choice = safe_prompt("\nSelect an option", default="1")
    return choice


def start_game_menu():
    console.clear()
    table = Table(show_header=False, box=None)
    table.add_row("[bold yellow]1.[/bold yellow]", "Classic")
    table.add_row("[bold yellow]2.[/bold yellow]", "Time Attack")
    table.add_row("[bold yellow]3.[/bold yellow]", "Survival")
    from rich.panel import Panel

    console.print(Panel.fit("Select Game Mode", border_style="cyan"))
    console.print(table)
    mode_choice = safe_prompt("\nSelect a mode", default="1")
    if mode_choice == "1":
        return "classic"
    elif mode_choice == "2":
        return "time_attack"
    elif mode_choice == "3":
        return "survival"


def instructions_menu():
    console.clear()
    instructions = """
[bold underline]How to Play:[/bold underline]
• Use the Arrow keys or W/A/S/D to control the snake.
• The snake’s head is represented by [green]●[/green] and its body by [green]■[/green].
• Your goal is to eat the food [red]♥[/red] which increases your score and grows your snake.
• Occasionally, power items will appear:
    - [bright_yellow]Power-Up (♦)[/bright_yellow]: Increases your score.
    - [bright_red]Power-Down (▲)[/bright_red]: Reduces your score and may shrink your snake.
• In Time Attack mode, you have a limited time to score as high as possible.
• In Survival mode, the game speeds up more aggressively.
• The walls are deadly – colliding with them or your own tail ends the game.
• After losing, press ENTER to return to the main menu.

[bold underline]Controls:[/bold underline]
• Movement: Arrow Keys or W/A/S/D
• Menu Selection: Type the corresponding option and press ENTER.

Enjoy the game and aim for a new high score!
    """
    console.print(
        Panel(
            instructions,
            title="[bold cyan]Instructions[/bold cyan]",
            border_style="cyan",
        )
    )
    safe_input("\nPress ENTER to return to the main menu...")


def about_menu():
    console.clear()
    about_text = """
[bold underline]About Snake Game[/bold underline]

This enhanced, terminal-based Snake game features creative visuals, animations, and engaging gameplay.
It includes multiple game modes:
• Classic: Standard gameplay.
• Time Attack: Score as high as possible within a time limit.
• Survival: Increase difficulty aggressively.

Audio feedback and background music enhance the experience.
Statistics and achievements track your progress.

[bold]Author:[/bold] Exonymos
[bold]GitHub:[/bold] github.com/Exonymos

Enjoy slithering through the game and challenge yourself to beat your records!
    """
    console.print(
        Panel(
            about_text,
            title="[bold magenta]About Snake Game[/bold magenta]",
            border_style="magenta",
        )
    )
    safe_input("\nPress ENTER to return to the main menu...")


def settings_menu(settings_manager):
    while True:
        console.clear()
        table = Table(title="Settings", show_header=True, header_style="bold cyan")
        table.add_column("Option", justify="center")
        table.add_column("Name", justify="left")
        table.add_column("Value", justify="center")
        options_list = list(settings_manager.options.items())
        for key, option in options_list:
            value = option["value"]
            if option["type"] == "toggle":
                value = "On" if value else "Off"
            table.add_row(key, option["name"], str(value))
        table.add_row("R", "Reset to Defaults", "")
        table.add_row("B", "Back to Main Menu", "")
        console.print(table)
        choice = (
            safe_prompt("\nSelect an option (number, R, or B)", default="B")
            .strip()
            .lower()
        )
        if choice in ["b", "back"]:
            break
        elif choice == "r":
            confirm = safe_prompt(
                "Reset all settings to default? (y/n)", choices=["y", "n"], default="n"
            )
            if confirm.lower() == "y":
                settings_manager.reset_settings()
                console.print("[green]Settings have been reset to default.[/green]")
                safe_input("Press ENTER to continue...")
                console.clear()
        elif choice in [opt_key for opt_key, _ in options_list]:
            opt_key = choice
            option = settings_manager.options[opt_key]
            if option["type"] == "toggle":
                new_val = not option["value"]
                settings_manager.update_setting(opt_key, new_val)
                console.print(
                    f"[green]{option['name']} set to {'On' if new_val else 'Off'}.[/green]"
                )
                safe_input("Press ENTER to continue...")
                console.clear()
            elif option["type"] == "choice":
                choices = option["choices"]
                choice_table = Table(
                    title=f"Select {option['name']}", show_header=False
                )
                for idx, ch in enumerate(choices, start=1):
                    choice_table.add_row(f"{idx}.", ch)
                console.print(choice_table)
                user_choice = safe_prompt(
                    "Enter the number corresponding to your choice",
                    default="1",
                )
                new_choice = choices[int(user_choice) - 1]
                settings_manager.update_setting(opt_key, new_choice)
                console.print(f"[green]{option['name']} set to {new_choice}.[/green]")
                input("Press ENTER to continue...")
        else:
            console.print("[red]Invalid input. Please try again.[/red]")
            safe_input("Press ENTER to continue...")
            console.clear()


def high_scores_menu(score_manager):
    console.clear()
    table = Table(title="High Scores", show_header=True, header_style="bold blue")
    table.add_column("Mode", justify="center")
    table.add_column("Last Score", justify="center")
    table.add_column("High Score", justify="center")
    modes = ["classic", "time_attack", "survival", "combined"]
    for mode in modes:
        mode_display = mode.replace("_", " ").title()
        last = score_manager.scores.get(mode, {}).get("last", 0)
        high = score_manager.scores.get(mode, {}).get("high", 0)
        table.add_row(mode_display, str(last), str(high))
    console.print(table)
    safe_input("\nPress ENTER to return to the main menu...")


def achievements_menu(achievements_manager):
    console.clear()
    stats = achievements_manager.get_stats()
    table = Table(
        title="Achievements & Statistics", show_header=True, header_style="bold green"
    )
    table.add_column("Total Games", justify="center")
    table.add_column("Total Score", justify="center")
    table.add_column("Best Score", justify="center")
    table.add_column("Last Game Time", justify="center")

    table.add_row(
        str(stats["total_games"]),
        str(stats["total_score"]),
        str(stats["best_score"]),
        str(stats["last_game_time"] or "N/A"),
    )
    console.print(table)
    safe_input("\nPress ENTER to return to the main menu...")
