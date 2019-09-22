
import logging
import pygame


from scripts.global_singletons.data_library import library
from scripts.ui_elements.palette import Palette
from scripts.core.constants import TILE_SIZE,  SkillShapes
from scripts.core.fonts import Font
from scripts.skills.skill import Skill


class TargetingOverlay:
    """
    The targeting overlay showing possible targets

    Attributes:
        skill_being_targeted (Skill): the skill in use

    """

    def __init__(self):
        # data
        self.skill_being_targeted = None
        self.tiles_in_range_and_fov = []
        self.tiles_in_skill_effect_range = []
        self.selected_tile = None
        self.is_visible = True

        # drawing info
        self.select_border_width = 5
        self.highlight_border_width = 3

        logging.debug(f"TargetingOverlay initialised.")

    def draw(self, surface):
        """
        Draw the targeting overlay

        Args:
            surface:
        """
        self.draw_range_highlight(surface)
        self.draw_effect_highlight(surface)
        self.draw_selected_tile(surface)

    def draw_range_highlight(self, surface):
        """
        Draw the highlights on top of the tiles_in_range_and_fov

        Args:
            surface:
        """
        from scripts.global_singletons.managers import ui_manager
        palette = ui_manager.Palette

        tile_colour = palette.highlighted_range_border
        rect = pygame.rect.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        # draw highlight on all tiles listed, except the one selected
        for tile in self.tiles_in_range_and_fov:
            if tile != self.selected_tile:
                # amend rect position to reflect tile sizes
                rect.x = tile.x * TILE_SIZE
                rect.y = tile.y * TILE_SIZE
                pygame.draw.rect(surface, tile_colour, rect, self.highlight_border_width)

    def draw_effect_highlight(self, surface):
        """
        Draw the highlights on top of the tiles_in_skill_effect_range

        Args:
            surface:
        """
        from scripts.global_singletons.managers import ui_manager
        palette = ui_manager.Palette

        tile_colour = palette.highlighted_effect_border
        rect = pygame.rect.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        # draw highlight on all tiles listed, except the one selected
        for tile in self.tiles_in_skill_effect_range:
            if tile != self.selected_tile:
                # amend rect position to reflect tile sizes
                rect.x = tile.x * TILE_SIZE
                rect.y = tile.y * TILE_SIZE
                pygame.draw.rect(surface, tile_colour, rect, self.highlight_border_width)

    def draw_selected_tile(self, surface):
        """
        Draw the highlight on the selected_tile.
        Args:
            surface:
        """
        from scripts.global_singletons.managers import ui_manager
        palette = ui_manager.Palette

        tile_colour = palette.selected_tile_border
        rect = pygame.rect.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        rect.x = self.selected_tile.x * TILE_SIZE
        rect.y = self.selected_tile.y * TILE_SIZE

        pygame.draw.rect(surface, tile_colour, rect, self.select_border_width)







