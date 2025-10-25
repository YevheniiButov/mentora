# 🚀 Mentora Production Deployment Checklist

## 📋 Pre-deployment Checklist

### ✅ Database & Migrations
- [ ] All migrations applied: `flask db upgrade`
- [ ] Seed data loaded for both professions:
  - [ ] Tandarts categories: `python scripts/seed_domain_categories.py --commit`
  - [ ] Huisarts categories: `python scripts/seed_huisarts_categories.py --commit`
  - [ ] Question professions assigned: `python scripts/assign_question_professions.py --commit`
- [ ] Database backed up: `pg_dump mentora_db > backup_$(date +%Y%m%d).sql`

### ✅ Environment Configuration
- [ ] Environment variables configured (copy `env.example` to `.env`)
- [ ] Production config validated: `python config.py`
- [ ] DigiD configuration tested (if using real DigiD)
- [ ] Email settings tested
- [ ] reCAPTCHA keys configured
- [ ] Stripe keys configured (if using payments)

### ✅ Static Files & Assets
- [ ] Lottie animations present in `/static/animations/`:
  - [ ] `flame.json` (streak widget)
  - [ ] `fist.json` (achievement)
  - [ ] `arm.json` (category completion)
  - [ ] `brain.json` (session completion)
- [ ] CSS files optimized (if needed)
- [ ] JavaScript files minified (if needed)

### ✅ Security & Performance
- [ ] `SECRET_KEY` is strong and unique
- [ ] `DEBUG = False` in production
- [ ] CSRF protection enabled
- [ ] Session cookies secure
- [ ] Database connection pooling configured
- [ ] Redis cache configured (if using)

## 🚀 Deployment Steps

### 1. Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip postgresql postgresql-contrib nginx redis-server

# Install Python dependencies
pip3 install -r requirements.txt
```

### 2. Database Setup
```bash
# Create production database
sudo -u postgres createdb mentora_production

# Set up database user
sudo -u postgres psql -c "CREATE USER mentora_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mentora_production TO mentora_user;"

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://mentora_user:secure_password@localhost/mentora_production
```

### 3. Application Deployment
```bash
# Clone/update repository
git clone https://github.com/your-repo/mentora.git
cd mentora

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with production values

# Run migrations
export FLASK_ENV=production
flask db upgrade

# Load seed data
python scripts/seed_domain_categories.py --commit
python scripts/seed_huisarts_categories.py --commit
python scripts/assign_question_professions.py --commit
```

### 4. Web Server Configuration (Nginx)
```nginx
# /etc/nginx/sites-available/mentora
server {
    listen 80;
    server_name bigmentor.nl www.bigmentor.nl;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/mentora/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5. Process Management (Systemd)
```ini
# /etc/systemd/system/mentora.service
[Unit]
Description=Mentora Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/mentora
Environment=PATH=/path/to/mentora/venv/bin
Environment=FLASK_ENV=production
ExecStart=/path/to/mentora/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 6. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d bigmentor.nl -d www.bigmentor.nl

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## ✅ Post-deployment Verification

### 🔍 Critical Functionality Tests
- [ ] **Login/Logout**: DigiD authentication works
- [ ] **Individual Plan**: Loads for both tandarts and huisarts
- [ ] **Quick Diagnostic**: 30 questions, 20 minutes, works correctly
- [ ] **Daily Practice**: IRT practice session works
- [ ] **Progress Tab**: Displays real data (not hardcoded)
- [ ] **Lottie Animations**: All animations play correctly
- [ ] **Mobile Responsive**: Works on mobile devices
- [ ] **Email**: Registration and password reset emails work

### 📊 Data Verification
- [ ] User can complete diagnostic test
- [ ] Learning plan updates with diagnostic results
- [ ] Progress tab shows real progress data
- [ ] Categories display correctly for both professions
- [ ] Practice sessions work and save results

### 🔒 Security Verification
- [ ] HTTPS redirect works
- [ ] CSRF protection active
- [ ] Session cookies secure
- [ ] No debug information exposed
- [ ] Error pages don't leak information

## 🚨 Rollback Plan

If issues occur after deployment:

### 1. Quick Rollback
```bash
# Stop the application
sudo systemctl stop mentora

# Restore from backup
sudo -u postgres psql mentora_production < backup_YYYYMMDD.sql

# Restart application
sudo systemctl start mentora
```

### 2. Code Rollback
```bash
# Revert to previous commit
git checkout HEAD~1

# Restart application
sudo systemctl restart mentora
```

### 3. Full Rollback
```bash
# Restore database
sudo -u postgres psql mentora_production < backup_YYYYMMDD.sql

# Revert code
git checkout <previous-stable-commit>

# Restart services
sudo systemctl restart mentora nginx
```

## 📈 Monitoring & Maintenance

### Daily Checks
- [ ] Application logs: `sudo journalctl -u mentora -f`
- [ ] Database performance: `sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"`
- [ ] Disk space: `df -h`
- [ ] Memory usage: `free -h`

### Weekly Tasks
- [ ] Database backup: `pg_dump mentora_production > backup_$(date +%Y%m%d).sql`
- [ ] Log rotation: `sudo logrotate /etc/logrotate.d/mentora`
- [ ] Security updates: `sudo apt update && sudo apt upgrade`

### Monthly Tasks
- [ ] SSL certificate renewal check
- [ ] Database optimization: `VACUUM ANALYZE;`
- [ ] Performance review
- [ ] Security audit

## 🆘 Emergency Contacts

- **System Administrator**: [Your contact]
- **Database Administrator**: [Your contact]
- **Security Officer**: [Your contact]
- **Hosting Provider**: [Your contact]

## 📝 Deployment Log

| Date | Version | Deployed By | Notes |
|------|---------|-------------|-------|
| YYYY-MM-DD | v1.0.0 | [Name] | Initial production deployment |

---

**⚠️ Important Notes:**
- Always test in staging environment first
- Keep database backups before major changes
- Monitor application logs during deployment
- Have rollback plan ready
- Test all critical user flows after deployment
