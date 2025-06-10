import pygame
import sys
import pickle
import os
import copy
import shelve
import gc

from scripts.menu import ButtonsMenu
from scripts.map import Map
from scripts.player import Player
from scripts.enemy import Enemy 
from scripts.physics import SCREEN_WIDTH, SCREEN_HEIGHT
from scripts.utils import load_image
from scripts.spark import Spark
from scripts.menu import (
    MainMenu,
    SelectLevelMenu,
    StartMenu,
    SettingsMenu,
    AdvancedSettingsMenu,
    MyLevelsMenu,
    KeyBindingsMenu
)
from scripts.widgets import Pages
from scripts import widgets
from scripts.combo import Combo
from scripts.custom_map_creator import run
from scripts import keyboard


from tour import Tour_1, Tour_2, Tour_3, Tour_4, Tour_5

from random import random
from math import pi, cos, sin

pygame.init()

STATE = 'menu'

if __name__ != "__main__":
	exit(0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Sky Hero")
clock = pygame.time.Clock()
achieved_level = 1
level = 1
level_config = None

keyboard.init_keyboard()

class App:
    def __init__(self, level_config=None):
        gc.collect()
        self.display = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = clock
        self.running = True
        self.level = level
        self.achieved_level = achieved_level
        self.map = Map(level, level_config=level_config)
        self.main_player = Player('entities/player/', *self.map.start_pos(), self.map, self)
        self._init_enemies()
        self.projectiles = [] # [[x, y], speed, timer]
        self.projectile_img = load_image('images/projectile.png', self.map.tile_size // self.map.base_tile_size, (0, 0, 0))
        self.sparks = []
        self.dead = 0
        self.transition = -30
        self.win_timer = 0

        if 'main_menu' not in self.__dict__:

            self.sfx = {
                'jump': pygame.mixer.Sound('sfx/jump.wav'),
                'dash': pygame.mixer.Sound('sfx/dash.wav'),
                'hit': pygame.mixer.Sound('sfx/hit.wav'),
                'shoot': pygame.mixer.Sound('sfx/shoot.wav'),
                'ambience': pygame.mixer.Sound('sfx/ambience.wav'),
            }

            self.sfx['ambience'].set_volume(.2)
            self.sfx['dash'].set_volume(.3)
            self.sfx['hit'].set_volume(.8)
            self.sfx['shoot'].set_volume(.4)
            self.sfx['jump'].set_volume(.7)

        # menu
        size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        if 'main_menu' not in self.__dict__:

            # play menu
            self.play_menu = Pages(size)
            
            start_menu = StartMenu(self.play_menu, size)
            start_menu.play_button.connect(self._continue_game)
            start_menu.new_game_button.connect(self._new_game)
            start_menu.exit_button.connect(self.go_to_main_menu)

            settings_menu = SettingsMenu(self.play_menu, size)
            settings_menu.effect_volume_slider.connect(lambda slider=settings_menu.effect_volume_slider: self._effectSliderMoved(slider))
            settings_menu.effect_volume_slider.setValue(20)
            settings_menu.volume_slider.connect(lambda slider=settings_menu.volume_slider: self._sliderMoved(slider))
            settings_menu.volume_slider.setValue(50)

            advanced_settings_menu = AdvancedSettingsMenu(self.play_menu, size)
            advanced_settings_menu.ambience_slider.connect(lambda slider=advanced_settings_menu.ambience_slider: self._certainEffectSliderMoved(slider, 'ambience'))
            advanced_settings_menu.ambience_slider.setValue(20)
            advanced_settings_menu.jump_slider.connect(lambda slider=advanced_settings_menu.jump_slider: self._certainEffectSliderMoved(slider, 'jump'))
            advanced_settings_menu.jump_slider.setValue(70)
            advanced_settings_menu.dash_slider.connect(lambda slider=advanced_settings_menu.dash_slider: self._certainEffectSliderMoved(slider, 'dash'))
            advanced_settings_menu.dash_slider.setValue(30)
            advanced_settings_menu.hit_slider.connect(lambda slider=advanced_settings_menu.hit_slider: self._certainEffectSliderMoved(slider, 'hit'))
            advanced_settings_menu.hit_slider.setValue(80)
            advanced_settings_menu.shoot_slider.connect(lambda slider=advanced_settings_menu.shoot_slider: self._certainEffectSliderMoved(slider, 'shoot'))
            advanced_settings_menu.shoot_slider.setValue(40)


            # main menu
            self.main_menu = Pages(size)

            mmenu = MainMenu(self, self.main_menu, size)
            select_level_menu = SelectLevelMenu(self, self.main_menu, size)
            self.my_levels_menu = MyLevelsMenu(self, self.main_menu, size)
            key_bindings_menu = KeyBindingsMenu(self.main_menu, size)

            pygame.mixer.music.load('sfx/music.wav')
            pygame.mixer.music.set_volume(0.5)
            self.sfx_sliders = {
                'ambience': advanced_settings_menu.ambience_slider,
                'jump': advanced_settings_menu.jump_slider,
                'dash': advanced_settings_menu.dash_slider,
                'hit': advanced_settings_menu.hit_slider,
                'shoot': advanced_settings_menu.shoot_slider
            }
            
            self.play_menu.addLayouts([start_menu, settings_menu, advanced_settings_menu])
            self.main_menu.addLayouts([mmenu, select_level_menu, self.my_levels_menu, key_bindings_menu])
            # enemy icon
            enemy_img = self.map.resources['spawners'][1]
            self.small_enemy_img = pygame.transform.scale(enemy_img, (enemy_img.get_width() / 1.5, enemy_img.get_height() / 1.5))
            
        self.pause = False
        self.combo = Combo('COMBO')
        self.lesson_tour_stop = False

    def open_map_creator(self):
        run()
        self.my_levels_menu.refresh_levels()

    def delete_level(self, level_name):
        with shelve.open('.levels') as shelf:
            del shelf[level_name]
        self.my_levels_menu.refresh_levels()

        
    def load_my_own_level(self, config):
        global level_config
        level_config = config
        self.go_to_game()

    def load_level(self, lvl):
        global level, level_config
        level_config = None
        if lvl > self.achieved_level: return
        level = lvl
        self.__init__()
        self.go_to_game()

    def go_to_main_menu(self):
        global STATE
        STATE = 'menu'
        self.pause = False
        self.running = False
        self.tour_running = False
        self.lesson_tour_stop = True
        pygame.mixer.music.stop()
        for sfx in self.sfx.values():
            sfx.stop()

    def go_to_game(self, from_main_menu=False):
        global STATE, level_config
        if from_main_menu:
            level_config = None
        STATE = 'game'
        self.pause = False
        self.running = True
        self.main_menu_running = False

    def set_state(self, state):
        global STATE
        STATE = state

    def exit_game(self):
        save()
        pygame.quit()
        sys.exit()

    def _continue_game(self):
        self.pause = False
        self.running = True
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


    def _new_game(self):
        global level, current_tour
        self.__init__(level_config)
        if level < 0:
            current_tour -= 1
            level += 1
            self.tour_running = False

    def _certainEffectSliderMoved(self, slider, effect_name):
        if effect_name in self.sfx:
            self.sfx[effect_name].set_volume(slider.value / 100)
        else:
            print(f"Effect '{effect_name}' not found in sfx dictionary.")

    def _effectSliderMoved(self, slider):
        for sfx_name, sfx in self.sfx.items():
            sfx.set_volume(slider.value / 100)
            self.sfx_sliders[sfx_name].setValue(slider.value)

    def _sliderMoved(self, slider):
        pygame.mixer.music.set_volume(slider.value / 100)

    def _init_enemies(self):
        self.enemies = []
        for pos in self.map.get_positions('spawners', 1, keep=False):
            self.enemies.append(Enemy('entities/enemy/', *pos, self.map, self))

    def main_menu_run(self):
        if not hasattr(self, 'main_menu_background'):
            self.main_menu_background = load_image('images/menu_bg.jpeg', scale=1, size=screen.get_size())
        self.main_menu_running = True
        self.main_menu.setPage(0)
        while self.main_menu_running:
            widgets.NUM_HOVERED = 0
            self.clock.tick(60)
            screen.blit(self.main_menu_background, (0, 0))
            mouse_pos = pygame.mouse.get_pos()
            self.main_menu.update(mouse_pos, False)
            self.main_menu.render(screen)
            if widgets.NUM_HOVERED:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            for event in pygame.event.get():
                if isinstance(self.main_menu.current_layout, KeyBindingsMenu):
                    self.main_menu.current_layout.handle_event(event)
                if event.type == pygame.KEYDOWN:
                    if isinstance(self.main_menu.current_layout, ButtonsMenu):
                        if event.key == keyboard.KEY_BINDINGS['up']:
                            self.main_menu.selectedUp()
                        elif event.key == keyboard.KEY_BINDINGS['down']:
                            self.main_menu.selectedDown()
                        elif event.key == pygame.K_RETURN:
                            self.main_menu.enterPressed()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.main_menu.update(mouse_pos, True)
            pygame.display.update()

    def play_menu_run(self):
        # if level < 0:
        #     self.play_menu.layouts[0].new_game_button.hide()
        copy_screen = screen.copy()
        self.pause = True
        self.main_player.move = [0] * 4
        while self.pause:
            widgets.NUM_HOVERED = 0
            self.clock.tick(60)
            screen.blit(copy_screen, (0, 0))
            mouse_pos = pygame.mouse.get_pos()
            self.play_menu.update(mouse_pos, False)
            self.play_menu.render(screen)
            if widgets.NUM_HOVERED:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if not isinstance(self.play_menu.current_layout, ButtonsMenu): continue
                    if event.key == keyboard.KEY_BINDINGS['up']:
                        self.play_menu.selectedUp()
                    elif event.key == keyboard.KEY_BINDINGS['down']:
                        self.play_menu.selectedDown()
                    elif event.key == pygame.K_RETURN:
                        self.play_menu.enterPressed()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.play_menu.update(mouse_pos, True)
            pygame.display.update()

    def run(self):
        while True:
            if STATE == 'menu':
                self.main_menu_run()
            else:
                self.run_game()
                level_config = None
        

    def run_game(self):
        global level, STATE, level_config
        if level < 0:
            self.lesson_tour_run()
            if not self.tour_running:
                STATE = 'menu'
                return
        STATE = 'game'
        self.__init__(level_config=level_config)
        pygame.mixer.music.play(-1)
        self.sfx['ambience'].play(-1)
        while self.running:
            self.clock.tick(60)
            self.display.fill((0, 0, 0, 0))

            if self.transition < 0:
                self.transition += 1

            if len(self.enemies) == 0:
                self.win_timer += 1
                if self.win_timer > 60:
                    self.transition += 1
                    if self.transition > 30:
                        if level_config:
                            self.go_to_main_menu()
                        else:
                            level += 1
                            save()
                            self.__init__()
            
            if self.dead > 60:
                self.transition += 1

            self.map.update()
            self.map.render(self.display, self.display_2)
            self.combo.update()
            self.combo.render(self.display)

            for i in range(len(self.enemies)):
                self.display.blit(self.small_enemy_img, (5 + i * (self.small_enemy_img.get_width() * 2), 5))

            # main player
            if self.dead > 0 or self.main_player.dead:
                self.dead += 1
                if self.dead > 100:
                    self.__init__(level_config)
                    self.dead = 0
            else:
                self.main_player.update()
                self.main_player.render(self.display)

            # enemies
            fordel = []
            for enemy in self.enemies:
                enemy.ai()
                enemy.update()
                enemy.render(self.display)
                if enemy.killed:
                    fordel.append(enemy)
            for enemy in fordel:
                self.enemies.remove(enemy)

            # projectiles
            fordel = []
            for p in self.projectiles:
                p[0][0] += p[1]
                p[2] += 1
                if self.map.issolid(*p[0]):
                    fordel.append(p)
                    for _ in range(4):
                        self.sparks.append(Spark(p[0], 3, dir=p[1]))
                if self.main_player.dashing < 50 and self.main_player.get_rect().collidepoint(p[0]):
                    self.sfx['hit'].play() 
                    self.map.screenshake = max(16, self.map.screenshake)
                    fordel.append(p)
                    for _ in range(30):
                        speed_spark = random() * 5
                        speed_particle = random() * 5
                        angle_spark=random() * 2 * pi
                        angle_particle = random() * 2 * pi
                        self.sparks.append(Spark(p[0], speed_spark, angle=angle_spark))
                        self.map.particles.add(p[0], [speed_particle * cos(angle_particle), speed_particle * sin(angle_particle)])
                    self.dead = 1
                    self.last_main_player_pos = copy.copy(self.main_player.pos)
                    self.main_player.pos = [10 ** 5, 10 ** 5]
                if p[2] > 360:
                    fordel.append(p)
                self.display.blit(
                    self.projectile_img,
                    (p[0][0] - self.map.camera[0], p[0][1] - self.map.camera[1])
                )
            for p in fordel:
                self.projectiles.remove(p)

            # sparks
            fordel = []
            for spark in self.sparks:
                if spark.update():
                    fordel.append(spark)
                spark.render(self.display, self.map.camera)
            for spark in fordel:
                self.sparks.remove(spark)


            if self.dead == 0:
                self.map.move_camera(self.main_player.pos[0] - SCREEN_WIDTH // 2, self.main_player.pos[1] - SCREEN_HEIGHT // 2)
            elif hasattr(self, 'last_main_player_pos'):
                self.map.move_camera(self.last_main_player_pos[0] - SCREEN_WIDTH // 2, self.last_main_player_pos[1] - SCREEN_HEIGHT // 2)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == keyboard.KEY_BINDINGS['left']:
                        self.main_player.move[0] = True
                        self.main_player.move[1] = False
                        self.main_player.flip = True
                    elif event.key == keyboard.KEY_BINDINGS['right']:
                        self.main_player.move[1] = True
                        self.main_player.move[0] = False
                        self.main_player.flip = False
                    elif event.key == pygame.K_ESCAPE:
                        # self.running = False
                        self.play_menu_run()
                    elif event.key == keyboard.KEY_BINDINGS['jump']:
                        self.main_player.jump()
                    elif event.key == keyboard.KEY_BINDINGS['attack']:
                        self.main_player.dash()

                elif event.type == pygame.KEYUP:
                    if event.key == keyboard.KEY_BINDINGS['left']:
                        self.main_player.move[0] = False
                    elif event.key == keyboard.KEY_BINDINGS['right']:
                        self.main_player.move[1] = False

            if self.transition:
                surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                surf.fill((0, 0, 0))
                coef = (SCREEN_WIDTH ** 2 + SCREEN_HEIGHT ** 2) ** .5 / 2 // 30 + 1
                pygame.draw.circle(surf, (255, 255, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), coef * (30 - abs(self.transition)))
                surf.set_colorkey((255, 255, 255))
                self.display.blit(surf, (0, 0))

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
            for pos in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, pos)
            self.display_2.blit(self.display, (0, 0))
            screen.blit(self.display_2, (0, 0))
            pygame.display.flip()

    def lesson_tour_run(self):
        global level, STATE, current_tour
        level = -1
        current_tour = 1
        tour_classes = [Tour_1, Tour_2, Tour_3, Tour_4, Tour_5]
        while current_tour - 1 < len(tour_classes):
            self.current_lesson_tour = tour_classes[current_tour - 1](app, screen)
            self.current_lesson_tour.run()
            if self.lesson_tour_stop: return
            current_tour += 1
            level -= 1
        self.current_lesson_tour = None
        level = 1
        app.__init__()
        save()
        STATE = 'game'

def save():
    if level_config: return
    global level, achieved_level
    if level < achieved_level: return
    print('saving: level = %d' % level)
    with open('.info', 'wb') as f:
        pickle.dump(level, f)
    achieved_level = level

def load():
    global level
    if not os.path.exists('.info'):
        level = -1
    else:
        with open('.info', 'rb') as f:
            level = pickle.load(f)
    print('loading: level = %d' % level)

load()
achieved_level = level
app = App()
    
app.run()
pygame.quit()
sys.exit()
