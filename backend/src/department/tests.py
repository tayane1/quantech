"""
Tests pour l'application department.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from department.models import Department
from employee.models import Employee
from datetime import date

CustomUser = get_user_model()


class DepartmentModelTest(TestCase):
    """Tests pour le modèle Department."""
    
    def setUp(self):
        """Configuration initiale."""
        self.department_data = {
            'name': 'IT',
            'code': 'IT001',
            'description': 'IT Department',
            'location': 'Paris',
            'budget': 100000.00
        }
    
    def test_create_department(self):
        """Test de création d'un département."""
        department = Department.objects.create(**self.department_data)
        self.assertEqual(department.name, 'IT')
        self.assertEqual(department.code, 'IT001')
        self.assertEqual(department.budget, 100000.00)
    
    def test_department_code_unique(self):
        """Test que le code doit être unique."""
        Department.objects.create(**self.department_data)
        with self.assertRaises(Exception):
            department_data = self.department_data.copy()
            department_data['name'] = 'IT2'
            Department.objects.create(**department_data)
    
    def test_department_str(self):
        """Test de la représentation string."""
        department = Department.objects.create(**self.department_data)
        self.assertEqual(str(department), 'IT')
    
    def test_department_employee_count(self):
        """Test du comptage des employés."""
        department = Department.objects.create(**self.department_data)
        employee = Employee.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+33123456789',
            date_of_birth=date(1990, 1, 1),
            gender=Employee.GENDER_MALE,
            employee_id='EMP001',
            hire_date=date(2020, 1, 1),
            department=department,
            salary=50000.00,
            status=Employee.STATUS_ACTIVE,
            address='123 Main St',
            city='Paris',
            country='France'
        )
        self.assertEqual(department.employee_count, 1)


class DepartmentAPITest(APITestCase):
    """Tests pour les API endpoints des départements."""
    
    def setUp(self):
        """Configuration initiale."""
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='hr_manager'
        )
        self.department = Department.objects.create(
            name='IT',
            code='IT001',
            description='IT Department',
            location='Paris',
            budget=100000.00
        )
    
    def test_list_departments_requires_authentication(self):
        """Test que la liste des départements nécessite une authentification."""
        response = self.client.get('/api/department/departments/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_departments_with_authentication(self):
        """Test de récupération de la liste des départements."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/api/department/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_department_detail(self):
        """Test de récupération des détails d'un département."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(f'/api/department/departments/{self.department.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'IT')
