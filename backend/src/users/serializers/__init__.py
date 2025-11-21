"""Serializers pour l'application users."""

from .customUser_serializer import (
    CustomUserSerializer,
    CustomUserListSerializer,
)
from .userRole_serializer import UserRoleSerializer
from .userPermission_serializer import UserPermissionSerializer
from .userPreference_serializer import UserPreferenceSerializer
from .userNotification_serializer import (
    UserNotificationSerializer,
    UserNotificationListSerializer,
)
from .userActivity_serializer import UserActivitySerializer

__all__ = [
    "CustomUserSerializer",
    "CustomUserListSerializer",
    "UserRoleSerializer",
    "UserPermissionSerializer",
    "UserPreferenceSerializer",
    "UserNotificationSerializer",
    "UserNotificationListSerializer",
    "UserActivitySerializer",
]
