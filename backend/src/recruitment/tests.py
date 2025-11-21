"""
Tests pour l'application recruitment.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from recruitment.models import JobPosition, Candidate, HiringProcess, TalentRequest
from department.models import Department
from datetime import date

CustomUser = get_user_model()


class JobPositionModelTest(TestCase):
    """Tests pour le modèle JobPosition."""
    
    def setUp(self):
        """Configuration initiale."""
        self.department = Department.objects.create(
            name='IT',
            code='IT001',
            description='IT Department',
            location='Paris',
            budget=100000.00
        )
        self.position_data = {
            'title': 'Software Engineer',
            'department': self.department,
            'description': 'Develop software using Python and Django',
            'status': JobPosition.STATUS_OPEN
        }
    
    def test_create_job_position(self):
        """Test de création d'un poste."""
        position = JobPosition.objects.create(**self.position_data)
        self.assertEqual(position.title, 'Software Engineer')
        self.assertEqual(position.department, self.department)
        self.assertEqual(position.status, JobPosition.STATUS_OPEN)


class CandidateModelTest(TestCase):
    """Tests pour le modèle Candidate."""
    
    def setUp(self):
        """Configuration initiale."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        self.department = Department.objects.create(
            name='IT',
            code='IT001',
            description='IT Department',
            location='Paris',
            budget=100000.00
        )
        self.position = JobPosition.objects.create(
            title='Software Engineer',
            department=self.department,
            description='Develop software'
        )
        # Créer un fichier mock pour le CV
        self.resume_file = SimpleUploadedFile(
            "resume.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        self.candidate_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+33123456789',
            'position': self.position,
            'status': Candidate.STATUS_APPLIED,
            'resume': self.resume_file
        }
    
    def test_create_candidate(self):
        """Test de création d'un candidat."""
        candidate = Candidate.objects.create(**self.candidate_data)
        self.assertEqual(candidate.first_name, 'John')
        self.assertEqual(candidate.status, Candidate.STATUS_APPLIED)
    
    def test_candidate_email_unique(self):
        """Test que l'email doit être unique."""
        Candidate.objects.create(**self.candidate_data)
        with self.assertRaises(Exception):
            from django.core.files.uploadedfile import SimpleUploadedFile
            resume_file2 = SimpleUploadedFile(
                "resume2.pdf",
                b"file_content",
                content_type="application/pdf"
            )
            candidate_data = self.candidate_data.copy()
            candidate_data['resume'] = resume_file2
            Candidate.objects.create(**candidate_data)
    
    def test_candidate_status_choices(self):
        """Test des choix de statut valides."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        valid_statuses = [
            Candidate.STATUS_APPLIED,
            Candidate.STATUS_REVIEWING,
            Candidate.STATUS_INTERVIEW,
            Candidate.STATUS_OFFERED,
            Candidate.STATUS_REJECTED,
            Candidate.STATUS_HIRED
        ]
        for status_val in valid_statuses:
            resume_file = SimpleUploadedFile(
                f"resume_{status_val}.pdf",
                b"file_content",
                content_type="application/pdf"
            )
            candidate_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': f'test_{status_val}@example.com',
                'phone': '+33123456789',
                'position': self.position,
                'status': status_val,
                'resume': resume_file
            }
            candidate = Candidate.objects.create(**candidate_data)
            self.assertEqual(candidate.status, status_val)


class RecruitmentAPITest(APITestCase):
    """Tests pour les API endpoints de recrutement."""
    
    def setUp(self):
        """Configuration initiale."""
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='recruiter'
        )
        self.department = Department.objects.create(
            name='IT',
            code='IT001',
            description='IT Department',
            location='Paris',
            budget=100000.00
        )
        self.position = JobPosition.objects.create(
            title='Software Engineer',
            department=self.department,
            description='Develop software'
        )
    
    def test_list_positions_requires_authentication(self):
        """Test que la liste des postes nécessite une authentification."""
        response = self.client.get('/api/recruitment/job-positions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_positions_with_authentication(self):
        """Test de récupération de la liste des postes."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/api/recruitment/job-positions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_candidates_requires_authentication(self):
        """Test que la liste des candidats nécessite une authentification."""
        response = self.client.get('/api/recruitment/candidates/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
