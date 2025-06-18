import pygame
import os
import sys
import platform

listdir = os.listdir

def get_save_dir():
    app_name = "sky_hero"
    system = platform.system()
    if system == "Windows":
        base_dir = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    elif system == "Darwin":  # macOS
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:  # Linux и всё остальное
        base_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))

    save_dir = os.path.join(base_dir, app_name)
    os.makedirs(save_dir, exist_ok=True)
    return save_dir

def save_path(rel_path):
    return os.path.join(get_save_dir(), rel_path)


def resource_path(rel_path):
    if "_MEIPASS" in sys.__dict__:
        return os.path.join(sys._MEIPASS, rel_path)
    return rel_path


os.listdir = lambda rel_path: listdir(resource_path(rel_path))


def load_image(path, scale, colorkey=None, size=None):
    path = resource_path(path)
    image = pygame.image.load(path)
    w, h = image.get_width(), image.get_height()
    w, h = int(w * scale), int(h * scale)
    if size:
        image = pygame.transform.scale(image, size)
    else:
        image = pygame.transform.scale(image, (w, h))
    if colorkey is not None:
        image.set_colorkey(colorkey)
    return image


def load_images(directory, scale, colorkey=None):
    images = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            path = os.path.join(directory, filename)
            image = load_image(path, scale, colorkey)
            images.append(image)
    return images


def sign(x):
    return 1 if x >= 0 else -1
