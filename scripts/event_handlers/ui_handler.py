
import logging

from scripts.core.constants import EventTopics, GameEventTypes, GameStates, EntityEventTypes, \
    UIEventTypes, MouseButtons, TILE_SIZE, MessageEventTypes, UIElementTypes
from scripts.events.entity_events import UseSkillEvent
from scripts.events.game_events import ChangeGameStateEvent
from scripts.events.message_events import MessageEvent
from scripts.global_singletons.event_hub import publisher
from scripts.global_singletons.managers import game_manager, ui_manager, world_manager
from scripts.event_handlers.pub_sub_hub import Subscriber

class UiHandler(Subscriber):
    """
    Handle events that effect the UI
    """

    def __init__(self, event_hub):
        Subscriber.__init__(self, "ui_handler", event_hub)
        # TODO - all UI functionality to watch events and update UI in response

    def run(self, event):
        """
        Process the events
        """

        # log that event has been received
        logging.debug(f"{self.name} received {event.topic}:{event.event_type}")

        if event.topic == EventTopics.UI:
            if event.event_type == UIEventTypes.CLICK_UI:
                button = event.button_pressed
                mouse_x = event.mouse_x
                mouse_y = event.mouse_y
                clicked_element = ui_manager.Mouse.get_colliding_ui_element_type(mouse_x, mouse_y)
                game_state = game_manager.game_state

                # Selecting an entity
                if button == MouseButtons.RIGHT_BUTTON and clicked_element == UIElementTypes.CAMERA:
                    self.attempt_to_set_selected_entity(mouse_x, mouse_y)

                # Selecting a skill
                elif button == MouseButtons.LEFT_BUTTON and clicked_element == UIElementTypes.SKILL_BAR:
                    self.attempt_to_trigger_targeting_mode(mouse_x, mouse_y)

                # using a selected skill
                elif button == MouseButtons.LEFT_BUTTON and clicked_element == UIElementTypes.CAMERA  and game_state \
                        == GameStates.TARGETING_MODE:
                    self.attempt_to_use_targeted_skill()

        if event.topic == EventTopics.ENTITY:

            # if an entity acts then hide the entity info element
            ui_manager.Element.set_element_visibility(UIElementTypes.ENTITY_INFO, False)

            # update UI based on entity action taken
            if event.event_type == EntityEventTypes.LEARN:
                ui_manager.Element.update_skill_bars_icons()
            elif event.event_type == EntityEventTypes.DIE:
                ui_manager.Element.update_entity_queue()
            elif event.event_type == EntityEventTypes.MOVE:
                self.refresh_camera()

        if event.topic == EventTopics.GAME:
            if event.event_type == GameEventTypes.CHANGE_GAME_STATE:

                if event.new_game_state == GameStates.GAME_INITIALISING:
                    self.init_ui()

                # if changing to targeting mode then turn on targeting overlay
                elif event.new_game_state == GameStates.TARGETING_MODE:
                    self.trigger_targeting_overlay_and_entity_info(event.skill_to_be_used)

                # if the previous game state was targeting mode we must be moving to something else, therefore the
                # overlay is no longer needed
                elif game_manager.previous_game_state.TARGETING_MODE:
                    ui_manager.Element.set_element_visibility(UIElementTypes.TARGETING_OVERLAY, False)

            elif event.event_type == GameEventTypes.END_TURN:
                ui_manager.Element.update_entity_queue()







    @staticmethod
    def attempt_to_set_selected_entity(mouse_x, mouse_y):
        """
        Check if clicked location includes an entity and if so set it as selected to display its info.

        Args:
            mouse_x (int):
            mouse_y (int):
        """
        tile_pos = ui_manager.Mouse.get_relative_scaled_mouse_pos(mouse_x, mouse_y)
        tile_x = tile_pos[0] // TILE_SIZE
        tile_y = tile_pos[1] // TILE_SIZE
        entity = world_manager.Entity.get_entity_in_fov_at_tile(tile_x, tile_y)

        if entity:
            ui_manager.Element.set_selected_entity(entity)
            ui_manager.Element.set_element_visibility(UIElementTypes.ENTITY_INFO, True)
            ui_manager.Element.set_element_visibility(UIElementTypes.MESSAGE_LOG, False)
        else:
            ui_manager.Element.set_element_visibility(UIElementTypes.ENTITY_INFO, False)
            ui_manager.Element.set_element_visibility(UIElementTypes.ENTITY_INFO, True)

    @staticmethod
    def attempt_to_trigger_targeting_mode(mouse_x, mouse_y):
        """
        Check if a skill was clicked in the skill bar and set targeting mode.

        Args:
            mouse_x (int):
            mouse_y (int):
        """
        relative_mouse_pos = ui_manager.Mouse.get_relative_scaled_mouse_pos(mouse_x, mouse_y)
        skill_number = ui_manager.Mouse.get_skill_index_from_skill_clicked(relative_mouse_pos[0], relative_mouse_pos[1])

        # if we clicked a skill in the skill bar create the targeting overlay
        player = world_manager.player
        skill = player.actor.known_skills[skill_number]

        if skill:
            publisher.publish(ChangeGameStateEvent(GameStates.TARGETING_MODE, skill))
        else:
            logging.debug(f"Left clicked skill bar but no skill found.")

    def trigger_targeting_overlay_and_entity_info(self, skill_to_be_used):
        """
        Show the targeting overlay for the skill specified and update the entity info in line.

        Args:
            skill_to_be_used ():
        """
        from scripts.global_singletons.managers import world_manager
        # get info for initial selected tile
        # TODO - get nearest entity in range, use player only if nothing in range
        player = world_manager.player
        tile = world_manager.Map.get_tile(player.x, player.y)

        # set the info needed to draw the overlay
        ui_manager.Element.set_skill_being_targeted(skill_to_be_used)
        ui_manager.Element.update_targeting_overlays_tiles_in_range_and_fov()
        ui_manager.Element.set_selected_tile(tile)
        ui_manager.Element.update_targeting_overlays_tiles_in_skill_effect_range()

        # show the entity info
        self.trigger_entity_info(tile)

        # show the overlay
        ui_manager.Element.set_element_visibility(UIElementTypes.TARGETING_OVERLAY, True)

    @staticmethod
    def trigger_entity_info(tile):
        """
        Trigger the entity info element and update the selected entity based on the tile.

        Args:
            tile (Tile):
        """
        entity = world_manager.Entity.get_blocking_entity_at_location(tile.x, tile.y)
        ui_manager.Element.set_selected_entity(entity)
        ui_manager.Element.set_element_visibility(UIElementTypes.ENTITY_INFO, True)

    @staticmethod
    def attempt_to_use_targeted_skill():
        """
        Check if player can use the selected skill on the selected target and if so trigger use.
        """
        selected_tile = ui_manager.targeting_overlay.selected_tile
        player = world_manager.player
        skill_being_targeted = ui_manager.targeting_overlay.skill_being_targeted

        if world_manager.Skill.can_use_skill(player, (selected_tile.x, selected_tile.y),
                                             skill_being_targeted):
            publisher.publish((UseSkillEvent(player, (selected_tile.x, selected_tile.y),
                                             skill_being_targeted)))
        else:
            # we already checked player can afford when triggering targeting mode so must be wrong target
            msg = f"You can't do that there!"
            publisher.publish(MessageEvent(MessageEventTypes.BASIC, msg))

    @staticmethod
    def refresh_camera():
        """
        Refresh the camera's information to show the correct tiles in view
        """
        # determine what size of tiles to get
        row_size, col_size = ui_manager.Element.get_camera_view_size()

        # retrieve that size of tiles
        from scripts.global_singletons.managers import world_manager
        # TODO - extend to work with rectangle rather than square
        tiles = world_manager.FOV.get_tiles_in_range_and_fov_of_player(row_size)

        # update camera
        ui_manager.Element.set_tiles_in_camera(tiles)

    def init_ui(self):
        """
        Initialise the UI
        """
        # show ui
        ui_manager.Element.set_element_visibility(UIElementTypes.CAMERA, True)
        ui_manager.Element.set_element_visibility(UIElementTypes.MESSAGE_LOG, True)
        ui_manager.Element.set_element_visibility(UIElementTypes.ENTITY_QUEUE, True)
        ui_manager.Element.set_element_visibility(UIElementTypes.SKILL_BAR, True)

        # update camera
        self.refresh_camera()