import pygame
import json
from .editor import Editor 
from scripts.physics import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK
from scripts.utils import load_image
from .cloud import Clouds
from .leaf import Leaves
from particle import Particles
from random import random

class Map(Editor):
    def __init__(self, level):
        super().__init__(level)
        self.background_image = load_image('images/background.png', 0, BLACK, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clouds = Clouds(count=30)
        self._init_leaves()
        self.particles = Particles()
        self.screenshake = 0


    def _init_leaves(self):
        tree_img = self.resources['large_decor'][2]
        w_tree, h_tree = tree_img.get_width(), tree_img.get_height()
        self.leaves = []
        for pos, tile in self.tile_map.items():
            if tile['resource'] == 'large_decor' and tile['variant'] == 2:
                self.leaves.append(
                    Leaves(
                        count=10,
                        x_tree=pos[0] * self.tile_size,
                        y_tree=pos[1] * self.tile_size,
                        w_tree=w_tree,
                        h_tree=h_tree,
                    )
                )
        for tile in self.nogrid_tiles:
            if tile['resource'] == 'large_decor' and tile['variant'] == 2:
                self.leaves.append(
                    Leaves(
                        count=10,
                        x_tree=tile['pos'][0] * self.k,
                        y_tree=tile['pos'][1] * self.k,
                        w_tree=w_tree,
                        h_tree=h_tree,
                    )
                )


    def update(self):
        self.screenshake = max(0, self.screenshake - 1)
        screen_offset = [(random() - .5) * self.screenshake, (random() - .5) * self.screenshake]
        self.camera[0] += screen_offset[0]
        self.camera[1] += screen_offset[1]
        self.clouds.update(self.camera)
        for l in self.leaves: l.update()
        self.particles.update()

    def render(self, display, display_2):
        display_2.blit(self.background_image, (0, 0))
        for l in self.leaves: l.render(display, self.camera)
        self.particles.render(display_2, self.camera)
        self.clouds.render(display)
        i_start = int(self.camera[0] // self.tile_size)
        j_start = int(self.camera[1] // self.tile_size)
        i_end = int((self.camera[0] + SCREEN_WIDTH) // self.tile_size + 1)
        j_end = int((self.camera[1] + SCREEN_HEIGHT) // self.tile_size + 1)
        for i in range(i_start, i_end):
            for j in range(j_start, j_end):
                if (i, j) in self.tile_map:
                    tile = self.tile_map[(i, j)]
                    img = self.resources[tile['resource']][tile['variant']]
                    display.blit(img, (i * self.tile_size - self.camera[0], j * self.tile_size - self.camera[1]))
        for tile in self.nogrid_tiles:
            img = self.resources[tile['resource']][tile['variant']]
            if tile['pos'][0] * self.k - self.camera[0] + img.get_width() < 0 or tile['pos'][0] * self.k - self.camera[0] > SCREEN_WIDTH:
                continue
            if tile['pos'][1] * self.k - self.camera[1] + img.get_height() < 0 or tile['pos'][1] * self.k - self.camera[1] > SCREEN_HEIGHT:
                continue
            display.blit(img, (tile['pos'][0] * self.k - self.camera[0], tile['pos'][1] * self.k - self.camera[1]))
            

    def get_rect_by_coords(self, x, y):
        i = x // self.tile_size
        j = y // self.tile_size
        return pygame.Rect(i * self.tile_size, j * self.tile_size, self.tile_size, self.tile_size)

    def start_pos(self):
        res = None
        fordel = []
        for pos, tile in self.tile_map.items():
            if tile['resource'] == 'spawners':
                if tile['variant'] == 0:
                    res = (pos[0] * self.tile_size, pos[1] * self.tile_size)
                    fordel.append(pos)
        for pos in fordel:
            del self.tile_map[pos]
        if res: 
            return res
        raise Exception("No start position found")


    def get_positions(self, resource_name, variant, keep=False):
        res = []
        for pos, tile in self.tile_map.items():
            if tile['resource'] == resource_name and tile['variant'] == variant:
                res.append((pos[0] * self.tile_size, pos[1] * self.tile_size))
        if not keep:
            for pos in res:
                del self.tile_map[(pos[0] // self.tile_size, pos[1] // self.tile_size)]
        return res
    

    def isprop(self, x, y, prop='solid'):
        i = x // self.tile_size
        j = y // self.tile_size
        if (i, j) not in self.tile_map: return False
        tile = self.tile_map[(i, j)]
        resource_name, variant = tile['resource'], tile['variant']
        if prop not in self.resource_props[resource_name]: return False
        return self.resource_props[resource_name][prop][variant]
    
    def issolid(self, x, y):
        return self.isprop(x, y)
    
    def move_camera(self, x, y):
        self.camera[0] += (x - self.camera[0]) / 30
        self.camera[1] += (y - self.camera[1]) / 30

    def intersect_solid(self, rect):
        for i in range(rect.left // self.tile_size, rect.right // self.tile_size + 1):
            for j in range(rect.top // self.tile_size, rect.bottom // self.tile_size + 1):
                tile_pos = i * self.tile_size, j * self.tile_size
                if self.isprop(*tile_pos):
                    tile_rect = pygame.Rect(*tile_pos, self.tile_size, self.tile_size)
                    if tile_rect.colliderect(rect):
                        return (i, j)
        return None