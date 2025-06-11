from . import utils
import os

RESOURCES = {}

def load_images(directory, scale, colorkey=None):
    directory = os.path.abspath(directory)
    key = (directory, scale, colorkey)
    if key not in RESOURCES:
        RESOURCES[key] = utils.load_images(directory, scale, colorkey)
    return RESOURCES[key]


def load_image(path, scale, colorkey=None, size=None):
    path = os.path.abspath(path)
    key = (path, scale, colorkey, size)
    if key not in RESOURCES:
        RESOURCES[key] = utils.load_image(path, scale, colorkey, size)
    return RESOURCES[key]