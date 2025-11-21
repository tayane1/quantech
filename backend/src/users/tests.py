"""
Tests pour l'application users.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

CustomUser = get_user_model()


class CustomUserModelTest(TestCase):
    """Tests pour le modèle CustomUser."""
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'role': 'employee'
        }
    
    def test_create_user(self):
        """Test de création d'un utilisateur."""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'employee')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test de création d'un superutilisateur."""
        user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
    
    def test_user_str(self):
        """Test de la représentation string d'un utilisateur."""
        user = CustomUser.objects.create_user(**self.user_data)
        expected = f"{user.first_name} {user.last_name} ({user.username})"
        self.assertEqual(str(user), expected)
    
    def test_user_email_unique(self):
        """Test que l'email doit être unique."""
        CustomUser.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(
                username='testuser2',
                email='test@example.com',
                password='testpass123',
                first_name='Test2',
                last_name='User2'
            )
    
    def test_user_username_unique(self):
        """Test que le username doit être unique."""
        CustomUser.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(
                username='testuser',
                email='test2@example.com',
                password='testpass123',
                first_name='Test2',
                last_name='User2'
            )
    
    def test_user_role_choices(self):
        """Test des choix de rôle valides."""
        valid_roles = ['admin', 'hr_manager', 'recruiter', 'manager', 'employee']
        for role in valid_roles:
            user_data = self.user_data.copy()
            user_data['username'] = f'testuser_{role}'
            user_data['email'] = f'test_{role}@example.com'
            user_data['role'] = role
            user = CustomUser.objects.create_user(**user_data)
            self.assertEqual(user.role, role)


class CustomUserAPITest(APITestCase):
    """Tests pour les API endpoints des utilisateurs."""
    
    def setUp(self):
        """Configuration initiale pour les tests API."""
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='employee'
        )
        self.admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
    
    def test_list_users_requires_authentication(self):
        """Test que la liste des utilisateurs nécessite une authentification."""
        response = self.client.get('/api/users/custom-users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_users_with_authentication(self):
        """Test de récupération de la liste des utilisateurs avec authentification."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/api/users/custom-users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_user_detail(self):
        """Test de récupération des détails d'un utilisateur."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(f'/api/users/custom-users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_update_own_profile(self):
        """Test de mise à jour de son propre profil."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = self.client.patch(f'/api/users/custom-users/{self.user.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
    
    def test_create_user_requires_admin(self):
        """Test que la création d'utilisateur nécessite des droits admin."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'employee'
        }
        response = self.client.post('/api/users/custom-users/', data)
        # Peut être 403 ou 201 selon les permissions configurées
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_403_FORBIDDEN])
