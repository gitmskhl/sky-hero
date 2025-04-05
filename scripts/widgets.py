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

    def popWidget(self, dispose_required=True):
        self.widgets.pop()
        if dispose_required:
            self.dispose()

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
    def __init__(self, root, text, dx=0, dy=0, positions=None, fontsize=50, font=None, color=BLACK, size=None):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.font = font if font else pygame.font.Font('fonts/Pacifico.ttf', fontsize)
        self.rendered_text = self.font.render(text, True, color)
        size = size if size else self.rendered_text.get_size()
        super().__init__(root, pygame.Rect(dx, dy, *size), positions)
    
    def update(self, mouse_pos, clicked): pass

    def render(self, surf, opacity=None):
        surf.blit(self.rendered_text, self.innerRect.topleft)

class BlinkingLabel(Label):
    def __init__(self, root, text, dx=0, dy=0, positions=None, fontsize=50, font=None, color=BLACK, blinktime=50):
        super().__init__(root, text, dx, dy, positions, fontsize, font, color)
        self.blinking = True
        self.opacity = 255
        self.blinktime = blinktime
        self.timer = 0

    def update(self, mouse_pos, clicked):
        if not self.showed: return
        self.timer += 1
        if self.timer >= self.blinktime:
            self.timer = 0
            self.blinking = not self.blinking

    def render(self, surf):
        if not self.showed: return
        if self.blinking:
            super().render(surf, opacity=self.opacity)


class GradualLabel(Label):
    def __init__(self, root, text, dx=0, dy=0, paddings=[0] * 4, positions=None, fontsize=50, font=None, color=BLACK, deltatime=10, size=None, expand=False, line_space=None):
        size = size if size else (root.rect.size if expand else None)
        super().__init__(root, text, dx, dy, positions, fontsize, font, color, size)
        self.color = color
        self.dx = dx
        self.dy = dy
        self.positions = positions
        self.fontsize = fontsize
        self.font = font
        self.color = color

        self.rendered_text = self.font.render('', True, color)
        self.line_space = line_space if line_space else 0
        self.main_layout = VerticalLayout(root, paddings=paddings, space=0)
        self.last_label = Label(self.main_layout, '', dx=dx, dy=dy, positions=positions, fontsize=fontsize, font=self.font, color=self.color)
        self.main_layout.addWidget(self.last_label)
        self.start_index = 0

        self.origin_text = text
        self.deltatime = deltatime
        self.timer = 0
        self.current_idx = 0
        self.finished = False

    def dispose(self):
        self.main_layout.rect.width = self.rect.width
        self.main_layout.rect.height = self.rect.height
        n = len([widget for widget in self.main_layout.widgets if widget.showed])
        h = self.last_label.rendered_text.get_height()
        self.main_layout.space = self.line_space
        self.main_layout.paddings[2] = self.main_layout.rect.height - h * n - self.line_space * (n - 1)
        self.main_layout.dispose()

    def update(self, mouse_pos, clicked):
        if not self.showed or self.finished: return
        if self.current_idx == len(self.origin_text): 
            self.finished = True
            return
        self.timer += 1
        if self.timer == self.deltatime:
            self.timer = 0
            self.current_idx += 1
            self.rendered_text = self.font.render(self.origin_text[self.start_index:self.current_idx + 1], True, self.color)
            if self.rendered_text.get_width() > self.innerRect.width or (self.current_idx < len(self.origin_text) and self.origin_text[self.current_idx] == '\n'):
                self.main_layout.addWidget(self.last_label)
                self.start_index = self.current_idx
            else:
                self.main_layout.popWidget(dispose_required=False)
                self.last_label = Label(self.main_layout, self.origin_text[self.start_index:self.current_idx + 1], self.dx, self.dy, self.positions, self.fontsize, self.font, self.color)
                self.main_layout.addWidget(self.last_label)
                self.dispose()

    def render(self, surf, opacity=None):
        if not self.showed: return
        self.main_layout.render(surf, opacity=opacity)


class GradualStoryWidget(FloatWidget):
    def __init__(self, root, texts, size, dx=0, dy=0, paddings=[0] * 4, positions=['left', 'top'], fontsize=60, font=None, color=BLACK, deltatime=10, delay=60, line_space=None):
        self.rect = pygame.Rect(0, 0, 0, 0)
        super().__init__(root, pygame.Rect(dx, dy, *size), positions)
        self.font = font if font else pygame.font.Font('fonts/Pacifico.ttf', fontsize)
        self.fontsize = fontsize
        self.color = color
        self.timer = 0
        self.delay = delay
        self.current_idx = 0
        self.glabels = [
            GradualLabel(root, text, paddings=paddings, positions=positions, fontsize=fontsize, font=self.font, color=self.color, deltatime=deltatime, size=size, expand=True, line_space=line_space)
            for text in texts
        ]
        self.pause = False
        self.finished = False
    

    def update(self, mouse_pos, clicked):
        if not self.showed or self.finished: return 
        if not self.pause:
            glabel = self.glabels[self.current_idx]
            glabel.update(mouse_pos, clicked)
            if glabel.finished:
                self.current_idx += 1
                if self.current_idx == len(self.glabels):
                    self.finished = True
                    return
                self.pause = True
                self.timer = 0
        else:
            self.timer += 1
            if self.timer == self.delay:
                self.pause = False
                self.timer = 0

    def render(self, surf, opacity=None):
        if not self.showed: return
        if not self.finished:
            if not self.pause:
                glabel = self.glabels[self.current_idx]
            else:
                glabel = self.glabels[self.current_idx - 1]
        else:
            glabel = self.glabels[-1]
        glabel.render(surf, opacity=opacity)



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