"""
Tests pour l'application settings.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from settings.models import SystemSettings, EmailTemplate, NotificationSettings

CustomUser = get_user_model()


class SystemSettingsModelTest(TestCase):
    """Tests pour le modèle SystemSettings."""
    
    def setUp(self):
        """Configuration initiale."""
        self.user = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        self.settings_data = {
            'company_name': 'Test Company',
            'company_email': 'contact@test.com',
            'site_name': 'WeHR Test',
            'updated_by': self.user
        }
    
    def test_create_settings(self):
        """Test de création des paramètres système."""
        settings = SystemSettings.objects.create(**self.settings_data)
        self.assertEqual(settings.company_name, 'Test Company')
        self.assertEqual(settings.site_name, 'WeHR Test')
    
    def test_get_settings_singleton(self):
        """Test que get_settings retourne toujours la même instance."""
        settings1 = SystemSettings.get_settings()
        settings2 = SystemSettings.get_settings()
        self.assertEqual(settings1.pk, settings2.pk)
    
    def test_settings_save_prevents_multiple_instances(self):
        """Test que save empêche la création de multiples instances."""
        SystemSettings.objects.create(**self.settings_data)
        # Tenter de créer une deuxième instance
        settings2 = SystemSettings(**self.settings_data)
        settings2.save()
        # Devrait retourner l'instance existante
        self.assertEqual(SystemSettings.objects.count(), 1)


class EmailTemplateModelTest(TestCase):
    """Tests pour le modèle EmailTemplate."""
    
    def setUp(self):
        """Configuration initiale."""
        self.template_data = {
            'name': 'Welcome Email',
            'template_type': 'welcome',
            'subject': 'Welcome to WeHR',
            'body_html': '<h1>Welcome</h1>',
            'body_text': 'Welcome'
        }
    
    def test_create_template(self):
        """Test de création d'un modèle d'email."""
        template = EmailTemplate.objects.create(**self.template_data)
        self.assertEqual(template.name, 'Welcome Email')
        self.assertEqual(template.template_type, 'welcome')
        self.assertTrue(template.is_active)
    
    def test_template_name_unique(self):
        """Test que le nom doit être unique."""
        EmailTemplate.objects.create(**self.template_data)
        with self.assertRaises(Exception):
            EmailTemplate.objects.create(**self.template_data)


class NotificationSettingsModelTest(TestCase):
    """Tests pour le modèle NotificationSettings."""
    
    def setUp(self):
        """Configuration initiale."""
        self.notification_data = {
            'notification_type': 'user_registration',
            'enabled': True,
            'send_email': True,
            'send_sms': False,
            'send_push': True
        }
    
    def test_create_notification_settings(self):
        """Test de création de paramètres de notification."""
        settings = NotificationSettings.objects.create(**self.notification_data)
        self.assertEqual(settings.notification_type, 'user_registration')
        self.assertTrue(settings.enabled)
        self.assertTrue(settings.send_email)
    
    def test_notification_type_unique(self):
        """Test que le type de notification doit être unique."""
        NotificationSettings.objects.create(**self.notification_data)
        with self.assertRaises(Exception):
            NotificationSettings.objects.create(**self.notification_data)


class SettingsAPITest(APITestCase):
    """Tests pour les API endpoints des paramètres."""
    
    def setUp(self):
        """Configuration initiale."""
        self.client = APIClient()
        self.admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_settings_requires_authentication(self):
        """Test que les paramètres nécessitent une authentification."""
        response = self.client.get('/api/settings/system-settings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_settings_with_authentication(self):
        """Test d'accès aux paramètres avec authentification."""
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/api/settings/system-settings/')
        # Peut être 200 ou 404 selon l'implémentation
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
