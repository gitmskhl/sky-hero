import pygame
import random

if __name__ == "__main__":
    from widgets import *
else:
    from scripts.widgets import *

class StartMenu(VerticalLayout):
    def __init__(self, pages: Pages, size):
        self.pages = pages
        root = pages.ml
        padding = size[0] // 4
        super().__init__(root, paddings=[50, padding, 50, padding], space=10)
        br = 40
        self.play_button = Button(root, text='Play', border_radius=br)
        self.new_game_button = Button(root, text='New Game', border_radius=br)
        self.settings_button = Button(root, text='Settings', border_radius=br)
        self.exit_button = Button(root, text='Exit', border_radius=br)
        self.addWidget(self.play_button)
        self.addWidget(self.new_game_button)
        self.addWidget(self.settings_button)
        self.addWidget(self.exit_button)
    
    def update(self, mouse_pos, clicked):
        if not self.showed: return
        super().update(mouse_pos, clicked)
        if self.settings_button.clicked:
            self.pages.setPage(1)


class SettingsMenu(VerticalLayout):
    def __init__(self, pages, size):
        self.pages = pages
        root = pages.ml
        padding = size[0] // 4
        super().__init__(root, paddings=[50, padding, 50, padding], space=10)
        br = 40
        
        # background sound
        self.volume_layout = VerticalLayout(root, paddings=[0] * 4, space=0)
        volume_label = Label(root, "Background sound", positions=['left', 'bottom'], fontsize=40)
        self.volume_slider = Slider(root, size[0] // 2, 10, positions=['center', 'top'], border_radius=10)
        self.volume_layout.addWidget(volume_label)
        self.volume_layout.addWidget(self.volume_slider)        

        # effects sounds
        self.effect_volume_layout = VerticalLayout(root, paddings=[0] * 4, space=0)
        volume_label = Label(root, "Sound effects", positions=['left', 'bottom'], fontsize=40)
        self.effect_volume_slider = Slider(root, size[0] // 2, 10, positions=['center', 'top'], border_radius=10)
        self.effect_volume_layout.addWidget(volume_label)
        self.effect_volume_layout.addWidget(self.effect_volume_slider)

        self.advanced_sound_button = Button(root, text='Advanced', border_radius=br)
        self.back_button = Button(root, text='Back', border_radius=br)
        self.addWidget(self.effect_volume_layout)
        self.addWidget(self.volume_layout)
        self.addWidget(self.advanced_sound_button)
        self.addWidget(self.back_button)
    

    def update(self, mouse_pos, clicked):
        if not self.showed: return
        super().update(mouse_pos, clicked)
        if self.back_button.clicked:
            self.pages.setPage(0)

class MainMenu(Pages):
    def __init__(self, size):
        super().__init__(size)
        st = StartMenu(self, self.ml, size)
        set = SettingsMenu(self, self.ml, size)
        self.addLayouts([st, set])


if __name__ == "__main__":
    screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
    clock = pygame.time.Clock()

    main = MainMenu((800, 600))

    while True:
        clock.tick(60)
        screen.fill((0, 0, 0))
        mouse_pos = pygame.mouse.get_pos()
        main.update(mouse_pos, False)
        main.render(screen)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                main.update(mouse_pos, True)


        pygame.display.update()