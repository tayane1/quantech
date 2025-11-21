"""ViewSets pour l'application users."""

from .customUser_viewset import CustomUserViewSet
from .userRole_viewset import UserRoleViewSet
from .userPermission_viewset import UserPermissionViewSet
from .userPreference_viewset import UserPreferenceViewSet
from .userNotification_viewset import UserNotificationViewSet
from .userActivity_viewset import UserActivityViewSet

__all__ = [
    "CustomUserViewSet",
    "UserRoleViewSet",
    "UserPermissionViewSet",
    "UserPreferenceViewSet",
    "UserNotificationViewSet",
    "UserActivityViewSet",
]
