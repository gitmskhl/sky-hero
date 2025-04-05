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
        self.label_1 = GradualStoryWidget(self.layout_1, texts, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), paddings=[0, 20, 0, 20], positions=['left', 'top'], fontsize=58, deltatime=6, delay=120)
        self.layout_1.addWidget(self.label_1)
        self.layout_1.dispose()
        
    def run(self):
        while True:
            self.app.clock.tick(60)
            self.app.display.fill((0, 0, 0, 0))

            self.app.map.update()
            self.app.map.render(self.app.display, self.app.display_2)

            self.layout_1.update(pygame.mouse.get_pos(), False)
            self.layout_1.render(self.app.display, opacity=255)

            self.app.main_player.update()
            self.app.main_player.render(self.app.display)
            
            self.app.map.move_camera(self.app.main_player.pos[0] - self.SCREEN_WIDTH // 2, self.app.main_player.pos[1] - self.SCREEN_HEIGHT // 2)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.app.main_player.move[0] = True
                        self.app.main_player.move[1] = False
                        self.app.main_player.flip = True
                    elif event.key == pygame.K_RIGHT:
                        self.app.main_player.move[1] = True
                        self.app.main_player.move[0] = False
                        self.app.main_player.flip = False
                    elif event.key == pygame.K_ESCAPE:
                        # self.running = False
                        self.app.menu_run()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.app.main_player.move[0] = False
                    elif event.key == pygame.K_RIGHT:
                        self.app.main_player.move[1] = False

            display_mask = pygame.mask.from_surface(self.app.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
            for pos in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.app.display_2.blit(display_sillhouette, pos)
            # self.app.display_2.blit(display_sillhouette, (0, 0))
            self.app.display_2.blit(self.app.display, (0, 0))
            self.screen.blit(self.app.display_2, (0, 0))
            pygame.display.flip()