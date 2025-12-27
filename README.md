# GroupLeft - WhatsApp Groups and Channel Directory

A modern web application for discovering, browsing, and managing WhatsApp groups And Channel. Users can submit groups for moderation, browse by categories/countries/languages, and connect with communities worldwide.

**Live Site:** https://groupleft.com

<img width="2560" height="1430" alt="image" src="https://github.com/user-attachments/assets/9f18c68b-28b7-429b-9975-bbd1482dc45b" />


## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Server Configuration](#server-configuration)
- [Deployment](#deployment)
- [Database](#database)
- [API Endpoints](#api-endpoints)
- [Admin Panel](#admin-panel)

## ✨ Features: 
WhatsApp group and channel have used demand and more than 5 to 7 lakh people in every month search online for Join WhatsApp group and channel. That's why they's project is successful. And recently I generate lots of organic click from Search Engine Optimisation of this website.

### User Features
- 🔍 **Search & Filter** - Find groups by category, country, language, and tags
- 📱 **Group and Channel Submission** - Users can submit WhatsApp groups for approval
- 🏷️ **Tagging System** - Rich tag management with auto-suggestions
- 📖 **Blog System** - Read articles and announcements
- 📱 **Responsive Design** - Mobile-first Bootstrap 5 interface
- 🔗 **Social Sharing** - Share groups on WhatsApp, Twitter, Facebook
- 📊 **Analytics** - All heder and footer code integration
- 🎨 **Modern UI** - Gradient designs, smooth animations

### Admin Features
- 👨‍💼 **Admin Dashboard** - Comprehensive statistics and management tools
- ✅ **Approval Workflow** - Moderate and approve group submissions
- 📝 **Content Management** - Create and edit blog posts and static pages
- 🏷️ **Tag Management** - Create and manage tags
- 🌍 **Category Management** - Organize groups by categories
- 🗺️ **Country Management** - Localize by country
- 🌐 **Language Support** - Multi-language group organization
- ⚙️ **Site Settings** - Configure site-wide settings

### SEO Features
- 🗺️ **Dynamic Sitemap** - Auto-generated XML sitemap for search engines
- 📝 **Meta Tags** - Optimized meta descriptions and titles
- 🔗 **Social Media Cards** - OpenGraph and Twitter Card support
- 📊 **Schema.org Markup** - Structured data for rich snippets
- 🔄 **Pagination** - SEO-friendly pagination

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 3.1.2
- **Database:** SQLAlchemy ORM with SQLite
- **Authentication:** Flask-Login
- **Forms:** WTForms with CSRF protection
- **Server:** Gunicorn (WSGI application server)
- **Reverse Proxy:** Nginx
- **Web Server:** Apache (alternative)

### Frontend
- **Template Engine:** Jinja2
- **CSS Framework:** Bootstrap 5
- **Icons:** Font Awesome 6
- **Rich Text Editor:** CKEditor
- **JavaScript:** Vanilla JS with tag input management

### Additional Libraries
- `python-slugify` - URL-friendly slug generation
- `beautifulsoup4` - Web scraping for group metadata
- `requests` - HTTP requests
- `email-validator` - Email validation
- `gunicorn` - WSGI HTTP server
- `flask-mail` - Email functionality
- `flask-ckeditor` - Rich text editing

## 📁 Project Structure

```
groupleft/
├── app.py                 # Flask application setup & configuration
├── models.py              # SQLAlchemy database models
├── routes.py              # Main application routes
├── admin_routes.py        # Admin panel routes
├── forms.py               # WTForms form definitions
├── utils.py               # Utility functions
├── whatsapp_api.py        # WhatsApp integration & scraping
├── main.py                # WSGI entry point
├── app.wsgi               # WSGI configuration
├── INSTALL.txt            # Manual installation guide
│
├── templates/             # Jinja2 HTML templates
│   ├── base.html         # Base layout template
│   ├── index.html        # Homepage with pagination
│   ├── group_detail.html # Individual group page
│   ├── submit_group.html # Group submission form
│   ├── admin/            # Admin templates
│   └── ...               # Other page templates
│
├── static/               # Static assets
│   ├── css/             # Custom stylesheets
│   ├── js/              # JavaScript files
│   │   ├── tags.js      # Tag input management
│   │   └── ...
│   ├── images/          # Images and logos
│   └── ...
│
├── instance/            # Instance folder
│   └── whatsapp_groups.db  # SQLite database
│
└── venv/                # Python virtual environment
```

## 💾 Database: SQLAlchemy ORM with SQLite 

### Models

#### User
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `password_hash` - Hashed password (min 256 chars)
- `is_admin` - Admin privilege flag
- `created_at` - Creation timestamp

#### WhatsAppGroup
- `id` - Primary key
- `name` - Group name
- `slug` - URL-friendly slug
- `description` - Group description
- `invite_link` - WhatsApp invite URL
- `invite_code` - Extracted invite code
- `image_url` - Group image/icon
- `member_count` - Estimated member count
- `status` - (pending, approved, rejected)
- `featured` - Featured flag for homepage
- `category_id` - Foreign key to Category
- `country_id` - Foreign key to Country
- `language_id` - Foreign key to Language
- `tags` - Many-to-many relationship with Tag
- `created_at`, `updated_at` - Timestamps

#### Category, Country, Language
- `id` - Primary key
- `name` - Display name
- `slug` - URL slug
- `description` - Optional description
- `created_at` - Timestamp

#### Tag
- `id` - Primary key
- `name` - Tag name (max 50 chars)
- `slug` - URL slug
- `usage_count` - Count of approved groups using tag
- `created_at` - Timestamp

#### Post (Blog)
- `id` - Primary key
- `title` - Post title
- `slug` - URL slug
- `content` - Rich text content
- `excerpt` - Short summary
- `featured_image` - Image URL
- `is_published` - Publication flag
- `created_at`, `updated_at` - Timestamps

#### Page (Static Pages)
- `id` - Primary key
- `title` - Page title
- `slug` - URL slug
- `content` - Rich text content
- `is_published` - Publication flag
- `created_at`, `updated_at` - Timestamps

#### SiteSettings
- Global site configuration
- Site name, logo, description
- Social media URLs
- Analytics codes
- Custom head/footer code

## 🚀 Installation

### Prerequisites
- Python 3.12+
- Ubuntu 24.04 LTS (or similar Linux)
- Apache or Nginx web server
- SQLite3

### Local Development

```bash
# Clone repository using:  git clone url 
cd groupleft

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask flask-sqlalchemy flask-login flask-wtf flask-mail flask-ckeditor gunicorn beautifulsoup4 python-slugify requests wtforms email-validator

# Set environment variables
export DATABASE_URL="sqlite:///instance/whatsapp_groups.db"
export SESSION_SECRET="your-secret-key-here"

# Initialize database
python3 -c "
from app import app, db
from models import *
with app.app_context():
    db.create_all()
    print('Database created!')
"

# Run development server
python3 main.py
```

Visit: http://localhost:5000

### Production Deployment

See [Server Configuration](#server-configuration) section below.

## 🖥️ Server Configuration

### Server Details
- **Host:** Linode VPS (Ubuntu 24.04 LTS)
- **IP Address:** restricted access
- **Domain:** groupleft.com
- **SSL:** Let's Encrypt (Certbot)
- **DNS:** Cloudflare (Flexible SSL mode)

### Installation on Production Server

#### 1. System Setup
```bash
# SSH into server
ssh root@ ip-address

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y apache2 libapache2-mod-wsgi-py3 python3-pip python3-venv
# OR for Nginx
apt install -y nginx python3-pip python3-venv certbot python3-certbot-nginx
```

#### 2. Application Setup
```bash
# Create application directory
mkdir -p /var/www/groupleft
cd /var/www/groupleft

# Clone repository (or upload files via FileZilla)
git clone https://github.com/Partha00000/groupleft.git .

# Create virtual environment
python3 -m venv venv

# Install Python packages
venv/bin/pip install flask flask-sqlalchemy flask-login flask-wtf flask-mail flask-ckeditor gunicorn beautifulsoup4 python-slugify requests wtforms email-validator
```

#### 3. Nginx Configuration (Recommended)

Create `/etc/nginx/sites-available/groupleft.com`:

```nginx
upstream groupleft_app {
    server 127.0.0.1:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomin.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomin.com www.yourdomin.com;
    client_max_body_size 10M;

    # Certbot SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomin.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomin.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://groupleft_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/groupleft/static/;
        expires 30d;
    }
}
```

Enable the site:
```bash
sudo ln -sf /etc/nginx/sites-available/yourdomin.com /etc/nginx/sites-enabled/yourdomin.com
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. SSL Certificate with Certbot

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get certificate
certbot certonly --nginx -d yourdomin.com -d www.yourdomin.com

# Auto-renew
systemctl enable certbot.timer
systemctl start certbot.timer
```

#### 5. Application Server Setup

Create `/etc/systemd/system/groupleft.service`:

```ini
[Unit]
Description=GroupLeft Flask Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/groupleft
Environment="DATABASE_URL=sqlite:////var/www/groupleft/instance/whatsapp_groups.db"
Environment="SESSION_SECRET=groupleft-secret-key-2025"
ExecStart=/var/www/groupleft/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 120 main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start groupleft
sudo systemctl enable groupleft
sudo systemctl status groupleft
```

#### 6. Permissions
```bash
sudo chown -R www-data:www-data /var/www/groupleft
sudo chmod -R 755 /var/www/groupleft
sudo chmod 644 /var/www/groupleft/instance/whatsapp_groups.db
```

#### 7. Initial Database & Admin User

```bash
cd /var/www/groupleft
export DATABASE_URL="sqlite:////var/www/groupleft/instance/whatsapp_groups.db"
export SESSION_SECRET="groupleft-secret-key-2025"

venv/bin/python3 << 'EOF'
from app import app, db
from models import Category, Country, Language, Tag, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    # Create admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@yourdomin.com',
            password_hash=generate_password_hash('changeme123'),
            is_admin=True
        )
        db.session.add(admin)
    
    # Add sample data
    for name in ['Business', 'Technology', 'Entertainment', 'Education', 'Sports']:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name, description=f'{name} related groups'))
    
    for name, code in [('United States', 'US'), ('India', 'IN'), ('United Kingdom', 'GB')]:
        if not Country.query.filter_by(name=name).first():
            db.session.add(Country(name=name, code=code))
    
    for name, code in [('English', 'en'), ('Spanish', 'es'), ('French', 'fr')]:
        if not Language.query.filter_by(name=name).first():
            db.session.add(Language(name=name, code=code))
    
    for tag_name in ['popular', 'trending', 'active', 'community']:
        if not Tag.query.filter_by(name=tag_name).first():
            db.session.add(Tag(name=tag_name))
    
    db.session.commit()
    print('✅ Database initialized!')
EOF
```

### Testing

```bash
# Test locally
curl -I http://localhost

# Test from external
curl -I https://yourdomin.com
```

Should return: `HTTP/1.1 200 OK`

## 🔌 API Endpoints

### Public Routes
- `GET /` - Homepage with pagination
- `GET /?page=X` - Paginated group listings
- `GET /group/<slug>` - Individual group detail page
- `GET /group/<category>/<slug>` - Group with category URL
- `GET /group/join/<invite_code>` - WhatsApp group join page
- `GET /category/<slug>` - Groups by category
- `GET /categories` - All categories
- `GET /country/<slug>` - Groups by country
- `GET /countries` - All countries
- `GET /language/<slug>` - Groups by language
- `GET /languages` - All languages
- `GET /tags/<slug>` - Groups by tag
- `GET /tags` - All tags
- `GET /search?q=query&page=X` - Search groups
- `GET /blog` - Blog posts listing
- `GET /blog/<slug>` - Individual blog post
- `GET /page/<slug>` - Static pages
- `GET /sitemap.xml` - XML sitemap for search engines

  
<img width="2560" height="1430" alt="image" src="https://github.com/user-attachments/assets/741a5cea-fa04-422f-8653-ff178859522b" />


### Group Submission
- `GET /submit-group` - Submission form
- `POST /submit-group` - Submit new group
- 
  <img width="2560" height="4340" alt="image" src="https://github.com/user-attachments/assets/0f87f6ce-4df5-4a4a-8eea-38ee0c53f44b" />


### Admin Routes (Login Required)
- `GET /admin` - Dashboard
- `GET /admin/groups` - Manage groups
- `POST /admin/groups/<id>/approve` - Approve group
- `POST /admin/groups/<id>/reject` - Reject group
- `GET /admin/categories` - Manage categories
- `GET /admin/blog` - Manage blog posts
- `GET /admin/pages` - Manage static pages
- `GET /admin/settings` - Site settings

  <img width="2560" height="1430" alt="image" src="https://github.com/user-attachments/assets/21bd1d56-5958-42d8-a7c2-01047384dd44" />


### API Endpoints
- `GET /api/tags` - Get tag suggestions for autocomplete

## 👨‍💼 Admin Panel

**Access:** https://yourdomin.com/admin

Default Login:
- **Username:** admin
- **Password:** changeme123 (⚠️ Change after first login!)

### Admin Features
- Dashboard with statistics
- Group approval workflow
- Content management (blog, pages)
- Category/Country/Language management
- Tag management
- Site-wide settings
- User management

## 📊 Google Search Console

- Dynamic XML sitemap: https://yourdomin.com/sitemap.xml
- Schema.org markup for rich snippets
- Meta tags and OpenGraph support
- Mobile-friendly responsive design

  <img width="2560" height="1430" alt="image" src="https://github.com/user-attachments/assets/8ec07322-bd58-408f-a44b-3691a95bc28e" />


## 🔒 Security

- CSRF protection on all forms
- Secure password hashing (Werkzeug)
- Session-based authentication
- Admin-only access control
- Input validation on all forms
- SQL injection prevention (SQLAlchemy ORM)

## 📝 License

This project is proprietary. All rights reserved.

## 👤 Author

PARTHA BHAKTA : https://parthabhakta.com/ 

## 📞 Support

For issues and support, contact: parthabhakta0000@gmail.com

---

**Last Updated:** December 27, 2025
**Version:** 1.0.0
**Status:** Live at https://yourdomin.com
