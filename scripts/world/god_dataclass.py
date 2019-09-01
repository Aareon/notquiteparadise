
from dataclasses import dataclass, field
from typing import List, Dict

from scripts.world.attitude_dataclass import AttitudeData
from scripts.world.intervention_dataclass import InterventionData


@dataclass()
class GodData:
    """
    Data class for a god
    """
    name: str = "None"
    description: str = "None"
    sprite: str = "None"
    attitudes: Dict = field(default_factory=dict)
    interventions: Dict = field(default_factory=dict)