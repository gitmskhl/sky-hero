import os
import pygame
from scripts.utils import resource_path

CREDITS_TEXT = [
    "You have walked the path, warrior",
    "The trials are behind you now",
    "You faced the world — and endured",
    "Your journey is written in the stars",
    "From student to hero, you have grown",
    "Thank you for playing",
] + \
[''] * 5 + \
[
    "Inspired by DaFluffyPotato",  
    "whose creativity and tutorials",  
    "sparked the idea behind this game",  
    "The project was born from one",
    "of his YouTube videos."
]

def count_levels():
    """Return the maximum positive level number based on files in the maps folder."""
    maps_dir = resource_path('maps')
    max_level = 0
    for filename in os.listdir(maps_dir):
        if not filename.startswith('map_level') or not filename.endswith('.json'):
            continue
        num_part = filename[len('map_level'):-5]
        try:
            lvl = int(num_part)
        except ValueError:
            continue
        if lvl > 0 and lvl > max_level:
            max_level = lvl
    return max_level


class Credits:
    """Simple scrolling credits screen."""

    def __init__(self, text=CREDITS_TEXT):
        if isinstance(text, str):
            self.lines = text.splitlines()
        else:
            self.lines = list(text)
        self.font_path = resource_path('fonts/Pacifico.ttf')

    def the_end(self, screen, clock):
        surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        surf.set_alpha(0)
        alpha = 0
        timer = 2
        font = pygame.font.Font(resource_path('fonts/Pacifico.ttf'), 58)
        while alpha != 256:
            screen.fill((0, 0, 0))
            surf.fill((0, 0, 0, 255))
            clock.tick(60)
            timer -= 1
            if timer == 0:
                alpha += 1
                timer = 2
                surf.set_alpha(alpha)
            text = font.render("The end...", True, (255, 255, 255))
            surf.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2 - text.get_height() // 2))
            screen.blit(surf, (0, 0))
            pygame.display.flip()
        timer = 2
        for _ in range(256):
            surf.fill((0, 0, 0, 1))
            clock.tick(60)
            timer -= 1
            if timer == 0:
                timer = 2
            screen.blit(surf, (0, 0))
            pygame.display.flip()


    def run(self, screen):
        clock = pygame.time.Clock()
        font = pygame.font.Font(self.font_path, 48)
        line_height = font.get_height() + 10
        y = screen.get_height()
        total_height = len(self.lines) * line_height
        timer = 1
        running = True
        while running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.KEYDOWN):
                    running = False

            screen.fill((0, 0, 0))
            if timer > 0:
                timer -= 1
                self.the_end(screen, clock)
            else:
                for i, line in enumerate(self.lines):
                    surf = font.render(line, True, (255, 255, 255))
                    rect = surf.get_rect(center=(screen.get_width() // 2, y + i * line_height))
                    screen.blit(surf, rect)

                y -= 1
                if y + total_height < 0:
                    running = False
            pygame.display.flip()
