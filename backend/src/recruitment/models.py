"""Point d'entrée des modèles de l'app recruitment."""

from .models.candidate import Candidate
from .models.hiring_process import HiringProcess
from .models.job_position import JobPosition
from .models.talent_request import TalentRequest

__all__ = [
    "Candidate",
    "HiringProcess",
    "JobPosition",
    "TalentRequest",
]
