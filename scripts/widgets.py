import pygame

from .custom_map_widget import State

pygame.init()

GRAY = (100, 100, 100)
DARK_GRAY = (150, 150, 150)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
MAGENTA = (255, 0, 255)

NUM_HOVERED = 0

class Widget:
    def __init__(self, root, fixedSizes: list[bool]=None):
        self.root = root
        self.fixedSizes = fixedSizes
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
    def __init__(self, root, innerRect, positions=None, fixedSizes=(False, False)):
        super().__init__(root, fixedSizes)
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
    def __init__(self, root, text, x=0, y=0, w=0, h=0, colors=None, textColors=None, fontsize='auto', font=None, border_radius=-1, fixedSizes=(False, False)):
        '''
            colors / textColors = [defaultColor, hoverColor]
        '''
        super().__init__(root, fixedSizes)
        self.root = root
        self.rect = pygame.Rect(x, y, w, h)
        self.dynamic_fontsize = False
        if fontsize == 'auto':
            fontsize = 60
            self.dynamic_fontsize = True
        self.font = font if font else pygame.font.Font('fonts/Amatic-Bold.ttf', fontsize)
        
        self.colors = colors if colors else Button.defaultColors
        self.textColors = textColors if textColors else Button.defaultTextColors
        self.color = self.colors[0]
        self.text_color = self.textColors[0]
        self.border_radius = border_radius
        self.text = text
        self.clicked = False
        self.hovered = False

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
        global NUM_HOVERED
        self.clicked = False
        self.hovered = False
        if not self.showed: return
        if self.rect.collidepoint(mouse_pos):
            NUM_HOVERED += 1
            self.color = self.colors[1]
            self.text_color = self.textColors[1]
            self.border_width = 0
            self.clicked = clicked
            self.hovered = True
            if clicked and self.callback:
                self.callback()
        else:
            self.color = self.colors[0]
            self.text_color = self.textColors[0]
            self.border_width = 2
            return False
        
    def setHover(self):
        if not self.showed: return
        self.color = self.colors[1]
        self.text_color = self.textColors[1]
        self.border_width = 0
        self.hovered = True

    def dispose(self):
        if self.dynamic_fontsize:
            fontsize = int(self.rect.height / 1.2)
            self.font = pygame.font.Font('fonts/Amatic-Bold.ttf', fontsize)

class FloatButton(FloatWidget):
    def __init__(self, root, text, w, h, dx=0, dy=0, positions=None, colors=None, textColors=None, fontsize='auto', font=None, border_radius=-1, fixedSizes=(False, False)):
        super().__init__(root, pygame.Rect(dx, dy, w, h), positions, fixedSizes)
        self.button = Button(self, text, x=0, y=0, w=w, h=h, colors=colors, textColors=textColors, fontsize=fontsize, font=font, border_radius=border_radius)
        self.rect = pygame.Rect(0, 0, w, h)

    def update(self, mouse_pos, clicked):
        self.button.update(mouse_pos, clicked)

    def __getattr__(self, attrname):
        self.button.showed = self.showed
        if hasattr(self.button, attrname):
            return getattr(self.button, attrname)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attrname}'")

    def dispose(self):
        if not self.showed: return
        super().dispose()
        self.button.rect = self.innerRect
        self.button.callback = self.callback
    
class ArrowButton(FloatButton):
    def __init__(self, root, isRightArrow, w, h, dx=0, dy=0, positions=None, colors=None, textColors=None, fontsize='auto', font=None, border_radius=-1, fixedSizes=(False, False)):
        super().__init__(root, '>' if isRightArrow else '<', positions=positions, dx=dx, dy=dy, w=w, h=h, colors=colors, textColors=textColors, fontsize=fontsize, font=font, border_radius=border_radius, fixedSizes=fixedSizes)


class Layout(Widget):
    def __init__(self, root, paddings, space, fixedSizes=(False, False), w=0, h=0):
        '''
            paddings = [Up, Right, Down, Left]
        '''
        super().__init__(root, fixedSizes)
        self.root = root
        self.rect = pygame.Rect(0, 0, w, h)
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
    def __init__(self, root, paddings=[0] * 4, space=0, fixedSizes=(False, False), w=0, h=0):
        super().__init__(root, paddings, space, fixedSizes, w, h)

    def dispose(self):
        if not self.showed: return
        FSH = sum([widget.rect.height for widget in self.widgets if widget.showed and widget.fixedSizes[1]])
        n = len([1 for widget in self.widgets if widget.showed and not widget.fixedSizes[1]])
        n_showed = len([1 for widget in self.widgets if widget.showed])
        h = 0
        if n > 0:
            h = (self.rect.height - self.paddings[0] - self.paddings[2] - FSH - self.space * (n_showed - 1)) / n
        w = self.rect.width - self.paddings[1] - self.paddings[3]
        x = self.rect.x + self.paddings[3]
        y = self.rect.y + self.paddings[0]
        for widget in self.widgets:
            if not widget.showed: continue
            widget.rect.topleft = (x, y)
            if not widget.fixedSizes[0]:
                widget.rect.width = w
            if not widget.fixedSizes[1]:
                widget.rect.height = h
            y += widget.rect.height + self.space
        for widget in self.widgets:
            widget.dispose()



