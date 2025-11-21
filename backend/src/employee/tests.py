"""
Tests pour l'application employee.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from employee.models import Employee
from department.models import Department
from datetime import date

CustomUser = get_user_model()


class EmployeeModelTest(TestCase):
    """Tests pour le modèle Employee."""
    
    def setUp(self):
        """Configuration initiale."""
        self.department = Department.objects.create(
            name='IT',
            code='IT001',
            description='IT Department',
            location='Paris',
            budget=100000.00
        )
        self.employee_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+33123456789',
            'date_of_birth': date(1990, 1, 1),
            'gender': Employee.GENDER_MALE,
            'employee_id': 'EMP001',
            'hire_date': date(2020, 1, 1),
            'department': self.department,
            'salary': 50000.00,
            'status': Employee.STATUS_ACTIVE,
            'address': '123 Main St',
            'city': 'Paris',
            'country': 'France'
        }
    
    def test_create_employee(self):
        """Test de création d'un employé."""
        employee = Employee.objects.create(**self.employee_data)
        self.assertEqual(employee.first_name, 'John')
        self.assertEqual(employee.last_name, 'Doe')
        self.assertEqual(employee.email, 'john.doe@example.com')
        self.assertEqual(employee.status, Employee.STATUS_ACTIVE)
    
    def test_employee_email_unique(self):
        """Test que l'email doit être unique."""
        Employee.objects.create(**self.employee_data)
        with self.assertRaises(Exception):
            employee_data = self.employee_data.copy()
            employee_data['employee_id'] = 'EMP002'
            Employee.objects.create(**employee_data)
    
    def test_employee_id_unique(self):
        """Test que l'ID employé doit être unique."""
        Employee.objects.create(**self.employee_data)
        with self.assertRaises(Exception):
            employee_data = self.employee_data.copy()
            employee_data['email'] = 'different@example.com'
            Employee.objects.create(**employee_data)
    
    def test_employee_status_choices(self):
        """Test des choix de statut valides."""
        valid_statuses = [
            Employee.STATUS_ACTIVE,
            Employee.STATUS_ON_LEAVE,
            Employee.STATUS_INACTIVE
        ]
        for status_val in valid_statuses:
            employee_data = self.employee_data.copy()
            employee_data['employee_id'] = f'EMP{status_val}'
            employee_data['email'] = f'test_{status_val}@example.com'
            employee_data['status'] = status_val
            employee = Employee.objects.create(**employee_data)
            self.assertEqual(employee.status, status_val)
    
    def test_employee_gender_choices(self):
        """Test des choix de genre valides."""
        valid_genders = [
            Employee.GENDER_MALE,
            Employee.GENDER_FEMALE,
            Employee.GENDER_OTHER
        ]
        for gender in valid_genders:
            employee_data = self.employee_data.copy()
            employee_data['employee_id'] = f'EMP{gender}'
            employee_data['email'] = f'test_{gender}@example.com'
            employee_data['gender'] = gender
            employee = Employee.objects.create(**employee_data)
            self.assertEqual(employee.gender, gender)
    
    def test_employee_manager_relationship(self):
        """Test de la relation manager-subordonné."""
        manager = Employee.objects.create(**self.employee_data)
        employee_data = self.employee_data.copy()
        employee_data['employee_id'] = 'EMP002'
        employee_data['email'] = 'subordinate@example.com'
        employee_data['manager'] = manager
        subordinate = Employee.objects.create(**employee_data)
        self.assertEqual(subordinate.manager, manager)
        self.assertIn(subordinate, manager.subordinates.all())


class EmployeeAPITest(APITestCase):
    """Tests pour les API endpoints des employés."""
    
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
        self.employee = Employee.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+33123456789',
            date_of_birth=date(1990, 1, 1),
            gender=Employee.GENDER_MALE,
            employee_id='EMP001',
            hire_date=date(2020, 1, 1),
            department=self.department,
            salary=50000.00,
            status=Employee.STATUS_ACTIVE,
            address='123 Main St',
            city='Paris',
            country='France'
        )
    
    def test_list_employees_requires_authentication(self):
        """Test que la liste des employés nécessite une authentification."""
        response = self.client.get('/api/employee/employees/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_employees_with_authentication(self):
        """Test de récupération de la liste des employés."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/api/employee/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_employee_detail(self):
        """Test de récupération des détails d'un employé."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(f'/api/employee/employees/{self.employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')
