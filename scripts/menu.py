import pygame
import random

if __name__ == "__main__":
    from widgets import *
else:
    from scripts.widgets import *

class Menu(VerticalLayout):
    def __init__(self, pages, size, paddings=None, space=10):
        self.pages = pages
        self.root = root = pages.ml
        padding = size[0] // 4
        paddings = paddings if paddings else [50, padding, 50, padding]
        super().__init__(root, paddings=paddings, space=10)
        self.showed = False
        self.size = size

    def update(self, mouse_pos, clicked):
        if not self.showed: return
        super().update(mouse_pos, clicked)

class StartMenu(Menu):
    def __init__(self, pages: Pages, size):
        super().__init__(pages, size, paddings=[50, size[0] // 4, 50, size[0] // 4], space=10)
        br = 40
        self.play_button = Button(self.root, text='Play', border_radius=br)
        self.new_game_button = Button(self.root, text='New Game', border_radius=br)
        self.settings_button = Button(self.root, text='Settings', border_radius=br)
        self.settings_button.connect(lambda: pages.setPage(1))
        self.exit_button = Button(self.root, text='Exit', border_radius=br)
        self.addWidget(self.play_button)
        self.addWidget(self.new_game_button)
        self.addWidget(self.settings_button)
        self.addWidget(self.exit_button)
    

class SettingsMenu(Menu):
    def __init__(self, pages, size):
        super().__init__(pages, size)
        root = self.root
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
        self.back_button.connect(lambda: pages.setPage(0))
        self.advanced_sound_button.connect(lambda: pages.setPage(2))
        self.addWidget(self.effect_volume_layout)
        self.addWidget(self.volume_layout)
        self.addWidget(self.advanced_sound_button)
        self.addWidget(self.back_button)
 

class AdvancedSettingsMenu(Menu):
    def __init__(self, pages, size):
        super().__init__(pages, size, paddings=[50] * 4, space=10)
        root = self.root
        br = 40

        # jump sound
        self.jump_layout = VerticalLayout(root, paddings=[0] * 4, space=0)
        jump_label = Label(root, "Jump sound", positions=['left', 'bottom'], fontsize=40)
        self.jump_slider = Slider(root, size[0] // 2, 10, positions=['center', 'top'], border_radius=10)
        self.jump_layout.addWidget(jump_label)
        self.jump_layout.addWidget(self.jump_slider)

        # dash sound
        self.dash_layout = VerticalLayout(root, paddings=[0] * 4, space=0)
        dash_label = Label(root, "Dash sound", positions=['left', 'bottom'], fontsize=40)
        self.dash_slider = Slider(root, size[0] // 2, 10, positions=['center', 'top'], border_radius=10)
        self.dash_layout.addWidget(dash_label)
        self.dash_layout.addWidget(self.dash_slider)
        # hit sound
        self.hit_layout = VerticalLayout(root, paddings=[0] * 4, space=0)
        hit_label = Label(root, "Hit sound", positions=['left', 'bottom'], fontsize=40)
        self.hit_slider = Slider(root, size[0] // 2, 10, positions=['center', 'top'], border_radius=10)
        self.hit_layout.addWidget(hit_label)
        self.hit_layout.addWidget(self.hit_slider)

        # shoot sound
        self.shoot_layout = VerticalLayout(root, paddings=[0] * 4, space=0)
        shoot_label = Label(root, "Shoot sound", positions=['left', 'bottom'], fontsize=40)
        self.shoot_slider = Slider(root, size[0] // 2, 10, positions=['center', 'top'], border_radius=10)
        self.shoot_layout.addWidget(shoot_label)
        self.shoot_layout.addWidget(self.shoot_slider)
        # ambience sound
        self.ambience_layout = VerticalLayout(root, paddings=[0] * 4, space=0)
        ambience_label = Label(root, "Ambience sound", positions=['left', 'bottom'], fontsize=40)
        self.ambience_slider = Slider(root, size[0] // 2, 10, positions=['center', 'top'], border_radius=10)
        self.ambience_layout.addWidget(ambience_label)
        self.ambience_layout.addWidget(self.ambience_slider)
 
        # add all layouts
        self.addWidget(self.ambience_layout)
        self.addWidget(self.jump_layout)
        self.addWidget(self.dash_layout)
        self.addWidget(self.hit_layout)
        self.addWidget(self.shoot_layout)
        self.back_button = Button(root, text='Back', border_radius=br)
        self.back_button.connect(lambda: pages.setPage(1))
        self.addWidget(self.back_button)


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