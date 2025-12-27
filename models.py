from app import db
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from datetime import datetime
from slugify import slugify
import uuid

# Association tables for many-to-many relationships
group_tags = db.Table('group_tags',
    db.Column('group_id', db.Integer, db.ForeignKey('whatsapp_group.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    groups = db.relationship('WhatsAppGroup', backref='category_ref', lazy=True)
    
    def __init__(self, name, description=None):
        self.name = name
        self.slug = slugify(name)
        self.description = description

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    groups = db.relationship('WhatsAppGroup', backref='country_ref', lazy=True)
    
    def __init__(self, name, code=None):
        self.name = name
        self.slug = slugify(name.replace(' ', '_'))
        self.code = code

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(5))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    groups = db.relationship('WhatsAppGroup', backref='language_ref', lazy=True)
    
    def __init__(self, name, code=None):
        self.name = name
        self.slug = slugify(name)
        self.code = code

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name):
        self.name = name
        self.slug = slugify(name)

class WhatsAppGroup(db.Model):
    __tablename__ = 'whatsapp_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    invite_link = db.Column(db.String(500), nullable=False, unique=True)
    invite_code = db.Column(db.String(100), nullable=False, unique=True)
    image_url = db.Column(db.String(500))
    member_count = db.Column(db.Integer, default=0)
    
    # Foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    
    # Status and moderation
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    featured = db.Column(db.Boolean, default=False)
    admin_notes = db.Column(db.Text)
    
    # SEO and metadata
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified = db.Column(db.DateTime)
    
    # Relationships
    tags = db.relationship('Tag', secondary=group_tags, lazy='subquery',
                          backref=db.backref('groups', lazy=True))
    
    def __init__(self, name, invite_link, category_id, country_id, language_id, description=None):
        self.name = name
        self.slug = slugify(name)
        self.invite_link = invite_link
        self.invite_code = self._extract_invite_code(invite_link)
        self.category_id = category_id
        self.country_id = country_id
        self.language_id = language_id
        self.description = description
        self.generate_meta_tags()
    
    def _extract_invite_code(self, invite_link):
        """Extract invite code from WhatsApp invite link"""
        if 'chat.whatsapp.com/' in invite_link:
            return invite_link.split('/')[-1]
        return str(uuid.uuid4())[:22]  # Fallback
    
    def generate_meta_tags(self):
        """Generate SEO meta tags"""
        if not self.meta_title:
            self.meta_title = f"{self.name} - WhatsApp Group"
        
        if not self.meta_description and self.description:
            # Take first 160 characters for meta description
            self.meta_description = (self.description[:157] + '...') if len(self.description) > 160 else self.description
        elif not self.meta_description:
            self.meta_description = f"Join {self.name} WhatsApp group. Connect with like-minded people and engage in interesting conversations."
    
    def get_related_groups(self, limit=6):
        """Get related groups based on tags and category"""
        if not self.tags:
            # If no tags, return groups from same category
            return WhatsAppGroup.query.filter(
                WhatsAppGroup.category_id == self.category_id,
                WhatsAppGroup.id != self.id,
                WhatsAppGroup.status == 'approved'
            ).limit(limit).all()
        
        # Get groups that share tags
        tag_ids = [tag.id for tag in self.tags]
        related = db.session.query(WhatsAppGroup).join(group_tags).filter(
            group_tags.c.tag_id.in_(tag_ids),
            WhatsAppGroup.id != self.id,
            WhatsAppGroup.status == 'approved'
        ).distinct().limit(limit).all()
        
        return related

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    content = db.Column(db.Text)
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, title, content=None):
        self.title = title
        self.slug = self._generate_unique_slug(title)
        self.content = content
    
    def _generate_unique_slug(self, title):
        """Generate a unique slug for the page"""
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        
        while Page.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    content = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(500))
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, title, content=None):
        self.title = title
        self.slug = self._generate_unique_slug(title)
        self.content = content
    
    def _generate_unique_slug(self, title):
        """Generate a unique slug for the post"""
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        
        while Post.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default='WhatsApp Groups Directory')
    site_description = db.Column(db.Text, default='Find and join WhatsApp groups from around the world')
    site_logo = db.Column(db.String(500))
    favicon = db.Column(db.String(500))
    google_analytics = db.Column(db.Text)
    custom_head_code = db.Column(db.Text)
    custom_footer_code = db.Column(db.Text)
    contact_email = db.Column(db.String(120))
    social_facebook = db.Column(db.String(200))
    social_twitter = db.Column(db.String(200))
    social_instagram = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), default='info')  # info, success, warning, error
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
