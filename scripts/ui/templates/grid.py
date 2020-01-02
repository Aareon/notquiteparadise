import logging
import pygame
from typing import List, Tuple
from scripts.ui.templates.widget import Widget
from scripts.ui.templates.widget_style import WidgetStyle


class Grid(Widget):
    """
    A structured container for other widgets. Draws children left to right, and row by row, to populate the grid.
    Overrides child's position. Can take size 0 children as will size on init.
    """

    def __init__(self, base_style: WidgetStyle, x: int = 0, y: int = 0, width: int = 0, height: int = 0,
            children: List = None,  name: str = "grid", rows: int = 1, columns: int = 1, gap_between_cells: int = 2):
        super().__init__(base_style, x, y, width, height, children, name)

        self.rows = rows
        self.columns = columns
        self.gap_between_cells = gap_between_cells
        self.cell_width = 0  # calculated in a moment
        self.cell_height = 0  # calculated in a moment

        # TODO - add init flag to determine if cells resize or not. should be customisable.

        self.update()

    def update(self):
        """
        If dirty update cell size, child size and position.
        """
        if self.is_dirty:
            self.update_cell_size()
            self.resize_children()
            self.update_childrens_pos()

        super().update()

    def draw(self, surface):
        """
        Draw the border, background and any children. OVERRIDES super().draw.

        Args:
            surface ():
        """
        super().draw(surface)

    def resize_children(self):
        """
        Resize the cells in line with the number of rows and columns
        """
        for child in self.children:
            child.rect.width = self.cell_width
            child.rect.height = self.cell_height

            child.is_dirty = True

    def update_childrens_pos(self):
        """
        Align children's position to the grid. Rows then cols.
        """
        rows = self.rows
        cols = self.columns
        gap = self.gap_between_cells
        width = self.cell_width
        height = self.cell_height
        row = 0
        column = 0

        # draw all contained widgets
        for child in self.children:
            x = int((column * (width + gap)) + gap) + self.rect.x
            y = int((row * (height + gap)) + gap) + self.rect.y
            cell_rect = pygame.Rect(x, y, width, height)
            child.rect = cell_rect

            row += 1
            if row >= rows:
                row = 0
                column += 1

                # check if all of the grid is full
                if column == cols:
                    break
                elif column > cols:
                    logging.warning(f"{self.name} tried to add more children than grid`s rows and cols.")
                    break

    def update_cell_size(self):
        """
        Ensure cells can fit based on rows and cols required
        """
        # calc size
        self.cell_width = int((self.rect.width - ((self.base_style.border_size + self.gap_between_cells) * 2)) /
                              self.columns)
        self.cell_height = int((self.rect.height - ((self.base_style.border_size + self.gap_between_cells) * 2)) /
                              self.rows)

    def get_cell_size(self) -> Tuple:
        """
        Get the size of the cells in the grid.

        Returns:
            Tuple: cell width, cell height

        """
        return self.cell_width, self.cell_height
