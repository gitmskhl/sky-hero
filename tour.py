import pygame
from scripts.widgets import *
from random import random
from math import cos, sin, pi
from scripts.spark import Spark
pygame.init()

BLACK = (0, 0, 0)

class Tour:
    inf = 100
    def __init__(self, app, screen):
        app.__init__()
        self.app = app
        self.screen = screen
        self.SCREEN_WIDTH = self.screen.get_width()
        self.SCREEN_HEIGHT = self.screen.get_height()
        self.step = 1
        self.transition = -30
        self.timer = 0 # time for the current layout
        self.time = 0 # time for the whole tour
        self.set_delta_time(1)
        self.first_move = True
        self.first_jump = True
        self.first_attack = True

        self.menu_step = Tour.inf
        self.enemy_step = 1
        self.font = pygame.font.Font("fonts/Pacifico.ttf", 58)

    def borders(self, time): pass
    def set_delta_time(self, step):
        self.delta_time = 60 * 2

    def finish_current_tour(self): pass

    def check_state(self): 
        return False

    def run(self):
        self.current_layout = self.layout_1
        self.current_widget = self.widget_1
        num_layouts = len([1 for attrname in self.__dict__ if attrname.startswith("layout_")])
        self.layouts = [getattr(self, "layout_" + str(i)) for i in range(2, num_layouts + 1)]
        self.widgets = [getattr(self, "widget_" + str(i)) for i in range(2, num_layouts + 1)]
        while True:
            if self.current_widget == self.widget_4:
                pass
            self.app.clock.tick(60)
            self.app.display.fill((0, 0, 0, 0))

            self.app.map.update()
            self.app.map.render(self.app.display, self.app.display_2)

            if self.current_widget.finished:
                self.timer += 1
                if self.timer >= self.delta_time:
                    self.timer = 0
                    self.step += 1
                    self.set_delta_time(self.step)
                    if self.step - 2 < len(self.layouts):
                        self.current_layout = self.layouts[self.step - 2]
                        self.current_widget = self.widgets[self.step - 2]

            self.start_delay_time = max(0, self.start_delay_time - 1)
            if self.start_delay_time == 0:
                self.current_layout.update(pygame.mouse.get_pos(), False)
                self.current_layout.render(self.app.display, opacity=255)

            if self.check_state():
                self.current_widget.finished = True

            if self.app.dead > 60:
                self.transition += 1

            self.time += 1
            self.borders(self.time)
            
            for i in range(len(self.app.enemies)):
                self.app.display.blit(self.app.small_enemy_img, (5 + i * (self.app.small_enemy_img.get_width() * 2), 5))
            
            # main player
            if self.app.dead > 0 or self.app.main_player.dead:
                self.app.dead += 1
                if self.app.dead > 100:
                    self.app.__init__()
                    self.app.dead = 0
                    self.transition = -30
            else:
                self.app.main_player.update()
                self.app.main_player.render(self.app.display)

            
            if len(self.app.enemies) == 0 and self.kill_enemies:
                self.current_widget.finished = True

             # enemies
            fordel = []
            for enemy in self.app.enemies:
                if self.step >= self.enemy_step:
                    enemy.ai()
                else:
                    enemy.flip = True
                enemy.update()
                enemy.render(self.app.display)
                if enemy.killed:
                    fordel.append(enemy)
            for enemy in fordel:
                self.app.enemies.remove(enemy)

            # projectiles
            fordel = []
            for p in self.app.projectiles:
                p[0][0] += p[1]
                p[2] += 1
                if self.app.map.issolid(*p[0]):
                    fordel.append(p)
                    for _ in range(4):
                        self.app.sparks.append(Spark(p[0], 3, dir=p[1]))
                if self.app.main_player.dashing < 50 and self.app.main_player.get_rect().collidepoint(p[0]):
                    self.app.sfx['hit'].play() 
                    self.app.map.screenshake = max(16, self.app.map.screenshake)
                    fordel.append(p)
                    for _ in range(30):
                        speed_spark = random() * 5
                        speed_particle = random() * 5
                        angle_spark=random() * 2 * pi
                        angle_particle = random() * 2 * pi
                        self.app.sparks.append(Spark(p[0], speed_spark, angle=angle_spark))
                        self.app.map.particles.add(p[0], [speed_particle * cos(angle_particle), speed_particle * sin(angle_particle)])
                    self.app.dead = 1
                if p[2] > 360:
                    fordel.append(p)
                self.app.display.blit(
                    self.app.projectile_img,
                    (p[0][0] - self.app.map.camera[0], p[0][1] - self.app.map.camera[1])
                )
            for p in fordel:
                self.app.projectiles.remove(p)

            # sparks
            fordel = []
            for spark in self.app.sparks:
                if spark.update():
                    fordel.append(spark)
                spark.render(self.app.display, self.app.map.camera)
            for spark in fordel:
                self.app.sparks.remove(spark)

            self.app.map.move_camera(self.app.main_player.pos[0] - self.SCREEN_WIDTH // 2, self.app.main_player.pos[1] - self.SCREEN_HEIGHT // 2)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and self.step >= self.move_step:
                        self.app.main_player.move[0] = True
                        self.app.main_player.move[1] = False
                        self.app.main_player.flip = True
                        if self.step == self.move_step and self.first_move:
                            self.current_widget.finished = True
                    elif event.key == pygame.K_RIGHT and self.step >= self.move_step:
                        self.app.main_player.move[1] = True
                        self.app.main_player.move[0] = False
                        self.app.main_player.flip = False
                        if self.step == self.move_step and self.first_move:
                            self.current_widget.finished = True
                    elif event.key == pygame.K_SPACE and self.step >= self.jump_step:
                        self.app.main_player.jump()
                        if self.step == self.jump_step and self.first_jump:
                            self.current_widget.finished = True
                    elif event.key == pygame.K_ESCAPE and self.step >= self.menu_step:
                        self.app.menu_run()
                    elif event.key == pygame.K_x and self.step >= self.attack_step:
                        self.app.main_player.dash()
                        if self.step == self.attack_step and self.first_attack:
                            self.current_widget.finished = True

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and self.step >= self.move_step:
                        self.app.main_player.move[0] = False
                    elif event.key == pygame.K_RIGHT and self.step >= self.move_step:
                        self.app.main_player.move[1] = False

            if self.transition or (self.step - 2 == len(self.layouts)):
                surf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                surf.fill((0, 0, 0))
                coef = (self.SCREEN_WIDTH ** 2 + self.SCREEN_HEIGHT ** 2) ** .5 / 2 // 30 + 1
                pygame.draw.circle(surf, (255, 255, 255), (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2), coef * (30 - abs(self.transition)))
                surf.set_colorkey((255, 255, 255))
                self.app.display.blit(surf, (0, 0))
                if self.app.dead == 0:
                    self.transition += 1
                if self.transition > 30 and self.step - 2 == len(self.layouts):
                    self.finish_current_tour()
                    return

            display_mask = pygame.mask.from_surface(self.app.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
            for pos in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.app.display_2.blit(display_sillhouette, pos)
            self.app.display_2.blit(self.app.display, (0, 0))
            self.screen.blit(self.app.display_2, (0, 0))
            pygame.display.flip()

            

class Tour_1(Tour):
    def __init__(self, app, screen):
        super().__init__(app, screen)
        DELTA_TIME = 2
        self.move_step = 2
        self.jump_step = 5
        self.attack_step = Tour.inf
        self.start_delay_time = 60 * 1
        self.kill_enemies = False

        # layout 1
        self.layout_1 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_1.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            'Welcome to the Sky Hero!',
            'Use the left and right arrows to move'
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, font=self.font, deltatime=DELTA_TIME, delay=120)
        self.layout_1.addWidget(self.widget_1)
        self.layout_1.dispose()

        # layout 2
        self.layout_2 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_2.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_2 = BlinkingLabel(self.layout_2, "Press the <-- and --> keys".replace(' ', '  '), positions=['center', 'top'], font=self.font, color=BLACK, blinktime=40)
        self.widget_2.finished = False
        self.layout_2.addWidget(self.widget_2)
        self.layout_2.dispose()

        # layout 3
        self.layout_3 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_3.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_3 = Label(self.layout_3, 'Good!'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK)
        self.widget_3.finished = True
        self.layout_3.addWidget(self.widget_3)
        self.layout_3.dispose()

        # layout 4
        self.layout_4 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_4.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "Press the space key to jump",
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_4 = GradualStoryWidget(self.layout_4, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_4.addWidget(self.widget_4)
        self.layout_4.dispose()

        # layout 5
        self.layout_5 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_5.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_5 = BlinkingLabel(self.layout_5, "Press SPACE".replace(' ', '  '), positions=['center', 'top'], font=self.font, color=BLACK, blinktime=40)
        self.widget_5.finished = False
        self.layout_5.addWidget(self.widget_5)
        self.layout_5.dispose()
 

class Tour_2(Tour):
    def __init__(self, app, screen):
        super().__init__(app, screen)
        DELTA_TIME = 2
        self.move_step = 2
        self.jump_step = 2
        self.attack_step = Tour.inf
        self.start_delay_time = 60 * 2
        self.kill_enemies = False
        self.first_jump = self.first_move = False

        self.finish_mission_timer = 30

        # layout 1
        self.layout_1 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_1.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            'Jump to the wall and press \nspace to bounce off it',
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, font=self.font, deltatime=DELTA_TIME, delay=120)
        self.layout_1.addWidget(self.widget_1)
        self.layout_1.dispose()

        # layout 2
        self.layout_2 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_2.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_2 = BlinkingLabel(self.layout_2, "Climb onto the stone tower".replace(' ', '  '), positions=['center', 'top'], font=self.font, color=BLACK, blinktime=40)
        self.widget_2.finished = False
        self.layout_2.addWidget(self.widget_2)
        self.layout_2.dispose()

        # layout 3
        self.layout_3 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_3.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_3 = Label(self.layout_3, 'You\'re the best!'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK)
        self.widget_3.finished = True
        self.layout_3.addWidget(self.widget_3)
        self.layout_3.dispose()

    def check_state(self):
        if self.app.main_player.pos[1] < -323:
            self.finish_mission_timer -= 1
            if self.finish_mission_timer <= 0:
                return True
        else:
            self.finish_mission_timer = 30    
        return False
    

class Tour_3(Tour):
    def __init__(self, app, screen):
        super().__init__(app, screen)
        DELTA_TIME = 2
        self.move_step = 2
        self.jump_step = 2
        self.attack_step = 2
        self.start_delay_time = 60 * 2
        self.kill_enemies = True
        self.first_jump = self.first_move = False

        # layout 1
        self.layout_1 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_1.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            'There are enemies in the game. They can shoot',
            'You can attack them by\n pressing the X key',
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, font=self.font, deltatime=DELTA_TIME, delay=120)
        self.layout_1.addWidget(self.widget_1)
        self.layout_1.dispose()

        # layout 2
        self.layout_2 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_2.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_2 = BlinkingLabel(self.layout_2, "Kill the enemy".replace(' ', '  '), positions=['center', 'top'], font=self.font, color=BLACK, blinktime=40)
        self.widget_2.finished = False
        self.layout_2.addWidget(self.widget_2)
        self.layout_2.dispose()

        # layout 3
        self.layout_3 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_3.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_3 = Label(self.layout_3, 'Excellent attack!'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK)
        self.widget_3.finished = True
        self.layout_3.addWidget(self.widget_3)
        self.layout_3.dispose()


    def set_delta_time(self, step):
        if step == 1:
            self.delta_time = 60 * 5  
        else:
            self.delta_time = 60 * 2  


