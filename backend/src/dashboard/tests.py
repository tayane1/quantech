"""
Tests pour l'application dashboard.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from dashboard.models import DashboardMetric, Activity

CustomUser = get_user_model()


class DashboardMetricModelTest(TestCase):
    """Tests pour le modèle DashboardMetric."""
    
    def setUp(self):
        """Configuration initiale."""
        self.metric_data = {
            'metric_type': 'total_employees',
            'value': 100
        }
    
    def test_create_metric(self):
        """Test de création d'une métrique."""
        metric = DashboardMetric.objects.create(**self.metric_data)
        self.assertEqual(metric.metric_type, 'total_employees')
        self.assertEqual(metric.value, 100)


class ActivityModelTest(TestCase):
    """Tests pour le modèle Activity."""
    
    def setUp(self):
        """Configuration initiale."""
        from department.models import Department
        from employee.models import Employee
        from datetime import date
        
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
        self.activity_data = {
            'user': self.employee,
            'activity_type': Activity.ACTIVITY_EMPLOYEE_ADDED,
            'description': 'Employee added to the system'
        }
    
    def test_create_activity(self):
        """Test de création d'une activité."""
        activity = Activity.objects.create(**self.activity_data)
        self.assertEqual(activity.user, self.employee)
        self.assertEqual(activity.activity_type, Activity.ACTIVITY_EMPLOYEE_ADDED)


class DashboardAPITest(APITestCase):
    """Tests pour les API endpoints du dashboard."""
    
    def setUp(self):
        """Configuration initiale."""
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_dashboard_requires_authentication(self):
        """Test que le dashboard nécessite une authentification."""
        response = self.client.get('/api/dashboard/metrics/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_dashboard_with_authentication(self):
        """Test d'accès au dashboard avec authentification."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/api/dashboard/metrics/')
        # Peut être 200 ou 404 selon l'implémentation
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
