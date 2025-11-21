"""Serializers pour l'application recruitment."""

from .candidate_serializer import CandidateSerializer
from .hiring_process_serializer import HiringProcessSerializer
from .job_position_serializer import JobPositionSerializer
from .talent_request_serializer import TalentRequestSerializer

__all__ = [
    "JobPositionSerializer",
    "CandidateSerializer",
    "TalentRequestSerializer",
    "HiringProcessSerializer",
]

