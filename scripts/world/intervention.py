
import logging

from scripts.core.constants import MessageEventTypes
from scripts.events.message_events import MessageEvent
from scripts.global_singletons.data_library import library
from scripts.global_singletons.event_hub import publisher
from scripts.world.god import God


class Intervention:
    """
    An intervention to be used by a god

    Attributes:
            name(str):
            owner(God):
    """
    def __init__(self, owner, intervention_name):
        self.owner = owner  # type: God
        self.name = intervention_name

        # TODO - add cooldown

    def use(self, target_pos):
        """
        Use the intervention

        Args:
            target_pos (tuple): x y of the target
        """
        from scripts.global_singletons.managers import world_manager
        data = library.get_god_intervention_data(self.owner.name, self.name)

        target_x, target_y = target_pos

        coords = world_manager.Skill.create_shape(data.shape, data.shape_size)
        effected_tiles = world_manager.Map.get_tiles(target_x, target_y, coords)

        # apply any effects
        for effect_name, effect_data in data.effects.items():
            effect = world_manager.Skill.create_effect(self, effect_data.effect_type)
            effect.trigger(effected_tiles)

        # logging
        tile = world_manager.Map.get_tile(target_x, target_y)
        entity = world_manager.Map.get_entity_on_tile(tile)
        msg = f"#col.info {self.owner.name} intervened, using {self.name} on {entity.name}."
        publisher.publish(MessageEvent(MessageEventTypes.BASIC, msg))