# DevSearch API

A Django REST API for a developer community platform where developers can showcase their projects, connect with other developers, and collaborate on exciting projects.

## 🚀 Features

- **Project Showcase**: Share and discover amazing developer projects
- **Developer Messaging**: Connect and communicate with other developers
- **Project Rating**: Rate and review other developers' work
- **Developer Search**: Find developers based on skills and location
- **User Authentication**: Secure JWT-based authentication
- **Admin Dashboard**: Comprehensive admin interface for platform management

## 🛠️ Tech Stack

- **Backend**: Django Rest Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **Media Storage**: Cloudinary
- **Containerization**: Docker & Docker Compose
- **API Documentation**: DRF Spectacular (OpenAPI/Swagger)
- **Admin Interface**: Django Jazzmin
  
## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Docker & Docker Compose (optional)

## 🚀 Quick Start

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd devsearch-api
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv env
   env\Scripts\activate
   
   # macOS/Linux
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   - Copy `.env.example` to `.env`
   ```bash
   cp .env.example .env
   ```
   - Update the environment variables in `.env`:
    

5. **Database Setup**
   - Create PostgreSQL database
   - Run migrations:
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### Option 2: Docker Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd devsearch-api
   ```

2. **Environment Setup**
   - Copy `.env.example` to `.env` and update values

3. **Build and run with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   docker-compose exec web python manage.py collectstatic
   ```

## 📁 Project Structure

```
devsearch-api/
├── apps/
│   ├── accounts/          # User authentication and management
│   ├── profiles/          # Developer profiles and skills
│   ├── projects/          # Project showcase and ratings
│   ├── messaging/         # Direct messaging system
│   └── common/           # Shared utilities and components
├── devsearch/
│   ├── settings/         # Environment-specific settings
│   ├── urls.py          # URL configuration
│   └── wsgi.py          # WSGI configuration
├── static/              # Static files
├── templates/           # Email templates
├── docker-compose.yml   # Docker configuration
├── Dockerfile          # Docker image definition
├── requirements.txt    # Python dependencies
└── manage.py          # Django management script
```

## 📚 API Documentation

The API is fully documented using OpenAPI/Swagger. Once the server is running, you can access the interactive API documentation.

### API Documentation Screenshots

<img src="./static/images/1-d.png">  
<img src="./static/images/2-d.png">  
<img src="./static/images/3-d.png">  
<img src="./static/images/4-d.png">  
<img src="./static/images/5-d.png">  

### API Endpoints Overview

- **Authentication**: `/api/accounts/` - User registration, login, password reset
- **Profiles**: `/api/profiles/` - Developer profiles and skills
- **Projects**: `/api/projects/` - Project CRUD operations and ratings
- **Messaging**: `/api/messages/` - Direct messaging between developers

## 🔐 Admin Panel

Access the admin interface at `http://localhost:8000/admin/` using your superuser credentials.

The admin panel provides:
- User management
- Project moderation
- Message monitoring
- System analytics

### Admin Panel Screenshots

**Admin Login**
<img src="./static/images/devsearch-admin-login.png">  

**Admin Dashboard**
<img src="./static/images/devsearch-admin-dashboard-1.png">  
<img src="./static/images/devsearch-admin-dashboard-2.png">

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

If you have any questions or need help, please open an issue on GitHub.

---

**Built with ❤️ by Praise**
base64 .env > .env.base64
docker compose -f docker-compose.dev.yml up
