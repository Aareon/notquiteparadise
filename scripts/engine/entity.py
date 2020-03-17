from __future__ import annotations as _annotations

import dataclasses
import logging
import random
import esper
import pygame
import tcod.map
from typing import TYPE_CHECKING, TypeVar
from scripts.engine import utility, world, debug
from scripts.engine.ai import ProjectileBehaviour
from scripts.engine.component import Component, IsPlayer, Position, Identity, Race, Savvy, Homeland, Aesthetic, \
    IsGod, Opinion, Knowledge, Resources, HasCombatStats, Blocking, FOV, Interactions, IsProjectile, Behaviour
from scripts.engine.core.constants import TILE_SIZE, ICON_SIZE, ENTITY_BLOCKS_SIGHT, FOVInfo, InteractionCause, Effect
from scripts.engine.core.definitions import CharacteristicSpritesData, CharacteristicSpritePathsData, InteractionData, \
    TriggerSkillEffectData
from scripts.engine.world_objects.combat_stats import CombatStats
from scripts.engine.world_objects.tile import Tile
from scripts.engine.library import library

if TYPE_CHECKING:
    from typing import Union, Type, List, Dict, Tuple, Any, Optional

_C = TypeVar("_C", bound=Component)
_esper = esper.World()

# TODO - Consider renaming module. Existence? Being?
###################### GET ############################################

get_entitys_components = _esper.components_for_entity
get_component = _esper.get_component
get_components = _esper.get_components
try_component = _esper.try_component
has_component = _esper.has_component


def get_player() -> Optional[int]:
    """
    Get the player.
    """
    for entity, flag in get_component(IsPlayer):
        return entity
    return None


def get_entity(unique_component: Type[Component]) -> Optional[int]:
    """
    Get a single entity that has a component. If multiple entities have the given component only the 
    first found is returned.
    """
    entities = []
    for entity, flag in get_component(unique_component):
        entities.append(entity)

    num_entities = len(entities)

    if num_entities > 1:
        logging.warning(f"Tried to get an entity with {unique_component} component but found {len(entities)} "
                        f"entities with that component.")
    elif num_entities == 0:
        logging.warning(f"Tried to get an entity with {unique_component} component but found none.")
        return None

    return entities[0]


def get_entities_and_components_in_area(area: List[Tile], *components: Any) -> Dict[int, Tuple[Any, ...]]:
    """
    Return a dict of entities and their specified components, plus Position. e.g. (Position, component1). If no
    components are specified the return will be (Position, None).

    N.B. Do not specify Position as a component.
    """
    entities = {}

    for entity, (pos, *rest) in get_components(*components):
        for tile in area:
            if tile.x == pos.x and tile.y == pos.y:
                entities[entity] = (pos, *rest)
    return entities


def get_entitys_component(entity: int, component: Type[_C]) -> Optional[_C]:
    """
    Get an entity's component.
    """
    if has_component(entity, component):
        return _esper.component_for_entity(entity, component)
    else:
        return None


def get_name(entity: int) -> str:
    """
    Get an entity's Identity component's name.
    """
    identity = get_identity(entity)
    if identity:
        name = identity.name
    else:
        name = f"Identity Component not found for {entity}."

    return name


def get_identity(entity: int) -> Optional[Identity]:
    """
    Get an entity's Identity component.
    """
    return get_entitys_component(entity, Identity)


def get_combat_stats(entity: int) -> CombatStats:
    """
    Create and return a stat object  for an entity.
    """
    return CombatStats(entity)


def get_primary_stat(entity: int, primary_stat: str) -> int:
    """
    Get an entity's primary stat.
    """
    stat = primary_stat
    value = 0

    for people in try_component(entity, Race):
        people_data = library.get_people_data(people.name)
        value += getattr(people_data, stat)

    for savvy in try_component(entity, Savvy):
        savvy_data = library.get_savvy_data(savvy.name)
        value += getattr(savvy_data, stat)

    for homeland in try_component(entity, Homeland):
        homeland_data = library.get_homeland_data(homeland.name)
        value += getattr(homeland_data, stat)

    # TODO - re add afflicitons
    # value += _manager.Affliction.get_stat_change_from_afflictions_on_entity(entity, primary_stat)

    # ensure no dodgy numbers, like floats or negative
    value = max(1, int(value))

    return value


def get_player_fov() -> Optional[tcod.map.Map]:
    """
    Get's the player's FOV component
    """
    player = get_player()
    if player:
        fov_c = get_entitys_component(player, FOV)
        if fov_c:
            return fov_c.map

    return None


######################### ENTITY EXISTENCE ##############################

def create(components: List[Component] = None) -> int:
    """
    Use each component in a list of components to create an entity
    """
    if components is None:
        components = []
    # create the entity
    entity = _esper.create_entity()

    # add all components
    for component in components:
        add_component(entity, component)

    return entity


