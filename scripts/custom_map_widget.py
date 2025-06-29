import pygame
import shelve
from scripts.resource_manager import load_image
from .utils import resource_path, save_path

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (100, 100, 100)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)

class State:
    alhabet = "qwertyuiopasdfghjklzxcvbnm1234567890"
    NUM_HOVERED = 0
    LAST_NUM_HOVERED = 0
    def __init__(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_clicked = False
        self.keys = {}

    def update(self, events):
        self.mouse_clicked = False
        if State.NUM_HOVERED > 0 and State.LAST_NUM_HOVERED == 0:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif State.NUM_HOVERED == 0 and State.LAST_NUM_HOVERED > 0:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        State.LAST_NUM_HOVERED = State.NUM_HOVERED
        State.NUM_HOVERED = 0
        self.mouse_pos = pygame.mouse.get_pos()
        self.keys['backspace'] = False
        self.keys['space'] = False
        for key in self.alhabet:
            if key in self.keys and self.keys[key]:
                self.keys[key] = False
        # check for events
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.keys['backspace'] = True
                if event.key == pygame.K_SPACE:
                    self.keys['space'] = True
                key_name = pygame.key.name(event.key)
                if key_name in State.alhabet:
                    self.keys[key_name] = True
        

class Widget:
    def __init__(self, parent):
        self.parent = parent
        # rect
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.innerRect = pygame.Rect(0, 0, 0, 0)
        self.fixedSizes = [False, False]
        self.positions = None
        self.paddings = [0] * 4
        self.margins = [0] * 4
        self.borderWidth = 1
        self.border_radius = 0
        self.clickable = False
        self.just_clicked = False
        
        # colors
        self.bgColors = [LIGHT_GRAY, GRAY]
        self.borderColors = [DARK_GRAY, BLACK]

        # bg image
        self.bgImage = None

        # visibility & states
        self.present = True
        self.visible = True
        self.hovered = False

        self.transparentBackground = False

    def setTransparentBackground(self, transparentBackground):
        self.transparentBackground = transparentBackground

    def setVisible(self, visible):
        self.visible = visible

    def setClickable(self, clickable):
        self.clickable = clickable

    def setBgImage(self, path):
        self.bgImage = path

    def setFixedSizes(self, fixedSizes):
        self.fixedSizes = list(fixedSizes)

    def setMargins(self, margins):
        if len(margins) == 1:
            self.margins = margins * 4
        elif len(margins) == 2:
            self.margins = [margins[0], margins[1], margins[0], margins[1]]
        else:
            assert len(margins) == 4, "You must provide 1, 2 or 4 margins"
            self.margins = list(margins)

    def setPaddings(self, paddings):
        if len(paddings) == 1:
            paddings = [paddings[0]] * 4
        elif len(paddings) == 2:
            paddings = [paddings[0], paddings[1], paddings[0], paddings[1]]
        assert len(paddings) == 4, "You must provide 1, 2 or 4 paddings"
        self.paddings = list(paddings)

    def setBorderColors(self, colors):
        assert len(colors) == 2, "You must provide two colors for borderColors"
        self.borderColors = colors

    def setBackgroundColors(self, colors):
        assert len(colors) == 2, "You must provide two colors for bgColors"
        self.bgColors = colors

    def setBorderRadius(self, r):
        self.border_radius = r

    def setBorderWidth(self, border_width):
        self.borderWidth = border_width

    def setPosition(self, x, y):
        self.rect.topleft = (x, y)

    def setHeight(self, h):
        assert not self.fixedSizes[1], "You cannot set height of a widget with fixed height"
        self.rect.height = h

    def setWidth(self, w):
        assert not self.fixedSizes[0], "You cannot set width of a widget with fixed width"
        self.rect.width = w

    def setSize(self, w, h):
        assert not self.fixedSizes[0] and not self.fixedSizes[1], "You cannot set size of a widget with fixed sizes"
        self.rect.width = w
        self.rect.height = h

    def show(self):
        self.present = True
    
    def hide(self):
        self.present = False
    
    def onClick(self):
        pass

    def update(self, state: State):
        if not self.present: return
        self.hovered = self.rect.collidepoint(state.mouse_pos)
        State.NUM_HOVERED += self.hovered * self.clickable
        self.just_clicked = False
        if self.hovered and state.mouse_clicked:
            if self.clickable:
                self.onClick()
            self.just_clicked = True

    def render(self, surf):
        if not self.present or not self.visible or self.transparentBackground: return
        if self.innerRect.width > 0 and self.innerRect.height > 0:
            pygame.draw.rect(
                surf,
                self.borderColors[self.hovered],
                (self.innerRect.x - self.borderWidth, self.innerRect.y - self.borderWidth, self.innerRect.width + 2 * self.borderWidth, self.innerRect.height + 2 * self.borderWidth),
                border_radius=self.border_radius    
            )
            pygame.draw.rect(
                surf,
                self.bgColors[self.hovered],
                self.innerRect,
                border_radius=self.border_radius
            )
        if self.bgImage:
            surf.blit(self.bgImage, (self.innerRect.x, self.innerRect.y))

    def _dispose_pos(self):
        if not self.parent or not self.parent.present: return
        if self.positions[0] == 'left':
            self.rect.left = self.parent.innerRect.x + self.paddings[3]
        elif self.positions[0] == 'center':
            self.rect.centerx = self.parent.innerRect.centerx
        elif self.positions[0] == 'right':
            self.rect.right = self.parent.innerRect.right - self.paddings[1]
        if self.positions[1] == 'top':
            self.rect.top = self.parent.innerRect.y + self.paddings[0]
        elif self.positions[1] == 'center':
            self.rect.centery = self.parent.innerRect.centery
        elif self.positions[1] == 'bottom':
            self.rect.bottom = self.parent.innerRect.bottom - self.paddings[2]

    def dispose(self):
        '''
        You must implement this method in subclasses to dispose the children widgets
        '''
        if not self.present: return
        if self.positions:
            self._dispose_pos()
        self.innerRect = pygame.Rect(
            self.rect.x + self.paddings[3],
            self.rect.y + self.paddings[0],
            self.rect.width - (self.paddings[1] + self.paddings[3]),
            self.rect.height - (self.paddings[0] + self.paddings[2])
        )
        if self.bgImage and isinstance(self.bgImage, str):
            self.bgImage = load_image(self.bgImage, scale=1, size=self.innerRect.size)



class StackedWidget(Widget):
    def __init__(self, parent):
        super().__init__(parent)
        self.widgets = []
        self.current_idx = None
        self.setBackgroundColors([WHITE, WHITE])
        self.setBorderWidth(0)
    
    def setTransparentBackground(self, transparentBackground):
        super().setTransparentBackground(transparentBackground)
        for widget in self.widgets:
            widget.setTransparentBackground(transparentBackground)

    def addWidget(self, widget, space=20, arrowColors=[LIGHT_GRAY, GRAY]):
        layout = HorizontalLayout(self)
        layout.hide()
        layout.setVisible(False)
        # left Arrow
        leftArrow = TextButton(layout, '<')
        if self.current_idx is None:
            leftArrow.setVisible(False)
            leftArrow.setClickable(False)

        # right Arrow
        rightArrow = TextButton(layout, '>')
        rightArrow.setVisible(False)
        rightArrow.setClickable(False)
        if self.current_idx is not None:
            self.widgets[-1].widgets[-1].setVisible(True)
            self.widgets[-1].widgets[-1].setClickable(True)

        
        for arrow in [leftArrow, rightArrow]:
            arrow.setBorderWidth(0)
            arrow.setSize(30, 30)
            arrow.setFixedSizes([True, True])
            arrow.setBorderRadius(20)
            arrow.setBackgroundColors(arrowColors)
        
        leftArrow.onClick = self.previousWidget
        rightArrow.onClick = self.nextWidget
        # add into layout
        layout.addWidget(leftArrow)
        layout.addWidget(widget)
        layout.addWidget(rightArrow)
        layout.setSpace(space)
        self.widgets.append(layout)
        if self.current_idx is None:
            self.current_idx = 0
        else:
            self.current_idx += 1
    
    def previousWidget(self):
        self.setPage(self.current_idx - 1)

    def nextWidget(self):
        self.setPage(self.current_idx + 1)

    def setPage(self, idx):
        assert idx < len(self.widgets), 'There is no such widget: idx is too big\n\tidx = %d\n\tnum of widgets = %d' % (idx, len(self.widgets))
        self.widgets[self.current_idx].hide()
        self.current_idx = idx
        self.widgets[self.current_idx].show()
        # self.dispose()
    
    def render(self, surf):
        if not self.present or not self.visible or not self.widgets: return
        super().render(surf)
        for kidWidget in self.widgets[self.current_idx].widgets:
            kidWidget.render(surf)
    
    def update(self, state):
        if not self.present or not self.widgets: return
        super().update(state)
        self.widgets[self.current_idx].update(state)
    
    def dispose(self, changePageIdx=True):
        if not self.present or not self.widgets: return
        super().dispose()
        for layout in self.widgets:
            layout.setPosition(*self.innerRect.topleft)
            layout.setSize(*self.innerRect.size)
            layout.show()
            layout.dispose()
            layout.hide()
        if changePageIdx:
            self.current_idx = 0
        self.widgets[self.current_idx].show()

class Button(Widget):
    def __init__(self, parent):
        super().__init__(parent)
        self.clickable = True

class TextButton(Button):
    def __init__(self, parent, text='Button'):
        super().__init__(parent)
        self.fontFamily = None
        self.text = text
        self.text_images = None
        self.text_rect = None
        self.colors = [BLACK, WHITE]
        self.fontSize = None

    def setFont(self, fontFamily, fontSize):
        self.setFontFamily(fontFamily)
        self.setFontSize(fontSize)

    def setFontFamily(self, fontFamily):
        self.fontFamily = fontFamily

    def setFontSize(self, fontSize):
        self.fontSize = fontSize

    def setColors(self, colors):
        self.colors = list(colors)

    def setText(self, text):
        self.text = text
    
    def render(self, surf):
        if not self.present or not self.visible: return
        super().render(surf)
        surf.blit(self.text_images[self.hovered], self.text_rect.topleft)

    def dispose(self):
        if not self.present: return
        super().dispose()
        if self.fontSize is None:
            count = 1000
            fontSize = int(min(self.innerRect.size) / 1.2)
            while True:
                font = pygame.font.Font(self.fontFamily, fontSize)
                text_img = font.render(self.text, True, self.colors[0])
                if text_img.get_width() < self.innerRect.width and text_img.get_height() < self.innerRect.height:
                    break
                fontSize -= 1
                count -= 1
                if count == 0 or fontSize <= 0:
                    raise "The text size couldn't be adjusted properly"   
            self.fontSize = fontSize
        self.font = pygame.font.Font(self.fontFamily, self.fontSize)
        self.text_images = [
            self.font.render(self.text, True, self.colors[0]),
            self.font.render(self.text, True, self.colors[1])    
        ]
        self.text_rect = self.text_images[0].get_rect()
        self.text_rect.x = self.innerRect.centerx - self.text_rect.width // 2
        self.text_rect.y = self.innerRect.centery - self.text_rect.height // 2


class Layout(Widget):
    def __init__(self, parent):
        super().__init__(parent)
        self.widgets: list[Widget] = []
    
    def setTransparentBackground(self, transparentBackground):
        super().setTransparentBackground(transparentBackground)
        for widget in self.widgets:
            widget.setTransparentBackground(transparentBackground)

    def popWidget(self):
        self.widgets.pop()

    def addWidget(self, widget):
        self.widgets.append(widget)

    def update(self, state):
        if not self.present: return
        super().update(state)
        for widget in self.widgets:
            widget.update(state)
    
    def render(self, surf):
        if not self.present or not self.visible: return
        super().render(surf)
        for widget in self.widgets:
            widget.render(surf)
        

class HorizontalLayout(Layout):
    def __init__(self, parent):
        super().__init__(parent)
        self.placementx = 'left'  # 'left', ''center' or 'right
        self.placementy = "center" # 'top', 'center' or 'bottom'
        self.space = 0
    
    def setSpace(self, space):
        self.space = space

    def setPlacements(self, placementx, placementy):
        self.setPlacementx(placementx)
        self.setPlacementy(placementy) 

    def setPlacementx(self, placementx):
        assert placementx in ['left', 'center', 'right'], 'There are only 3 variant: left, center or right'
        self.placementx = placementx


    def setPlacementy(self, placementy):
        assert placementy in ['top', 'center', 'bottom'], 'There are only 3 variant: top, center or bottom'
        self.placementy = placementy
    
    def dispose_x(self):
        widgets = [widget for widget in self.widgets if widget.present]
        if not widgets: return
        max_margin = max(widgets[0].margins[3], widgets[-1].margins[1])
        num_not_fixed = len([widget for widget in widgets if widget.fixedSizes[0] == False])
        FS = sum([widget.rect.width for widget in widgets if widget.fixedSizes[0]])
        if self.placementx == 'center':
            M = 2 * max_margin
        else:
            M = widgets[0].margins[3] + widgets[-1].margins[1]
        for w_p, w_n in zip(widgets[:-1], widgets[1:]):
            M += max(w_p.margins[1], w_n.margins[3], self.space)
        RestW = self.innerRect.width - FS - M
        assert RestW >= 0, 'DisposeResizeError: Can not dispose elements: the inner widgets do not fit into the layout'
        w = 0 if num_not_fixed == 0 else RestW / num_not_fixed
        
        if self.placementx == 'left':
            x = self.innerRect.left + widgets[0].margins[3]
        elif self.placementx == 'center':
            x = self.innerRect.left + (RestW - num_not_fixed * w) / 2 + max_margin
        elif self.placementx == 'right':
            x = self.innerRect.left + RestW - num_not_fixed * w + widgets[0].margins[3]
        for idx, widget in enumerate(widgets):            
            if widget.fixedSizes[0] == False:
                widget.rect.width = w
            widget.rect.left = x
            if idx < len(widgets) - 1:
                x += widget.rect.width + max(widget.margins[1], widgets[idx + 1].margins[3], self.space)
            

    def dispose_top(self):
        widgets = [widget for widget in self.widgets if widget.present]
        for widget in widgets:
            widget.rect.top = self.innerRect.top + widget.margins[0]
            if widget.fixedSizes[1] == False:
                widget.rect.height = self.innerRect.height - widget.margins[0] - widget.margins[2]
                assert widget.rect.height >= 0, 'DisposeResizeError: Can not dispose an element: its height is below 0'
            else:
                assert self.innerRect.height - widget.rect.height - widget.margins[0] - widget.margins[2] >= 0, 'DisposeResizeError: Can not dispose an element: the inner widget does not fit into the layout'
        self.dispose_x()


    def dispose_bottom(self):
        widgets = [widget for widget in self.widgets if widget.present]
        for widget in widgets:
            if widget.fixedSizes[1] == False:
                widget.rect.height = self.innerRect.height - widget.margins[0] - widget.margins[2]
                assert widget.rect.height >= 0, 'DisposeResizeError: Can not dispose an element: its height is below 0'
            else:
                assert self.innerRect.height - widget.rect.height - widget.margins[0] - widget.margins[2] >= 0, 'DisposeResizeError: Can not dispose an element: the inner widget does not fit into the layout'
            widget.rect.bottom = self.innerRect.bottom - widget.margins[2]
        self.dispose_x()

    def dispose_center(self):
        widgets = [widget for widget in self.widgets if widget.present]
        for widget in widgets:
            if widget.fixedSizes[1] == False:
                widget.rect.height = self.innerRect.height - 2 * max(widget.margins[0], widget.margins[2])
                assert widget.rect.height >= 0, 'DisposeResizeError: Can not dispose an element: its height is below 0'
            else:
                assert 0 <= widget.rect.height <= self.innerRect.height - 2 * max(widget.margins[0], widget.margins[2]), 'DisposeResizeError: Can not dispose an element: the inner widget does not fit into the layout'
            widget.rect.centery = self.innerRect.centery
        self.dispose_x()

    def dispose(self):
        if not self.present: return
        super().dispose()
        if self.placementy == 'center': self.dispose_center()
        elif self.placementy == 'top': self.dispose_top()
        elif self.placementy == 'bottom': self.dispose_bottom()
        else:
            assert False, 'Unknown type of placement: `%s`' % self.placementy 
        for widget in self.widgets:
            widget.dispose()

# ---------------------------- EXPERIMENTAL ------------------------------------------------#
class VerticalLayout(Layout):
    def __init__(self, parent):
        super().__init__(parent)
        self.placementx = 'left'  # 'left', ''center' or 'right
        self.placementy = "center" # 'top', 'center' or 'bottom'
        self.space = 0

    def setSpace(self, space):
        self.space = space

    def setPlacements(self, placementx, placementy):
        self.setPlacementx(placementx)
        self.setPlacementy(placementy) 

    def setPlacementx(self, placementx):
        assert placementx in ['left', 'center', 'right'], 'There are only 3 variant: left, center or right'
        self.placementx = placementx


    def setPlacementy(self, placementy):
        assert placementy in ['top', 'center', 'bottom'], 'There are only 3 variant: top, center or bottom'
        self.placementy = placementy
    
    def dispose_y(self):
        widgets = [widget for widget in self.widgets if widget.present]
        if not widgets: return
        max_margin = max(widgets[0].margins[0], widgets[-1].margins[2])
        num_not_fixed = len([widget for widget in widgets if widget.fixedSizes[1] == False])
        FS = sum([widget.rect.height for widget in widgets if widget.fixedSizes[1]])
        if self.placementy == 'center':
            M = 2 * max_margin
        else:
            M = widgets[0].margins[0] + widgets[-1].margins[2]
        for w_p, w_n in zip(widgets[:-1], widgets[1:]):
            M += max(w_p.margins[2], w_n.margins[0], self.space)
        RestH = self.innerRect.height - FS - M
        assert RestH >= 0, 'DisposeResizeError: Can not dispose elements: the inner widgets do not fit into the layout'
        w = 0 if num_not_fixed == 0 else RestH / num_not_fixed
        
        if self.placementy == 'top':
            y = self.innerRect.top + widgets[0].margins[0]
        elif self.placementy == 'center':
            y = self.innerRect.top + (RestH - num_not_fixed * w) / 2 + max_margin
        elif self.placementy == 'bottom':
            y = self.innerRect.top + RestH - num_not_fixed * w + widgets[0].margins[0]
        for idx, widget in enumerate(widgets):            
            if widget.fixedSizes[1] == False:
                widget.rect.height = w
            widget.rect.top = y
            if idx < len(widgets) - 1:
                y += widget.rect.height + max(widget.margins[2], widgets[idx + 1].margins[0], self.space)
            

    def dispose_left(self):
        widgets = [widget for widget in self.widgets if widget.present]
        for widget in widgets:
            widget.rect.left = self.innerRect.left + widget.margins[3]
            if widget.fixedSizes[0] == False:
                widget.rect.width = self.innerRect.width - widget.margins[3] - widget.margins[1]
                assert widget.rect.width >= 0, 'DisposeResizeError: Can not dispose an element: its width is below 0'
            else:
                assert self.innerRect.width - widget.rect.width - widget.margins[3] - widget.margins[1] >= 0, 'DisposeResizeError: Can not dispose an element: the inner widget does not fit into the layout'
        self.dispose_y()


    def dispose_right(self):
        widgets = [widget for widget in self.widgets if widget.present]
        for widget in widgets:
            if widget.fixedSizes[0] == False:
                widget.rect.width = self.innerRect.width - widget.margins[3] - widget.margins[1]
                assert widget.rect.width >= 0, 'DisposeResizeError: Can not dispose an element: its width is below 0'
            else:
                assert self.innerRect.width - widget.rect.width - widget.margins[3] - widget.margins[1] >= 0, 'DisposeResizeError: Can not dispose an element: the inner widget does not fit into the layout'
            widget.rect.right = self.innerRect.right - widget.margins[1]
        self.dispose_y()

    def dispose_center(self):
        widgets = [widget for widget in self.widgets if widget.present]
        for widget in widgets:
            if widget.fixedSizes[0] == False:
                widget.rect.width = self.innerRect.width - 2 * max(widget.margins[3], widget.margins[1])
                assert widget.rect.width >= 0, 'DisposeResizeError: Can not dispose an element: its width is below 0'
            else:
                assert 0 <= widget.rect.width <= self.innerRect.width - 2 * max(widget.margins[3], widget.margins[1]), 'DisposeResizeError: Can not dispose an element: the inner widget does not fit into the layout'
            widget.rect.centerx = self.innerRect.centerx
        self.dispose_y()

    def dispose(self):
        if not self.present: return
        super().dispose()
        if self.placementx == 'center': self.dispose_center()
        elif self.placementx == 'left': self.dispose_left()
        elif self.placementx == 'right': self.dispose_right()
        else:
            assert False, 'Unknown type of placement: `%s`' % self.placementy 
        for widget in self.widgets:
            widget.dispose()

# ---------------------------- EXPERIMENTAL ------------------------------------------------#
  

class GridLayoutV(VerticalLayout):
    def __init__(self, parent):
        super().__init__(parent)
        self.dims = None

    def setDims(self, numRows, numCols):
        assert self.dims is None, 'You can not change dims: it has already been set up'
        self.dims = numRows, numCols
        for _ in range(numRows):
            VerticalLayout.addWidget(self, HorizontalLayout(self))

    def isFull(self):
        assert self.dims is not None, 'Dims has not been set up yet'
        for hlayout in self.widgets:
            if len(hlayout.widgets) < self.dims[1]:
                return False
        return True

    def setAllRows(self, attrname, *args):
        for widget in self.widgets:
            getattr(widget, attrname)(*args)

    def setRowBackgroundColors(self, row, bg_colors):
        self.widgets[row].setBackgroundColors(bg_colors)

    def setRowBorderWidth(self, row, border_width):
        self.widgets[row].setBorderWidth(border_width)

    def setRowSpace(self, row, space):
        self.widgets[row].setSpace(space)

    def setRowPlacements(self, row, placementx, placementy):
        self.widgets[row].setPlacements(placementx, placementy)

    def appendWidget(self, row, widget):
        '''
        Appends a widget to the current row.
        Row belongs to [0, dims[0]-1] 
        '''
        assert self.dims is not None, 'Dims has not been set up yet'
        assert row < self.dims[0], 'An attempt to add a widget to a row which does not exist: dims = %s, row = %d' % (self.dims, row)
        assert len(self.widgets[row].widgets) < self.dims[1], 'An attempt to add a widget to a row which is full'
        self.widgets[row].addWidget(widget)

    def appendWidgetFree(self, widget):
        assert self.dims is not None, 'Dims has not been set up yet'
        for hlayout in self.widgets:
            if len(hlayout.widgets) < self.dims[1]:
                hlayout.addWidget(widget)
                return
        assert False, 'Attempting to add an element to a fully filled grid layout'

    def addWidget(self):
        raise 'This method is not defined for GridLayoutV class'

    def addRow(self):
        assert self.dims is not None, 'Dims has not been set up yet'
        VerticalLayout.addWidget(self, HorizontalLayout(self))
        self.dims = (self.dims[0] + 1, self.dims[1])
        
class StackedGridLayout(StackedWidget):
    def __init__(self, parent, dims):
        super().__init__(parent)
        self.dims = list(dims)
        self.current_grid = None
    
    def addWidget(self, widget):
        if self.current_grid is None or self.current_grid.isFull():
            self.current_grid = GridLayoutV(self)
            self.current_grid.setDims(*self.dims)
            self.current_grid.setBorderWidth(0)
            self.current_grid.setAllRows('setPlacements', 'center', 'center')
            self.current_grid.setAllRows('setSpace', 10)
            self.current_grid.setAllRows('setBackgroundColors', [RESOURCE_PANEL_BACKGROUND_COLOR] * 2)
            self.current_grid.setAllRows('setBorderWidth', 0)
            super().addWidget(self.current_grid)
        self.current_grid.appendWidgetFree(widget)

    


class LineEdit(Widget):
    def __init__(self, parent):
        super().__init__(parent)
        self.placeholder = None
        self.text = ''
        self.text_image = None
        self.text_rect = None
        self.fontFamily = None
        self.placeholder_image = None
        self.placeholder_rect = None
        self.colors = [BLACK, WHITE]
        self.fontSize = None
        self.active = False
        self.cursor_timer_period = 30
        self.cursor_timer = 0
        
    def setPlaceholder(self, placeholder):
        self.placeholder = placeholder
    
    def setFont(self, fontFamily, fontSize):
        self.setFontFamily(fontFamily)
        self.setFontSize(fontSize)

    def setFontFamily(self, fontFamily):
        self.fontFamily = fontFamily

    def setFontSize(self, fontSize):
        self.fontSize = fontSize

    def render(self, surf):
        if not self.present or not self.visible: return
        last_hovered = self.hovered
        if self.active:
            self.hovered = True
        super().render(surf)
        self.hovered = last_hovered
        if self.cursor_timer > 0 and self.active:
            cursor_y = self.innerRect.top + self.paddings[0]
            cursor_y_dest = self.innerRect.bottom - self.paddings[2]
            if self.text:
                cursor_x = self.text_rect.right
            else:
                cursor_x = self.innerRect.top + self.paddings[3]
            pygame.draw.line(surf, "black", (cursor_x, cursor_y), (cursor_x, cursor_y_dest), width=2)
        if self.text:
            surf.blit(self.text_image, self.text_rect.topleft)
        elif self.placeholder_image and not self.text:
            surf.blit(self.placeholder_image, self.placeholder_rect.topleft)

    def update(self, state: State):
        if not self.present: return
        super().update(state)
        if self.hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        if self.hovered and state.mouse_clicked:
            self.active = True
        elif state.mouse_clicked:
            self.active = False
            self.cursor_timer = 0

        if self.active:
            self.cursor_timer -= 1
            if self.cursor_timer <= -self.cursor_timer_period:
                self.cursor_timer = self.cursor_timer_period
            new = False
            for key, val in state.keys.items():
                if val and key in State.alhabet:
                    self.text += key
                    new = True
                elif val and key == 'backspace':
                    self.text = self.text[:-1]
                    new = True
                elif val and key == 'space':
                    self.text += ' '
                    new = True
            if new:
                self.text_image = self.font.render(self.text, True, self.colors[0])
                self.text_rect = self.text_image.get_rect(topleft=(self.innerRect.x + self.paddings[3], self.innerRect.centery - self.text_image.get_height() // 2))
                while self.text_image.get_width() > self.innerRect.width - self.paddings[1] - self.paddings[3]:
                    self.text = self.text[:-1]
                    self.text_image = self.font.render(self.text, True, self.colors[0])
                    self.text_rect = self.text_image.get_rect(topleft=(self.innerRect.x + self.paddings[3], self.innerRect.centery - self.text_image.get_height() // 2))
                    if not self.text:
                        break

    def dispose(self):
        if not self.present: return
        super().dispose()
        if self.fontSize is None:
            count = 1000
            fontSize = int(min(self.innerRect.size) / 1.2)
            while True:
                font = pygame.font.Font(self.fontFamily, fontSize)
                self.placeholder_image = font.render(self.placeholder, True, self.colors[0])
                if self.placeholder_image.get_width() < self.innerRect.width and self.placeholder_image.get_height() < self.innerRect.height:
                    break
                fontSize -= 1
                count -= 1
                if count == 0 or fontSize <= 0:
                    raise "The text size couldn't be adjusted properly"
            self.fontSize = fontSize
            self.placeholder_rect = self.placeholder_image.get_rect(topleft=(self.innerRect.left + self.paddings[3], self.innerRect.top + self.paddings[0]))
        self.font = pygame.font.Font(self.fontFamily, self.fontSize)


# ------------------------------- FOR THE GAME --------------------------------
RESOURCE_PANEL_BACKGROUND_COLOR = GRAY

class ResourcePanel(StackedWidget):
    def __init__(self, resources, dims):
        super().__init__(None)
        self.resources = resources
        tile_size = next(iter(resources.values()))[0].get_width()
        space = 10
        self.panel_width, self.panel_height = (tile_size + space * 3) * dims[1], (tile_size + 5) * dims[0]
        placements = ['center', 'center']
        grid = None
        for resource_name, images in self.resources.items():
            if grid is None:
                grid = GridLayoutV(self)
                grid.setDims(1, dims[1])
                nrow = 1
            if resource_name == 'large_decor':
                continue
            for variant, image in enumerate(images):
                if grid.isFull():
                    if nrow < dims[0]:
                        grid.addRow()
                        nrow += 1
                    else:
                        self.addWidget(grid)
                        grid.setBorderWidth(0)
                        grid.setAllRows('setPlacements', *placements)
                        grid.setAllRows('setSpace', space)
                        grid.setAllRows('setBackgroundColors', [RESOURCE_PANEL_BACKGROUND_COLOR] * 2)
                        grid.setAllRows('setBorderWidth', 0)
                        grid = GridLayoutV(self)
                        grid.setDims(1, dims[1])
                        nrow = 1
                tile_img = Button(grid)
                tile_img.setSize(tile_size, tile_size)
                tile_img.setFixedSizes([True, True])
                tile_img.setBackgroundColors([RESOURCE_PANEL_BACKGROUND_COLOR, DARK_GRAY])
                tile_img.setBgImage(image)
                tile_img.setBorderColors([RESOURCE_PANEL_BACKGROUND_COLOR, BLACK])
                tile_img.setBorderRadius(2)
                tile_img.tile = {
                    'type': resource_name,
                    'variant': variant
                }
                grid.appendWidgetFree(tile_img)
        self.addWidget(grid)
        grid.setBorderWidth(0)
        grid.setAllRows('setPlacements', *placements)
        grid.setAllRows('setSpace', space)
        grid.setAllRows('setBackgroundColors', [RESOURCE_PANEL_BACKGROUND_COLOR] * 2)
        grid.setAllRows('setBorderWidth', 0)
        grid = GridLayoutV(self)
        grid.setDims(1, dims[1])
        for variant, image in enumerate(self.resources['large_decor']):
            tile_img = Button(grid)
            iw, ih = image.get_size()
            max_height = self.panel_height - 5
            if ih >= max_height:
                image = pygame.transform.scale(image, (iw * max_height / ih, max_height))
            tile_img.setSize(*image.get_size())
            tile_img.setFixedSizes([True, True])
            tile_img.setBgImage(image)
            tile_img.setBackgroundColors([RESOURCE_PANEL_BACKGROUND_COLOR, DARK_GRAY])
            tile_img.setBgImage(image)
            tile_img.setBorderColors([RESOURCE_PANEL_BACKGROUND_COLOR, BLACK])
            tile_img.tile = {
                    'type': 'large_decor',
                    'variant': variant
                }
            grid.appendWidgetFree(tile_img)
        
        self.addWidget(grid)
        grid.setBorderWidth(0)
        grid.setAllRows('setPlacements', *placements)
        grid.setAllRows('setSpace', space)
        grid.setAllRows('setBackgroundColors', [RESOURCE_PANEL_BACKGROUND_COLOR] * 2)
        grid.setAllRows('setBorderWidth', 0)
        
        self.setSize(self.panel_width, self.panel_height)
        self.setFixedSizes([True, True])
        self.setBackgroundColors([RESOURCE_PANEL_BACKGROUND_COLOR] * 2)

        self.selected_tile = None

    def update(self, state):
        if not self.present: return
        super().update(state)
        for row_idx, hlayout in enumerate(self.widgets[self.current_idx].widgets[1].widgets):
            for col_idx, button in enumerate(hlayout.widgets):
                if button.just_clicked:
                    if self.selected_tile is not None and self.selected_tile['button'] == button:
                        self.selected_tile = None
                    else:
                        self.selected_tile = {
                            'page_idx': self.current_idx,
                            'row_idx': row_idx,
                            'col_idx': col_idx,
                            'tile': button.tile,
                            'button': button
                        }

    def render(self, surf):
        if not self.present or not self.visible: return
        super().render(surf)
        if self.selected_tile is not None and self.current_idx == self.selected_tile['page_idx']:
            delta = 2
            r = self.selected_tile['button'].rect
            rect = pygame.Rect(r.x - delta, r.y - delta, r.width + 2 * delta, r.height + 2 * delta)
            pygame.draw.rect(surf, (255, 0, 0), rect, width=delta)

    def addWidget(self, widget):
        super().addWidget(widget, space=0, arrowColors=[GRAY, GRAY])


font = pygame.font.Font(None, 30)
def debug(text, position=[10, 10], fontSize=30, fontColor='red'):
    text = str(text)
    if fontSize != 30:
        global font
        font = pygame.font.Font(None, fontSize)
    text = font.render(text, True, fontColor)
    screen.blit(text, position)
    
class MessageBox(VerticalLayout):
    def __init__(self, parent):
        super().__init__(parent)

        # --- Современная и чистая цветовая палитра ---
        BG_COLOR = (248, 249, 250)      # Очень светлый серый, почти белый
        BORDER_COLOR = (222, 226, 230)  # Мягкая, неконтрастная рамка
        TEXT_COLOR = (33, 37, 41)       # Темный, но не чисто черный текст
        PRIMARY_BLUE = (13, 110, 253)   # Приятный синий цвет для акцентов
        PRIMARY_BLUE_HOVER = (10, 98, 227) # Более темный синий для наведения
        
        LINE_EDIT_BG = (255, 255, 255)
        LINE_EDIT_BORDER = (206, 212, 218)
        LINE_EDIT_BORDER_ACTIVE = PRIMARY_BLUE 
        
        BTN_CANCEL_BG = (248, 249, 250)
        BTN_CANCEL_HOVER = (222, 226, 230)

        # --- Настройка главного контейнера (self) ---
        self.setBackgroundColors([BG_COLOR, BG_COLOR])
        self.setBorderColors([BORDER_COLOR, BORDER_COLOR])
        self.setBorderWidth(1) # Кстати, здесь лучше поставить 1, как я рекомендовал ранее
        self.setBorderRadius(12)
        self.setPaddings([5])
        self.setSpace(15)
        
        # ===> ИЗМЕНИТЕ ЭТУ СТРОКУ <===
        self.setPlacementy('top') # Вместо 'top'
        # --- Создание и настройка поля для ввода текста (LineEdit) ---
        self.line_edit = LineEdit(self)
        self.line_edit.setPlaceholder("Введите имя карты...")
        self.line_edit.setBackgroundColors([LINE_EDIT_BG, LINE_EDIT_BG])
        # При наведении или активации рамка становится синей
        self.line_edit.setBorderColors([LINE_EDIT_BORDER, LINE_EDIT_BORDER_ACTIVE])
        self.line_edit.setBorderWidth(1)
        self.line_edit.setBorderRadius(8)
        self.line_edit.setPaddings([10, 12, 10, 12]) # Отступы внутри поля ввода
        self.line_edit.setFont(None, 24) # Системный шрифт, размер 24
        self.line_edit.colors[0] = TEXT_COLOR # Установка цвета текста

        # --- Создание контейнера для кнопок ---
        self.horizontal_layout = HorizontalLayout(self)
        self.horizontal_layout.setBackgroundColors([BG_COLOR, BG_COLOR]) # Прозрачный фон
        self.horizontal_layout.setBorderWidth(0)
        self.horizontal_layout.setPlacementx("right") # Выравнивание кнопок по правому краю
        self.horizontal_layout.setSpace(10)
        self.horizontal_layout.setHeight(60)
        self.horizontal_layout.setFixedSizes([False, True]) # Растягивается по ширине, фикс. высота
        self.horizontal_layout.setPlacementy("center")
        self.horizontal_layout.setPaddings([10])
        # --- Создание и настройка кнопки "Cancel" (вторичное действие) ---
        self.cancel_btn = TextButton(self.horizontal_layout, "Отмена")
        self.cancel_btn.setSize(110, 40)
        self.cancel_btn.setFixedSizes([True, True])
        self.cancel_btn.setFont(None, 18)
        self.cancel_btn.setColors([TEXT_COLOR, TEXT_COLOR])
        self.cancel_btn.setBackgroundColors([BTN_CANCEL_BG, BTN_CANCEL_HOVER])
        self.cancel_btn.setBorderColors([LINE_EDIT_BORDER, LINE_EDIT_BORDER]) # Рамка в том же стиле
        self.cancel_btn.setBorderWidth(1)
        self.cancel_btn.setBorderRadius(8)
        
        # --- Создание и настройка кнопки "OK" (основное действие) ---
        self.ok_btn = TextButton(self.horizontal_layout, "OK")
        self.ok_btn.setSize(110, 40)
        self.ok_btn.setFixedSizes([True, True])
        self.ok_btn.setFont(None, 18)
        self.ok_btn.setColors([WHITE, WHITE]) # Белый текст на синем фоне
        self.ok_btn.setBackgroundColors([PRIMARY_BLUE, PRIMARY_BLUE_HOVER])
        self.ok_btn.setBorderWidth(0) # Без рамки, т.к. есть яркий фон
        self.ok_btn.setBorderRadius(8)

        # --- Добавление виджетов в слои ---
        self.horizontal_layout.addWidget(self.cancel_btn)
        self.horizontal_layout.addWidget(self.ok_btn)

        self.addWidget(self.line_edit)
        self.addWidget(self.horizontal_layout)


# ----------------------------------- ONLY FOR THE GAME -------------------------------------
# ======================================================================
# НОВЫЙ КЛАСС ВЫБОРА УРОВНЯ - MyLevels (Версия 2.0)
# Замените старый класс MyLevels на этот
# ======================================================================

class MyLevels(StackedGridLayout):
    """
    Красивый и современный виджет для выбора уровня.
    
    Принимает:
    - parent: родительский виджет.
    - dims: кортеж (rows, cols) для сетки уровней на странице.
    - level_names: СПИСОК С НАЗВАНИЯМИ УРОВНЕЙ для создания кнопок.
    """
    def __init__(self, parent, dims):
        try:
            with shelve.open(save_path('.levels'), 'r') as shelf:
                filenames = [
                    filename
                    for filename, _ in sorted(
                        [(key, val) for key, val in shelf.items() if isinstance(val, dict) and 'no' in val], 
                        key=lambda conf: conf[1]['no']
                    )
                ]
        except:
            filenames = []
        level_names = filenames[::-1]
        self.style = {
            "bg": (240, 242, 245),
            "border": (220, 223, 227),
            "text_dark": (50, 50, 50),
            "text_light": (255, 255, 255),
            "accent": (52, 152, 219),
            "accent_darker": (41, 128, 185),
            "button_bg": (255, 255, 255),
            "button_border": (210, 214, 218)
        }
        self.selected_level_button = None

        super().__init__(parent, dims)

        self.setBackgroundColors([self.style["bg"], self.style["bg"]])
        self.setBorderColors([self.style["border"], self.style["border"]])
        self.setBorderWidth(1)
        self.setBorderRadius(16)
        self.setPaddings([20])

        for name in level_names:
            self.add_level_button(name)

    def allReallWidgets(self, layout):
        result = []
        for widget in layout.widgets:
            if isinstance(widget, Layout):
                result += self.allReallWidgets(widget)
            else:
                result += [widget]
        return result

    def setTransparentBackground(self, transparentBackground):
        super().setTransparentBackground(transparentBackground)
        for widget in self.allReallWidgets(self):
            widget.setTransparentBackground(False)

    def _create_new_page(self):
        grid = GridLayoutV(self)
        grid.setDims(*self.dims)
        
        # Применяем наш стиль к гриду
        grid.setAllRows('setSpace', 10) # <-- УВЕЛИЧИВАЕМ РАССТОЯНИЕ МЕЖДУ КНОПКАМИ
        grid.setAllRows('setPlacements', 'center', 'center')
        grid.setAllRows('setBackgroundColors', [self.style["bg"]] * 2)
        grid.setAllRows('setBorderWidth', 0)
        
        return grid

    def add_level_button(self, level_name):
        container = HorizontalLayout(self)
        container.setSpace(10)
        container.setPlacements('center', 'center')

        btn = TextButton(container, text=str(level_name))
        btn.setFont(None, None)

        
        btn.setPaddings([10])
        btn.setBorderRadius(12)
        btn.setBorderWidth(1)
        btn.setColors([self.style["text_dark"], "black"])
        btn.setBackgroundColors(["black", (240, 240, 0)])
        btn.setBorderColors([self.style["button_border"], self.style["accent_darker"]])

        with shelve.open(save_path('.levels'), 'r') as shelf:
            level_config = shelf[level_name]

        btn.onClick = lambda config=level_config: self.parent.app.load_my_own_level(config)

        del_btn = TextButton(container, "X")
        del_btn.setSize(30, 30)
        del_btn.setFixedSizes([True, True])
        del_btn.setFont(None, 20)
        del_btn.setColors([(255, 255, 255), (255, 255, 255)])
        del_btn.setBackgroundColors([(200, 0, 0), (255, 0, 0)])
        del_btn.setBorderColors([(150, 0, 0), (180, 0, 0)])
        del_btn.setBorderRadius(8)
        del_btn.onClick = lambda name=level_name: self.parent.app.delete_level(name)

        container.addWidget(btn)
        container.addWidget(del_btn)

        self.addWidget(container)

    def addWidget(self, widget):
        if self.current_grid is None or self.current_grid.isFull():
            self.current_grid = self._create_new_page()
            super(StackedGridLayout, self).addWidget(
                self.current_grid, 
                space=15, 
                arrowColors=[self.style["button_bg"], self.style["button_border"]]
            )
        self.current_grid.appendWidgetFree(widget)

    def render(self, surf):
        super().render(surf)

class WarningMessageBox(VerticalLayout):
    def __init__(self, parent, text="Warning"):
        super().__init__(parent)

        BG_COLOR = (248, 215, 218)  # light red background
        BORDER_COLOR = (220, 53, 69)  # red border
        TEXT_COLOR = (114, 28, 36)   # dark red text
        PRIMARY_RED = (220, 53, 69)  # red for button
        PRIMARY_RED_HOVER = (200, 30, 50)

        self.setBackgroundColors([BG_COLOR, BG_COLOR])
        self.setBorderColors([BORDER_COLOR, BORDER_COLOR])
        self.setBorderWidth(1)
        self.setBorderRadius(12)
        self.setPaddings([10])
        self.setSpace(15)

        self.message_label = TextButton(self, text)
        self.message_label.setClickable(False)
        self.message_label.setBackgroundColors([BG_COLOR, BG_COLOR])
        self.message_label.setBorderWidth(0)
        self.message_label.setColors([TEXT_COLOR, TEXT_COLOR])

        self.ok_btn = TextButton(self, "OK")
                # --- Создание и настройка кнопки "OK" (основное действие) ---
        self.ok_btn.setSize(110, 40)
        self.ok_btn.setFixedSizes([True, True])
        self.ok_btn.setFont(None, 18)
        self.ok_btn.setColors([WHITE, WHITE]) # Белый текст на синем фоне
        self.ok_btn.setBackgroundColors([PRIMARY_RED, PRIMARY_RED_HOVER])
        self.ok_btn.setBorderWidth(0)
        self.ok_btn.setBorderRadius(8)
        # добавляем отступ слева и снизу
        self.ok_btn.setMargins([0, 0, 10, 10])


        self.addWidget(self.message_label)
        self.addWidget(self.ok_btn)

# ======================================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# Замените ваш `if __name__ == "__main__":` на этот код, чтобы увидеть результат
# ======================================================================
# ======================================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ (Версия 2.0)
# Замените ваш `if __name__ == "__main__":` на этот код
# ======================================================================
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 750))
    pygame.display.set_caption("Красивый выбор уровня v2.0")

    main_layout = VerticalLayout(None)
    main_layout.rect = screen.get_rect()
    main_layout.innerRect = main_layout.rect
    main_layout.setBackgroundColors([(45, 52, 54)]*2)
    main_layout.setBorderWidth(0)
    main_layout.setSpace(10)
    main_layout.setPlacementy('center')

    title_label = TextButton(main_layout, "Выберите уровень")
    title_label.setHeight(80)
    title_label.setFixedSizes([False, True])
    title_label.setFont(None, 60)
    title_label.setColors([(255, 255, 255), (255, 255, 255)])
    title_label.setClickable(False)
    title_label.setBackgroundColors([(45, 52, 54)]*2) 
    title_label.setBorderWidth(0)
    
    # --- ГЛАВНЫЕ ИЗМЕНЕНИЯ ЗДЕСЬ ---
    # 1. Создаем список с названиями наших уровней
    my_level_list = [
        "1", "2", "3", "4", "5", "Лес", "Пещеры", "Замок",
        "Подземелье", "10", "11", "Снега", "Пустыня", "14",
        "Болото", "Финальный босс"
    ]

    # 2. Задаем сетку (например, 2 строки по 4 уровня на странице)
    DIMS = (2, 4)
    
    # 3. Создаем виджет, передавая ему наш список уровней
    my_levels_widget = MyLevels(main_layout, dims=DIMS, level_names=my_level_list)

    # my_levels_widget.setSize(800, 450) # Сделаем виджет чуть побольше
    # my_levels_widget.setFixedSizes([True, True])

    main_layout.addWidget(title_label)
    main_layout.addWidget(my_levels_widget)

    main_layout.dispose()
    
    state = State()
    clock = pygame.time.Clock()
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        state.update(events)
        main_layout.update(state)
        
        screen.fill((45, 52, 54))
        main_layout.render(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
