from rest_framework.routers import DefaultRouter
from users.viewsets import CustomUserViewSet, UserPreferenceViewSet, UserNotificationViewSet, UserPermissionViewSet, UserRoleViewSet, UserActivityViewSet

router = DefaultRouter()
router.register(r'custom-users', CustomUserViewSet, basename='custom-user')
router.register(r'user-preferences', UserPreferenceViewSet, basename='user-preference')
router.register(r'user-notifications', UserNotificationViewSet, basename='user-notification')
router.register(r'user-permissions', UserPermissionViewSet, basename='user-permission')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'user-activities', UserActivityViewSet, basename='user-activity')

urlpatterns = router.urls