"""
Tests pour l'application support.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from support.models import SupportCategory, SupportTicket, TicketComment
from django.utils import timezone

CustomUser = get_user_model()


class SupportCategoryModelTest(TestCase):
    """Tests pour le modèle SupportCategory."""
    
    def setUp(self):
        """Configuration initiale."""
        self.category_data = {
            'name': 'Bug',
            'description': 'Bug reports',
            'icon': 'bug',
            'color': '#ff0000'
        }
    
    def test_create_category(self):
        """Test de création d'une catégorie."""
        category = SupportCategory.objects.create(**self.category_data)
        self.assertEqual(category.name, 'Bug')
        self.assertEqual(category.icon, 'bug')
        self.assertTrue(category.is_active)
    
    def test_category_name_unique(self):
        """Test que le nom doit être unique."""
        SupportCategory.objects.create(**self.category_data)
        with self.assertRaises(Exception):
            SupportCategory.objects.create(**self.category_data)


class SupportTicketModelTest(TestCase):
    """Tests pour le modèle SupportTicket."""
    
    def setUp(self):
        """Configuration initiale."""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.category = SupportCategory.objects.create(
            name='Bug',
            description='Bug reports'
        )
        self.ticket_data = {
            'title': 'Test Ticket',
            'description': 'This is a test ticket',
            'category': self.category,
            'priority': 'medium',
            'status': 'open',
            'created_by': self.user
        }
    
    def test_create_ticket(self):
        """Test de création d'un ticket."""
        ticket = SupportTicket.objects.create(**self.ticket_data)
        self.assertEqual(ticket.title, 'Test Ticket')
        self.assertEqual(ticket.status, 'open')
        self.assertEqual(ticket.priority, 'medium')
        self.assertTrue(ticket.is_open)
    
    def test_ticket_status_choices(self):
        """Test des choix de statut valides."""
        valid_statuses = ['open', 'in_progress', 'waiting', 'resolved', 'closed']
        for status_val in valid_statuses:
            ticket_data = self.ticket_data.copy()
            ticket_data['title'] = f'Ticket {status_val}'
            ticket_data['status'] = status_val
            ticket = SupportTicket.objects.create(**ticket_data)
            self.assertEqual(ticket.status, status_val)
    
    def test_ticket_priority_choices(self):
        """Test des choix de priorité valides."""
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        for priority in valid_priorities:
            ticket_data = self.ticket_data.copy()
            ticket_data['title'] = f'Ticket {priority}'
            ticket_data['priority'] = priority
            ticket = SupportTicket.objects.create(**ticket_data)
            self.assertEqual(ticket.priority, priority)
    
    def test_ticket_resolved_at_auto_set(self):
        """Test que resolved_at est défini automatiquement."""
        ticket = SupportTicket.objects.create(**self.ticket_data)
        ticket.status = 'resolved'
        ticket.save()
        self.assertIsNotNone(ticket.resolved_at)
    
    def test_ticket_closed_at_auto_set(self):
        """Test que closed_at est défini automatiquement."""
        ticket = SupportTicket.objects.create(**self.ticket_data)
        ticket.status = 'closed'
        ticket.save()
        self.assertIsNotNone(ticket.closed_at)
    
    def test_ticket_is_open_property(self):
        """Test de la propriété is_open."""
        ticket = SupportTicket.objects.create(**self.ticket_data)
        self.assertTrue(ticket.is_open)
        ticket.status = 'resolved'
        ticket.save()
        self.assertFalse(ticket.is_open)
    
    def test_ticket_duration_days(self):
        """Test du calcul de la durée en jours."""
        ticket = SupportTicket.objects.create(**self.ticket_data)
        # Le ticket vient d'être créé, donc la durée devrait être 0 ou 1 jour
        duration = ticket.duration_days
        self.assertGreaterEqual(duration, 0)


class TicketCommentModelTest(TestCase):
    """Tests pour le modèle TicketComment."""
    
    def setUp(self):
        """Configuration initiale."""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.category = SupportCategory.objects.create(
            name='Bug',
            description='Bug reports'
        )
        self.ticket = SupportTicket.objects.create(
            title='Test Ticket',
            description='This is a test ticket',
            category=self.category,
            created_by=self.user
        )
    
    def test_create_comment(self):
        """Test de création d'un commentaire."""
        comment = TicketComment.objects.create(
            ticket=self.ticket,
            author=self.user,
            content='This is a test comment'
        )
        self.assertEqual(comment.ticket, self.ticket)
        self.assertEqual(comment.author, self.user)
        self.assertFalse(comment.is_internal)


class SupportAPITest(APITestCase):
    """Tests pour les API endpoints de support."""
    
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
        self.category = SupportCategory.objects.create(
            name='Bug',
            description='Bug reports'
        )
        self.ticket = SupportTicket.objects.create(
            title='Test Ticket',
            description='This is a test ticket',
            category=self.category,
            created_by=self.user
        )
    
    def test_list_tickets_requires_authentication(self):
        """Test que la liste des tickets nécessite une authentification."""
        response = self.client.get('/api/support/support-tickets/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_tickets_with_authentication(self):
        """Test de récupération de la liste des tickets."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/api/support/support-tickets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_ticket(self):
        """Test de création d'un ticket."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        data = {
            'title': 'New Ticket',
            'description': 'This is a new ticket',
            'category': self.category.id,
            'priority': 'high'
        }
        response = self.client.post('/api/support/support-tickets/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