def delete(entity: int):
    """
    Queues entity for removal from the world_objects. Happens at the next run of World.process.
    """
    if entity:
        _esper.delete_entity(entity)
        logging.info(f"Entity ({entity}) deleted.")
    else:
        logging.error("Tried to delete an entity but entity was None.")


def create_god(god_name: str) -> int:
    """
    Create an entity with all of the components to be a god. god_name must be in the gods json file.
    """
    data = library.get_god_data(god_name)
    god: List[Component] = []

    # get aesthetic info
    idle = utility.get_image(data.sprite_paths.idle, (TILE_SIZE, TILE_SIZE))
    icon = utility.get_image(data.sprite_paths.icon, (ICON_SIZE, ICON_SIZE))
    sprites = CharacteristicSpritesData(icon=icon, idle=idle)

    # get knowledge info
    interventions = data.interventions
    intervention_names = []
    for name, intervention in interventions.items():
        intervention_names.append(intervention.skill_key)

    god.append(Identity(data.name, data.description))
    god.append(Aesthetic(sprites.idle, sprites))
    god.append(IsGod())
    god.append(Opinion())
    god.append(Knowledge(intervention_names))
    god.append((Resources(9999, 9999)))
    entity = create(god)

    return entity


def create_actor(name: str, description: str, x: int, y: int, people_name: str, homeland_name: str,
        savvy_name: str, is_player: bool = False) -> int:
    """
    Create an entity with all of the components to be an actor. is_player is Optional and defaults to false.
    Returns entity ID.
    """
    # TODO - rename create player. add new method for create actor that uses actor characteristic

    actor: List[Component] = []

    # player components
    if is_player:
        actor.append(IsPlayer())

    # actor components
    actor.append(Identity(name, description))
    actor.append(Position(x, y))  # TODO - check position not blocked before spawning
    actor.append(HasCombatStats())
    actor.append(Blocking(True, ENTITY_BLOCKS_SIGHT))
    actor.append(Race(people_name))
    actor.append(Homeland(homeland_name))
    actor.append(Savvy(savvy_name))
    actor.append(FOV(world.create_fov_map()))

    entity = create(actor)

    # give full resources
    stats = get_combat_stats(entity)
    add_component(entity, Resources(stats.max_health, stats.max_stamina))

    # setup basic attack as a known skill and an interaction
    basic_attack_name = "basic_attack"
    known_skills = [basic_attack_name]  # N.B. All actors start with basic attack
    trigger_skill = TriggerSkillEffectData(skill_name=basic_attack_name)
    basic_attack = InteractionData(cause=InteractionCause.ENTITY_COLLISION, trigger_skill=trigger_skill)
    actor.append(Interactions({InteractionCause.ENTITY_COLLISION: basic_attack}))

    # get skills from characteristics
    people_data = library.get_people_data(people_name)
    if people_data.known_skills != ["none"]:
        known_skills += people_data.known_skills

    homeland_data = library.get_homeland_data(homeland_name)
    if homeland_data.known_skills != ["none"]:
        known_skills += homeland_data.known_skills

    savvy_data = library.get_savvy_data(savvy_name)
    if savvy_data.known_skills != ["none"]:
        known_skills += savvy_data.known_skills

    # add skills to entity
    add_component(entity, Knowledge(known_skills))

    # add aesthetic
    characteristics = [homeland_data.sprite_paths, people_data.sprite_paths, savvy_data.sprite_paths]
    sprites = build_characteristic_sprites(characteristics)
    add_component(entity, Aesthetic(sprites.idle, sprites))

    return entity


def create_projectile(creating_entity: int, skill_name: str, x: int, y: int, target_dir_x: int, target_dir_y: int):
    """
    Create an entity with all of the components to be a projectile. Returns entity ID.
    """
    data = library.get_skill_data(skill_name).projectile
    projectile: List[Component] = []

    # TODO - get aesthetic info
    name = get_name(creating_entity)
    projectile_name = f"{skill_name}'s projectile"
    desc = f"{name}'s {skill_name} projectile"
    projectile.append(Identity(projectile_name, desc))
    projectile.append(IsProjectile())
    projectile.append(Position(x, y))  # TODO - check position not blocked before spawning
    projectile.append(Behaviour(ProjectileBehaviour(creating_entity, (target_dir_x, target_dir_y), data.range,
                                                    skill_name)))

    entity = create(projectile)

    return entity


############################## COMPONENT ACTIONS ################################

def add_component(entity: int, component: Component):
    """
    Add a component to the entity
    """
    _esper.add_component(entity, component)


