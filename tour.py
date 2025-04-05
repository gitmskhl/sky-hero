import pygame
from scripts.widgets import *
pygame.init()

BLACK = (0, 0, 0)

class Tour_1:
    def __init__(self, app, screen):
        self.app = app
        self.screen = screen
        self.SCREEN_WIDTH = self.screen.get_width()
        self.SCREEN_HEIGHT = self.screen.get_height()
        self.step = 0
        
        DELTA_TIME = 1#6

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


        self.layouts = [self.layout_2, self.layout_3, self.layout_4]
        self.wigdets = [self.widget_2, self.blinkin_label_3, self.widget_4]

        self.current_layout = self.layout_1
        self.current_widget = self.widget_1
        self.timer = 0
        self.delta_time = 120

        # debug
        self.timer = 0
        self.step = 1
        self.current_layout =self.layout_2
        self.current_widget = self.widget_2
        
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
                    self.current_layout = self.layouts[self.step - 1]
                    self.current_widget = self.wigdets[self.step - 1]

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
                        self.current_widget.finished = True
                    elif event.key == pygame.K_RIGHT and self.step >= 2:
                        self.app.main_player.move[1] = True
                        self.app.main_player.move[0] = False
                        self.app.main_player.flip = False
                        self.current_widget.finished = True
                    elif event.key == pygame.K_ESCAPE:
                        # self.running = False
                        self.app.menu_run()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and self.step >= 2:
                        self.app.main_player.move[0] = False
                    elif event.key == pygame.K_RIGHT and self.step >= 2:
                        self.app.main_player.move[1] = False

            display_mask = pygame.mask.from_surface(self.app.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
            for pos in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.app.display_2.blit(display_sillhouette, pos)
            # self.app.display_2.blit(display_sillhouette, (0, 0))
            self.app.display_2.blit(self.app.display, (0, 0))
            self.screen.blit(self.app.display_2, (0, 0))
            pygame.display.flip()