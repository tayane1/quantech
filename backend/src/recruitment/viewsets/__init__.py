"""ViewSets pour l'application recruitment."""

from .candidate_viewset import CandidateViewSet
from .hiring_process_viewset import HiringProcessViewSet
from .job_position_viewset import JobPositionViewSet
from .talent_request_viewset import TalentRequestViewSet

__all__ = [
    "JobPositionViewSet",
    "CandidateViewSet",
    "TalentRequestViewSet",
    "HiringProcessViewSet",
]

