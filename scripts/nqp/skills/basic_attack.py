from __future__ import annotations

from typing import TYPE_CHECKING, Type
from snecs.types import EntityID
from scripts.engine import skill, utility, world
from scripts.engine.core.constants import PrimaryStat, Shape, TargetTag, DamageType
from scripts.engine.core.definitions import DamageEffectData
from scripts.engine.world_objects.tile import Tile

if TYPE_CHECKING:
    from typing import Union, Optional, Any, Tuple, Dict, List

def use():
    pass


def activate(causing_entity: EntityID, target_tiles: List[Tile]):
    # create damage effect
    effect_dict = {
        "accuracy": 0,
        "stat_to_target": PrimaryStat.VIGOUR,
        "shape": Shape.TARGET,
        "shape_size": 1,
        "required_tags": [
            TargetTag.OTHER_ENTITY
        ],
        "damage": 2,
        "damage_type": DamageType.MUNDANE,
        "mod_amount": 0.1,
        "mod_stat": PrimaryStat.CLOUT
    }
    effect = DamageEffectData(**effect_dict)

    for tile in target_tiles:
        coords = utility.get_coords_from_shape(effect.shape, effect.shape_size)
        effected_tiles = world.get_tiles(tile.x, tile.y, coords)
        skill.process_effect(effect, effected_tiles, causing_entity)



##################################################
# something triggers a UseSkillEvent
# this checks affordability, pays skill costs and  creates a projectile
# -> we could move projectile creation to a "use" method here to allow for additional creation actions
# projectile given turn, as any other entity
# projectile travels in direction until it activates or expires
# -> this should call the relevant skill activation

# ! make sure to use standardised funcs held in skills.py where possible
# ! think about how to make it easy to amend lots of values - use base values and an offset?
# ! there probs needs to be an activation effect in the json