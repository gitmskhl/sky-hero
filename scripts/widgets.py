import pygame

pygame.init()

GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
MAGENTA = (255, 0, 255)

class Widget:
    def __init__(self, root):
        self.showed = True
        self.callback = None
    
    def connect(self, callback):
        self.callback = callback

    def show(self):
        self.showed = True
        if self.root:
            self.root.dispose()
    
    def hide(self):
        self.showed = False
        if self.root:
            self.root.dispose()

    def dispose(self):
        raise NotImplementedError
    
class FloatWidget(Widget):
    def __init__(self, root, innerRect, positions=None):
        super().__init__(root)
        self.innerRect = innerRect
        self.dx, self.dy = self.innerRect.topleft
        self.positions = list(positions) if positions else None
    
    def _dispose_positions(self):
        if self.positions[0] == 'left':
            self.innerRect.left =  self.rect.left
        elif self.positions[0] == 'center':
            self.innerRect.centerx=  self.rect.centerx
        else:
            self.innerRect.right = self.rect.right
        if self.positions[1] == 'top':
            self.innerRect.top = self.rect.top
        elif self.positions[1] == 'center':
            self.innerRect.centery = self.rect.centery
        else:
            self.innerRect.bottom = self.rect.bottom

    def dispose(self):
        if self.positions:
            self._dispose_positions()
        else:
            self.innerRect.topleft = (self.rect.x + self.dx, self.rect.y + self.dy)

