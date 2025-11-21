# Quantech - WeHR

Application de gestion des ressources humaines (WeHR) avec backend Django et frontend Angular.

## 🏗️ Structure du projet

```
quantech/
├── backend/          # Backend Django REST Framework
└── frontend/         # Frontend Angular 21
```

## 🚀 Installation

### Backend

```bash
cd backend
python -m venv env
source env/bin/activate  # Sur Windows: env\Scripts\activate
pip install -r requirements.txt
cd src
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## 📝 Configuration

Les fichiers `.env` sont nécessaires pour la configuration :
- `backend/.env` - Variables d'environnement du backend
- `frontend/.env` - Variables d'environnement du frontend

Consultez les fichiers `.env.example` pour les variables requises.

## 📄 Licence

Propriétaire