class Tour_4(Tour):
    def __init__(self, app, screen):
        super().__init__(app, screen)
        DELTA_TIME = 2
        self.move_step = 2
        self.jump_step = 2
        self.attack_step = 2
        self.enemy_step = 2
        self.start_delay_time = 60 * 2
        self.kill_enemies = True
        self.first_jump = self.first_move = self.first_attack = False

        # layout 1
        self.layout_1 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_1.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "A bullet won't kill you \nif you touch it while attacking",
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, font=self.font, deltatime=DELTA_TIME, delay=120)
        self.layout_1.addWidget(self.widget_1)
        self.layout_1.dispose()

        # layout 2
        self.layout_2 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_2.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_2 = BlinkingLabel(self.layout_2, "Kill the enemy".replace(' ', '  '), positions=['center', 'top'], font=self.font, color=BLACK, blinktime=40)
        self.widget_2.finished = False
        self.layout_2.addWidget(self.widget_2)
        self.layout_2.dispose()

    def set_delta_time(self, step):
        if step == 1:
            self.delta_time = 60 * 4  
        else:
            self.delta_time = 60 * 1  



class Tour_5(Tour):
    def __init__(self, app, screen):
        super().__init__(app, screen)
        DELTA_TIME = 2
        self.move_step = 2
        self.jump_step = 2
        self.attack_step = 2
        self.enemy_step = 2
        self.start_delay_time = 60 * 2
        self.kill_enemies = True
        self.first_jump = self.first_move = self.first_attack = False

        # layout 1
        self.layout_1 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_1.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "The main goal of the game is to kill all the enemies",
            "After that, you will proceed to the next level",
            "The number of living enemies \non the map is shown in the \ntop left corner"
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, font=self.font, deltatime=DELTA_TIME, delay=120)
        self.layout_1.addWidget(self.widget_1)
        self.layout_1.dispose()

        # layout 2
        self.layout_2 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_2.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_2 = BlinkingLabel(self.layout_2, "Kill all the enemies".replace(' ', '  '), positions=['center', 'top'], font=self.font, color=BLACK, blinktime=40)
        self.widget_2.finished = False
        self.layout_2.addWidget(self.widget_2)
        self.layout_2.dispose()

        # layout 3
        self.layout_3 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_3.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_3 = Label(self.layout_3, 'Excellent!'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK)
        self.widget_3.finished = True
        self.layout_3.addWidget(self.widget_3)
        self.layout_3.dispose()

        # layout 4
        self.layout_4 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_4.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "Your training is complete, \nwarrior",
            "The path ahead is yours now",
            "You are now ready to face the world",
            "May your journey be filled\n with success",
            "The lessons are learned.\n The adventure begins",
            "      Good luck, hero!",
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_4 = GradualStoryWidget(self.layout_4, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, font=self.font, deltatime=DELTA_TIME, delay=120)
        self.layout_4.addWidget(self.widget_4)
        self.layout_4.dispose()


    def set_delta_time(self, step):
        if step == 1:
            self.delta_time = 60 * 3
        elif step == 4:
            self.delta_time = 60 * 4
        else:
            self.delta_time = 60 * 2
        # some dirty code 
        if step == 4:
            self.kill_enemies = False


    def borders(self, time): 
        if (
            (self.widget_1.current_idx == 2 and not self.widget_1.pause) or 
            (self.widget_1.current_idx == 3 and self.step == 1)
        ):
            if self.app.enemies:
                total_width = len(self.app.enemies) * (self.app.small_enemy_img.get_width() * 2) - self.app.small_enemy_img.get_width()
                enemy_icons_rect = pygame.Rect(
                    0,
                    0,
                    total_width + 10,
                    self.app.small_enemy_img.get_height() + 10
                )
                pygame.draw.rect(self.app.display, (255, 0, 0), enemy_icons_rect, 2)

    def finish_current_tour(self):
        surf = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        surf.set_alpha(0)
        alpha = 0
        timer = 2
        font = pygame.font.Font('fonts/Pacifico.ttf', 58)
        while alpha != 256:
            self.screen.fill((0, 0, 0))
            surf.fill((0, 0, 0, 255))
            self.app.clock.tick(60)
            timer -= 1
            if timer == 0:
                alpha += 1
                timer = 2
                surf.set_alpha(alpha)
            text = font.render("Let's   start...", True, (255, 255, 255))
            surf.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, self.screen.get_height() // 2 - text.get_height() // 2))
            self.screen.blit(surf, (0, 0))
            pygame.display.flip()