class Button(Widget):
    defaultColors = [BLACK, YELLOW]
    defaultTextColors = [WHITE, BLACK] 
    def __init__(self, root, text, x=0, y=0, w=0, h=0, colors=None, textColors=None, fontsize=60, font=None, border_radius=-1):
        '''
            colors / textColors = [defaultColor, hoverColor]
        '''
        super().__init__(root)
        self.root = root
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font if font else pygame.font.Font('fonts/Amatic-Bold.ttf', fontsize)
        self.colors = colors if colors else Button.defaultColors
        self.textColors = textColors if textColors else Button.defaultTextColors
        self.color = self.colors[0]
        self.text_color = self.textColors[0]
        self.border_radius = border_radius
        self.text = text
        self.clicked = False

    def render(self, surf, opacity=None):
        if not self.showed: return
        text_color = self.text_color
        color = self.color
        if opacity:
            text_color = list(self.text_color) + [opacity]
            color = list(self.color) + [opacity]
        text = self.font.render(self.text, True, text_color)
        pygame.draw.rect(surf, color, self.rect, border_radius=self.border_radius)
        surf.blit(text, (self.rect.centerx - text.get_width() // 2, self.rect.centery - text.get_height()//2))

    def update(self, mouse_pos, clicked):
        self.clicked = False
        if not self.showed: return
        if self.rect.collidepoint(mouse_pos):
            self.color = self.colors[1]
            self.text_color = self.textColors[1]
            self.border_width = 0
            self.clicked = clicked
            if clicked and self.callback:
                self.callback()
        else:
            self.color = self.colors[0]
            self.text_color = self.textColors[0]
            self.border_width = 2
            return False

    def dispose(self):
        pass


class Layout(Widget):
    def __init__(self, root, paddings, space):
        '''
            paddings = [Up, Right, Down, Left]
        '''
        super().__init__(root)
        self.root = root
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.widgets = []
        self.paddings = list(paddings)
        self.space = space
    
    def setSize(self, width, height):
        self.rect.width = width
        self.rect.height = height

    def addWidget(self, widget):
        self.widgets.append(widget)

    def update(self, mouse_pos, clicked):
        if not self.showed: return
        for widget in self.widgets:
            widget.update(mouse_pos, clicked)
    
    def render(self, surf, opacity=None):
        if not self.showed: return
        for widget in self.widgets:
            widget.render(surf, opacity)


class VerticalLayout(Layout):
    def __init__(self, root, paddings=[0] * 4, space=0):
        super().__init__(root, paddings, space)

    def dispose(self):
        n = len([widget for widget in self.widgets if widget.showed])
        if not self.showed or n == 0: return
        h = (self.rect.height - self.paddings[0] - self.paddings[2] - self.space * (n - 1)) / n
        w = self.rect.width - self.paddings[1] - self.paddings[3]
        x = self.rect.x + self.paddings[3]
        y = self.rect.y + self.paddings[0]
        for widget in self.widgets:
            if not widget.showed: continue
            widget.rect.topleft = (x, y)
            widget.rect.width = w
            widget.rect.height = h
            y += h + self.space
        for widget in self.widgets:
            widget.dispose()


class HorizontalLayout(Layout):
    def __init__(self, root, paddings=[0] * 4, space=0):
        super().__init__(root, paddings, space)

    def dispose(self):
        n = len([widget for widget in self.widgets if widget.showed])
        if not self.showed or n == 0: return
        w = (self.rect.width - self.paddings[3] - self.paddings[1] - self.space * (n - 1)) / n
        h = self.rect.height - self.paddings[0] - self.paddings[2]
        x = self.rect.x + self.paddings[3]
        y = self.rect.y + self.paddings[0]
        for widget in self.widgets:
            if not widget.showed: continue
            widget.rect.topleft = (x, y)
            widget.rect.width = w
            widget.rect.height = h
            x += w + self.space
        for widget in self.widgets:
            widget.dispose()

class CheckBox(FloatWidget):
    defaultActiveColor = ORANGE
    defaultBorderColors = [WHITE, BLUE]
    def __init__(self, root, w, h, dx=0, dy=0, positions=['left', 'top'], borderColors=None, activeColor=None):
        super().__init__(root, pygame.Rect(dx, dy, w, h), positions)
        self.root = root
        self.w = w
        self.h = h
        self.borderColors = borderColors if borderColors else CheckBox.defaultBorderColors
        self.borderColor = self.borderColors[0]
        self.activeColor = activeColor if activeColor else CheckBox.defaultActiveColor
        self.activated = False
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.innerRect = pygame.Rect(0, 0, w, h)
    
    def update(self, mouse_pos, clicked):
        if not self.showed: return
        if self.innerRect.collidepoint(mouse_pos):
            if clicked:
                self.activated = not self.activated
            self.borderColor = self.borderColors[1]
        else:
            self.borderColor = self.borderColors[0]

    def render(self, surf, opacity=None):
        if not self.showed: return
        borderColor = self.borderColor
        activeColor = self.activeColor
        if opacity is not None:
            borderColor = list(borderColor) + [opacity]
            activeColor = list(activeColor) + [opacity]
        if self.activated:
            pygame.draw.rect(surf, activeColor, self.innerRect)
        else:
            pygame.draw.rect(surf, borderColor, self.innerRect, 2)

class Slider(FloatWidget):
    defaultSliderColors = [GRAY, MAGENTA]
    defaultHandleColor = WHITE
    def __init__(self, root, w, h, dx=0, dy=0, positions=['left', 'center'], r=8, border_radius=-1):
        super().__init__(root, pygame.Rect(dx, dy, w, h), positions)
        self.w = w
        self.h = h
        self.r = r
        self.border_radius = border_radius
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.innerRect = pygame.Rect(0, 0, w, h)
        self.value = 0
        self.drag = False

    def setValue(self, value):
        self.value = value

    def update(self, mouse_pos, clicked):
        if not self.showed: return
        
        if self.innerRect.collidepoint(mouse_pos) and clicked:
            self.value = (mouse_pos[0] - self.innerRect.left) / self.innerRect.width * 100
            self.drag = True
            return
        if self.drag and not pygame.mouse.get_pressed()[0]:
            self.drag = False
        if self.drag:
            self.value = (mouse_pos[0] - self.innerRect.left) / self.innerRect.width * 100
            self.value = min(100, self.value)
            self.value = max(0, self.value)
            if self.callback:
                self.callback()

    def render(self, surf, opacity=None):
        if not self.showed: return

        sliderColor, activeColor = Slider.defaultSliderColors
        handleColor = Slider.defaultHandleColor
        if opacity is not None:
            sliderColor = list(sliderColor) + [opacity]
            handleColor = list(handleColor) + [opacity]
        pygame.draw.rect(surf, sliderColor, self.innerRect, border_radius=self.border_radius)
        pygame.draw.rect(
            surf,
            activeColor,
            (
                *self.innerRect.topleft,
                self.innerRect.width * self.value / 100,
                self.innerRect.height
            ),
            border_radius=self.border_radius
        )
        pygame.draw.circle(
            surf,
            handleColor,
            (
                self.innerRect.x + self.value * self.innerRect.width / 100,
                self.innerRect.centery
            ),
            self.r
        )

class Label(FloatWidget):
    def __init__(self, root, text, dx=0, dy=0, positions=None, fontsize=50, font=None, color=BLACK):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.font = font if font else pygame.font.Font('fonts/Pacifico.ttf', fontsize)
        self.rendered_text = self.font.render(text, True, color)
        super().__init__(root, pygame.Rect(dx, dy, *self.rendered_text.get_size()), positions)
    
    def update(self, mouse_pos, clicked): pass

    def render(self, surf, opacity=None):
        surf.blit(self.rendered_text, self.innerRect.topleft)


class Pages:
    def __init__(self, size):
        self.ml = VerticalLayout(None)
        self.ml.setSize(*size)
        self.layouts = []
        self.current_layout = None
        self.actions = []

    def addLayouts(self, layouts):
        self.layouts.extend(layouts)
        for l in layouts: 
            l.hide()
            l.root = self.ml
            self.ml.addWidget(l)
        if self.current_layout is None:
            self.current_layout = self.layouts[0]
            self.current_layout.show()

    def _setPage(self, idx):
        self.current_layout.hide()
        self.current_layout = self.layouts[idx]
        self.current_layout.show()
    
    def setPage(self, idx):
        self.actions.append(lambda: self._setPage(idx))

    def update(self, mouse_pos, clicked):
        self.ml.update(mouse_pos, clicked)
        for action in self.actions:
            action()
        self.actions = []
    
    def render(self, surf, opacity=None):
        self.ml.render(surf, opacity)

    def dispose(self):
        self.ml.dispose()