class HorizontalLayout(Layout):
    def __init__(self, root, paddings=[0] * 4, space=0, fixedSizes=(False, False), w=0, h=0):
        super().__init__(root, paddings, space, fixedSizes, w, h)

    def dispose(self):
        if not self.showed: return
        FSW = sum([widget.rect.width for widget in self.widgets if widget.showed and widget.fixedSizes[0]])
        n = len([1 for widget in self.widgets if widget.showed and not widget.fixedSizes[0]])
        n_showed = len([1 for widget in self.widgets if widget.showed])
        w = 0
        if n > 0:
            w = (self.rect.width - self.paddings[3] - self.paddings[1] - FSW - self.space * (n_showed - 1)) / n
        h = self.rect.height - self.paddings[0] - self.paddings[2]
        x = self.rect.x + self.paddings[3]
        y = self.rect.y + self.paddings[0]
        for widget in self.widgets:
            if not widget.showed: continue
            widget.rect.topleft = (x, y)
            if not widget.fixedSizes[0]:
                widget.rect.width = w
            if not widget.fixedSizes[1]:
                widget.rect.height = h
            x += widget.rect.width + self.space
        for widget in self.widgets:
            widget.dispose()

class GridLayout(Widget):
    def __init__(self, root, paddings=[0] * 4, dims=(0, 0), vspace=0, hspace=0, fixedSizes=(False, False)):
        super().__init__(root, fixedSizes)
        self.root = root
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.paddings = list(paddings)

        self.grid = [[None] * dims[1] for _ in range(dims[0])]
        self.dims = list(dims)
        self.vspace = vspace
        self.hspace = hspace
    
    def isFull(self):
        for row in self.grid:
            for widget in row:
                if widget is None:
                    return False
        return True

    def addWidgetFreeCell(self, widget):
        for i in range(self.dims[0]):
            for j in range(self.dims[1]):
                if self.grid[i][j] is None:
                    self.grid[i][j] = widget
                    return True
        return False

    def addWidget(self, widget, i, j):
        '''
        i from 1 to dims[0]
        j from 1 to dims[1]
        '''
        if i <= 0 or j <= 0:
            raise 'Position elements must be positive. Got: %s' % (i, j)
        if i > self.dims[0] or j > self.dims[1]:
            raise 'There is no such row: dims=%s but you want to place it here: %s' % (self.dims, (i, j))
        self.grid[i - 1][j - 1] = widget
    
    def newRow(self):
        self.grid.append([None] * self.dims[1])
    
    def newColumn(self):
        for row in self.grid:
            row.append(None)
    
    def update(self, mouse_pos, clicked):
        if not self.showed: return
        for row in self.grid:
            for widget in row:
                if widget:
                    widget.update(mouse_pos, clicked)
    
    def render(self, surf, opacity=None):
        if not self.showed: return
        for row in self.grid:
            for widget in row:
                if widget:
                    widget.render(surf, opacity)

    def dispose(self):
        W, H = self.rect.size
        w = (W - self.hspace * (self.dims[1] - 1) - self.paddings[3] - self.paddings[1]) / self.dims[1]
        h = (H - self.vspace * (self.dims[0] - 1) - self.paddings[0] - self.paddings[2]) / self.dims[0]
        
        y = self.rect.y + self.paddings[0]
        for i in range(self.dims[0]):
            x = self.rect.x + self.paddings[3]
            for j in range(self.dims[1]):
                if self.grid[i][j] is not None:
                    self.grid[i][j].rect.topleft = (x, y)
                    self.grid[i][j].rect.width = w
                    self.grid[i][j].rect.height = h
                x += w + self.hspace    
            y += h + self.vspace
        
        for row in self.grid:
            for widget in row:
                if widget:
                    widget.dispose()


