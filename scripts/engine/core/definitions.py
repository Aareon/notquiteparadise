from __future__ import annotations

from abc import ABC

import pygame
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional, Union
from snecs.typedefs import EntityID
from scripts.engine.core.constants import EffectTypeType, PrimaryStatType, ProjectileExpiry, TargetTag, TargetTagType, \
    DamageTypeType, \
    AfflictionCategoryType, ShapeType, TerrainCollision, TerrainCollisionType, TravelMethod, TravelMethodType, \
    ProjectileExpiryType, DirectionType, SecondaryStatType, ProjectileSpeedType, ProjectileSpeed, EffectType, Shape, \
    ResourceType, TargetingMethod, TargetingMethodType, Direction, Resource
from scripts.engine.core.extend_json import register_dataclass_with_json


if TYPE_CHECKING:
    from scripts.nqp.actions.skills import Skill


######################### SKILLS ##################################

@register_dataclass_with_json
@dataclass
class SkillData:
    """
    Data class for a skill. Used by the library to load from json.
    """
    # TODO - rename relevant sections to indicate they are base values
    # how do we know it?
    name: str = field(default="none")
    description: str = field(default="none")
    icon: str = field(default="none")
    class_name: str = ""

    # when do we use it?
    required_tags: List[TargetTagType] = field(default_factory=list)

    # what does it cost?
    resource_type: ResourceType = Resource.STAMINA
    resource_cost: int = 0
    time_cost: int = 0
    cooldown: int = 0

    # how does it travel from the user?
    targeting_method: TargetingMethodType = TargetingMethod.TARGET
    target_directions: List[DirectionType] = field(default_factory=list)

    # what is the area of effect?
    shape: ShapeType = Shape.TARGET
    shape_size: int = 1

    # projectile info
    uses_projectile: bool = True
    projectile_speed: ProjectileSpeedType = ProjectileSpeed.SLOW
    travel_method: TravelMethodType = TravelMethod.STANDARD
    range: int = 1
    terrain_collision: TerrainCollisionType = TerrainCollision.FIZZLE
    expiry_type: ProjectileExpiryType = ProjectileExpiry.FIZZLE


@register_dataclass_with_json
@dataclass
class ProjectileData:
    """
    Data class for a projectile
    """
    # what created it?
    creator: EntityID
    skill_name: str = field(default="none")
    skill_instance: Skill = False
    name: str = ""
    description: str = ""

    # what does it look like?
    sprite: str = field(default="none")

    # who are we targeting?
    required_tags: List[TargetTagType] = field(default_factory=list)

    # how does it travel?
    direction: Optional[DirectionType] = None
    speed: ProjectileSpeedType = ProjectileSpeed.SLOW
    travel_method: Optional[TravelMethodType] = None
    range: int = 1

    # how does it interact?
    terrain_collision: Optional[TerrainCollisionType] = None
    expiry_type: Optional[ProjectileExpiryType] = None


####################### EFFECTS ######################################

@register_dataclass_with_json
@dataclass
class EffectData(ABC):
    """
    Base data class for an effect.
    """
    # who am I?
    originator: Optional[EntityID] = None  # actor
    creators_name: Optional[str] = None  # skill, projectile, etc.'s name
    effect_type = EffectType.MOVE

    # who are we targeting?
    required_tags: List[TargetTagType] = field(default_factory=list)

    # how are we targeting?
    stat_to_target: Optional[PrimaryStatType] = None
    accuracy: int = 0

    # what is the area of effect?
    shape: ShapeType = Shape.TARGET
    shape_size: int = 1

    # what next?
    success_effects: List[Optional[EffectData]] = field(default_factory=list)
    fail_effects: List[Optional[EffectData]] = field(default_factory=list)


@register_dataclass_with_json
@dataclass
class ApplyAfflictionEffectData(EffectData):
    """
    Data for the Apply Afflictions effect.
    """
    effect_type = EffectType.APPLY_AFFLICTION

    duration: int = 0
    affliction_name: str = field(default="none")


@register_dataclass_with_json
@dataclass
class DamageEffectData(EffectData):
    """
    Data for the Damage effect.
    """
    effect_type = EffectType.DAMAGE

    damage: int = 0
    damage_type: Optional[DamageTypeType] = None
    mod_stat: Optional[PrimaryStatType] = None
    mod_amount: float = 0.0


@register_dataclass_with_json
@dataclass
class AffectStatEffectData(EffectData):
    """
    Data for the Affect Stat effect.
    """
    effect_type = EffectType.AFFECT_STAT

    stat_to_affect: Optional[PrimaryStatType] = None
    affect_stat_amount: int = 0


@register_dataclass_with_json
@dataclass
class AddAspectEffectData(EffectData):
    """
    Data for the Add Aspect effect.
    """
    effect_type = EffectType.ADD_ASPECT

    aspect_name: str = field(default="none")  # TODO - confirm if we want aspect name or key


@register_dataclass_with_json
@dataclass
class RemoveAspectEffectData(EffectData):
    """
    Data for the Remove Aspect effect.
    """
    effect_type = EffectType.REMOVE_ASPECT

    aspect_name: str = field(default="none")  # TODO - confirm if we want aspect name or key