def build_characteristic_sprites(sprite_paths: List[CharacteristicSpritePathsData]) -> CharacteristicSpritesData:
    """
    Build a CharacteristicSpritesData class from a list of sprite paths
    """
    paths: Dict[str, List[str]] = {}
    sprites: Dict[str, List[pygame.Surface]] = {}
    flattened_sprites: Dict[str, pygame.Surface] = {}

    # bundle into cross-characteristic sprite path lists
    for characteristic in sprite_paths:
        char_dict = dataclasses.asdict(characteristic)
        for name, path in char_dict.items():
            # check if key exists
            if name in paths:
                paths[name].append(path)
            # if not init the dict
            else:
                paths[name] = [path]

    # convert to sprites
    for name, path_list in paths.items():
        # get the size to convert to
        if name == "icon":
            size = (ICON_SIZE, ICON_SIZE)
        else:
            size = (TILE_SIZE, TILE_SIZE)

        sprites[name] = utility.get_images(path_list, size)

    # flatten the images
    for name, surface_list in sprites.items():
        flattened_sprites[name] = utility.flatten_images(surface_list)

    # convert to dataclass
    converted = CharacteristicSpritesData(**flattened_sprites)
    return converted


def spend_time(entity: int, time_spent: int):
    """
    Add time_spent to the entity's total time spent.
    """
    # TODO - modify by time modifier stat
    if entity:
        resources = get_entitys_component(entity, Resources)
        if resources:
            resources.time_spent += time_spent
        else:
            debug.log_component_not_found(entity, "spend time", Resources)
    else:
        logging.error("Tried to spend entity's time but entity was None.")


def learn_skill(entity: int, skill_name: str):
    """
    Add the skill name to the entity's knowledge component.
    """
    if not has_component(entity, Knowledge):
        add_component(entity, Knowledge())
    knowledge = get_entitys_component(entity, Knowledge)

    if knowledge:
        knowledge.skills.append(skill_name)


def judge_action(entity: int, action: Any):
    """
    Have all entities alter opinions of the entity based on the action taken, if they have an attitude towards
    that  action. Action can be str if matching name, e.g. affliction name, or class, e.g. Hit Type name.
    """
    for ent, (is_god, opinion, identity) in get_components(IsGod, Opinion, Identity):

        attitudes = library.get_god_attitudes_data(identity.name)
        action_name = action

        # check if the god has an attitude towards the action and apply the opinion change,
        # adding the entity to the dict if necessary
        if action_name in attitudes:
            if entity in opinion.opinions:
                opinion.opinions[entity] = opinion.opinions[entity] + attitudes[action_name].opinion_change
            else:
                opinion.opinions[entity] = attitudes[action_name].opinion_change

            name = get_name(entity)
            logging.info(f"'{identity.name}' reacted to '{name}' using {action_name}.  New "
                         f"opinion = {opinion.opinions[entity]}")


def consider_intervening(entity: int, action: Any) -> List[Tuple[int, Any]]:
    """
    Have all entities consider intervening. Action can be str if matching name, e.g. affliction name,
    or class attribute, e.g. Hit Type name. Returns a list of tuples containing (god_entity_id, intervention name).
    """
    chosen_interventions = []
    desire_to_intervene = 10
    desire_to_do_nothing = 75  # weighting for doing nothing # TODO - move magic number to config

    for ent, (is_god, opinion, identity, knowledge) in get_components(IsGod, Opinion, Identity, Knowledge):
        attitudes = library.get_god_attitudes_data(identity.name)
        action_name = action

        # check if the god has an attitude towards the action and increase likelihood of intervening
        if action_name in attitudes:
            desire_to_intervene = 30

        # get eligible interventions and their weightings. Need separate lists for random.choices
        eligible_interventions = []
        intervention_weightings = []
        for intervention_name in knowledge.skills:
            intervention_data = library.get_god_intervention_data(identity.name, intervention_name)

            # is the god willing to intervene i.e. does the opinion score meet the required opinion
            opinion_score = opinion.opinions[entity]
            required_opinion = intervention_data.required_opinion
            # check if greater or lower, depending on whether required opinion is positive or negative
            if 0 <= required_opinion < opinion_score:
                amount_exceeding_requirement = opinion_score - required_opinion

                eligible_interventions.append(intervention_name)
                intervention_weightings.append(amount_exceeding_requirement)

            elif 0 > required_opinion > opinion_score:
                amount_exceeding_requirement = required_opinion - opinion_score  # N.B. opposite to above
                eligible_interventions.append(intervention_name)
                intervention_weightings.append(amount_exceeding_requirement)

        # add chance to do nothing
        eligible_interventions.append("Nothing")
        intervention_weightings.append(desire_to_do_nothing - desire_to_intervene)

        # which intervention, if any, shall the god consider using?
        chosen_intervention, = random.choices(eligible_interventions, intervention_weightings)
        # N.B. use , to unpack the result

        # if god has chosen to take an action then add to list
        if chosen_intervention != "Nothing":
            chosen_interventions.append((ent, chosen_intervention))

    return chosen_interventions