class GridLayoutAjaxH(Widget):
    def __init__(self, root, paddings=[0] * 4, dims=(0, 0), vspace=0, hspace=0, fixedSizes=(False, False)):
        super().__init__(root, fixedSizes)
        self.root = root
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.paddings = list(paddings)

        self.dims = list(dims)
        self.grids = []
        self.current_grid_idx = None
        self.vspace = vspace
        self.hspace = hspace

        self.hlayout = HorizontalLayout(root, paddings=paddings, space=10)
        w = 30
        h = 60
        colors = [(100,)*3, (150,)*3]
        fontsize = 40
        self.right_arrow = ArrowButton(root, True, w=w, h=h, positions=['center', 'center'], fontsize=fontsize, colors=colors, border_radius=10, fixedSizes=(True, False))
        self.right_arrow.connect(lambda: self.setPage(self.current_grid_idx + 1))
        self.left_arrow = ArrowButton(root, False, w=w, h=h, positions=['center', 'center'], fontsize=fontsize, colors=colors, border_radius=10, fixedSizes=(True, False))
        self.left_arrow.connect(lambda: self.setPage(self.current_grid_idx - 1))
        self.hlayout.addWidget(self.left_arrow)
        self.hlayout.addWidget(self.right_arrow)
        self.left_arrow.hide()
        self.right_arrow.hide()

    def setSize(self, width, height):
        self.rect.width = width
        self.rect.height = height

    def addWidget(self, widget):
        if self.current_grid_idx is None or self.grids[self.current_grid_idx].isFull():
            self.grids.append(GridLayout(self.root, paddings=[0] * 4, dims=self.dims, vspace=self.vspace, hspace=self.hspace))
            self.current_grid_idx = len(self.grids) - 1
            self.hlayout.popWidget(dispose_required=False)
            self.hlayout.addWidget(self.grids[-1])
            self.hlayout.addWidget(self.right_arrow)
            self.grids[-1].hide()
        self.grids[self.current_grid_idx].addWidgetFreeCell(widget)


    def setPage(self, page):
        '''
        page from 0 to len(self.grids) - 1
        '''
        if page < 0 or page >= len(self.grids):
            raise 'There is no such page: %s' % page
        if self.current_grid_idx is not None:
            self.grids[self.current_grid_idx].hide()
        self.current_grid_idx = page
        self.grids[self.current_grid_idx].show()
        self.left_arrow.show()
        self.right_arrow.show()
        if self.current_grid_idx == 0:
            self.left_arrow.hide()
        if self.current_grid_idx == len(self.grids) - 1:
            self.right_arrow.hide()
        self.hlayout.dispose()


    def dispose(self):
        if not self.showed: return
        self.hlayout.setSize(self.rect.width, self.rect.height)
        self.hlayout.dispose()


    def update(self, mouse_pos, clicked):
        if not self.showed: return
        self.hlayout.update(mouse_pos, clicked)

    def render(self, surf, opacity=None):
        if not self.showed: return
        self.hlayout.render(surf, opacity=opacity)
        


