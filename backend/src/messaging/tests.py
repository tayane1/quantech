"""
Tests pour l'application messaging.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from messaging.models import Conversation, Message, MessageReadStatus
from django.utils import timezone

CustomUser = get_user_model()


class ConversationModelTest(TestCase):
    """Tests pour le modèle Conversation."""
    
    def setUp(self):
        """Configuration initiale."""
        self.user1 = CustomUser.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = CustomUser.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123',
            first_name='User',
            last_name='Two'
        )
    
    def test_create_direct_conversation(self):
        """Test de création d'une conversation directe."""
        conversation = Conversation.objects.create(
            created_by=self.user1,
            conversation_type='direct'
        )
        conversation.participants.add(self.user1, self.user2)
        # La validation se fait maintenant après l'ajout des participants
        conversation.save()
        self.assertEqual(conversation.conversation_type, 'direct')
        self.assertEqual(conversation.participants.count(), 2)
    
    def test_direct_conversation_requires_two_participants(self):
        """Test qu'une conversation directe nécessite exactement 2 participants."""
        conversation = Conversation.objects.create(
            created_by=self.user1,
            conversation_type='direct'
        )
        conversation.participants.add(self.user1)
        # La validation se fait lors du save après l'ajout des participants
        with self.assertRaises(ValidationError):
            conversation.save()
    
    def test_conversation_requires_at_least_two_participants(self):
        """Test qu'une conversation nécessite au moins 2 participants."""
        conversation = Conversation.objects.create(
            created_by=self.user1,
            conversation_type='group'
        )
        conversation.participants.add(self.user1)
        # La validation se fait lors du save après l'ajout des participants
        with self.assertRaises(ValidationError):
            conversation.save()
    
    def test_get_unread_count(self):
        """Test du comptage des messages non lus."""
        conversation = Conversation.objects.create(
            created_by=self.user1,
            conversation_type='direct'
        )
        conversation.participants.add(self.user1, self.user2)
        conversation.save()  # Sauvegarder pour valider
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user1,
            recipient=self.user2,
            content='Test message'
        )
        unread_count = conversation.get_unread_count_for_user(self.user2)
        self.assertEqual(unread_count, 1)


class MessageModelTest(TestCase):
    """Tests pour le modèle Message."""
    
    def setUp(self):
        """Configuration initiale."""
        self.user1 = CustomUser.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = CustomUser.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123',
            first_name='User',
            last_name='Two'
        )
        self.conversation = Conversation.objects.create(
            created_by=self.user1,
            conversation_type='direct'
        )
        self.conversation.participants.add(self.user1, self.user2)
    
    def test_create_message(self):
        """Test de création d'un message."""
        # S'assurer que la conversation a les participants
        self.conversation.participants.add(self.user1, self.user2)
        self.conversation.save()
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            recipient=self.user2,
            content='Hello, this is a test message'
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.recipient, self.user2)
        self.assertFalse(message.is_read)
    
    def test_message_content_cannot_be_empty(self):
        """Test qu'un message ne peut pas être vide."""
        self.conversation.participants.add(self.user1, self.user2)
        self.conversation.save()
        message = Message(
            conversation=self.conversation,
            sender=self.user1,
            recipient=self.user2,
            content=''
        )
        with self.assertRaises(ValidationError):
            message.save()  # La validation se fait lors du save
    
    def test_message_content_max_length(self):
        """Test de la longueur maximale du contenu."""
        self.conversation.participants.add(self.user1, self.user2)
        self.conversation.save()
        long_content = 'a' * 5001
        message = Message(
            conversation=self.conversation,
            sender=self.user1,
            recipient=self.user2,
            content=long_content
        )
        with self.assertRaises(ValidationError):
            message.save()
    
    def test_sender_must_be_participant(self):
        """Test que l'expéditeur doit être un participant."""
        self.conversation.participants.add(self.user1, self.user2)
        self.conversation.save()
        user3 = CustomUser.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='pass123',
            first_name='User',
            last_name='Three'
        )
        message = Message(
            conversation=self.conversation,
            sender=user3,
            recipient=self.user2,
            content='Test'
        )
        with self.assertRaises(ValidationError):
            message.save()
    
    def test_mark_message_as_read(self):
        """Test de marquage d'un message comme lu."""
        self.conversation.participants.add(self.user1, self.user2)
        self.conversation.save()
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            recipient=self.user2,
            content='Test message'
        )
        message.mark_as_read()
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)
    
    def test_direct_message_requires_recipient(self):
        """Test qu'un message direct nécessite un destinataire."""
        self.conversation.participants.add(self.user1, self.user2)
        self.conversation.save()
        message = Message(
            conversation=self.conversation,
            sender=self.user1,
            recipient=None,
            content='Test'
        )
        with self.assertRaises(ValidationError):
            message.save()
    
    def test_cannot_send_message_to_self(self):
        """Test qu'on ne peut pas s'envoyer un message à soi-même."""
        self.conversation.participants.add(self.user1, self.user2)
        self.conversation.save()
        message = Message(
            conversation=self.conversation,
            sender=self.user1,
            recipient=self.user1,
            content='Test'
        )
        with self.assertRaises(ValidationError):
            message.save()


class MessagingAPITest(APITestCase):
    """Tests pour les API endpoints de messagerie."""
    
    def setUp(self):
        """Configuration initiale."""
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = CustomUser.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123',
            first_name='User',
            last_name='Two'
        )
        self.conversation = Conversation.objects.create(
            created_by=self.user1,
            conversation_type='direct'
        )
        self.conversation.participants.add(self.user1, self.user2)
        self.conversation.save()  # Sauvegarder pour valider
    
    def test_list_conversations_requires_authentication(self):
        """Test que la liste des conversations nécessite une authentification."""
        response = self.client.get('/api/messages/conversations/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_conversations_with_authentication(self):
        """Test de récupération de la liste des conversations."""
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get('/api/messages/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_message(self):
        """Test de création d'un message."""
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        data = {
            'conversation': self.conversation.id,
            'recipient': self.user2.id,
            'content': 'Hello, this is a test message'
        }
        response = self.client.post('/api/messages/messages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