@register_dataclass_with_json
@dataclass
class UseSkillEffectData(EffectData):
    """
    Data for the  Trigger Skill effect.
    """
    effect_type = EffectType.TRIGGER_SKILL

    skill_name: str = field(default="none")  # TODO - confirm if we want skill name or key
    required_tags: List = field(default_factory=list)


@register_dataclass_with_json
@dataclass
class ActivateSkillEffectData(EffectData):
    """
    Data for the  Activate Skill effect.
    """
    effect_type = EffectType.TRIGGER_SKILL

    skill_name: str = field(default="none")  # TODO - confirm if we want skill name or key


@register_dataclass_with_json
@dataclass
class KillEntityEffectData(EffectData):
    """
    Data for the  Kill Entity effect.
    """
    effect_type = EffectType.KILL

    # use an init to prevent need to specify default arg
    def __init__(self, target_entity):
        self.target_entity: EntityID = target_entity


@register_dataclass_with_json
@dataclass
class MoveActorEffectData(EffectData):
    """
    Data for the  Activate Skill effect.
    """
    effect_type = EffectType.MOVE

    # TODO - likley to need different options to get the direction, e.g. absolute, away, towards
    move_direction: DirectionType = Direction.CENTRE
    # TODO - this needs to be determined at use, between the two affected entities
    move_amount: int = 0
    move_target: EntityID = 1  # type: ignore
    allow_bump_attack: bool = False
    move_time_cost: int = 0


##################### ACTORS #################################

@register_dataclass_with_json
@dataclass
class BaseStatData:
    """
    Data class to contain primary and secondary stats
    """
    primary: Dict[str, BasePrimaryStatData] = field(default_factory=dict)
    secondary: Dict[str, BaseSecondaryStatData] = field(default_factory=dict)


@register_dataclass_with_json
@dataclass
class BasePrimaryStatData:
    """
    Data class for primary  stats
    """
    name: str = field(default="none")
    primary_stat_type: Optional[PrimaryStatType] = None
    base_value: int = 0


@register_dataclass_with_json
@dataclass
class BaseSecondaryStatData:
    """
    Data class for secondary stats
    """
    name: str = field(default="none")
    secondary_stat_type: Optional[SecondaryStatType] = None
    base_value: int = 0
    vigour_mod: int = 0
    clout_mod: int = 0
    skullduggery_mod: int = 0
    bustle_mod: int = 0
    exactitude_mod: int = 0


@register_dataclass_with_json
@dataclass
class CharacteristicSpritesData:
    """
    Possible sprites for a characteristic
    """
    icon: Optional[pygame.Surface] = None
    idle: Optional[pygame.Surface] = None
    attack: Optional[pygame.Surface] = None
    hit: Optional[pygame.Surface] = None
    dead: Optional[pygame.Surface] = None
    move: Optional[pygame.Surface] = None


@register_dataclass_with_json
@dataclass
class CharacteristicSpritePathsData:
    """
    Possible sprites paths for a characteristic
    """
    icon: str = field(default="none")
    idle: str = field(default="none")
    attack: str = field(default="none")
    hit: str = field(default="none")
    dead: str = field(default="none")
    move: str = field(default="none")


@register_dataclass_with_json
@dataclass
class CharacteristicData:
    """
    Data class for an aspects
    """
    name: str = field(default="none")
    description: str = field(default="none")
    sprite_paths: CharacteristicSpritePathsData = field(default_factory=CharacteristicSpritePathsData)
    sight_range: int = 0
    vigour: int = 0
    clout: int = 0
    skullduggery: int = 0
    bustle: int = 0
    exactitude: int = 0
    known_skills: List[str] = field(default_factory=list)
    permanent_afflictions: List[str] = field(default_factory=list)


@register_dataclass_with_json
@dataclass()
class AfflictionData:
    """
    Data class for an Afflictions
    """
    name: str = field(default="none")
    class_name: str = field(default="none")
    description: str = field(default="none")
    icon: str = field(default="none")
    category: Optional[AfflictionCategoryType] = None
    shape: ShapeType = Shape.TARGET
    shape_size: int = 1
    required_tags: List[TargetTagType] = field(default_factory=list(TargetTag.OTHER_ENTITY))
    identity_tags: List[EffectTypeType] = field(default_factory=list(EffectType.DAMAGE))


########################## WORLD #########################################

@register_dataclass_with_json
@dataclass
class AspectData:
    """
    Data class for an aspects
    """
    name: str = field(default="none")
    description: str = field(default="none")
    duration: int = 0
    sprite: str = field(default="none")
    blocks_sight: bool = False
    blocks_movement: bool = False


#################### GODS ###################################################

@register_dataclass_with_json
@dataclass
class AttitudeData:
    """
    Data class for  a god's attitude
    """
    action: str = field(default="none")  # TODO - standardise what this can be
    opinion_change: int = 0


@register_dataclass_with_json
@dataclass
class InterventionData:
    """
    Data class for a god's intervention
    """
    skill_key: str = field(default="none")  # TODO - confirm if we want skill key or name
    required_opinion: int = 0


@register_dataclass_with_json
@dataclass
class GodData:
    """
    Data class for a god
    """
    name: str = field(default="none")
    description: str = field(default="none")
    sprite_paths: CharacteristicSpritePathsData = field(default_factory=CharacteristicSpritePathsData)
    attitudes: Dict[int, AttitudeData] = field(default_factory=dict)
    interventions: Dict[int, InterventionData] = field(default_factory=dict)