# 🦷 Mentora Clean - Getting Started

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd dental-academy-clean
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"
```

### 3. Create Admin User
```bash
python -c "
from app import create_app
from extensions import db
from models import User

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created: admin / admin123')
"
```

### 4. Create Sample Data
```bash
python -c "
from app import create_app
from models import create_sample_data

app = create_app()
with app.app_context():
    create_sample_data()
    print('Sample data created!')
"
```

### 5. Create Virtual Patients (Optional)
```bash
python create_sample_virtual_patients.py
```

### 6. Run Application
```bash
python run.py
```

🌐 **Open in browser:** http://127.0.0.1:5000

## 🔐 Default Login
- **Username:** admin
- **Password:** admin123

## 📁 Project Structure

```
dental-academy-clean/
├── app.py                      # Main Flask application
├── extensions.py               # Flask extensions setup
├── models.py                   # Database models
├── requirements.txt            # Python dependencies
├── run.py                      # Application runner
├── routes/                     # Route blueprints
│   ├── __init__.py
│   ├── main_routes.py         # Home, about, contact
│   ├── auth_routes.py         # Login, register, profile
│   ├── dashboard_routes.py    # Learning dashboard
│   ├── learning_routes.py     # Learning system
│   ├── test_routes.py         # Testing system
│   └── admin_routes.py        # Admin panel
├── templates/                  # Jinja2 templates
│   ├── base.html              # Base template
│   ├── index.html             # Homepage
│   ├── auth/                  # Authentication pages
│   ├── dashboard/             # Dashboard pages
│   ├── learning/              # Learning pages
│   ├── tests/                 # Test pages
│   ├── admin/                 # Admin pages
│   └── errors/                # Error pages
└── static/                    # Static files
    ├── css/
    │   └── main.css           # Main stylesheet
    ├── js/
    │   └── main.js            # Main JavaScript
    └── images/
```

## ⚡ Features Included

### ✅ **Core Features**
- ✅ User authentication (login/register)
- ✅ Learning dashboard with progress tracking
- ✅ Learning paths, subjects, modules, and lessons
- ✅ Test system with questions and results
- ✅ Virtual patients with interactive clinical scenarios
- ✅ User progress analytics
- ✅ Admin panel for content management
- ✅ Multi-language support (9 languages)
- ✅ Light/Dark theme switching
- ✅ Responsive design (mobile-friendly)
- ✅ Modern UI with Bootstrap 5

### 🗄️ **Database Models**
- **User** - Authentication and profile
- **LearningPath** - Top-level categories
- **Subject** - Subject areas
- **Module** - Learning modules
- **Lesson** - Individual lessons
- **UserProgress** - Progress tracking
- **Question** - Test questions
- **QuestionCategory** - Question organization
- **VirtualPatientScenario** - Clinical scenarios
- **VirtualPatientAttempt** - User attempts and results

### 🎯 **Key Benefits**
- **65% fewer dependencies** (25 vs 71 packages)
- **Clean architecture** - organized by feature
- **Modern design** - Bootstrap 5 + custom CSS
- **Production ready** - includes error handling, logging
- **Scalable** - modular structure for easy expansion

## 🔧 Configuration

### Environment Variables
```bash
# Development
export FLASK_DEBUG=true
export SECRET_KEY=your-secret-key

# Database (optional - defaults to SQLite)
export DATABASE_URL=postgresql://user:pass@localhost/db

# Server
export HOST=0.0.0.0
export PORT=5000
```

### Development Mode
```bash
FLASK_DEBUG=true python run.py
```

### Production Deployment
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

## 📊 Database Commands

### Reset Database
```bash
python -c "
from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print('Database reset complete!')
"
```

### Create More Sample Data
```bash
python -c "
from app import create_app
from extensions import db
from models import *

app = create_app()
with app.app_context():
    # Add more learning paths, subjects, etc.
    # Your custom data creation here
    print('Custom data created!')
"
```

## 🎨 Customization

### Adding New Routes
1. Create new file in `routes/`
2. Define blueprint and routes
3. Register in `app.py`

### Adding New Templates
1. Create HTML files in `templates/`
2. Extend `base.html`
3. Add custom CSS/JS as needed

### Styling Changes
- Edit `static/css/main.css`
- Add custom CSS variables
- Modify Bootstrap theme

## 🦷 Virtual Patients System

### Overview
The virtual patients system allows students to practice clinical skills through interactive scenarios. Each scenario presents a patient case with multiple decision points, providing a safe environment to learn and make mistakes.

### Features
- **Interactive Dialogues**: Step-by-step conversations with virtual patients
- **Clinical Decision Making**: Multiple-choice decisions with immediate feedback
- **Progress Tracking**: Detailed analytics on performance and choices
- **Difficulty Levels**: Easy, medium, and hard scenarios
- **Scoring System**: Points-based evaluation with detailed feedback
- **Admin Management**: Full control over scenarios and student progress

### Sample Scenarios
The system includes three sample scenarios:

1. **"Pain After Filling"** (Easy)
   - Patient complains of pain after recent dental work
   - Focus: Basic diagnostic skills and treatment planning

2. **"Acute Pain with Diabetes"** (Medium)
   - Patient with diabetes experiencing severe tooth pain
   - Focus: Managing patients with medical conditions

3. **"Anxious Patient with Dental Phobia"** (Hard)
   - Patient with severe dental anxiety requiring special approach
   - Focus: Communication skills and patient management

### How It Works
1. Students select a scenario from the list
2. Read patient information and medical history
3. Engage in step-by-step dialogue with the virtual patient
4. Make clinical decisions at each decision point
5. Receive immediate feedback on choices
6. Complete the scenario and review results
7. Access detailed performance analytics

### Admin Features
- View all scenarios and their statistics
- Monitor student progress and performance
- Publish/unpublish scenarios
- Export data for analysis
- Create custom scenarios (through database)

### Getting Started
1. Run the sample data creation script
2. Log in as admin to manage scenarios
3. Students can access scenarios through the navigation menu
4. Review progress in the admin dashboard

The virtual patients system is designed to be extensible, allowing for easy addition of new scenarios and features.

## 🐛 Troubleshooting

### Common Issues

**Database connection error:**
```bash
# Check database URL
echo $DATABASE_URL

# Reset database
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

**Import errors:**
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version (requires 3.8+)
python --version
```

**Permission errors:**
```bash
# Make run script executable
chmod +x run.py

# Run with Python
python run.py
```

## 🔄 Migration from Original Project

### What was removed:
- Content editor (GrapesJS, visual builder)
- Virtual patients (complex scenarios)
- Forum system
- AI integration
- Complex admin features
- Deployment tools
- Video streaming
- Payment system

### What was kept:
- Core learning system
- User management
- Test system
- Progress tracking
- Basic admin panel
- Theme system
- Multi-language support

## 📈 Next Steps

### Phase 1 - Basic Setup
- [x] Setup and run application
- [x] Create admin user
- [x] Add sample content
- [x] Test user registration

### Phase 2 - Content Creation
- [ ] Add real learning content
- [ ] Create test questions
- [ ] Organize learning paths
- [ ] Setup user roles

### Phase 3 - Customization
- [ ] Brand styling
- [ ] Additional features
- [ ] Performance optimization
- [ ] Production deployment

---

🎉 **Congratulations!** You now have a clean, working dental education platform ready for customization and development. 