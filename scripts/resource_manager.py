from . import utils
import os

RESOURCES = {}

def load_images(directory, scale, colorkey=None):
    key = (directory, scale, colorkey)
    if key not in RESOURCES:
        RESOURCES[key] = utils.load_images(directory, scale, colorkey)
    return RESOURCES[key]


def load_image(path, scale, colorkey=None, size=None):
    key = (path, scale, colorkey, size)
    if key not in RESOURCES:
        RESOURCES[key] = utils.load_image(path, scale, colorkey, size)
    return RESOURCES[key]
