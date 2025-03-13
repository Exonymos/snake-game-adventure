# ui.py
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
import time

console = Console()


def entrance_menu():
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
    console.clear()
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
    choice = Prompt.ask(
        "\nSelect an option", choices=[str(i) for i in range(1, 10)], default="1"
    )
    return choice


def start_game_menu():
    from rich.table import Table
    from rich.prompt import Prompt

    table = Table(show_header=False, box=None)
    table.add_row("[bold yellow]1.[/bold yellow]", "Classic")
    table.add_row("[bold yellow]2.[/bold yellow]", "Time Attack")
    table.add_row("[bold yellow]3.[/bold yellow]", "Survival")
    import time
    from rich.panel import Panel

    console.clear()
    console.print(Panel.fit("Select Game Mode", border_style="cyan"))
    console.print(table)
    mode_choice = Prompt.ask("\nSelect a mode", choices=["1", "2", "3"], default="1")
    if mode_choice == "1":
        return "classic"
    elif mode_choice == "2":
        return "time_attack"
    elif mode_choice == "3":
        return "survival"


def instructions_menu():
    instructions = """
[bold underline]How to Play:[/bold underline]
• Use the Arrow keys or W/A/S/D to control the snake.
• The snake’s head is represented by [green]●[/green] and its body by [green]■[/green].
• Your goal is to eat the food [red]♥[/red] which increases your score by 10 and grows your snake.
• Occasionally, power items will appear:
    - [bright_yellow]Power-Up (♦)[/bright_yellow]: Increases your score by 20.
    - [bright_red]Power-Down (▲)[/bright_red]: Reduces your score by 5 and may shrink your snake if its length exceeds the starting length.
• In Time Attack mode, you have a limited time to score as high as possible.
• In Survival mode, the game speeds up more aggressively.
• The walls (borders) are deadly – colliding with them or your own tail ends the game.
• After losing, press ENTER to return to the main menu.

[bold underline]Controls:[/bold underline]
• Movement: Arrow Keys or W/A/S/D
• Menu Selection: Type the corresponding number and press ENTER.

Enjoy the game and aim for a new high score!
    """
    console.clear()
    console.print(
        Panel(
            instructions,
            title="[bold cyan]Instructions[/bold cyan]",
            border_style="cyan",
        )
    )
    input("\nPress ENTER to return to the main menu...")


def about_menu():
    about_text = """
[bold underline]About Snake Game[/bold underline]

This enhanced, terminal-based Snake game features creative visuals, animations, and engaging gameplay.
It includes multiple game modes:
• Classic: Standard gameplay.
• Time Attack: Score as high as possible within a time limit.
• Survival: Increase difficulty aggressively to test your endurance.

Audio feedback and background music enhance the experience.
Statistics and achievements track your progress.

[bold]Author:[/bold] Exonymos
[bold]GitHub:[/bold] github.com/Exonymos

Enjoy slithering through the game and challenge yourself to beat your records!
    """
    console.clear()
    console.print(
        Panel(
            about_text,
            title="[bold magenta]About Snake Game[/bold magenta]",
            border_style="magenta",
        )
    )
    input("\nPress ENTER to return to the main menu...")


def settings_menu(settings_manager):
    from rich.table import Table
    from rich.prompt import Prompt

    console.clear()
    while True:
        table = Table(title="Settings", show_header=True, header_style="bold cyan")
        table.add_column("Option Number", justify="center")
        table.add_column("Name", justify="left")
        table.add_column("Value", justify="center")
        options_list = list(settings_manager.options.items())
        for i, (key, option) in enumerate(options_list, start=1):
            table.add_row(str(i), option["name"], str(option["value"]))
        console.print(table)
        console.print(
            "\nType the Option Number to change or type 'back' to return to the main menu."
        )
        choice = Prompt.ask("Your choice").strip()
        if choice.lower() == "back":
            break
        if choice.isdigit() and 1 <= int(choice) <= len(options_list):
            opt_key, opt = options_list[int(choice) - 1]
            if opt["type"] == "toggle":
                new_val = not opt["value"]
                settings_manager.update_setting(opt_key, new_val)
                console.print(f"[green]{opt['name']} set to {new_val}.[/green]")
            elif opt["type"] == "choice":
                choices = opt["choices"]
                choices_table = Table(title=f"Select {opt['name']}", show_header=False)
                for idx, choice_str in enumerate(choices, start=1):
                    choices_table.add_row(f"{idx}.", choice_str)
                console.print(choices_table)
                user_choice = Prompt.ask(
                    "Enter the number corresponding to your choice",
                    choices=[str(i) for i in range(1, len(choices) + 1)],
                )
                new_choice = choices[int(user_choice) - 1]
                settings_manager.update_setting(opt_key, new_choice)
                console.print(f"[green]{opt['name']} set to {new_choice}.[/green]")
            input("\nPress ENTER to continue...")
        else:
            console.print("[red]Invalid input. Please try again.[/red]")
            input("\nPress ENTER to continue...")


def high_scores_menu(score_manager):
    from rich.table import Table

    console.clear()
    table = Table(title="High Scores", show_header=True, header_style="bold blue")
    table.add_column("Last Score", justify="center")
    table.add_column("High Score", justify="center")
    table.add_column("High Score Time", justify="center")
    table.add_row(
        str(score_manager.scores.get("last_score", 0)),
        str(score_manager.scores.get("high_score", 0)),
        str(score_manager.scores.get("high_score_time", "N/A")),
    )
    console.print(table)
    input("\nPress ENTER to return to the main menu...")


def achievements_menu(achievements_manager):
    from rich.table import Table

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
    input("\nPress ENTER to return to the main menu...")
