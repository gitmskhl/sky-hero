# custom_map_creator.py

import pygame
import os
import sys
import shelve
from collections import deque
import copy
import utils
# Импортируем необходимые виджеты
from custom_map_widget import (
    ResourcePanel, State, TextButton, HorizontalLayout, VerticalLayout, Widget
)

pygame.init()

MAP_FILE = '.levels'
HISTORY_MAX = 10000
GRAY = (50,) * 3
LIGHT_GRAY_BG = (200, 200, 200)
BUTTON_COLOR = (180, 180, 180)
BUTTON_HOVER_COLOR = (210, 210, 210)
BUTTON_ACTIVE_COLOR = (150, 200, 150)
BUTTON_ACTIVE_HOVER_COLOR = (170, 220, 170)


SCREEN_WIDTH = 950 # Увеличим ширину для панели
SCREEN_HEIGHT = 600

MAX_FILLED_SECTOR = 500
RESOURCES_DIR = 'resources'
MAP_DIR = '.'

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

    def __init__(self, filename, editor_surface_size):
        self.editor_surface_size = editor_surface_size
        self.base_tile_size = 16
        self.tile_size = 32
        self.change_tiles_size = 2
        self.k = self.tile_size / self.base_tile_size
        self.tile_map = {}
        self.nogrid_tiles = []
        self._load_resources()
        self.resource_names = list(self.resources.keys())
        self.current_resource = self.resource_names[0]
        self.current_variant = 0
        # mouse (relative to editor surface)
        self.mouse_pos_editor = (0, 0)
        self.clicked = [False, False, False] # Left, Middle, Right clicks for editor area
        self.pressed = [False, False, False] # Left, Middle, Right presses for editor area
        self.mouse_over_editor = False

        # Modes / States
        self.grid = True
        self.fill_activated = False
        self.continuous_mode = False # Replaces shift for continuous placement
        self.select_area_mode = False # Replaces ctrl for area selection start
        self.moving_selected_area = False # Internal state for moving
        self.selecting_area_active = False # Is selection currently being drawn

        # camera
        self.camera = [0, 0]
        self.move = [0, 0]
        #history
        self.history = []
        self.history_index = 0
        self.load(filename)
        # fill
        self.last_ij_filled = None
        self.last_filled = None
        # select area
        self.start_selected_area_abs = [] # Absolute screen coordinates
        self.selected_area_abs = [] # Absolute screen coordinates (top-left, bottom-right) in editor space
        self.moving_tiles = None
        self.moving_offgrid_tiles = None
        self.start_mouse_position_abs = None # Absolute editor coordinates
        # copy
        self.copied_grid_tiles = None
        self.copied_offgrid_tiles = None

    # --- Button Interface Methods ---
    def toggle_grid(self):
        self.grid = not self.grid

    def toggle_fill_mode(self):
        self.fill_activated = not self.fill_activated
        if self.fill_activated:
            self.select_area_mode = False # Deactivate select mode if fill is activated
            self.continuous_mode = False # Deactivate continuous mode if fill is activated
            self._clear_selection() # Clear selection when activating fill

    def toggle_continuous_mode(self):
        self.continuous_mode = not self.continuous_mode
        if self.continuous_mode:
            self.select_area_mode = False # Deactivate select mode if continuous is activated
            self.fill_activated = False # Deactivate fill mode
            self._clear_selection() # Clear selection when activating continuous

    def toggle_select_area_mode(self):
        self.select_area_mode = not self.select_area_mode
        if self.select_area_mode:
            self.fill_activated = False # Deactivate fill mode
            self.continuous_mode = False # Deactivate continuous mode
        else:
            # If deactivating select mode, clear the current selection
            self._clear_selection()

    def activate_paste(self):
         # We don't need ctrl to paste anymore, just call the paste function
        self._save_copy_sector()
        # Optionally, deactivate select mode after pasting
        # self.select_area_mode = False
        # self._clear_selection()

    def _clear_selection(self):
        self.selected_area_abs = []
        self.start_selected_area_abs = []
        self.selecting_area_active = False
        # Don't clear copied data here, only visual selection

    def zoom_plus(self):
        self.tile_size += self.change_tiles_size
        last_k = self.k
        # Adjust camera based on center of editor view
        center_x_abs = self.camera[0] + self.editor_surface_size[0] / 2
        center_y_abs = self.camera[1] + self.editor_surface_size[1] / 2
        center_x_tile = center_x_abs / last_k
        center_y_tile = center_y_abs / last_k

        self.k = self.tile_size / self.base_tile_size
        self._resize_resources()

        # Recalculate camera position to keep center fixed
        self.camera[0] = center_x_tile * self.k - self.editor_surface_size[0] / 2
        self.camera[1] = center_y_tile * self.k - self.editor_surface_size[1] / 2

        # Adjust selection area coordinates
        if self.selected_area_abs:
            for i in range(2):
                self.selected_area_abs[i][0] = self.selected_area_abs[i][0] / last_k * self.k
                self.selected_area_abs[i][1] = self.selected_area_abs[i][1] / last_k * self.k


    def zoom_minus(self):
        if self.tile_size > self.change_tiles_size:
            last_k = self.k
            self.tile_size -= self.change_tiles_size

            # Adjust camera based on center of editor view
            center_x_abs = self.camera[0] + self.editor_surface_size[0] / 2
            center_y_abs = self.camera[1] + self.editor_surface_size[1] / 2
            center_x_tile = center_x_abs / last_k
            center_y_tile = center_y_abs / last_k

            self.k = self.tile_size / self.base_tile_size
            self._resize_resources()

            # Recalculate camera position to keep center fixed
            self.camera[0] = center_x_tile * self.k - self.editor_surface_size[0] / 2
            self.camera[1] = center_y_tile * self.k - self.editor_surface_size[1] / 2

             # Adjust selection area coordinates
            if self.selected_area_abs:
                for i in range(2):
                    self.selected_area_abs[i][0] = self.selected_area_abs[i][0] / last_k * self.k
                    self.selected_area_abs[i][1] = self.selected_area_abs[i][1] / last_k * self.k

    def delete_selected(self):
        self._remove_tiles_in_selected_area()
        # Optionally clear selection after deleting
        self._clear_selection()

    def copy_selected(self):
        self._copy_sector()
        # Optionally clear selection after copying
        # self._clear_selection()

    # --- Existing Methods (adapted slightly if needed) ---

    def transform(self): # No changes needed from original
        sarect = self._get_selected_area_rect()
        for pos, tile in self.tile_map.items():
            tilerect = pygame.Rect(pos[0] * self.tile_size, pos[1] * self.tile_size, self.tile_size, self.tile_size)
            if sarect and not tilerect.colliderect(sarect): continue
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

    def _resize_resources(self):
        dirpath = os.path.join(RESOURCES_DIR)
        for dirname in os.listdir(dirpath):
            # Ensure directory exists before loading images
            if os.path.isdir(os.path.join(dirpath, dirname)):
                try:
                    self.resources[dirname] = utils.load_images(os.path.join(dirpath, dirname), self.tile_size / self.base_tile_size, (0, 0, 0))
                except FileNotFoundError:
                    print(f"Warning: Could not load images from {os.path.join(dirpath, dirname)}")
                    self.resources[dirname] = [] # Assign empty list if loading fails

    def _load_resources(self):
        self.resources = {}
        self.resource_props = {}
        if not os.path.exists(RESOURCES_DIR):
             print(f"Error: Resources directory '{RESOURCES_DIR}' not found.")
             return # Exit early if the main resources directory doesn't exist

        for dirname in os.listdir(RESOURCES_DIR):
            dir_path = os.path.join(RESOURCES_DIR, dirname)
            if not os.path.isdir(dir_path):
                continue # Skip if it's not a directory

            try:
                self.resources[dirname] = utils.load_images(dir_path, 1, (0, 0, 0))
                res_count = len(self.resources[dirname])
                info_path = os.path.join(dir_path, 'info.txt')
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
                                idxs_str = lst[1].split() # Split by space
                                idxs = [int(i) for i in idxs_str if i.isdigit()] # Filter non-numeric parts
                                for i in idxs:
                                     if 0 <= i < res_count: # Check index bounds
                                        self.resource_props[dirname][prop][i] = True
                                     else:
                                          print(f"Warning: Index {i} out of bounds for resource '{dirname}' in info.txt")
            except FileNotFoundError:
                 print(f"Warning: Could not load images from {dir_path}")
                 self.resources[dirname] = []
            except Exception as e:
                print(f"Error loading resources from {dir_path}: {e}")
                self.resources[dirname] = [] # Assign empty list on other errors

        self._resize_resources()

    def _draw_grid(self, screen, i_start, j_start, i_end, j_end):
        editor_w, editor_h = self.editor_surface_size
        for j in range(j_start, j_end):
            y_pos = j * self.tile_size - self.camera[1]
            pygame.draw.line(screen, GRAY, (0, y_pos), (editor_w, y_pos))
        for i in range(i_start, i_end):
            x_pos = i * self.tile_size - self.camera[0]
            pygame.draw.line(screen, GRAY, (x_pos, 0), (x_pos, editor_h))

    # Requires absolute editor coordinates
    def _get_filled(self, pos_abs):
        result = []
        i = int(pos_abs[0] // self.tile_size)
        j = int(pos_abs[1] // self.tile_size)
        if (i, j) in self.tile_map: return []
        d = deque()
        d.append((i, j))
        visited = set([(i, j)]) # Keep track of visited to avoid cycles and redundant checks

        while d and len(result) < MAX_FILLED_SECTOR:
            i_, j_ = d.popleft()
            # Check bounds (optional, but good practice if map has limits)
            # if not (0 <= i_ < MAP_WIDTH_TILES and 0 <= j_ < MAP_HEIGHT_TILES):
            #     continue

            # Check if it's already in the map (should not happen if start check works, but safety)
            if (i_, j_) in self.tile_map:
                continue

            result.append((i_, j_))

            for p, q in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                tup = (i_ + p, j_ + q)
                # Check bounds, if not visited, and not already in the map
                if tup not in visited and tup not in self.tile_map:
                    # Add to queue and mark as visited
                    d.append(tup)
                    visited.add(tup)

        self.last_ij_filled = (i, j) # Store the starting tile index
        self.last_filled = result
        return result


    def _render_moving_tiles(self, screen): # Pass screen surface
        if not self.moving_tiles: return
        mx_abs, my_abs = self.mouse_pos_editor # Use relative editor mouse pos
        mx_abs += self.camera[0]
        my_abs += self.camera[1]
        shiftx = mx_abs - self.start_mouse_position_abs[0]
        shifty = my_abs - self.start_mouse_position_abs[1]
        for pos, tile in self.moving_tiles:
            xrel = pos[0] * self.tile_size + shiftx
            yrel = pos[1] * self.tile_size + shifty
            tx = xrel // self.tile_size
            ty = yrel // self.tile_size
            try:
                tile_img = self.resources[tile['resource']][tile['variant']].copy() # Use copy to avoid modifying original
                tile_img.set_alpha(100)
                screen.blit(tile_img, (tx * self.tile_size - self.camera[0], ty * self.tile_size - self.camera[1]))
            except (KeyError, IndexError):
                 print(f"Warning: Could not render moving tile {tile} at {pos}") # Handle missing resource/variant
                 continue # Skip rendering this tile

        if not self.moving_offgrid_tiles: return
        for tile in self.moving_offgrid_tiles:
            pos = tile['pos']
            xrel = pos[0] * self.k + shiftx
            yrel = pos[1] * self.k + shifty
            try:
                tile_img = self.resources[tile['resource']][tile['variant']].copy() # Use copy
                tile_img.set_alpha(100)
                screen.blit(tile_img, (xrel - self.camera[0], yrel - self.camera[1]))
            except (KeyError, IndexError):
                 print(f"Warning: Could not render moving offgrid tile {tile}") # Handle missing resource/variant
                 continue # Skip rendering this tile


    def _render_copied_tiles(self, screen): # Pass screen surface
        # This function seems unused in the original logic where copy is just data.
        # If you want visual feedback for copied data, implement it here.
        # For now, it does nothing.
        pass

    def render(self, screen): # Pass the surface to draw on
        editor_w, editor_h = self.editor_surface_size
        i_start = int(self.camera[0] // self.tile_size)
        j_start = int(self.camera[1] // self.tile_size)
        i_end = int((self.camera[0] + editor_w) // self.tile_size + 1)
        j_end = int((self.camera[1] + editor_h) // self.tile_size + 1)

        if self.grid:
            self._draw_grid(screen, i_start, j_start, i_end, j_end)

        moving_tiles_positions = set(pos for pos, _ in self.moving_tiles) if self.moving_selected_area else set()

        # Render grid tiles
        for i in range(i_start - 1, i_end + 1):
            for j in range(j_start - 1, j_end + 1):
                if (i, j) in moving_tiles_positions: continue
                if (i, j) in self.tile_map:
                    tile = self.tile_map[(i, j)]
                    try:
                        img = self.resources[tile['resource']][tile['variant']]
                        screen.blit(img, (i * self.tile_size - self.camera[0], j * self.tile_size - self.camera[1]))
                    except (KeyError, IndexError):
                         # Optionally draw a placeholder if resource/variant is missing
                         # pygame.draw.rect(screen, (255,0,0), (i * self.tile_size - self.camera[0], j * self.tile_size - self.camera[1], self.tile_size, self.tile_size), 1)
                         continue # Skip rendering this tile


        # Render off-grid tiles
        for tile in self.nogrid_tiles:
            if self.moving_selected_area and tile in self.moving_offgrid_tiles: continue
            try:
                img = self.resources[tile['resource']][tile['variant']]
                render_x = tile['pos'][0] * self.k - self.camera[0]
                render_y = tile['pos'][1] * self.k - self.camera[1]

                # Basic culling
                if render_x + img.get_width() < 0 or render_x > editor_w:
                    continue
                if render_y + img.get_height() < 0 or render_y > editor_h:
                    continue

                screen.blit(img, (render_x, render_y))
            except (KeyError, IndexError):
                  # Optionally draw a placeholder if resource/variant is missing
                  continue # Skip rendering this tile

        # Render placement preview / fill preview / selection box / moving preview
        if self.mouse_over_editor:
            try:
                selected_img_preview = self.resources[self.current_resource][self.current_variant].copy()
                selected_img_preview.set_alpha(100)
                mpos_rel = self.mouse_pos_editor # Relative editor coordinates
                mpos_abs = (mpos_rel[0] + self.camera[0], mpos_rel[1] + self.camera[1])

                if self.fill_activated:
                    # Use cached fill result if mouse tile hasn't changed
                    current_tile_ij = (int(mpos_abs[0] // self.tile_size), int(mpos_abs[1] // self.tile_size))
                    if current_tile_ij == self.last_ij_filled:
                        filled = self.last_filled
                    else:
                        filled = self._get_filled(mpos_abs) # Calculate fill preview

                    if filled: # Only render if fill calculation returned something
                         for i, j in filled:
                            screen.blit(selected_img_preview, (i * self.tile_size - self.camera[0], j * self.tile_size - self.camera[1]))

                elif not self.select_area_mode and not self.moving_selected_area: # Normal placement preview
                    if self.grid:
                        pos_snap = (
                            int(mpos_abs[0] // self.tile_size) * self.tile_size - self.camera[0],
                            int(mpos_abs[1] // self.tile_size) * self.tile_size - self.camera[1]
                        )
                    else:
                        pos_snap = (mpos_abs[0] - self.camera[0], mpos_abs[1] - self.camera[1]) # Render at exact mouse pos for offgrid
                    screen.blit(selected_img_preview, pos_snap)

            except (KeyError, IndexError):
                 # Don't render preview if selected resource is invalid
                 pass


        # Render selection rectangle (use absolute editor coordinates)
        self._render_selected_area(screen)

        # Render moving tiles preview (if active)
        if self.moving_selected_area:
            self._render_moving_tiles(screen)

        # Render copied tiles preview (if implemented)
        # self._render_copied_tiles(screen)

    def _render_selected_area(self, screen): # Pass screen surface
        if not self.selected_area_abs or len(self.selected_area_abs) != 2: return

        # Ensure coordinates are ordered: top-left, bottom-right
        x1, y1 = self.selected_area_abs[0]
        x2, y2 = self.selected_area_abs[1]
        rect_x = min(x1, x2) - self.camera[0]
        rect_y = min(y1, y2) - self.camera[1]
        rect_w = abs(x1 - x2)
        rect_h = abs(y1 - y2)

        # Draw only if width and height are positive
        if rect_w > 0 and rect_h > 0:
             # Draw a dashed or distinct selection rectangle
             pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, rect_w, rect_h), 1)


    def _get_selected_area_rect(self):
        if not self.selected_area_abs or len(self.selected_area_abs) != 2: return None

        x1, y1 = self.selected_area_abs[0]
        x2, y2 = self.selected_area_abs[1]
        rect_x = min(x1, x2)
        rect_y = min(y1, y2)
        rect_w = abs(x1 - x2)
        rect_h = abs(y1 - y2)

        if rect_w > 0 and rect_h > 0:
            return pygame.Rect(rect_x, rect_y, rect_w, rect_h)
        return None


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
            # self.history_index = HISTORY_MAX # Not needed if popping from start
            self.history.pop(0) # Remove oldest entry
            self.history_index -= 1 # Adjust index accordingly


    # Requires relative editor coordinates
    def _add_grid_tile(self, pos_rel):
        pos_abs = (pos_rel[0] + self.camera[0], pos_rel[1] + self.camera[1])
        i = int(pos_abs[0] // self.tile_size)
        j = int(pos_abs[1] // self.tile_size)
        current_tile_data = {'resource': self.current_resource, 'variant': self.current_variant}

        # Prevent placing over existing tile unless in continuous mode
        if (i, j) in self.tile_map and not self.continuous_mode:
             return # Don't place if tile exists and not in continuous mode

        self.tile_map[(i, j)] = copy.deepcopy(current_tile_data)
        self._add_history('add', (i, j), self.tile_map[(i, j)], 'grid')

    # Requires relative editor coordinates
    def _add_nogrid_tile(self, pos_rel):
        pos_abs = ((pos_rel[0] + self.camera[0]) / self.k, (pos_rel[1] + self.camera[1]) / self.k)
        tile_data = {'resource': self.current_resource, 'variant': self.current_variant, 'pos': pos_abs}
        self.nogrid_tiles.append(copy.deepcopy(tile_data))
        self._add_history('add', pos_abs, self.nogrid_tiles[-1], 'nogrid') # Store the absolute position used

    # Requires relative editor coordinates
    def _del_grid_tile(self, pos_rel):
        pos_abs = (pos_rel[0] + self.camera[0], pos_rel[1] + self.camera[1])
        i = int(pos_abs[0] // self.tile_size)
        j = int(pos_abs[1] // self.tile_size)
        if (i, j) in self.tile_map:
            tile = self.tile_map[(i, j)]
            del self.tile_map[(i, j)]
            # self.history = self.history[:self.history_index] # Handled by _add_history
            self._add_history('delete', (i, j), tile, 'grid')

    # Requires relative editor coordinates
    def _del_nogrid_tile(self, pos_rel):
        pos_abs_scaled = ((pos_rel[0] + self.camera[0]) / self.k, (pos_rel[1] + self.camera[1]) / self.k)
        tile_to_remove = None
        for tile in self.nogrid_tiles:
            try:
                img = self.resources[tile['resource']][tile['variant']]
                # Check collision using the tile's stored absolute position (tile['pos'])
                # Important: tile['pos'] is already scaled by 1/k
                tile_rect_abs = img.get_rect(topleft=(tile['pos'][0] * self.k, tile['pos'][1] * self.k))
                # Check collision with mouse absolute scaled position
                if tile_rect_abs.collidepoint(pos_abs_scaled[0] * self.k, pos_abs_scaled[1] * self.k):
                    tile_to_remove = tile
                    break # Found the tile to remove
            except (KeyError, IndexError):
                continue # Skip if resource is invalid

        if tile_to_remove:
            removed_tile_copy = copy.deepcopy(tile_to_remove) # Copy before removing
            self.nogrid_tiles.remove(tile_to_remove)
            # self.history = self.history[:self.history_index] # Handled by _add_history
            self._add_history('delete', removed_tile_copy['pos'], removed_tile_copy, 'nogrid') # Store original pos and tile data

    # Uses absolute coordinates from self.selected_area_abs
    def _remove_tiles_in_selected_area(self):
        sarect = self._get_selected_area_rect()
        if not sarect: return
        tiles_in_area = self._get_tiles_in_area(sarect)
        offgridtiles_in_area = self._get_offgrid_tiles_in_area(sarect)

        if not tiles_in_area and not offgridtiles_in_area: return # Nothing to remove

        # Create copies before deleting
        removed_grid_data = copy.deepcopy(tiles_in_area)
        removed_offgrid_data = copy.deepcopy(offgridtiles_in_area)

        for pos, _ in tiles_in_area:
            if pos in self.tile_map:
                del self.tile_map[pos]
        for tile in offgridtiles_in_area:
            if tile in self.nogrid_tiles: # Check if it still exists
                self.nogrid_tiles.remove(tile)

        self._add_history('remove_selected_area', None, {
            'grid': removed_grid_data,
            'offgrid': removed_offgrid_data
        }, None)

    # Uses absolute coordinates from self.selected_area_abs
    def _copy_sector(self):
        sarect = self._get_selected_area_rect()
        if not sarect:
            self.copied_grid_tiles = None
            self.copied_offgrid_tiles = None
            return

        grid_tiles_in_area = self._get_tiles_in_area(sarect)
        offgrid_tiles_in_area = self._get_offgrid_tiles_in_area(sarect)

        if not grid_tiles_in_area and not offgrid_tiles_in_area:
            self.copied_grid_tiles = None
            self.copied_offgrid_tiles = None
            return

        # Store copies relative to the top-left of the selection rectangle
        origin_x, origin_y = sarect.topleft

        self.copied_grid_tiles = []
        for (i, j), tile in grid_tiles_in_area:
             # Store relative grid position
             rel_i = i - int(origin_x // self.tile_size)
             rel_j = j - int(origin_y // self.tile_size)
             self.copied_grid_tiles.append( ((rel_i, rel_j), copy.deepcopy(tile)) )

        self.copied_offgrid_tiles = []
        for tile in offgrid_tiles_in_area:
            # Store relative position (in original tile coordinates, 1/k scale)
            rel_pos_x = tile['pos'][0] - (origin_x / self.k)
            rel_pos_y = tile['pos'][1] - (origin_y / self.k)
            copied_tile = copy.deepcopy(tile)
            copied_tile['pos'] = (rel_pos_x, rel_pos_y) # Store relative position
            self.copied_offgrid_tiles.append(copied_tile)

    # Uses mouse position (relative editor coordinates) for placement origin
    def _save_copy_sector(self):
        if not self.copied_grid_tiles and not self.copied_offgrid_tiles:
             return # Nothing to paste

        paste_origin_rel = self.mouse_pos_editor
        paste_origin_abs = (paste_origin_rel[0] + self.camera[0], paste_origin_rel[1] + self.camera[1])

        added_tiles_info = {'grid': [], 'offgrid': []}

        # Paste grid tiles
        if self.copied_grid_tiles:
             paste_origin_i = int(paste_origin_abs[0] // self.tile_size)
             paste_origin_j = int(paste_origin_abs[1] // self.tile_size)
             for (rel_i, rel_j), tile_data in self.copied_grid_tiles:
                abs_i = paste_origin_i + rel_i
                abs_j = paste_origin_j + rel_j
                # Overwrite existing tiles when pasting
                self.tile_map[(abs_i, abs_j)] = copy.deepcopy(tile_data)
                added_tiles_info['grid'].append(((abs_i, abs_j), self.tile_map[(abs_i, abs_j)])) # Store absolute pos

        # Paste offgrid tiles
        if self.copied_offgrid_tiles:
             paste_origin_x_scaled = paste_origin_abs[0] / self.k
             paste_origin_y_scaled = paste_origin_abs[1] / self.k
             for tile_copy in self.copied_offgrid_tiles:
                rel_pos_x, rel_pos_y = tile_copy['pos']
                abs_pos_x = paste_origin_x_scaled + rel_pos_x
                abs_pos_y = paste_origin_y_scaled + rel_pos_y
                new_tile = copy.deepcopy(tile_copy)
                new_tile['pos'] = (abs_pos_x, abs_pos_y) # Set absolute position
                self.nogrid_tiles.append(new_tile)
                added_tiles_info['offgrid'].append(new_tile)


        # Don't clear copied data after pasting, allow multiple pastes
        # self.copied_grid_tiles = None
        # self.copied_offgrid_tiles = None

        if added_tiles_info['grid'] or added_tiles_info['offgrid']:
            # Use paste origin as the position for history
            self._add_history('paste_sector', paste_origin_abs, added_tiles_info, None)


    # Uses absolute coordinates
    def _save_moved_tiles(self):
        if not self.moving_tiles and not self.moving_offgrid_tiles: return

        mx_abs = self.mouse_pos_editor[0] + self.camera[0]
        my_abs = self.mouse_pos_editor[1] + self.camera[1]
        shiftx = mx_abs - self.start_mouse_position_abs[0]
        shifty = my_abs - self.start_mouse_position_abs[1]

        # Check if movement actually happened
        if abs(shiftx) < 1 and abs(shifty) < 1:
             # No significant movement, don't save history, just reset state
             self.moving_selected_area = False
             self.moving_tiles = None
             self.moving_offgrid_tiles = None
             # Keep selection rect where it is (or reset if desired)
             # self._clear_selection()
             return

        # Backup original state before modification
        original_grid_state = copy.deepcopy(self.moving_tiles)
        original_offgrid_state = copy.deepcopy(self.moving_offgrid_tiles)

        final_state_info = {
             'grid': [],
             'offgrid': [],
             'original_grid': original_grid_state, # Store original positions for undo
             'original_offgrid': original_offgrid_state # Store original positions for undo
         }

        # Apply movement to grid tiles
        temp_new_grid_tiles = {} # Store new positions temporarily to handle overwrites
        for pos, tile in original_grid_state:
            if pos in self.tile_map: # Ensure the tile still exists at the original position
                 del self.tile_map[pos] # Remove from original position

        for pos, tile in original_grid_state:
            xrel = pos[0] * self.tile_size + shiftx
            yrel = pos[1] * self.tile_size + shifty
            tx = int(xrel // self.tile_size) # Use int() for clarity
            ty = int(yrel // self.tile_size)
            temp_new_grid_tiles[(tx, ty)] = tile # Place in new position (overwrites handled by dict)
            final_state_info['grid'].append(((tx, ty), tile)) # Record final state

        # Add the moved grid tiles back to the main map
        self.tile_map.update(temp_new_grid_tiles)

        # Apply movement to offgrid tiles
        if original_offgrid_state:
            for tile in original_offgrid_state:
                if tile in self.nogrid_tiles: # Ensure the tile still exists
                     # Calculate new absolute position (scaled by 1/k)
                     new_pos_x = (tile['pos'][0] * self.k + shiftx) / self.k
                     new_pos_y = (tile['pos'][1] * self.k + shifty) / self.k
                     tile['pos'] = (new_pos_x, new_pos_y) # Update position in-place
                     final_state_info['offgrid'].append(copy.deepcopy(tile)) # Record final state
                else:
                    # If tile was removed during move (unlikely), don't add to final state
                    pass


        self._add_history('move_selected_area', (shiftx, shifty), final_state_info, None)

        # Clear moving state AFTER saving history
        self.moving_selected_area = False
        self.moving_tiles = None
        self.moving_offgrid_tiles = None

        # Update selection rectangle to final position
        if self.selected_area_abs:
             self.selected_area_abs[0][0] += shiftx
             self.selected_area_abs[0][1] += shifty
             self.selected_area_abs[1][0] += shiftx
             self.selected_area_abs[1][1] += shifty


    # Uses absolute coordinates (pygame.Rect)
    def _get_offgrid_tiles_in_area(self, rect):
        tiles = []
        for tile in self.nogrid_tiles:
            try:
                # Calculate absolute rect based on stored position (which is 1/k scale)
                tile_rect = self.resources[tile['resource']][tile['variant']].get_rect()
                tile_rect.x = tile['pos'][0] * self.k
                tile_rect.y = tile['pos'][1] * self.k
                if tile_rect.colliderect(rect):
                    tiles.append(tile)
            except (KeyError, IndexError):
                continue # Skip invalid tiles
        return tiles

    # Uses absolute coordinates (pygame.Rect)
    def _get_tiles_in_area(self, rect):
        tiles = []
        # Determine the grid cell range potentially overlapping the rect
        # Add a small buffer (+/- 1) to handle edge cases/floating point inaccuracies
        i_start = int(rect.left // self.tile_size) - 1
        i_end = int(rect.right // self.tile_size) + 1
        j_start = int(rect.top // self.tile_size) - 1
        j_end = int(rect.bottom // self.tile_size) + 1

        for i in range(i_start, i_end): # Iterate through potential cells
            for j in range(j_start, j_end):
                if (i, j) in self.tile_map:
                    # Create the precise rect for this grid tile
                    tilerect = pygame.Rect(i * self.tile_size, j * self.tile_size, self.tile_size, self.tile_size)
                    # Check for collision with the selection rect
                    if tilerect.colliderect(rect):
                        tiles.append(((i, j), self.tile_map[(i, j)]))
        return tiles


    # Uses relative editor coordinates
    def _is_start_moving_selected_area(self, mouse_pos_rel):
        sarect = self._get_selected_area_rect() # Gets absolute rect
        if not sarect: return False
        # Check collision with mouse absolute position
        mouse_pos_abs = (mouse_pos_rel[0] + self.camera[0], mouse_pos_rel[1] + self.camera[1])
        return sarect.collidepoint(mouse_pos_abs)

    def update_mouse_state(self, mouse_pos_screen, editor_rect, mouse_buttons_pressed):
         self.mouse_over_editor = editor_rect.collidepoint(mouse_pos_screen)

         if self.mouse_over_editor:
             self.mouse_pos_editor = (mouse_pos_screen[0] - editor_rect.left, mouse_pos_screen[1] - editor_rect.top)
             # Update pressed state based on current global mouse state ONLY if over editor
             self.pressed = list(mouse_buttons_pressed[:3]) # Store current frame's pressed state (LMB, MMB, RMB)
         else:
             self.mouse_pos_editor = (-1, -1) # Indicate mouse is outside
             # Reset pressed state if mouse is not over editor
             self.pressed = [False, False, False]

         # Click events are handled separately in the event loop based on MOUSEBUTTONDOWN

    def handle_editor_click(self, button_index):
         # This function is called from the main loop on MOUSEBUTTONDOWN *if* mouse_over_editor
         if 0 <= button_index < 3:
             self.clicked[button_index] = True

             # --- Selection Logic ---
             if button_index == 0: # Left Mouse Button
                 mpos_abs = (self.mouse_pos_editor[0] + self.camera[0], self.mouse_pos_editor[1] + self.camera[1])

                 if self.select_area_mode:
                     # Check if clicking inside existing selection to start move
                     if self._is_start_moving_selected_area(self.mouse_pos_editor):
                         if not self.moving_selected_area: # Start move only if not already moving
                             self.moving_selected_area = True
                             self.start_selected_area_abs = copy.deepcopy(self.selected_area_abs)
                             sarect = self._get_selected_area_rect()
                             self.moving_tiles = self._get_tiles_in_area(sarect)
                             self.moving_offgrid_tiles = self._get_offgrid_tiles_in_area(sarect)
                             self.start_mouse_position_abs = mpos_abs
                     else:
                         # Start drawing a new selection
                         self.selected_area_abs = [list(mpos_abs), list(mpos_abs)]
                         self.selecting_area_active = True
                         self.moving_selected_area = False # Ensure not moving
                         self.moving_tiles = None
                         self.moving_offgrid_tiles = None
                 else:
                      # If not in select mode, clicking clears selection and pastes if needed
                      if self.copied_grid_tiles or self.copied_offgrid_tiles:
                           self._save_copy_sector() # Paste if something is copied
                      self._clear_selection() # Clear visual selection


    def update(self):
        # Camera movement based on arrow keys (or buttons later)
        self.camera[0] += self.move[0]
        self.camera[1] += self.move[1]

        # --- Selection Drawing/Updating ---
        if self.selecting_area_active and self.pressed[0]: # If drawing and LMB is held
            mpos_abs = (self.mouse_pos_editor[0] + self.camera[0], self.mouse_pos_editor[1] + self.camera[1])
            self.selected_area_abs[1] = list(mpos_abs) # Update the second corner

        # --- Moving Selection Update ---
        elif self.moving_selected_area and self.pressed[0]: # If moving and LMB is held
            mx_abs = self.mouse_pos_editor[0] + self.camera[0]
            my_abs = self.mouse_pos_editor[1] + self.camera[1]
            shiftx = mx_abs - self.start_mouse_position_abs[0]
            shifty = my_abs - self.start_mouse_position_abs[1]
            # Update visual representation of the selection box being moved
            if self.start_selected_area_abs: # Check if start state exists
                 self.selected_area_abs[0][0] = self.start_selected_area_abs[0][0] + shiftx
                 self.selected_area_abs[0][1] = self.start_selected_area_abs[0][1] + shifty
                 self.selected_area_abs[1][0] = self.start_selected_area_abs[1][0] + shiftx
                 self.selected_area_abs[1][1] = self.start_selected_area_abs[1][1] + shifty
        # --- Tile Placement/Deletion ---
        # Use self.pressed for continuous actions, self.clicked for single actions
        perform_action = False
        if self.mouse_over_editor:
            # LMB: Place Tile / Fill
            if self.clicked[0] or (self.pressed[0] and self.continuous_mode):
                if not self.select_area_mode and not self.moving_selected_area:
                    if self.fill_activated:
                         # Trigger fill calculation (preview already handled rendering)
                         mpos_abs = (self.mouse_pos_editor[0] + self.camera[0], self.mouse_pos_editor[1] + self.camera[1])
                         filled_tiles_ij = self._get_filled(mpos_abs)
                         if filled_tiles_ij:
                             tile_data = {'resource': self.current_resource, 'variant': self.current_variant}
                             added_fill_info = []
                             for i, j in filled_tiles_ij:
                                 # Only add if not already present (though _get_filled should handle this)
                                 if (i,j) not in self.tile_map:
                                     self.tile_map[(i, j)] = copy.deepcopy(tile_data)
                                     added_fill_info.append(((i,j), self.tile_map[(i, j)]))
                             if added_fill_info:
                                 self._add_history('add_filled', mpos_abs, added_fill_info, 'grid') # Use mouse pos as fill origin for history

                    elif self.grid:
                        self._add_grid_tile(self.mouse_pos_editor)
                    else:
                        self._add_nogrid_tile(self.mouse_pos_editor)

            # RMB: Delete Tile
            elif self.clicked[2] or (self.pressed[2] and self.continuous_mode):
                 if not self.select_area_mode and not self.moving_selected_area: # Can't delete while selecting/moving
                    if self.grid:
                        self._del_grid_tile(self.mouse_pos_editor)
                    else:
                        self._del_nogrid_tile(self.mouse_pos_editor)


        # Reset click states after processing
        self.clicked = [False, False, False]

    # --- Save/Load ---
    def save(self, filename='untitled'):
        # Ensure MAP_DIR exists
        if not os.path.exists(MAP_DIR):
            try:
                os.makedirs(MAP_DIR)
            except OSError as e:
                print(f"Error creating map directory {MAP_DIR}: {e}")
                return # Cannot save if directory creation fails

        path = os.path.join(MAP_DIR, MAP_FILE)
        try:
            with shelve.open(path, 'c') as shelf:
                # Check for existing filename and append count if needed
                base_filename = filename
                count = 0
                while filename in shelf:
                    count += 1
                    filename = f"{base_filename}({count})"

                # Prepare data for saving
                save_data = {
                    'tile_map': {str(k): v for k, v in self.tile_map.items()}, # Convert tuple keys to strings
                    'nogrid_tiles': self.nogrid_tiles,
                    'base_tile_size': self.base_tile_size,
                    'change_tiles_size': self.change_tiles_size,
                    'tile_size': self.tile_size,
                    'camera_x': self.camera[0],
                    'camera_y': self.camera[1],
                }
                shelf[filename] = save_data
                print(f"Map saved as: {filename}") # Give feedback

        except Exception as e:
             print(f"Error saving map {filename}: {e}")


    def load(self, filename):
        # Check if MAP_DIR and MAP_FILE exist
        path = os.path.join(MAP_DIR, MAP_FILE + ".db") # Shelve adds extensions like .db, .dat, .dir
        # Need to check for common shelve extensions
        base_path = os.path.join(MAP_DIR, MAP_FILE)
        possible_paths = [base_path + ext for ext in ['.db', '.dat', '.dir', '']] # Check common extensions + base name

        actual_path = None
        for p in possible_paths:
            if os.path.exists(p):
                actual_path = base_path # Use the base name for shelve.open
                break

        if actual_path is None:
             print(f"Map file '{MAP_FILE}' not found in '{MAP_DIR}'. Starting new map.")
             # Reset to default state for a new map
             self.tile_map = {}
             self.nogrid_tiles = []
             self.camera = [0, 0]
             self.history = []
             self.history_index = 0
             # Keep current tile size settings
             self.k = self.tile_size / self.base_tile_size
             # Don't resize resources here, they should be loaded already
             return # Exit load function

        try:
            with shelve.open(actual_path, 'r') as shelf:
                if filename not in shelf:
                     print(f"Map name '{filename}' not found in file. Starting new map.")
                     # Reset to default state
                     self.tile_map = {}
                     self.nogrid_tiles = []
                     self.camera = [0, 0]
                     self.history = []
                     self.history_index = 0
                     self.k = self.tile_size / self.base_tile_size
                     return

                data = shelf[filename]
                # Safely load data with defaults for missing keys
                self.tile_map = {tuple(map(int, k.strip('()').split(','))): v for k, v in data.get('tile_map', {}).items()}
                self.nogrid_tiles = data.get('nogrid_tiles', [])
                self.base_tile_size = data.get('base_tile_size', 16)
                self.tile_size = data.get('tile_size', 32)
                self.change_tiles_size = data.get('change_tiles_size', 2)
                self.camera = [data.get('camera_x', 0), data.get('camera_y', 0)]
                self.k = self.tile_size / self.base_tile_size
                self.history = [] # Clear history on load
                self.history_index = 0
                self._resize_resources() # Resize based on loaded tile size
                print(f"Map '{filename}' loaded successfully.")

        except Exception as e:
            print(f"Error loading map '{filename}': {e}. Starting new map.")
            # Reset to default state on error
            self.tile_map = {}
            self.nogrid_tiles = []
            self.camera = [0, 0]
            self.history = []
            self.history_index = 0
            # Keep default tile size settings? Or reset? Let's reset.
            self.base_tile_size = 16
            self.tile_size = 32
            self.change_tiles_size = 2
            self.k = self.tile_size / self.base_tile_size
            self._resize_resources()


# --- Global Helper Functions (Undo/Redo need access to editor instance) ---
def undo(editor):
    while True:
        if editor.history_index == 0: return
        editor.history_index -= 1
        action = editor.history[editor.history_index]

        if action['action'] == 'add':
            if action['type'] == 'grid':
                if action['pos'] in editor.tile_map:
                    del editor.tile_map[action['pos']]
                # else: continue # Should not happen if history is correct
            else: # nogrid
                # Find and remove the specific tile added (match object ID or content)
                # Safest is to find by content if object ID isn't reliable
                 tile_to_remove = None
                 for t in editor.nogrid_tiles:
                     # Compare content (pos, resource, variant)
                     if t['pos'] == action['pos'] and t['resource'] == action['tile']['resource'] and t['variant'] == action['tile']['variant']:
                         tile_to_remove = t
                         break
                 if tile_to_remove:
                     editor.nogrid_tiles.remove(tile_to_remove)


        elif action['action'] == 'delete':
            if action['type'] == 'grid':
                editor.tile_map[action['pos']] = action['tile'] # Restore tile
            else: # nogrid
                editor.nogrid_tiles.append(action['tile']) # Restore tile

        elif action['action'] == 'add_filled':
            filled_tiles_data = action['tile'] # This is a list of ((i,j), tile_data)
            for pos, _ in filled_tiles_data:
                if pos in editor.tile_map:
                    del editor.tile_map[pos]

        elif action['action'] == 'move_selected_area':
            shiftx, shifty = action['pos']
            original_grid = action['tile']['original_grid']
            original_offgrid = action['tile']['original_offgrid']
            final_grid = action['tile']['grid']
            final_offgrid = action['tile']['offgrid']

            # Remove tiles from their final moved positions
            for pos, _ in final_grid:
                if pos in editor.tile_map:
                    del editor.tile_map[pos]
            for tile_final in final_offgrid:
                 # Find the moved tile in the current list and remove it
                 tile_to_remove = None
                 for t in editor.nogrid_tiles:
                      # Compare by final position and content
                     if t['pos'] == tile_final['pos'] and t['resource'] == tile_final['resource'] and t['variant'] == tile_final['variant']:
                         tile_to_remove = t
                         break
                 if tile_to_remove:
                      editor.nogrid_tiles.remove(tile_to_remove)


            # Restore tiles to their original positions
            for pos, tile in original_grid:
                editor.tile_map[pos] = tile
            editor.nogrid_tiles.extend(original_offgrid)

            # Restore selection rectangle to original position
            if editor.selected_area_abs:
                 editor.selected_area_abs[0][0] -= shiftx
                 editor.selected_area_abs[0][1] -= shifty
                 editor.selected_area_abs[1][0] -= shiftx
                 editor.selected_area_abs[1][1] -= shifty


        elif action['action'] == 'remove_selected_area':
            # Restore the removed tiles
            tiles_in_area = action['tile']['grid']
            offgrid_tiles_in_area = action['tile']['offgrid']
            for pos, tile in tiles_in_area:
                editor.tile_map[pos] = tile
            editor.nogrid_tiles.extend(offgrid_tiles_in_area)

        elif action['action'] == 'paste_sector':
             # Remove the pasted tiles
            pasted_grid_tiles = action['tile']['grid']
            pasted_offgrid_tiles = action['tile']['offgrid']
            for pos, _ in pasted_grid_tiles:
                if pos in editor.tile_map:
                    del editor.tile_map[pos]
            for tile_pasted in pasted_offgrid_tiles:
                 # Find and remove the pasted tile
                 tile_to_remove = None
                 for t in editor.nogrid_tiles:
                     if t['pos'] == tile_pasted['pos'] and t['resource'] == tile_pasted['resource'] and t['variant'] == tile_pasted['variant']:
                         tile_to_remove = t
                         break
                 if tile_to_remove:
                     editor.nogrid_tiles.remove(tile_to_remove)

        # We only undo one action at a time now.
        break # Exit the while loop after processing one action


def redo(editor):
    while True: # Loop may not be needed if only redoing one step
        if editor.history_index == len(editor.history): return
        action = editor.history[editor.history_index]
        # Don't increment index until *after* successful redo
        # editor.history_index += 1 # Increment after processing

        if action['action'] == 'add':
            if action['type'] == 'grid':
                editor.tile_map[action['pos']] = action['tile']
            else: # nogrid
                editor.nogrid_tiles.append(action['tile'])

        elif action['action'] == 'delete':
            if action['type'] == 'grid':
                if action['pos'] in editor.tile_map:
                    del editor.tile_map[action['pos']]
                # else: continue # If tile doesn't exist, maybe skip redo?
            else: # nogrid
                 # Find and remove the specific tile restored by undo
                 tile_to_remove = None
                 for t in editor.nogrid_tiles:
                     # Compare content (pos, resource, variant)
                     if t['pos'] == action['pos'] and t['resource'] == action['tile']['resource'] and t['variant'] == action['tile']['variant']:
                         tile_to_remove = t
                         break
                 if tile_to_remove:
                     editor.nogrid_tiles.remove(tile_to_remove)


        elif action['action'] == 'add_filled':
            filled_tiles_data = action['tile'] # This is a list of ((i,j), tile_data)
            for pos, tile_data in filled_tiles_data:
                editor.tile_map[pos] = tile_data

        elif action['action'] == 'move_selected_area':
            shiftx, shifty = action['pos']
            original_grid = action['tile']['original_grid']
            original_offgrid = action['tile']['original_offgrid']
            final_grid = action['tile']['grid']
            final_offgrid = action['tile']['offgrid']

            # Remove tiles from original positions
            for pos, _ in original_grid:
                 if pos in editor.tile_map:
                    del editor.tile_map[pos]
            for tile_orig in original_offgrid:
                 # Find by original position and remove
                 tile_to_remove = None
                 for t in editor.nogrid_tiles:
                     if t['pos'] == tile_orig['pos'] and t['resource'] == tile_orig['resource'] and t['variant'] == tile_orig['variant']:
                         tile_to_remove = t
                         break
                 if tile_to_remove:
                      editor.nogrid_tiles.remove(tile_to_remove)


            # Add tiles to their final moved positions
            temp_new_grid = {}
            for pos, tile in final_grid:
                 temp_new_grid[pos] = tile
            editor.tile_map.update(temp_new_grid)
            editor.nogrid_tiles.extend(copy.deepcopy(final_offgrid)) # Add copies of final state

             # Restore selection rectangle to final position
            if editor.selected_area_abs:
                 editor.selected_area_abs[0][0] += shiftx
                 editor.selected_area_abs[0][1] += shifty
                 editor.selected_area_abs[1][0] += shiftx
                 editor.selected_area_abs[1][1] += shifty


        elif action['action'] == 'remove_selected_area':
            # Redo the removal
            tiles_in_area = action['tile']['grid']
            offgrid_tiles_in_area = action['tile']['offgrid']
            for pos, _ in tiles_in_area:
                if pos in editor.tile_map:
                    del editor.tile_map[pos]
            for tile_removed in offgrid_tiles_in_area:
                 # Find by content and remove
                 tile_to_remove = None
                 for t in editor.nogrid_tiles:
                      if t['pos'] == tile_removed['pos'] and t['resource'] == tile_removed['resource'] and t['variant'] == tile_removed['variant']:
                           tile_to_remove = t
                           break
                 if tile_to_remove:
                      editor.nogrid_tiles.remove(tile_to_remove)


        elif action['action'] == 'paste_sector':
             # Redo the paste operation
            pasted_grid_tiles = action['tile']['grid']
            pasted_offgrid_tiles = action['tile']['offgrid']
            for pos, tile_data in pasted_grid_tiles:
                 editor.tile_map[pos] = tile_data # Overwrite existing
            editor.nogrid_tiles.extend(copy.deepcopy(pasted_offgrid_tiles)) # Add copies


        editor.history_index += 1 # Increment index after successful redo processing
        break # Exit the while loop after processing one action


# --- Main Execution Logic ---
def run(screen_, filename=None):
    global screen # Make screen global for render functions if needed (better to pass)
    screen = screen_
    clock = pygame.time.Clock()

    # --- Layout Setup ---
    TOOLBAR_HEIGHT = 40
    RESOURCE_PANEL_WIDTH = 250 # Example width, adjust as needed

    editor_surface_width = SCREEN_WIDTH - RESOURCE_PANEL_WIDTH
    editor_surface_height = SCREEN_HEIGHT - TOOLBAR_HEIGHT
    editor_surface = pygame.Surface((editor_surface_width, editor_surface_height))
    editor_rect = pygame.Rect(0, TOOLBAR_HEIGHT, editor_surface_width, editor_surface_height)

    # Initialize Editor with the surface size it will draw on
    editor = Editor(filename, (editor_surface_width, editor_surface_height))

    # --- Toolbar Setup ---
    toolbar_layout = HorizontalLayout(None) # No parent needed for root layout
    toolbar_layout.setPosition(0, 0)
    toolbar_layout.setSize(SCREEN_WIDTH, TOOLBAR_HEIGHT)
    toolbar_layout.setBackgroundColors([LIGHT_GRAY_BG, LIGHT_GRAY_BG]) # Use custom color
    toolbar_layout.setSpace(5)
    toolbar_layout.setPaddings([2, 5, 2, 5]) # Top, Right, Bottom, Left

    # Create Toolbar Buttons
    buttons = {}
    button_defs = [
        ('save', "Save (S)", lambda: editor.save(filename if filename else 'untitled')),
        ('grid', "Grid (G)", editor.toggle_grid, True), # Add toggle flag
        ('fill', "Fill (F)", editor.toggle_fill_mode, True),
        ('cont', "Cont. (Shift)", editor.toggle_continuous_mode, True),
        ('sel', "Select (Ctrl)", editor.toggle_select_area_mode, True),
        ('del_sel', "Del Sel (Bksp)", editor.delete_selected),
        ('copy', "Copy (Ctrl+C)", editor.copy_selected),
        ('paste', "Paste", editor.activate_paste), # Paste button replaces Ctrl+V logic
        ('trans', "Trans. (T)", editor.transform),
        ('undo', "Undo (Ctrl+Z)", lambda: undo(editor)),
        ('redo', "Redo (Ctrl+Y/Sh+Z)", lambda: redo(editor)),
        ('zoom+', "Zoom + (=)", editor.zoom_plus),
        ('zoom-', "Zoom - (-)", editor.zoom_minus),
        ('exit', "Exit (Esc)", None) # Special handling for exit
    ]

    button_size_h = TOOLBAR_HEIGHT - toolbar_layout.paddings[0] - toolbar_layout.paddings[2] # Calculate height based on padding

    for key, text, callback, *is_toggle in button_defs:
        btn = TextButton(toolbar_layout, text)
        # btn.setSize(button_size_w, button_size_h) # Width is determined by layout
        btn.setFixedSizes([False, True]) # Width dynamic, Height fixed
        btn.rect.height = button_size_h # Set fixed height directly
        btn.setFont(None, 18) # Smaller font for toolbar
        btn.setBackgroundColors([BUTTON_COLOR, BUTTON_HOVER_COLOR])
        btn.setBorderWidth(1)
        btn.setBorderRadius(3)
        if callback:
             btn.onClick = callback # Use onClick provided by widget
        buttons[key] = btn
        buttons[key].is_toggle = bool(is_toggle and is_toggle[0]) # Store toggle state
        toolbar_layout.addWidget(btn)

    toolbar_layout.dispose() # Calculate initial layout

    # --- Resource Panel Setup ---
    # Make ResourcePanel a child of the main screen/layout if needed, or manage separately
    resource_panel = ResourcePanel(editor.resources, (6, 2)) # Example dims (rows, cols)
    # Position the resource panel
    rp_x = editor_surface_width
    rp_y = TOOLBAR_HEIGHT
    resource_panel.setPosition(rp_x, rp_y)
    resource_panel.setSize(RESOURCE_PANEL_WIDTH, editor_surface_height) # Fit remaining height
    resource_panel.setFixedSizes([True, True])
    resource_panel.setBackgroundColors([GRAY, GRAY]) # Match editor style
    resource_panel.setBorderWidth(0)
    resource_panel.show()
    try:
        resource_panel.dispose() # Calculate its internal layout
    except Exception as e:
         print(f"Error disposing resource panel: {e}") # Catch potential errors during init


    # --- State Variables for Main Loop ---
    state = State() # Widget state manager
    running = True
    mouse_wheel_pressed = False
    last_mpos_screen = (0, 0)
    # Keyboard state (keep for camera, undo/redo shortcuts maybe)
    key_pressed = pygame.key.get_pressed()
    ctrl_pressed = False
    shift_pressed = False


    while running:
        dt = clock.tick(60) / 1000.0 # Delta time in seconds

        # --- Event Handling ---
        events = pygame.event.get()
        state.update(events) # Update widget state first
        key_pressed = pygame.key.get_pressed() # Get current key state
        mouse_buttons_pressed = pygame.mouse.get_pressed() # Get mouse button state
        mouse_pos_screen = pygame.mouse.get_pos() # Get mouse position

        # Update editor's internal mouse state
        editor.update_mouse_state(mouse_pos_screen, editor_rect, mouse_buttons_pressed)


        for event in events:
            if event.type == pygame.QUIT:
                running = False
            # --- Keyboard Shortcuts (Keep some for convenience?) ---
            if event.type == pygame.KEYDOWN:
                ctrl_pressed = key_pressed[pygame.K_LCTRL] or key_pressed[pygame.K_RCTRL]
                shift_pressed = key_pressed[pygame.K_LSHIFT] or key_pressed[pygame.K_RSHIFT]

                if event.key == pygame.K_ESCAPE:
                    running = False # Allow Esc shortcut for exit button
                elif event.key == pygame.K_s and ctrl_pressed:
                     editor.save(filename if filename else 'untitled') # Ctrl+S to save
                elif event.key == pygame.K_g:
                     editor.toggle_grid()
                elif event.key == pygame.K_f:
                     editor.toggle_fill_mode()
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                     pass # Shift is now handled by continuous mode button
                elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                     pass # Ctrl is now handled by select area mode button
                elif event.key == pygame.K_BACKSPACE:
                     editor.delete_selected() # Allow Backspace shortcut
                elif event.key == pygame.K_c and ctrl_pressed:
                     editor.copy_selected() # Allow Ctrl+C shortcut
                #elif event.key == pygame.K_v and ctrl_pressed: # Remove Ctrl+V, use Paste button
                #     editor.activate_paste()
                elif event.key == pygame.K_t:
                     editor.transform()
                elif event.key == pygame.K_z and ctrl_pressed and not shift_pressed:
                     undo(editor) # Ctrl+Z
                elif event.key == pygame.K_y and ctrl_pressed: # Ctrl+Y for redo
                     redo(editor)
                elif event.key == pygame.K_z and ctrl_pressed and shift_pressed: # Ctrl+Shift+Z for redo
                     redo(editor)
                elif event.key == pygame.K_EQUALS: # = key for zoom in
                     editor.zoom_plus()
                elif event.key == pygame.K_MINUS: # - key for zoom out
                     editor.zoom_minus()
                # Camera Movement (Keep shortcuts)
                elif event.key == pygame.K_RIGHT: editor.move[0] = 5
                elif event.key == pygame.K_LEFT: editor.move[0] = -5
                elif event.key == pygame.K_DOWN: editor.move[1] = 5
                elif event.key == pygame.K_UP: editor.move[1] = -5
                 # Resource Cycling (Keep shortcuts)
                elif event.key == pygame.K_e:
                    if editor.resource_names:
                        current_idx = editor.resource_names.index(editor.current_resource)
                        editor.current_resource = editor.resource_names[(current_idx + 1) % len(editor.resource_names)]
                        editor.current_variant = 0
                        resource_panel.selected_tile = None # Deselect in panel
                elif event.key == pygame.K_q:
                    if editor.resource_names:
                        current_idx = editor.resource_names.index(editor.current_resource)
                        editor.current_resource = editor.resource_names[(current_idx - 1 + len(editor.resource_names)) % len(editor.resource_names)]
                        editor.current_variant = 0
                        resource_panel.selected_tile = None # Deselect in panel
                elif event.key == pygame.K_SPACE:
                     if editor.resources.get(editor.current_resource): # Check if resource exists
                         num_variants = len(editor.resources[editor.current_resource])
                         if num_variants > 0:
                              editor.current_variant = (editor.current_variant + 1) % num_variants
                              resource_panel.selected_tile = None # Deselect in panel


            elif event.type == pygame.KEYUP:
                 ctrl_pressed = key_pressed[pygame.K_LCTRL] or key_pressed[pygame.K_RCTRL]
                 shift_pressed = key_pressed[pygame.K_LSHIFT] or key_pressed[pygame.K_RSHIFT]
                 # Stop camera movement
                 if event.key == pygame.K_RIGHT and editor.move[0] > 0: editor.move[0] = 0
                 elif event.key == pygame.K_LEFT and editor.move[0] < 0: editor.move[0] = 0
                 elif event.key == pygame.K_DOWN and editor.move[1] > 0: editor.move[1] = 0
                 elif event.key == pygame.K_UP and editor.move[1] < 0: editor.move[1] = 0

            # --- Mouse Input ---
            elif event.type == pygame.MOUSEWHEEL:
                if editor.mouse_over_editor: # Only zoom if mouse is over editor area
                    if event.y > 0: editor.zoom_plus()
                    elif event.y < 0: editor.zoom_minus()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                 if event.button == 1: # Left Click
                     # Check toolbar first
                     toolbar_layout.update(state) # This triggers onClick if hovered
                     # Check resource panel
                     resource_panel.update(state)
                     # Check editor area
                     if editor.mouse_over_editor:
                         editor.handle_editor_click(0) # Handle editor-specific LMB down
                 elif event.button == 3: # Right Click
                      if editor.mouse_over_editor:
                           editor.handle_editor_click(2) # Handle editor-specific RMB down
                 elif event.button == 2: # Middle Click
                     mouse_wheel_pressed = True
                     last_mpos_screen = mouse_pos_screen # Store screen pos for panning
                     if editor.mouse_over_editor:
                          editor.handle_editor_click(1)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # Left Mouse Up
                    editor.pressed[0] = False # Update internal pressed state
                    if editor.selecting_area_active: # Finish drawing selection
                        editor.selecting_area_active = False
                        # Check if selection has valid size, otherwise clear it
                        if editor.selected_area_abs:
                             w = abs(editor.selected_area_abs[0][0] - editor.selected_area_abs[1][0])
                             h = abs(editor.selected_area_abs[0][1] - editor.selected_area_abs[1][1])
                             if w < 2 or h < 2: # Minimal size check
                                 editor._clear_selection()

                    elif editor.moving_selected_area: # Finish moving selection
                        editor._save_moved_tiles() # This now resets moving_selected_area
                elif event.button == 3: # Right Mouse Up
                     editor.pressed[2] = False
                elif event.button == 2: # Middle Mouse Up
                     mouse_wheel_pressed = False
                     editor.pressed[1] = False


        # --- Updates ---
        editor.update() # Update editor logic (camera, placement based on current state)
        toolbar_layout.update(state) # Update toolbar (hover states) - click handled above
        resource_panel.update(state) # Update resource panel (hover, selection)

        # Middle mouse panning
        if mouse_wheel_pressed:
            dx = mouse_pos_screen[0] - last_mpos_screen[0]
            dy = mouse_pos_screen[1] - last_mpos_screen[1]
            editor.camera[0] -= dx
            editor.camera[1] -= dy
            last_mpos_screen = mouse_pos_screen
            # Optional: Change cursor during pan
            # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
        # else:
            # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


        # Update Resource Panel Selection -> Editor State
        if resource_panel.selected_tile:
            sel = resource_panel.selected_tile['tile']
            if editor.current_resource != sel['type'] or editor.current_variant != sel['variant']:
                 editor.current_resource = sel['type']
                 editor.current_variant = sel['variant']
                 # Deactivate special modes when selecting a new tile
                 editor.fill_activated = False
                 editor.select_area_mode = False
                 editor._clear_selection()


        # Update Toggle Button Appearances
        buttons['grid'].setBackgroundColors([BUTTON_ACTIVE_COLOR, BUTTON_ACTIVE_HOVER_COLOR] if editor.grid else [BUTTON_COLOR, BUTTON_HOVER_COLOR])
        buttons['fill'].setBackgroundColors([BUTTON_ACTIVE_COLOR, BUTTON_ACTIVE_HOVER_COLOR] if editor.fill_activated else [BUTTON_COLOR, BUTTON_HOVER_COLOR])
        buttons['cont'].setBackgroundColors([BUTTON_ACTIVE_COLOR, BUTTON_ACTIVE_HOVER_COLOR] if editor.continuous_mode else [BUTTON_COLOR, BUTTON_HOVER_COLOR])
        buttons['sel'].setBackgroundColors([BUTTON_ACTIVE_COLOR, BUTTON_ACTIVE_HOVER_COLOR] if editor.select_area_mode else [BUTTON_COLOR, BUTTON_HOVER_COLOR])


        # --- Rendering ---
        screen.fill((50, 50, 50)) # Background color for areas outside editor/panels

        # Render editor onto its dedicated surface
        editor_surface.fill((0, 0, 0)) # Clear editor surface
        editor.render(editor_surface)
        screen.blit(editor_surface, editor_rect.topleft) # Blit editor surface to screen

        # Render UI elements
        toolbar_layout.render(screen)
        resource_panel.render(screen)


        pygame.display.flip() # Update the full display


    print("Exiting editor...")
    # Optionally save on exit?
    # editor.save(filename if filename else 'untitled')

if __name__ == "__main__":
    # Determine map name from arguments or default
    map_to_load = None
    if len(sys.argv) > 1:
        map_to_load = sys.argv[1]
    else:
         # Example: load the first map found or default to 'untitled'
         try:
             with shelve.open(os.path.join(MAP_DIR, MAP_FILE), 'r') as shelf:
                 map_to_load = next(iter(shelf.keys()), 'untitled') # Get first key or default
         except Exception:
             map_to_load = 'untitled' # Default if file doesn't exist or is invalid

    main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#, pygame.NOFRAME) # Use NOFRAME if desired
    pygame.display.set_caption(f"Map Editor - {map_to_load}")
    run(main_screen, map_to_load)
    pygame.quit()
    sys.exit()
