import pygame
import shelve

from .utils import save_path

pygame.init()

KEY_BINDINGS = {
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'jump': pygame.K_SPACE,
    'attack': pygame.K_x,
}

def init_keyboard():
    global KEY_BINDINGS
    try:
        with shelve.open(save_path('key_bindings')) as db:
            if 'key_bindings' in db:
                KEY_BINDINGS = db['key_bindings']
    except Exception as e:
        print(f"Error loading key bindings: {e}")


def save_key_bindings():
    with shelve.open(save_path('key_bindings'), 'c') as db:
        db['key_bindings'] = KEY_BINDINGS
