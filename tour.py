import pygame
from scripts.widgets import *
from random import random
from math import cos, sin, pi
from scripts.spark import Spark
pygame.init()

BLACK = (0, 0, 0)

class Tour_1:
    def __init__(self, app, screen):
        self.app = app
        self.screen = screen
        self.SCREEN_WIDTH = self.screen.get_width()
        self.SCREEN_HEIGHT = self.screen.get_height()
        self.step = 0
        
        DELTA_TIME = 2#6

        # layout 1
        self.layout_1 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_1.setSize(self.screen.get_width(), self.screen.get_height())
        # self.label_1 = GradualLabel(self.layout_1, "Welcome  to  the  Sky-Hero! I really love this game", positions=['left', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK, deltatime=4, expand=True, line_space=400)
        texts = [
            'Welcome to the Sky-Hero!',
            'Before you start playing this\n game, you need to complete',
            'basic training on player control mechanics.',
            'I wish you a pleasant game.\n Let\'s get started!'
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_1.addWidget(self.widget_1)
        self.layout_1.dispose()

        # layout 2
        self.layout_2 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_2.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            'First of all, let\'s study the\n basics of movement.',
            'To make the character move, \nyou need to press the arrow\n keys: Left nd Right'
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_2 = GradualStoryWidget(self.layout_2, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_2.addWidget(self.widget_2)
        self.layout_2.dispose()


        # layout 3
        self.layout_3 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_3.setSize(self.screen.get_width(), self.screen.get_height())
        self.blinkin_label_3 = BlinkingLabel(self.layout_3, "Press <-- and --> to move".replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK, blinktime=30)
        self.blinkin_label_3.finished = False
        self.layout_3.addWidget(self.blinkin_label_3)
        self.layout_3.dispose()

        # layout 4
        self.layout_4 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_4.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_4 = Label(self.layout_4, 'Excellent!'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK)
        self.widget_4.finished = True
        self.layout_4.addWidget(self.widget_4)
        self.layout_4.dispose()


        # layout 5
        self.layout_5 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_5.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "The next step is to learn how to jump.",
            "There will be many obstacles\n in the game, and you need\n to be able to jump.",
            "To jump, press the `Space` key.",
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_5 = GradualStoryWidget(self.layout_5, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_5.addWidget(self.widget_5)
        self.layout_5.dispose()

        # layout 6
        self.layout_6 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_6.setSize(self.screen.get_width(), self.screen.get_height())
        self.blinkin_label_6 = BlinkingLabel(self.layout_6, "Press `Space` to jump".replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK, blinktime=30)
        self.blinkin_label_6.finished = False
        self.layout_6.addWidget(self.blinkin_label_6)
        self.layout_6.dispose()

        # layout 7
        self.layout_7 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_7.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_7 = Label(self.layout_7, 'Perfect!'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK)
        self.widget_7.finished = True
        self.layout_7.addWidget(self.widget_7)
        self.layout_7.dispose()

        self.layouts = [self.layout_2, self.layout_3, self.layout_4, self.layout_5, self.layout_6, self.layout_7]
        self.widgets = [self.widget_2, self.blinkin_label_3, self.widget_4, self.widget_5, self.blinkin_label_6, self.widget_7]

        self.current_layout = self.layout_1
        self.current_widget = self.widget_1
        self.timer = 0
        self.delta_time = 120

        self.transition = 0

        # debug
#        self.timer = 0
#        self.step = 1
#        self.current_layout =self.layout_2
#        self.current_widget = self.widget_2
        
    def run(self):
        while True:
            self.app.clock.tick(60)
            self.app.display.fill((0, 0, 0, 0))

            self.app.map.update()
            self.app.map.render(self.app.display, self.app.display_2)
            
            if self.current_widget.finished:
                self.timer += 1
                if self.timer >= self.delta_time:
                    self.timer = 0
                    self.step += 1
                    if self.step == 3:
                        self.delta_time = 60 * 5
                    else:
                        self.delta_time = 120
                    if self.step - 1 < len(self.layouts):
                        self.current_layout = self.layouts[self.step - 1]
                        self.current_widget = self.widgets[self.step - 1]

            self.current_layout.update(pygame.mouse.get_pos(), False)
            self.current_layout.render(self.app.display, opacity=255)

            self.app.main_player.update()
            self.app.main_player.render(self.app.display)
            
            self.app.map.move_camera(self.app.main_player.pos[0] - self.SCREEN_WIDTH // 2, self.app.main_player.pos[1] - self.SCREEN_HEIGHT // 2)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and self.step >= 2:
                    if event.key == pygame.K_LEFT:
                        self.app.main_player.move[0] = True
                        self.app.main_player.move[1] = False
                        self.app.main_player.flip = True
                        self.blinkin_label_3.finished = True
                    elif event.key == pygame.K_RIGHT and self.step >= 2:
                        self.app.main_player.move[1] = True
                        self.app.main_player.move[0] = False
                        self.app.main_player.flip = False
                        self.blinkin_label_3.finished = True
                    elif event.key == pygame.K_SPACE and self.step >= 5:
                        self.app.main_player.jump()
                        self.blinkin_label_6.finished = True
                    elif event.key == pygame.K_ESCAPE:
                        # self.running = False
                        self.app.menu_run()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and self.step >= 2:
                        self.app.main_player.move[0] = False
                    elif event.key == pygame.K_RIGHT and self.step >= 2:
                        self.app.main_player.move[1] = False

            if self.transition or (self.step > len(self.layouts)):
                surf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                surf.fill((0, 0, 0))
                coef = (self.SCREEN_WIDTH ** 2 + self.SCREEN_HEIGHT ** 2) ** .5 / 2 // 30 + 1
                pygame.draw.circle(surf, (255, 255, 255), (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2), coef * (30 - abs(self.transition)))
                surf.set_colorkey((255, 255, 255))
                self.app.display.blit(surf, (0, 0))
                self.transition += 1
                if self.transition > 30:
                    return

            display_mask = pygame.mask.from_surface(self.app.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
            for pos in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.app.display_2.blit(display_sillhouette, pos)
            self.app.display_2.blit(self.app.display, (0, 0))
            self.screen.blit(self.app.display_2, (0, 0))
            pygame.display.flip()



class Tour_2:
    def __init__(self, app, screen):
        app.__init__()
        self.app = app
        self.screen = screen
        self.SCREEN_WIDTH = self.screen.get_width()
        self.SCREEN_HEIGHT = self.screen.get_height()
        self.step = 0

        DELTA_TIME = 2
        self.transition = -30
        self.timer = 0
        self.delta_time = 120
        self.start_delay_time = 120
        self.destination_timer_2 = 30
        self.destination_timer_5 = 30

        # layout 1
        self.layout_1 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_1.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "Great, you've mastered simple movements.",
            "Now it's time for more complex motions.",
            "To start, jump to the island \non your right."            
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_1.addWidget(self.widget_1)
        self.layout_1.dispose()

        # layout 2
        self.layout_2 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_2.setSize(self.screen.get_width(), self.screen.get_height())
        self.blinkin_label_2 = BlinkingLabel(self.layout_2, "Jump to the island.".replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK, blinktime=40)
        self.blinkin_label_2.finished = False
        self.layout_2.addWidget(self.blinkin_label_2)
        self.layout_2.dispose()

        # layout 3
        self.layout_3 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_3.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_3 = Label(self.layout_3, 'Cool!'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK)
        self.widget_3.finished = True
        self.layout_3.addWidget(self.widget_3)
        self.layout_3.dispose()

        # layout 4
        self.layout_4 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_4.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "Now let's learn to bounce off walls.",
            "To do this, jump onto the wall and, at the moment of contact, press the Space key again."                        
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_4 = GradualStoryWidget(self.layout_4, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_4.addWidget(self.widget_4)
        self.layout_4.dispose()

        # layout 5
        self.layout_5 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_5.setSize(self.screen.get_width(), self.screen.get_height())
        self.blinkin_label_5 = BlinkingLabel(self.layout_5, "Climb onto the stone building.".replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK, blinktime=40)
        self.blinkin_label_5.finished = False
        self.layout_5.addWidget(self.blinkin_label_5)
        self.layout_5.dispose()

        # layout 6
        self.layout_6 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_6.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_6 = Label(self.layout_6, 'You are the best!'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK)
        self.widget_6.finished = True
        self.layout_6.addWidget(self.widget_6)
        self.layout_6.dispose()

        self.current_layout = self.layout_1
        self.current_widget = self.widget_1

        self.layouts = [self.layout_2, self.layout_3, self.layout_4, self.layout_5, self.layout_6]
        self.widgets = [self.blinkin_label_2, self.widget_3, self.widget_4, self.blinkin_label_5, self.widget_6]
        


    def run(self):
        while True:
            self.app.clock.tick(60)
            self.app.display.fill((0, 0, 0, 0))

            self.app.map.update()
            self.app.map.render(self.app.display, self.app.display_2)

            if self.current_widget.finished:
                self.timer += 1
                if self.timer >= self.delta_time:
                    self.timer = 0
                    self.step += 1
                    if self.step == 2:
                        self.delta_time = 60 * 5
                    elif self.step == 3:
                        self.delta_time = 60 * 8
                    elif self.step == 5:
                        self.delta_time = 60 * 5
                    else:
                        self.delta_time = 120
                    if self.step - 1 < len(self.layouts):
                        self.current_layout = self.layouts[self.step - 1]
                        self.current_widget = self.widgets[self.step - 1]

            self.start_delay_time = max(0, self.start_delay_time - 1)
            if self.start_delay_time == 0:
                self.current_layout.update(pygame.mouse.get_pos(), False)
                self.current_layout.render(self.app.display, opacity=255)

            if self.app.dead > 60:
                self.transition += 1

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

            if self.step == 1 and (
                self.app.main_player.pos[0] >= 481
                and (124 <= self.app.main_player.pos[1] <= 160)
            ):
                self.destination_timer_2 -= 1
            else:
                self.destination_timer_2 = 30
            
            if self.destination_timer_2 <= 0:
                self.blinkin_label_2.finished = True

            if self.step == 4 and self.app.main_player.pos[1] <= -323:
                self.destination_timer_5 -= 1
            else:
                self.destination_timer_5 = 30
            if self.destination_timer_5 <= 0:
                self.blinkin_label_5.finished = True


            self.app.map.move_camera(self.app.main_player.pos[0] - self.SCREEN_WIDTH // 2, self.app.main_player.pos[1] - self.SCREEN_HEIGHT // 2)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and self.step >= 1:
                    if event.key == pygame.K_LEFT:
                        self.app.main_player.move[0] = True
                        self.app.main_player.move[1] = False
                        self.app.main_player.flip = True
                    elif event.key == pygame.K_RIGHT and self.step >= 1:
                        self.app.main_player.move[1] = True
                        self.app.main_player.move[0] = False
                        self.app.main_player.flip = False
                    elif event.key == pygame.K_SPACE and self.step >= 1:
                        self.app.main_player.jump()
                    elif event.key == pygame.K_ESCAPE:
                        # self.running = False
                        self.app.menu_run()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and self.step >= 1:
                        self.app.main_player.move[0] = False
                    elif event.key == pygame.K_RIGHT and self.step >= 1:
                        self.app.main_player.move[1] = False

            if self.transition or (self.step > len(self.layouts)):
                surf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                surf.fill((0, 0, 0))
                coef = (self.SCREEN_WIDTH ** 2 + self.SCREEN_HEIGHT ** 2) ** .5 / 2 // 30 + 1
                pygame.draw.circle(surf, (255, 255, 255), (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2), coef * (30 - abs(self.transition)))
                surf.set_colorkey((255, 255, 255))
                self.app.display.blit(surf, (0, 0))
                if self.app.dead == 0:
                    self.transition += 1
                if self.transition > 30 and self.step > len(self.layouts):
                    return

            display_mask = pygame.mask.from_surface(self.app.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
            for pos in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.app.display_2.blit(display_sillhouette, pos)
            self.app.display_2.blit(self.app.display, (0, 0))
            self.screen.blit(self.app.display_2, (0, 0))
            pygame.display.flip()


class Tour_3:
    def __init__(self, app, screen):
        app.__init__()
        self.app = app
        self.screen = screen
        self.SCREEN_WIDTH = self.screen.get_width()
        self.SCREEN_HEIGHT = self.screen.get_height()
        self.step = 0

        DELTA_TIME = 2
        self.transition = -30
        self.timer = 0
        self.delta_time = 60 * 3
        self.start_delay_time = 120
        self.lock = True

        # layout 1
        self.layout_1 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_1.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "Now it's time to learn how to attack enemies.",
            "Enemies have weapons and\n know how to shoot. If they hit you, you’ll die.",
            "To attack an enemy,\n you need to get within",
            'a certain distance of them and press the "X" key.'           
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_1.addWidget(self.widget_1)
        self.layout_1.dispose()

        # layout 2
        self.layout_2 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_2.setSize(self.screen.get_width(), self.screen.get_height())
        self.blinkin_label_2 = BlinkingLabel(self.layout_2, 'Press the "X" key'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK, blinktime=40)
        self.blinkin_label_2.finished = False
        self.layout_2.addWidget(self.blinkin_label_2)
        self.layout_2.dispose()


        # layout 3
        self.layout_3 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_3.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "Now get close to the enemy\n and attack him",
            "Remember that enemies can\n shoot, be careful"
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_3 = GradualStoryWidget(self.layout_3, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_3.addWidget(self.widget_3)
        self.layout_3.dispose()

        # layout 4
        self.layout_4 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_4.setSize(self.screen.get_width(), self.screen.get_height())
        self.blinkin_label_4 = BlinkingLabel(self.layout_4, "Attack the enemy".replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK, blinktime=40)
        self.blinkin_label_4.finished = False
        self.layout_4.addWidget(self.blinkin_label_4)
        self.layout_4.dispose()        

        # layout 5
        self.layout_5 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_5.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_5 = Label(self.layout_5, 'Excellent attack!'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK)
        self.widget_5.finished = True
        self.layout_5.addWidget(self.widget_5)
        self.layout_5.dispose()

        self.current_layout = self.layout_1
        self.current_widget = self.widget_1

        self.layouts = [self.layout_2, self.layout_3, self.layout_4, self.layout_5]
        self.widgets = [self.blinkin_label_2, self.widget_3, self.blinkin_label_4, self.widget_5]


    def run(self):
        while True:
            self.app.clock.tick(60)
            self.app.display.fill((0, 0, 0, 0))

            self.app.map.update()
            self.app.map.render(self.app.display, self.app.display_2)

            if self.current_widget.finished:
                self.timer += 1
                if self.timer >= self.delta_time:
                    self.timer = 0
                    self.step += 1
                    if self.step == 2:
                        self.delta_time = 60 * 5
                    elif self.step == 3:
                        self.delta_time = 60
                    elif self.step == 5:
                        self.delta_time = 60 * 5
                    else:
                        self.delta_time = 120
                    if self.step - 1 < len(self.layouts):
                        self.current_layout = self.layouts[self.step - 1]
                        self.current_widget = self.widgets[self.step - 1]

            self.start_delay_time = max(0, self.start_delay_time - 1)
            if self.start_delay_time == 0:
                self.current_layout.update(pygame.mouse.get_pos(), False)
                self.current_layout.render(self.app.display, opacity=255)

            if self.app.dead > 60:
                self.transition += 1

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

            
            if len(self.app.enemies) == 0:
                if self.lock:
                    self.blinkin_label_4.finished = True
                else:
                    self.blinkin_label_2.finished = True

             # enemies
            fordel = []
            for enemy in self.app.enemies:
                if self.lock or (self.lock == False and self.step >= 1):
                    enemy.ai()
                if self.lock == False:
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
                if event.type == pygame.KEYDOWN and self.step >= 1:
                    if event.key == pygame.K_LEFT:
                        self.app.main_player.move[0] = True
                        self.app.main_player.move[1] = False
                        self.app.main_player.flip = True
                    elif event.key == pygame.K_RIGHT and self.step >= 1:
                        self.app.main_player.move[1] = True
                        self.app.main_player.move[0] = False
                        self.app.main_player.flip = False
                    elif event.key == pygame.K_SPACE and (self.step >= 3 or self.lock == False):
                        self.app.main_player.jump()
                    elif event.key == pygame.K_ESCAPE:
                        # self.running = False
                        self.app.menu_run()
                    elif event.key == pygame.K_x and self.step >= 1:
                        self.app.main_player.dash()
                        if self.lock:
                            self.blinkin_label_2.finished = True

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and self.step >= 1:
                        self.app.main_player.move[0] = False
                    elif event.key == pygame.K_RIGHT and self.step >= 1:
                        self.app.main_player.move[1] = False

            if self.transition or (self.step > len(self.layouts)):
                surf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                surf.fill((0, 0, 0))
                coef = (self.SCREEN_WIDTH ** 2 + self.SCREEN_HEIGHT ** 2) ** .5 / 2 // 30 + 1
                pygame.draw.circle(surf, (255, 255, 255), (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2), coef * (30 - abs(self.transition)))
                surf.set_colorkey((255, 255, 255))
                self.app.display.blit(surf, (0, 0))
                if self.app.dead == 0:
                    self.transition += 1
                if self.transition > 30 and self.step > len(self.layouts):
                    return

            display_mask = pygame.mask.from_surface(self.app.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
            for pos in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.app.display_2.blit(display_sillhouette, pos)
            self.app.display_2.blit(self.app.display, (0, 0))
            self.screen.blit(self.app.display_2, (0, 0))
            pygame.display.flip()



class Tour_4(Tour_3):
    def __init__(self, app, screen):
        app.__init__()
        self.app = app
        self.screen = screen
        self.SCREEN_WIDTH = self.screen.get_width()
        self.SCREEN_HEIGHT = self.screen.get_height()
        self.step = 0

        DELTA_TIME = 2
        self.transition = -30
        self.timer = 0
        self.delta_time = 60 * 3
        self.start_delay_time = 120
        self.lock = False

        # layout 1
        self.layout_1 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_1.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "Let’s do some training.",
            "If a bullet hits you,\n you will die.",
            "But you are invulnerable to\n bullets during an attack.",
            "So if an enemy shoots at you,\n don’t be afraid to\n strike back at that moment."
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_1.addWidget(self.widget_1)
        self.layout_1.dispose()


        # layout 2
        self.layout_2 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_2.setSize(self.screen.get_width(), self.screen.get_height())
        self.blinkin_label_2 = BlinkingLabel(self.layout_2, 'Kill the enemy'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK, blinktime=40)
        self.blinkin_label_2.finished = False
        self.layout_2.addWidget(self.blinkin_label_2)
        self.layout_2.dispose()

        self.current_layout = self.layout_1
        self.current_widget = self.widget_1

        self.layouts = [self.layout_2]
        self.widgets = [self.blinkin_label_2]




class Tour_5:
    def __init__(self, app, screen):
        app.__init__()
        self.app = app
        self.screen = screen
        self.SCREEN_WIDTH = self.screen.get_width()
        self.SCREEN_HEIGHT = self.screen.get_height()
        self.step = 0

        DELTA_TIME = 2
        self.transition = -30
        self.timer = 0
        self.delta_time = 60 * 3
        self.start_delay_time = 120
        self.border_timer = 0

        # layout 1
        self.layout_1 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_1.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "The main goal of the game is to kill all the enemies.",
            "In the top-left corner of \nthe screen, you can see \nhow many enemies",
            " are still alive on the map.\n"
            "Your aim is to kill them all.",
            "Once you’ve killed all the \nenemies, you’ll move on to\n the next level."
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_1.addWidget(self.widget_1)
        self.layout_1.dispose()

        # layout 2
        self.layout_2 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_2.setSize(self.screen.get_width(), self.screen.get_height())
        self.blinkin_label_2 = BlinkingLabel(self.layout_2, 'Kill all the enemies'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK, blinktime=40)
        self.blinkin_label_2.finished = False
        self.layout_2.addWidget(self.blinkin_label_2)
        self.layout_2.dispose()

        # layout 3
        self.layout_3 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_3.setSize(self.screen.get_width(), self.screen.get_height())
        self.widget_3 = Label(self.layout_3, 'That was awesome! 😎'.replace(' ', '  '), positions=['center', 'top'], font=pygame.font.Font('fonts/Pacifico.ttf', 60), color=BLACK)
        self.widget_3.finished = True
        self.layout_3.addWidget(self.widget_3)
        self.layout_3.dispose()

        # layout 4
        self.layout_4 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_4.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "The training for the game\n is complete.",
            "You are now ready to walk \nthis challenging path on \nyour own and defeat your \nenemies.",
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_4 = GradualStoryWidget(self.layout_4, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_4.addWidget(self.widget_4)
        self.layout_4.dispose()

        # layout 5
        self.layout_5 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_5.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            " " * 4 + "Good luck, warrior!"
        ]
        texts = [text.replace(' ', '  ') for text in texts]
        self.widget_5 = GradualStoryWidget(self.layout_5, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=DELTA_TIME, delay=120)
        self.layout_5.addWidget(self.widget_5)
        self.layout_5.dispose()


        self.current_layout = self.layout_1
        self.current_widget = self.widget_1

        self.layouts = [self.layout_2, self.layout_3, self.layout_4, self.layout_5]
        self.widgets = [self.blinkin_label_2, self.widget_3, self.widget_4, self.widget_5]


    def run(self):
        while True:
            self.app.clock.tick(60)
            self.app.display.fill((0, 0, 0, 0))

            self.app.map.update()
            self.app.map.render(self.app.display, self.app.display_2)

            if self.current_widget.finished:
                self.timer += 1
                if self.timer >= self.delta_time:
                    self.timer = 0
                    self.step += 1
                    if self.step == 2:
                        self.delta_time = 60 * 5
                    elif self.step == 3:
                        self.delta_time = 60
                    elif self.step == 5:
                        self.delta_time = 60 * 5
                    else:
                        self.delta_time = 120
                    if self.step - 1 < len(self.layouts):
                        self.current_layout = self.layouts[self.step - 1]
                        self.current_widget = self.widgets[self.step - 1]

            self.start_delay_time = max(0, self.start_delay_time - 1)
            if self.start_delay_time == 0:
                self.current_layout.update(pygame.mouse.get_pos(), False)
                self.current_layout.render(self.app.display, opacity=255)

            if self.app.dead > 60:
                self.transition += 1

            self.border_timer += 1
            if self.border_timer > 60 * 7 and self.border_timer < 60 * 15:
                n = len(self.app.enemies)
                w = self.app.small_enemy_img.get_width()
                h = self.app.small_enemy_img.get_height()
                pygame.draw.rect(self.app.display, (255, 0, 0), (0, 0, 5 + 2 * n * w + 5, 5 + h + 5), width=2)
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

            
            if len(self.app.enemies) == 0:
                self.blinkin_label_2.finished = True

             # enemies
            fordel = []
            for enemy in self.app.enemies:
                enemy.ai()
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
                if event.type == pygame.KEYDOWN and self.step >= 1:
                    if event.key == pygame.K_LEFT:
                        self.app.main_player.move[0] = True
                        self.app.main_player.move[1] = False
                        self.app.main_player.flip = True
                    elif event.key == pygame.K_RIGHT and self.step >= 1:
                        self.app.main_player.move[1] = True
                        self.app.main_player.move[0] = False
                        self.app.main_player.flip = False
                    elif event.key == pygame.K_SPACE and self.step >= 1:
                        self.app.main_player.jump()
                    elif event.key == pygame.K_ESCAPE:
                        self.app.menu_run()
                    elif event.key == pygame.K_x and self.step >= 1:
                        self.app.main_player.dash()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and self.step >= 1:
                        self.app.main_player.move[0] = False
                    elif event.key == pygame.K_RIGHT and self.step >= 1:
                        self.app.main_player.move[1] = False

            if self.transition or (self.step > len(self.layouts)):
                surf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                surf.fill((0, 0, 0))
                coef = (self.SCREEN_WIDTH ** 2 + self.SCREEN_HEIGHT ** 2) ** .5 / 2 // 30 + 1
                pygame.draw.circle(surf, (255, 255, 255), (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2), coef * (30 - abs(self.transition)))
                surf.set_colorkey((255, 255, 255))
                self.app.display.blit(surf, (0, 0))
                if self.app.dead == 0:
                    self.transition += 1
                if self.transition > 30 and self.step > len(self.layouts):
                    return

            display_mask = pygame.mask.from_surface(self.app.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
            for pos in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.app.display_2.blit(display_sillhouette, pos)
            self.app.display_2.blit(self.app.display, (0, 0))
            self.screen.blit(self.app.display_2, (0, 0))
            pygame.display.flip()

'''

        # layout 6
        self.layout_6 = VerticalLayout(None, paddings=[0] * 4, space=0)
        self.layout_6.setSize(self.screen.get_width(), self.screen.get_height())
        texts = [
            "The training for the game is now complete.",
            "You are now ready to walk this challenging path on your own and defeat your enemies.",
            "Good luck, warrior!"
        ]

'''