# audio.py
import os
import sys
import pygame


def resourse_path(relative_path):
    """Get absolute path to resource for dev or for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def init_audio():
    pygame.mixer.init()
    # Start background music (loop indefinitely)
    pygame.mixer.pre_init(frequency=16000, size=-16, channels=2, buffer=1024) # Fixed sound mismatch
    pygame.mixer.init()
    play_music("assets/music.wav")


def play_sound(sound_file):
    file_path = resourse_path(sound_file)
    if os.path.exists(file_path):
        sound = pygame.mixer.Sound(file_path)
        sound.play()
    else:
        print(f"Sound file {sound_file} not found.")


def play_music(music_file):
    file_path = resourse_path(music_file)
    if os.path.exists(file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(-1)  # Loop indefinitely
    else:
        print(f"Music file {music_file} not found.")


def stop_music():
    pygame.mixer.music.stop()
