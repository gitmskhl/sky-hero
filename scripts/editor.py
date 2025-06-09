import pygame
import os
import sys
import json

BASE_DIR = '.'
if __name__ == "__main__":
    import utils
    pygame.init()
    HISTORY_MAX=100
    GRAY = (50,) * 3

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
else:
    from . import utils

# 16 x 16 is the base
class Editor:
    TRANSFORM_TILES = {'grass', 'stone'}
    TRANSFORM_RULES = {
        ((1, 0),): 0,
        ((-1, 0), (1, 0)): 1,
        ((-1, 0),): 2,
        ((0, -1), (0, 1), (-1, 0)): 3,
        ((0, -1), (-1, 0)): 4,
        ((0, -1), (-1, 0), (1, 0)): 5,
        ((0, -1), (1, 0)): 6,
        ((0, -1), (1, 0), (0, 1)): 7,
        ((0, -1), (0, 1), (1, 0), (-1, 0)): 5
    }
    TRANSFORM_RULES = {tuple(sorted(k)): v for k, v in TRANSFORM_RULES.items()}

    def transform(self):
        for pos, tile in self.tile_map.items():
            tilerect = pygame.Rect(pos[0] * self.tile_size, pos[1] * self.tile_size, self.tile_size, self.tile_size)
            if tile['resource'] in Editor.TRANSFORM_TILES:
                neighbours = []
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i == 0 and j == 0 or i != 0 and j != 0: continue
                        if (pos[0] + i, pos[1] + j) in self.tile_map and self.tile_map[(pos[0] + i, pos[1] + j)]['resource'] == tile['resource']:
                            neighbours.append((i, j))
                situation = tuple(sorted(neighbours))
                if situation in Editor.TRANSFORM_RULES:
                    tile['variant'] = Editor.TRANSFORM_RULES[situation]
                else:
                    suits = []
                    for req_situation in Editor.TRANSFORM_RULES:
                        if all([x in situation for x in req_situation]):
                            suits.append(req_situation)
                    if suits:
                        suit_situation = sorted(suits, key=lambda x: -len(x))[0]
                        tile['variant'] = Editor.TRANSFORM_RULES[suit_situation]
                    
    def __init__(self, level, level_config=None):
        level = level
        self.level = level
        self.base_tile_size = 16
        self.tile_size = 16
        self.k = 1
        self.tile_map = {}
        self.nogrid_tiles = []
        self._load_resources()
        self.resource_names = list(self.resources.keys())
        self.current_resource = self.resource_names[0]
        self.current_variant = 0
        # mouse
        self.clicked = [False, False, False]
        self.pressed = [False, False, False]
        self.shift = False
        # grid  
        self.grid = True
        # camera
        self.camera = [0, 0]
        self.move = [0, 0]
        #history
        self.history = []
        self.history_index = 0
        if level_config:
            self.load_from_config(level_config)
        else:
            self.load()

    def _resize_resources(self):
        for dirname in os.listdir('resources'):
            self.resources[dirname] = utils.load_images('resources/' + dirname, self.tile_size / 16, (0, 0, 0))

    def _load_resources(self):
        self.resources = {}
        self.resource_props = {}
        for dirname in os.listdir('resources'):
            self.resources[dirname] = utils.load_images('resources/' + dirname, 1, (0, 0, 0))
            res_count = len(self.resources[dirname])
            info_path = os.path.join('resources', dirname, 'info.txt')
            self.resource_props[dirname] = {}
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    for line in f:
                        lst = line.split(':')
                        prop = lst[0].strip()
                        if len(lst) == 1:
                            self.resource_props[dirname][prop] = [True] * res_count
                        else:
                            self.resource_props[dirname][prop] = [False] * res_count
                            idxs = [int(i) for i in lst[1].split(' ') if i]
                            for i in idxs:
                                self.resource_props[dirname][prop][int(i)] = True
        self._resize_resources()

    def _draw_grid(self, screen, i_start, j_start, i_end, j_end):
        for j in range(j_start, j_end):
            pygame.draw.line(
                screen,
                GRAY,
                (0, j * self.tile_size - self.camera[1]),
                (SCREEN_WIDTH, j * self.tile_size - self.camera[1])
            )
        for i in range(i_start, i_end):
            pygame.draw.line(
                screen,
                GRAY,
                (i * self.tile_size - self.camera[0], 0),
                (i * self.tile_size - self.camera[0], SCREEN_HEIGHT)
            )


    def render(self, screen):
        i_start = int(self.camera[0] // self.tile_size)
        j_start = int(self.camera[1] // self.tile_size)
        i_end = int((self.camera[0] + SCREEN_WIDTH) // self.tile_size + 1)
        j_end = int((self.camera[1] + SCREEN_HEIGHT) // self.tile_size + 1)
        if self.grid:
            self._draw_grid(screen, i_start, j_start, i_end, j_end)
        for i in range(i_start, i_end):
            for j in range(j_start, j_end):
                if (i, j) in self.tile_map:
                    tile = self.tile_map[(i, j)]
                    img = self.resources[tile['resource']][tile['variant']]
                    screen.blit(img, (i * self.tile_size - self.camera[0], j * self.tile_size - self.camera[1]))
        for tile in self.nogrid_tiles:
            img = self.resources[tile['resource']][tile['variant']]
            if tile['pos'][0] * self.k - self.camera[0] + img.get_width() < 0 or tile['pos'][0] * self.k - self.camera[0] > SCREEN_WIDTH:
                continue
            if tile['pos'][1] * self.k - self.camera[1] + img.get_height() < 0 or tile['pos'][1] * self.k - self.camera[1] > SCREEN_HEIGHT:
                continue
            screen.blit(img, (tile['pos'][0] * self.k - self.camera[0], tile['pos'][1] * self.k - self.camera[1]))
        
        selected_img = self.resources[self.current_resource][self.current_variant]
        selected_img.set_alpha(100)
        mpos = pygame.mouse.get_pos()
        if self.grid:
            pos = ((mpos[0] + self.camera[0])//self.tile_size*self.tile_size - self.camera[0], (mpos[1] + self.camera[1])//self.tile_size*self.tile_size - self.camera[1])
        else:pos=mpos
        screen.blit(selected_img, pos)
        selected_img.set_alpha(255)

    def _add_history(self, action, pos, tile, type):
        self.history = self.history[:self.history_index]
        self.history.append(
            {
                'action': action,
                'pos': pos,
                'type': type,
                'tile': tile
            }
        )
        self.history_index += 1
        if self.history_index > HISTORY_MAX:
            self.history_index = HISTORY_MAX
            self.history = self.history[-HISTORY_MAX:]

    def _add_grid_tile(self, pos):
        i = int((pos[0] + self.camera[0]) // self.tile_size)
        j = int((pos[1] + self.camera[1]) // self.tile_size)
        self.tile_map[(i, j)] = {'resource': self.current_resource, 'variant': self.current_variant}
        self._add_history('add', (i, j), self.tile_map[(i, j)], 'grid')

    def _add_nogrid_tile(self, pos):
        pos = ((pos[0] + self.camera[0]) / self.k, (pos[1] + self.camera[1]) / self.k)
        self.nogrid_tiles.append({'resource': self.current_resource, 'variant': self.current_variant, 'pos': pos})
        self._add_history('add', pos, self.nogrid_tiles[-1], 'nogrid')

    def _del_grid_tile(self, pos):
        i = int((pos[0] + self.camera[0]) // self.tile_size)
        j = int((pos[1] + self.camera[1]) // self.tile_size)
        if (i, j) in self.tile_map:
            tile = self.tile_map[(i, j)]
            del self.tile_map[(i, j)]
            self.history = self.history[:self.history_index]
            self._add_history('delete', (i, j), tile, 'grid')

    def _del_nogrid_tile(self, pos):
        # pos = (pos[0] + self.camera[0], pos[1] + self.camera[1])
        pos = ((pos[0] + self.camera[0]) / self.k, (pos[1] + self.camera[1]) / self.k)
        for tile in self.nogrid_tiles:
            img = self.resources[tile['resource']][tile['variant']]
            if img.get_rect(topleft=tile['pos']).collidepoint(pos):
                self.nogrid_tiles.remove(tile)
                self.history = self.history[:self.history_index]
                break

    def update(self):
        self.camera[0] += self.move[0]
        self.camera[1] += self.move[1]
        if self.clicked[0] or (self.pressed[0] and self.shift):
            pos = pygame.mouse.get_pos()
            if self.grid: self._add_grid_tile(pos)
            else: self._add_nogrid_tile(pos)
        elif self.clicked[2] or (self.pressed[2] and self.shift):
            pos = pygame.mouse.get_pos()
            if self.grid: self._del_grid_tile(pos)
            else: self._del_nogrid_tile(pos)
            
        self.clicked = [False, False, False]

    def save(self):
        assert False, 'It is impossible'
        with open(BASE_DIR + f'/maps/map_level{self.level}.json', 'w') as f:
            json.dump(
                {
                    'tile_map': {str(k): v for k, v in self.tile_map.items()},
                    'nogrid_tiles': self.nogrid_tiles,
                    'tile_size': self.tile_size,
                    'camera_x': self.camera[0],
                    'camera_y': self.camera[1],
                },
                f
            )

    def load_from_config(self, level_config):
        self.tile_map = {tuple(map(int, [x.replace('(', '').replace(')', '') for x in k.split(',')])): v for k, v in level_config['tile_map'].items()}
        self.nogrid_tiles = level_config['nogrid_tiles']
        self.tile_size = level_config['tile_size']
        self.camera = [level_config['camera_x'], level_config['camera_y']]
        self.k = self.tile_size // 16
        self._resize_resources()


    def load(self):
        try:
            with open(BASE_DIR + f'/maps/map_level{self.level}.json', 'r') as f:
                data = json.load(f)
                self.tile_map = {tuple(map(int, [x.replace('(', '').replace(')', '') for x in k.split(',')])): v for k, v in data['tile_map'].items()}
                self.nogrid_tiles = data['nogrid_tiles']
                self.tile_size = data['tile_size']
                self.camera = [data['camera_x'], data['camera_y']]
                self.k = self.tile_size // 16
                self._resize_resources()
        except FileNotFoundError:
            pass    

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
    clock = pygame.time.Clock()

    if len(sys.argv) > 2:
        print('Usage: python editor.py [level]')
        exit(1)
    elif len(sys.argv) == 2:
        level = int(sys.argv[1])
    else:
        level = 1
    editor = Editor(level)

    ctrl_pressed = False
    shift_pressed = False

    def undo():
        while True:
            if editor.history_index == 0: return
            editor.history_index -= 1
            action = editor.history[editor.history_index]
            if action['action'] == 'add':
                if action['type'] == 'grid':
                    if action['pos'] in editor.tile_map:
                        del editor.tile_map[action['pos']]
                    else: continue
                else:
                    editor.nogrid_tiles.remove(action['tile'])
            else:
                if action['type'] == 'grid':
                    editor.tile_map[action['pos']] = action['tile']
                else:
                    editor.nogrid_tiles.append(action['tile'])
            break

    def redo():
        while True:
            if editor.history_index == len(editor.history): return
            action = editor.history[editor.history_index]
            editor.history_index += 1
            if action['action'] == 'add':
                if action['type'] == 'grid':
                    editor.tile_map[action['pos']] = action['tile']
                else:
                    editor.nogrid_tiles.append(action['tile'])
            else:
                if action['type'] == 'grid':
                    if action['pos'] in editor.tile_map:
                        del editor.tile_map[action['pos']]
                    else: continue
                else:
                    editor.nogrid_tiles.remove(action['tile'])
            break

    while True:
        clock.tick(60)
        screen.fill((0, 0, 0))
        editor.update()
        editor.render(screen)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    editor.shift = True
                    shift_pressed = True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_EQUALS:
                    editor.tile_size += 16
                    editor.camera[0] /= editor.k
                    editor.camera[1] /= editor.k
                    editor.k += 1
                    editor.camera[0] *= editor.k
                    editor.camera[1] *= editor.k
                    editor._resize_resources()
                elif event.key == pygame.K_MINUS:
                    if editor.tile_size > 16:
                        editor.tile_size -= 16
                        editor.camera[0] /= editor.k
                        editor.camera[1] /= editor.k
                        editor.k -= 1
                        editor.camera[0] *= editor.k
                        editor.camera[1] *= editor.k
                        editor._resize_resources()
                elif event.key == pygame.K_t:
                    editor.transform()
                elif event.key == pygame.K_RIGHT:
                    editor.move[0] = 5
                elif event.key == pygame.K_LEFT:
                    editor.move[0] = -5
                elif event.key == pygame.K_DOWN:
                    editor.move[1] = 5
                elif event.key == pygame.K_UP:
                    editor.move[1] = -5
                if event.key == pygame.K_g:
                    editor.grid = not editor.grid
                elif event.key == pygame.K_SPACE:
                    editor.current_variant = (editor.current_variant + 1) % len(editor.resources[editor.current_resource])
                elif event.key == pygame.K_e:
                    editor.current_resource = editor.resource_names[(editor.resource_names.index(editor.current_resource) + 1) % len(editor.resource_names)]
                    editor.current_variant = 0
                elif event.key == pygame.K_q:
                    editor.current_resource = editor.resource_names[(editor.resource_names.index(editor.current_resource) - 1) % len(editor.resource_names)]
                    editor.current_variant = 0
                elif event.key == pygame.K_LCTRL:
                    ctrl_pressed = True
                elif event.key == pygame.K_z:
                    if ctrl_pressed and not shift_pressed:
                        undo()
                    elif ctrl_pressed and shift_pressed:
                        redo()
                elif event.key == pygame.K_s:
                    editor.save()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    editor.shift = False
                    shift_pressed = False
                elif event.key == pygame.K_RIGHT:
                    editor.move[0] = 0
                elif event.key == pygame.K_LEFT:
                    editor.move[0] = 0
                elif event.key == pygame.K_DOWN:
                    editor.move[1] = 0
                elif event.key == pygame.K_UP:
                    editor.move[1] = 0
                elif event.key == pygame.K_LCTRL:
                    ctrl_pressed = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    editor.clicked[0] = True
                    editor.pressed[0] = True
                elif event.button == 3:
                    editor.clicked[2] = True
                    editor.pressed[2] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    editor.pressed[0] = False
                elif event.button == 3:
                    editor.pressed[2] = False

        pygame.display.flip()