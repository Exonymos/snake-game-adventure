import pyinstaller_versionfile

pyinstaller_versionfile.create_versionfile(
    output_file="versionfile.txt",
    version="1.0.0.0",
    company_name="Exonymos",
    file_description=(
        "A modern, console-based Snake game that combines classic arcade gameplay "
        "with modern features like asynchronous game logic, dynamic menus, audio integration, "
        "high score tracking, and achievements."
    ),
    internal_name="SnakeGameAdventure",
    legal_copyright="MIT License",
    original_filename="SnakeGameAdventure.exe",
    product_name="Snake Game Adventure",
    translations=[1033, 1200],  # 1033 = English (US); 1200 is a common charset ID.
)