class CheckBox(FloatWidget):
    defaultActiveColor = ORANGE
    defaultBorderColors = [WHITE, BLUE]
    def __init__(self, root, w, h, dx=0, dy=0, positions=['left', 'top'], borderColors=None, activeColor=None, fixedSizes=(False, False)):
        super().__init__(root, pygame.Rect(dx, dy, w, h), positions, fixedSizes)
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
    def __init__(self, root, w, h, dx=0, dy=0, positions=['left', 'center'], r=8, border_radius=-1, fixedSizes=(False, False)):
        super().__init__(root, pygame.Rect(dx, dy, w, h), positions, fixedSizes)
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
        global NUM_HOVERED
        if not self.showed: return
        if self.innerRect.collidepoint(mouse_pos) :
            NUM_HOVERED += 1
            if clicked:
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
class LineEdit(FloatWidget):
    borderColors = [GRAY, WHITE]
    defaultColors = [DARK_GRAY, GRAY]
    defaultTextColors = [BLACK, BLACK]
    alphabet = "qwertyuiopasdfghjklzxcvbnm1234567890"
    pressed = {c: False for c in alphabet}
    pressed['backspace'] = pressed['space'] = pressed['return'] = False
    def __init__(self, root, placeholder='', max_len=None, dx=0, dy=0, w=0, h=0, positions=None, colors=None, textColors=None, borderColors=None, fontsize='auto', font=None, border_width=2, border_radius=-1, fixedSizes=(False, False)):
        super().__init__(root, pygame.Rect(dx, dy, w, h), positions=positions, fixedSizes=fixedSizes)
        self.root = root
        self.max_len = max_len
        self.rect = pygame.Rect(0, 0, w, h)
        self.colors = colors if colors else LineEdit.defaultColors
        self.textColors = textColors if textColors else LineEdit.defaultTextColors
        self.borderColors = borderColors if borderColors else LineEdit.borderColors
        self.color = self.colors[0]
        self.text_color = self.textColors[0]
        self.border_radius = border_radius
        self.border_width = border_width
        self.fontsize = fontsize
        self.font = font if font else pygame.font.Font('fonts/Amatic-Bold.ttf', 30)
        self.text = None
        self.placeholder = placeholder
        self.focused = False
        self.cursor_timer = self.default_cursor_timer = 30

    def render(self, surf, opacity=None):
        if not self.showed: return
        text_color = self.text_color
        color = self.color
        if opacity:
            text_color = list(self.text_color) + [opacity]
            color = list(self.color) + [opacity]
        if self.text:
            text = self.text
            if self.cursor_timer <= 0:
                if self.cursor_timer <= -self.default_cursor_timer:
                    self.cursor_timer = self.default_cursor_timer
                text = text + "|"
            text = self.font.render(text, True, text_color)
        else:
            delta = min(50, *text_color)
            text = self.font.render(self.placeholder, True, (text_color[0] - delta, text_color[1] - delta, text_color[2] - delta))
        border_color = self.borderColors[self.focused]
        pygame.draw.rect(surf, border_color, (self.rect.left - self.border_width, self.rect.top-self.border_width, self.rect.width + 2 * self.border_width, self.rect.height + 2 * self.border_width), border_radius=self.border_radius)
        pygame.draw.rect(surf, color, self.rect, border_radius=self.border_radius)
        surf.blit(text, (self.innerRect.left + 5, self.innerRect.centery - text.get_height()//2))

    def update(self, mouse_pos, clicked):
        if clicked and self.rect.collidepoint(mouse_pos):
            self.focused = True
        elif clicked:
            self.focused = False
            self.cursor_timer = self.default_cursor_timer
        if self.focused:
            self.cursor_timer -= 1
            for key, pressed in LineEdit.pressed.items():
                if pressed:
                    if key == 'backspace':
                        if self.text is not None:
                            self.text = self.text[:-1]
                            if self.text == '':
                                self.text = None
                    elif key == 'space':
                        if self.text is None:
                            self.text = ''
                        self.text += ' '
                    elif key == 'return':
                        if self.callback:
                            self.callback()
                    elif key in LineEdit.alphabet:
                        if self.text is None:
                            self.text = ''
                        if self.max_len is None or len(self.text) < self.max_len:
                            self.text += key
        if self.fontsize == 'auto':
            fontsize = int(self.rect.height / 1.2)
            self.font = pygame.font.Font('fonts/Amatic-Bold.ttf', fontsize)
        self.color = self.colors[self.focused]
        self.text_color = self.textColors[self.focused]


class Label(FloatWidget):
    def __init__(self, root, text, dx=0, dy=0, positions=None, fontsize=50, font=None, color=BLACK, size=None, fixedSizes=(False, False)):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.font = font if font else pygame.font.Font('fonts/Pacifico.ttf', fontsize)
        self.rendered_text = self.font.render(text, True, color)
        size = size if size else self.rendered_text.get_size()
        super().__init__(root, pygame.Rect(dx, dy, *size), positions, fixedSizes)
    
    def update(self, mouse_pos, clicked): pass

    def render(self, surf, opacity=None):
        surf.blit(self.rendered_text, self.innerRect.topleft)

class BlinkingLabel(Label):
    def __init__(self, root, text, dx=0, dy=0, positions=None, fontsize=50, font=None, color=BLACK, blinktime=50, fixedSizes=(False, False)):
        super().__init__(root, text, dx, dy, positions, fontsize, font, color, fixedSizes=fixedSizes)
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

    def render(self, surf, opacity=None):
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


class New2LastBroker(Widget):
    def __init__(self, root, newObject):
        super().__init__(root, newObject.fixedSizes)
        self.newObject = newObject
        self.disposed = False
        self.state = State()

    def __getattr__(self, name):
        return getattr(self.newObject, name)        

    def update(self, mouse_pos, clicked):
        global NUM_HOVERED
        self.state.mouse_clicked = clicked
        self.state.mouse_pos = mouse_pos
        self.newObject.update(self.state)
        NUM_HOVERED += State.NUM_HOVERED
        State.NUM_HOVERED = 0

    def render(self, surf, opacity=None):
        self.newObject.render(surf)

    def dispose(self):
        if not self.disposed:
            self.newObject.dispose()
            self.disposed = True

class Pages:
    def __init__(self, size):
        self.ml = VerticalLayout(None)
        self.ml.setSize(*size)
        self.layouts = []
        self.current_layout = None
        self.actions = []

    def __getattr__(self, attrname):
        if hasattr(self.current_layout, attrname):
            return getattr(self.current_layout, attrname)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attrname}'")

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