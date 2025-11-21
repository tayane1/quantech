"""
Commande de management pour remplir la base de données avec des données de test.
Usage: python manage.py seed_database
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
import random
from decimal import Decimal
from faker import Faker

# Imports des modèles
from users.models import CustomUser
from department.models import Department
from employee.models import Employee
from recruitment.models import JobPosition, Candidate, TalentRequest, HiringProcess
from support.models import SupportCategory, SupportTicket, TicketComment
from announcement.models import Announcement
from schedule.models import Meeting, Schedule
from messaging.models import Conversation, Message
from settings.models import SystemSettings, EmailTemplate, NotificationSettings
from dashboard.models import Activity, DashboardMetric


class Command(BaseCommand):
    help = 'Remplit la base de données avec des données de test'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Vider les tables avant de les remplir',
        )

    def handle(self, *args, **options):
        fake = Faker('fr_FR')
        
        if options['clear']:
            self.stdout.write(self.style.WARNING('Vidage des tables...'))
            # Ne pas vider les tables système critiques
            Employee.objects.all().delete()
            CustomUser.objects.filter(is_superuser=False).delete()
            Department.objects.all().delete()
            JobPosition.objects.all().delete()
            Candidate.objects.all().delete()
            SupportTicket.objects.all().delete()
            SupportCategory.objects.all().delete()
            Announcement.objects.all().delete()
            Meeting.objects.all().delete()
            Schedule.objects.all().delete()
            Conversation.objects.all().delete()
            Message.objects.all().delete()
            Activity.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Tables vidées'))

        self.stdout.write(self.style.SUCCESS('Début du remplissage de la base de données...'))

        # 1. SystemSettings (déjà créé, on le met à jour)
        self.stdout.write('Configuration des paramètres système...')
        settings, _ = SystemSettings.objects.get_or_create(pk=1)
        settings.company_name = "WeHR Côte d'Ivoire"
        settings.company_email = "contact@wehr-ci.com"
        settings.currency = "XOF"
        settings.save()

        # 2. Departments
        self.stdout.write('Création des départements...')
        departments_data = [
            {'name': 'Ressources Humaines', 'code': 'RH', 'location': 'Abidjan, Plateau'},
            {'name': 'Informatique', 'code': 'IT', 'location': 'Abidjan, Cocody'},
            {'name': 'Finance', 'code': 'FIN', 'location': 'Abidjan, Plateau'},
            {'name': 'Marketing', 'code': 'MKT', 'location': 'Abidjan, Marcory'},
            {'name': 'Commercial', 'code': 'COM', 'location': 'Abidjan, Yopougon'},
            {'name': 'Production', 'code': 'PROD', 'location': 'Abidjan, Port-Bouët'},
            {'name': 'Qualité', 'code': 'QUAL', 'location': 'Abidjan, Cocody'},
            {'name': 'Logistique', 'code': 'LOG', 'location': 'Abidjan, Port-Bouët'},
        ]
        
        departments = []
        for dept_data in departments_data:
            dept, _ = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={
                    'name': dept_data['name'],
                    'location': dept_data['location'],
                    'description': f"Description du département {dept_data['name']}",
                    'budget': Decimal(random.randint(5000000, 50000000))
                }
            )
            departments.append(dept)

        # 3. Users (Créer quelques utilisateurs de base)
        self.stdout.write('Création des utilisateurs...')
        users_data = [
            {'username': 'admin', 'email': 'admin@wehr-ci.com', 'first_name': 'Admin', 'last_name': 'System', 'role': 'admin', 'is_staff': True, 'is_superuser': True},
            {'username': 'hr_manager', 'email': 'hr@wehr-ci.com', 'first_name': 'Marie', 'last_name': 'Kouassi', 'role': 'hr_manager'},
            {'username': 'recruiter1', 'email': 'recruiter1@wehr-ci.com', 'first_name': 'Jean', 'last_name': 'Yao', 'role': 'recruiter'},
            {'username': 'manager1', 'email': 'manager1@wehr-ci.com', 'first_name': 'Sophie', 'last_name': 'Diabaté', 'role': 'manager'},
        ]
        
        users = []
        for user_data in users_data:
            user, created = CustomUser.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'is_staff': user_data.get('is_staff', False),
                    'is_superuser': user_data.get('is_superuser', False),
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)

        # Créer plus d'utilisateurs
        for i in range(20):
            username = f"user{i+1}"
            # Vérifier que le username n'existe pas déjà
            if CustomUser.objects.filter(username=username).exists():
                continue
                
            email = fake.email()
            while CustomUser.objects.filter(email=email).exists():
                email = fake.email()
            
            user = CustomUser.objects.create(
                username=username,
                email=email,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=random.choice(['employee', 'manager', 'recruiter']),
                phone=fake.phone_number()[:20],
                is_active=True,
            )
            user.set_password('password123')
            user.save()
        
        all_users = list(CustomUser.objects.all())

        # 4. Employees
        self.stdout.write('Création des employés...')
        employee_count = 0
        for user in all_users[:30]:  # Limiter à 30 employés
            if not hasattr(user, 'employee') or user.employee is None:
                employee_id = f"EMP{str(employee_count + 1).zfill(4)}"
                dept = random.choice(departments)
                status = random.choice(['active', 'active', 'active', 'on_leave', 'inactive'])  # Plus d'actifs
                
                employee = Employee.objects.create(
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email if not Employee.objects.filter(email=user.email).exists() else f"{user.email}.emp",
                    phone=fake.phone_number()[:20],
                    date_of_birth=fake.date_of_birth(minimum_age=22, maximum_age=65),
                    gender=random.choice(['M', 'F', 'F']),  # Plus de femmes
                    employee_id=employee_id,
                    hire_date=fake.date_between(start_date=date.today() - timedelta(days=5*365), end_date=date.today()),
                    department=dept,
                    position=dept,
                    status=status,
                    salary=Decimal(random.randint(200000, 2000000)),  # Salaires en XOF
                    manager=None,  # Sera mis à jour après
                )
                user.employee = employee
                user.save()
                employee_count += 1

        # Mettre à jour les managers
        employees = list(Employee.objects.all())
        for dept in departments:
            dept_employees = [e for e in employees if e.department == dept]
            if dept_employees:
                manager = random.choice(dept_employees)
                dept.manager = manager
                dept.save()
                # Mettre à jour les employés du département
                for emp in dept_employees:
                    if emp != manager:
                        emp.manager = manager
                        emp.save()

        # 5. JobPositions
        self.stdout.write('Création des offres d\'emploi...')
        job_titles = [
            'Développeur Full Stack', 'Développeur Frontend', 'Développeur Backend',
            'Chef de Projet', 'Analyste Business', 'Comptable',
            'Responsable Marketing', 'Commercial', 'Designer',
            'DevOps Engineer', 'Data Analyst', 'RH Assistant'
        ]
        
        for title in job_titles:
            JobPosition.objects.get_or_create(
                title=title,
                defaults={
                    'description': f"Description détaillée du poste {title}",
                    'department': random.choice(departments),
                    'status': random.choice(['open', 'open', 'open', 'on_hold', 'closed']),
                    'urgency': random.choice([True, False]),
                }
            )

        # 6. Candidates
        self.stdout.write('Création des candidats...')
        job_positions = list(JobPosition.objects.all())
        if job_positions:
            for _ in range(25):
                email = fake.email()
                while Candidate.objects.filter(email=email).exists():
                    email = fake.email()
                
                # Créer un fichier résumé factice (vide)
                from django.core.files.base import ContentFile
                resume_file = ContentFile(b'Fake resume content')
                resume_file.name = f'resume_{fake.uuid4()}.pdf'
                
                Candidate.objects.create(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=email,
                    phone=fake.phone_number()[:20],
                    position=random.choice(job_positions),
                    resume=resume_file,
                    status=random.choice(['applied', 'reviewing', 'interview', 'offered', 'rejected', 'hired']),
                )

        # 7. SupportCategories
        self.stdout.write('Création des catégories de support...')
        categories_data = [
            {'name': 'Bug Technique', 'icon': 'bug', 'color': '#dc3545'},
            {'name': 'Question Générale', 'icon': 'question', 'color': '#007bff'},
            {'name': 'Demande de Fonctionnalité', 'icon': 'lightbulb', 'color': '#28a745'},
            {'name': 'Problème de Connexion', 'icon': 'wifi', 'color': '#ffc107'},
            {'name': 'Autre', 'icon': 'info', 'color': '#6c757d'},
        ]
        
        categories = []
        for cat_data in categories_data:
            cat, _ = SupportCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories.append(cat)

        # 8. SupportTickets
        self.stdout.write('Création des tickets de support...')
        for _ in range(30):
            SupportTicket.objects.create(
                title=fake.sentence(nb_words=6),
                description=fake.text(max_nb_chars=500),
                priority=random.choice(['low', 'medium', 'high', 'urgent']),
                status=random.choice(['open', 'in_progress', 'waiting', 'resolved', 'closed']),
                category=random.choice(categories),
                created_by=random.choice(all_users),
                assigned_to=random.choice(all_users) if random.random() > 0.3 else None,
            )

        # 9. Announcements
        self.stdout.write('Création des annonces...')
        employees_list = list(Employee.objects.all())
        if employees_list:
            for _ in range(15):
                Announcement.objects.create(
                    title=fake.sentence(nb_words=8),
                    content=fake.text(max_nb_chars=1000),
                    published=random.choice([True, True, True, False]),  # Plus de publiées
                    author=random.choice(employees_list),
                    visible_to_all=random.choice([True, True, False]),
                )

        # 10. Meetings
        self.stdout.write('Création des réunions...')
        employees_list = list(Employee.objects.all())
        if employees_list:
            for _ in range(20):
                start = timezone.now() + timedelta(days=random.randint(-7, 30))
                Meeting.objects.create(
                    title=fake.sentence(nb_words=5),
                    description=fake.text(max_nb_chars=300),
                    start_time=start,
                    end_time=start + timedelta(hours=random.randint(1, 3)),
                    location=fake.address(),
                    organizer=random.choice(employees_list),
                )

        # 11. Schedules
        self.stdout.write('Création des tâches planifiées...')
        employees_list = list(Employee.objects.all())
        if employees_list:
            for _ in range(25):
                scheduled = timezone.now() + timedelta(days=random.randint(-14, 60))
                Schedule.objects.create(
                    title=fake.sentence(nb_words=6),
                    description=fake.text(max_nb_chars=400),
                    scheduled_date=scheduled,
                    priority=random.choice(['high', 'medium', 'low']),
                    completed=random.choice([True, False, False, False]),  # Plus de non complétées
                    assigned_to=random.choice(employees_list),
                    assigned_by=random.choice(employees_list) if random.random() > 0.2 else None,
                )

        # 12. Conversations et Messages
        self.stdout.write('Création des conversations et messages...')
        for _ in range(15):
            participants = random.sample(all_users, k=min(random.randint(2, 5), len(all_users)))
            creator = participants[0]
            is_direct = len(participants) == 2
            conversation = Conversation.objects.create(
                conversation_type='direct' if is_direct else 'group',
                subject=fake.sentence(nb_words=4) if not is_direct else None,
                created_by=creator,
            )
            conversation.participants.set(participants)
            
            # Créer quelques messages
            for _ in range(random.randint(3, 10)):
                sender = random.choice(participants)
                # Pour les messages directs, il faut un destinataire
                if is_direct:
                    recipient = [p for p in participants if p != sender][0]
                else:
                    recipient = None
                
                Message.objects.create(
                    conversation=conversation,
                    sender=sender,
                    recipient=recipient,
                    content=fake.text(max_nb_chars=200),
                )

        # 13. Activities
        self.stdout.write('Création des activités...')
        employees_list = list(Employee.objects.all())
        job_positions = list(JobPosition.objects.all())
        candidates = list(Candidate.objects.all())
        if employees_list:
            activity_types = ['job_posted', 'candidate_applied', 'employee_added', 'announcement_posted', 'schedule_created', 'meeting_scheduled']
            for _ in range(50):
                Activity.objects.create(
                    user=random.choice(employees_list),
                    activity_type=random.choice(activity_types),
                    description=fake.sentence(nb_words=8),
                    related_position=random.choice(job_positions) if job_positions and random.random() > 0.5 else None,
                    related_candidate=random.choice(candidates) if candidates and random.random() > 0.7 else None,
                    related_employee=random.choice(employees_list) if random.random() > 0.7 else None,
                )

        # 14. EmailTemplates
        self.stdout.write('Création des modèles d\'email...')
        templates_data = [
            {'name': 'Bienvenue', 'template_type': 'welcome', 'subject': 'Bienvenue dans WeHR', 'body_html': '<p>Bienvenue {{user_name}}!</p>'},
            {'name': 'Réinitialisation mot de passe', 'template_type': 'password_reset', 'subject': 'Réinitialisation de votre mot de passe', 'body_html': '<p>Cliquez sur ce lien pour réinitialiser votre mot de passe.</p>'},
        ]
        for template_data in templates_data:
            EmailTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )

        # 15. NotificationSettings
        self.stdout.write('Création des paramètres de notifications...')
        notification_types = [
            'user_registration', 'password_reset', 'employee_created',
            'employee_updated', 'announcement_published', 'ticket_created',
            'ticket_updated', 'system_maintenance'
        ]
        for notif_type in notification_types:
            NotificationSettings.objects.get_or_create(
                notification_type=notif_type,
                defaults={'enabled': True, 'send_email': True, 'send_sms': False, 'send_push': True}
            )

        self.stdout.write(self.style.SUCCESS('\n✅ Base de données remplie avec succès!'))
        self.stdout.write(f'   - {Department.objects.count()} départements')
        self.stdout.write(f'   - {CustomUser.objects.count()} utilisateurs')
        self.stdout.write(f'   - {Employee.objects.count()} employés')
        self.stdout.write(f'   - {JobPosition.objects.count()} offres d\'emploi')
        self.stdout.write(f'   - {Candidate.objects.count()} candidats')
        self.stdout.write(f'   - {SupportTicket.objects.count()} tickets de support')
        self.stdout.write(f'   - {Announcement.objects.count()} annonces')
        self.stdout.write(f'   - {Meeting.objects.count()} réunions')
        self.stdout.write(f'   - {Schedule.objects.count()} tâches planifiées')
        self.stdout.write(f'   - {Conversation.objects.count()} conversations')
        self.stdout.write(f'   - {Message.objects.count()} messages')
        self.stdout.write(f'   - {Activity.objects.count()} activités')

