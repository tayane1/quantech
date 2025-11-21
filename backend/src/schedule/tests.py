"""
Tests pour l'application schedule.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from schedule.models import Meeting, Schedule
from employee.models import Employee
from department.models import Department
from datetime import date, datetime, timedelta
from django.utils import timezone

CustomUser = get_user_model()


class ScheduleModelTest(TestCase):
    """Tests pour le modèle Schedule."""
    
    def setUp(self):
        """Configuration initiale."""
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
        self.schedule_data = {
            'assigned_to': self.employee,
            'title': 'Daily Standup',
            'description': 'Daily team meeting',
            'scheduled_date': timezone.now(),
            'priority': Schedule.PRIORITY_MEDIUM
        }
    
    def test_create_schedule(self):
        """Test de création d'un planning."""
        schedule = Schedule.objects.create(**self.schedule_data)
        self.assertEqual(schedule.title, 'Daily Standup')
        self.assertEqual(schedule.assigned_to, self.employee)


class MeetingModelTest(TestCase):
    """Tests pour le modèle Meeting."""
    
    def setUp(self):
        """Configuration initiale."""
        self.department = Department.objects.create(
            name='IT',
            code='IT001',
            description='IT Department',
            location='Paris',
            budget=100000.00
        )
        self.employee1 = Employee.objects.create(
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
        self.employee2 = Employee.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            phone='+33123456790',
            date_of_birth=date(1991, 1, 1),
            gender=Employee.GENDER_FEMALE,
            employee_id='EMP002',
            hire_date=date(2020, 1, 1),
            department=self.department,
            salary=50000.00,
            status=Employee.STATUS_ACTIVE,
            address='456 Main St',
            city='Paris',
            country='France'
        )
        self.meeting_data = {
            'title': 'Team Meeting',
            'description': 'Weekly team meeting',
            'organizer': self.employee1,
            'start_time': timezone.now(),
            'end_time': timezone.now() + timedelta(hours=1),
            'location': 'Conference Room A'
        }
    
    def test_create_meeting(self):
        """Test de création d'une réunion."""
        meeting = Meeting.objects.create(**self.meeting_data)
        meeting.attendees.add(self.employee1, self.employee2)
        self.assertEqual(meeting.title, 'Team Meeting')
        self.assertEqual(meeting.organizer, self.employee1)
        self.assertEqual(meeting.attendees.count(), 2)


class ScheduleAPITest(APITestCase):
    """Tests pour les API endpoints de planning."""
    
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
    
    def test_list_schedules_requires_authentication(self):
        """Test que la liste des plannings nécessite une authentification."""
        response = self.client.get('/api/schedule/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_meetings_requires_authentication(self):
        """Test que la liste des réunions nécessite une authentification."""
        response = self.client.get('/api/schedule/meetings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
