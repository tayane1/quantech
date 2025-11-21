"""
Tests pour l'application login.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from login.models.login_attempt import LoginAttempt
from login.models.login_history import LoginHistory
from django.utils import timezone
from datetime import timedelta

CustomUser = get_user_model()


class LoginAPITest(APITestCase):
    """Tests pour les endpoints d'authentification."""
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='employee'
        )
    
    def test_login_success(self):
        """Test de connexion réussie."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/login/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Test de connexion avec des identifiants invalides."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/login/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
    
    def test_login_missing_credentials(self):
        """Test de connexion sans identifiants."""
        response = self.client.post('/api/login/login/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_inactive_user(self):
        """Test de connexion avec un utilisateur inactif."""
        self.user.is_active = False
        self.user.save()
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/login/login/', data, format='json')
        # L'API retourne 401 pour les utilisateurs inactifs (authentification échouée)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_refresh_token(self):
        """Test de rafraîchissement de token."""
        refresh = RefreshToken.for_user(self.user)
        data = {'refresh': str(refresh)}
        response = self.client.post('/api/login/refresh/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_refresh_token_invalid(self):
        """Test de rafraîchissement avec un token invalide."""
        data = {'refresh': 'invalid_token'}
        response = self.client.post('/api/login/refresh/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout(self):
        """Test de déconnexion."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        data = {'refresh': str(refresh)}
        response = self.client.post('/api/login/logout/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LoginAttemptModelTest(TestCase):
    """Tests pour le modèle LoginAttempt."""
    
    def setUp(self):
        """Configuration initiale."""
        self.attempt_data = {
            'email': 'test@example.com',
            'ip_address': '127.0.0.1',
            'failed_attempts': 0
        }
    
    def test_create_login_attempt(self):
        """Test de création d'une tentative de connexion."""
        attempt = LoginAttempt.objects.create(**self.attempt_data)
        self.assertEqual(attempt.email, 'test@example.com')
        self.assertEqual(attempt.ip_address, '127.0.0.1')
        self.assertEqual(attempt.failed_attempts, 0)
    
    def test_increment_failed_attempts(self):
        """Test d'incrémentation des tentatives échouées."""
        attempt = LoginAttempt.objects.create(**self.attempt_data)
        attempt.failed_attempts += 1
        attempt.save()
        self.assertEqual(attempt.failed_attempts, 1)
    
    def test_lock_after_multiple_failures(self):
        """Test de verrouillage après plusieurs échecs."""
        attempt = LoginAttempt.objects.create(**self.attempt_data)
        attempt.failed_attempts = 5
        attempt.locked_until = timezone.now() + timedelta(minutes=15)
        attempt.save()
        self.assertIsNotNone(attempt.locked_until)
        self.assertTrue(attempt.locked_until > timezone.now())


class LoginHistoryModelTest(TestCase):
    """Tests pour le modèle LoginHistory."""
    
    def setUp(self):
        """Configuration initiale."""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_create_login_history(self):
        """Test de création d'un historique de connexion."""
        history = LoginHistory.objects.create(
            user=self.user,
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            is_successful=True
        )
        self.assertEqual(history.user, self.user)
        self.assertTrue(history.is_successful)
        self.assertIsNotNone(history.login_time)
    
    def test_login_history_with_logout(self):
        """Test d'historique avec déconnexion."""
        history = LoginHistory.objects.create(
            user=self.user,
            ip_address='127.0.0.1',
            is_successful=True
        )
        history.logout_time = timezone.now()
        history.save()
        self.assertIsNotNone(history.logout_time)
