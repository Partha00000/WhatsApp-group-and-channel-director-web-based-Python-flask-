from slugify import slugify
from models import Tag, db
import re

def create_or_get_tag(tag_name):
    """Create a new tag or get existing one"""
    tag_name = tag_name.strip()
    if not tag_name:
        return None
    
    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.session.add(tag)
        db.session.flush()  # To get the ID
    
    return tag

def process_tags(tags_string):
    """Process comma-separated tags string into Tag objects"""
    if not tags_string:
        return []
    
    tag_names = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
    tags = []
    
    for tag_name in tag_names:
        tag = create_or_get_tag(tag_name)
        if tag:
            tags.append(tag)
    
    return tags

def generate_seo_friendly_url(category_slug, group_slug):
    """Generate SEO-friendly URL for group detail page"""
    return f"/group/{category_slug}/{group_slug}"

def extract_whatsapp_invite_code(invite_link):
    """Extract invite code from WhatsApp invite link"""
    if 'chat.whatsapp.com/' in invite_link:
        return invite_link.split('/')[-1]
    return None

def validate_whatsapp_link(invite_link):
    """Validate WhatsApp invite link format"""
    pattern = r'https://chat\.whatsapp\.com/[A-Za-z0-9]+'
    return bool(re.match(pattern, invite_link))

def truncate_text(text, length=160):
    """Truncate text to specified length with ellipsis"""
    if not text:
        return ""
    return (text[:length-3] + '...') if len(text) > length else text

def update_tag_usage_counts():
    """Update usage_count for all tags based on approved groups"""
    from models import Tag, WhatsAppGroup, group_tags
    from app import db
    
    tags = Tag.query.all()
    for tag in tags:
        approved_count = db.session.query(WhatsAppGroup)\
                                  .join(group_tags)\
                                  .filter(group_tags.c.tag_id == tag.id,
                                         WhatsAppGroup.status == 'approved')\
                                  .count()
        tag.usage_count = approved_count
    
    db.session.commit()

def get_site_settings():
    """Get site settings or create default ones"""
    from models import SiteSettings
    from app import db
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    return settings
