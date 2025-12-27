from flask import render_template, request, redirect, url_for, flash, abort, jsonify, Response
from app import app, db
from models import WhatsAppGroup, Category, Country, Language, Tag, Page, Post, SiteSettings, Notification
from forms import GroupSubmissionForm
from utils import process_tags, get_site_settings
from datetime import datetime, timezone
from whatsapp_api import get_group_info, fetch_group_image
from sqlalchemy import or_, and_

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category')
    country_filter = request.args.get('country') 
    language_filter = request.args.get('language')
    search_query = request.args.get('q', '')
    
    # Base query - only approved groups
    query = WhatsAppGroup.query.filter_by(status='approved')
    
    # Apply filters
    if category_filter and category_filter != 'Any Category':
        category = Category.query.filter_by(slug=category_filter).first()
        if category:
            query = query.filter_by(category_id=category.id)
    
    if country_filter and country_filter != 'Any Country':
        country = Country.query.filter_by(slug=country_filter).first()
        if country:
            query = query.filter_by(country_id=country.id)
    
    if language_filter and language_filter != 'Any Language':
        language = Language.query.filter_by(slug=language_filter).first()
        if language:
            query = query.filter_by(language_id=language.id)
    
    if search_query:
        query = query.filter(
            or_(
                WhatsAppGroup.name.contains(search_query),
                WhatsAppGroup.description.contains(search_query)
            )
        )
    
    # Order by featured first, then by creation date
    query = query.order_by(WhatsAppGroup.featured.desc(), WhatsAppGroup.created_at.desc())
    
    # Paginate results
    groups = query.paginate(page=page, per_page=20, error_out=False)
    
    # Get filter options
    categories = Category.query.order_by(Category.name).all()
    countries = Country.query.order_by(Country.name).all()
    languages = Language.query.order_by(Language.name).all()
    
    # Get popular categories (with most groups) for homepage
    try:
        popular_categories = db.session.query(Category)\
            .join(WhatsAppGroup)\
            .filter(WhatsAppGroup.status == 'approved')\
            .group_by(Category.id)\
            .order_by(db.func.count(WhatsAppGroup.id).desc())\
            .limit(8).all()
    except Exception:
        popular_categories = Category.query.limit(8).all()
    
    # Get popular tags for homepage
    try:
        from models import group_tags
        popular_tags = db.session.query(Tag)\
            .join(group_tags)\
            .join(WhatsAppGroup)\
            .filter(WhatsAppGroup.status == 'approved')\
            .group_by(Tag.id)\
            .order_by(db.func.count(WhatsAppGroup.id).desc())\
            .limit(15).all()
    except Exception:
        popular_tags = Tag.query.limit(15).all()
    
    # Get site settings and notifications
    settings = get_site_settings()
    notifications = Notification.query.filter_by(is_active=True).all()
    
    return render_template('index.html', 
                         groups=groups, 
                         categories=categories,
                         countries=countries,
                         languages=languages,
                         popular_categories=popular_categories,
                         popular_tags=popular_tags,
                         current_category=category_filter,
                         current_country=country_filter,
                         current_language=language_filter,
                         search_query=search_query,
                         settings=settings,
                         notifications=notifications)

@app.route('/group/<group_slug>')
@app.route('/group/<category_slug>/<group_slug>')
def group_detail(group_slug, category_slug=None):
    """Handle both /group/slug and /group/category/slug URL patterns"""
    if category_slug:
        # Traditional category/group URL pattern
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        group = WhatsAppGroup.query.filter_by(slug=group_slug, category_id=category.id, status='approved').first_or_404()
    else:
        # Direct group URL pattern - find group by slug only
        group = WhatsAppGroup.query.filter_by(slug=group_slug, status='approved').first_or_404()
    
    # Get related groups
    related_groups = group.get_related_groups()
    
    settings = get_site_settings()
    
    return render_template('group_detail.html', group=group, related_groups=related_groups, settings=settings)

@app.route('/group/join/<invite_code>')
def group_join(invite_code):
    group = WhatsAppGroup.query.filter_by(invite_code=invite_code, status='approved').first_or_404()
    settings = get_site_settings()
    return render_template('group_join.html', group=group, settings=settings)

@app.route('/api/tags')
def get_tags():
    """API endpoint to get existing tags for suggestions"""
    try:
        # Get all unique tags from approved groups
        tags = db.session.query(Tag.name).distinct().order_by(Tag.name).limit(50).all()
        tag_list = [tag[0] for tag in tags]
        return jsonify({'tags': tag_list})
    except Exception as e:
        app.logger.error(f"Error fetching tags: {e}")
        return jsonify({'tags': []})

@app.route('/submit-group', methods=['GET', 'POST'])
def submit_group():
    form = GroupSubmissionForm()
    
    # Populate form choices
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    form.country_id.choices = [(c.id, c.name) for c in Country.query.order_by(Country.name).all()]
    form.language_id.choices = [(l.id, l.name) for l in Language.query.order_by(Language.name).all()]
    
    if form.validate_on_submit():
        # Check if group already exists
        existing_group = WhatsAppGroup.query.filter_by(invite_link=form.invite_link.data).first()
        if existing_group:
            flash('This WhatsApp group has already been submitted.', 'warning')
            return redirect(url_for('submit_group'))
        
        # Create new group
        group = WhatsAppGroup(
            name=form.name.data,
            description=form.description.data,
            invite_link=form.invite_link.data,
            category_id=form.category_id.data,
            country_id=form.country_id.data,
            language_id=form.language_id.data
        )
        
        # Process tags
        if form.tags.data:
            tags = process_tags(form.tags.data)
            group.tags = tags
        
        # Try to fetch group image and info
        try:
            group_info = get_group_info(form.invite_link.data)
            if group_info and group_info.get('image_url'):
                group.image_url = group_info['image_url']
                if group_info.get('member_count'):
                    group.member_count = group_info['member_count']
        except Exception as e:
            app.logger.warning(f"Could not fetch group info: {e}")
        
        try:
            db.session.add(group)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Database error during group submission: {e}")
            flash('There was an error submitting your group. Please try again.', 'error')
            return render_template('submit_group.html', form=form, settings=get_site_settings())
        
        flash('Your group has been submitted for review. It will be published after approval.', 'success')
        return redirect(url_for('index'))
    
    settings = get_site_settings()
    return render_template('submit_group.html', form=form, settings=settings)

@app.route('/category/<category_slug>')
def category_groups(category_slug):
    category = Category.query.filter_by(slug=category_slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    groups = WhatsAppGroup.query.filter_by(category_id=category.id, status='approved')\
                                .order_by(WhatsAppGroup.featured.desc(), WhatsAppGroup.created_at.desc())\
                                .paginate(page=page, per_page=12, error_out=False)
    
    settings = get_site_settings()
    return render_template('category.html', category=category, groups=groups, settings=settings)

@app.route('/categories')
def all_categories():
    """Display all categories in a grid layout"""
    categories = Category.query.order_by(Category.name.asc()).all()
    settings = get_site_settings()
    return render_template('categories.html', categories=categories, settings=settings)

@app.route('/tags')
def all_tags():
    """Display all tags in a grid layout with pagination"""
    page = request.args.get('page', 1, type=int)
    # Get tags with their approved group counts
    tags = Tag.query.outerjoin(Tag.groups.and_(WhatsAppGroup.status == 'approved'))\
                   .group_by(Tag.id)\
                   .order_by(Tag.name.asc())\
                   .paginate(page=page, per_page=24, error_out=False)
    settings = get_site_settings()
    return render_template('tags.html', tags=tags, settings=settings)

@app.route('/languages')
def all_languages():
    """Display all languages in a grid layout with pagination"""
    page = request.args.get('page', 1, type=int)
    languages = Language.query.order_by(Language.name.asc()).paginate(page=page, per_page=24, error_out=False)
    settings = get_site_settings()
    return render_template('languages.html', languages=languages, settings=settings)

@app.route('/countries')
def all_countries():
    """Display all countries in a grid layout with pagination"""
    page = request.args.get('page', 1, type=int)
    countries = Country.query.order_by(Country.name.asc()).paginate(page=page, per_page=24, error_out=False)
    settings = get_site_settings()
    return render_template('countries.html', countries=countries, settings=settings)

@app.route('/country/<country_slug>')
def country_groups(country_slug):
    country = Country.query.filter_by(slug=country_slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    groups = WhatsAppGroup.query.filter_by(country_id=country.id, status='approved')\
                                .order_by(WhatsAppGroup.featured.desc(), WhatsAppGroup.created_at.desc())\
                                .paginate(page=page, per_page=12, error_out=False)
    
    settings = get_site_settings()
    return render_template('country.html', country=country, groups=groups, settings=settings)

@app.route('/language/<language_slug>')
def language_groups(language_slug):
    language = Language.query.filter_by(slug=language_slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    groups = WhatsAppGroup.query.filter_by(language_id=language.id, status='approved')\
                                .order_by(WhatsAppGroup.featured.desc(), WhatsAppGroup.created_at.desc())\
                                .paginate(page=page, per_page=12, error_out=False)
    
    settings = get_site_settings()
    return render_template('language.html', language=language, groups=groups, settings=settings)

@app.route('/tags/<tag_slug>')
def tag_groups(tag_slug):
    tag = Tag.query.filter_by(slug=tag_slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    groups = db.session.query(WhatsAppGroup).join(WhatsAppGroup.tags)\
                      .filter(Tag.id == tag.id, WhatsAppGroup.status == 'approved')\
                      .order_by(WhatsAppGroup.featured.desc(), WhatsAppGroup.created_at.desc())\
                      .paginate(page=page, per_page=12, error_out=False)
    
    settings = get_site_settings()
    return render_template('tag.html', tag=tag, groups=groups, settings=settings)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return redirect(url_for('index'))
    
    # Search in groups, tags
    groups = WhatsAppGroup.query.filter(
        and_(
            WhatsAppGroup.status == 'approved',
            or_(
                WhatsAppGroup.name.contains(query),
                WhatsAppGroup.description.contains(query)
            )
        )
    ).order_by(WhatsAppGroup.featured.desc(), WhatsAppGroup.created_at.desc())\
     .paginate(page=page, per_page=12, error_out=False)
    
    settings = get_site_settings()
    return render_template('search.html', groups=groups, query=query, settings=settings)

@app.route('/page/<page_slug>')
def page_detail(page_slug):
    page = Page.query.filter_by(slug=page_slug, is_published=True).first_or_404()
    settings = get_site_settings()
    return render_template('page_detail.html', page=page, settings=settings)

@app.route('/blog')
def blog():
    page_num = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_published=True)\
                     .order_by(Post.created_at.desc())\
                     .paginate(page=page_num, per_page=6, error_out=False)
    
    settings = get_site_settings()
    return render_template('blog.html', posts=posts, settings=settings)

@app.route('/blog/<post_slug>')
def post_detail(post_slug):
    post = Post.query.filter_by(slug=post_slug, is_published=True).first_or_404()
    settings = get_site_settings()
    return render_template('post_detail.html', post=post, settings=settings)

@app.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap for search engines"""
    # Get the current domain from the request
    from urllib.parse import urljoin
    base_url = request.url_root.rstrip('/')
    
    def format_date(dt):
        """Format datetime for sitemap"""
        if dt:
            return dt.strftime('%Y-%m-%d')
        return datetime.now().strftime('%Y-%m-%d')
    
    # Start building sitemap XML
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Static pages with high priority
    static_pages = [
        ('/', '1.0', 'daily'),
        ('/submit-group', '0.8', 'weekly'),
        ('/categories', '0.9', 'weekly'),
        ('/tags', '0.9', 'weekly'),
        ('/languages', '0.8', 'weekly'),
        ('/countries', '0.8', 'weekly'),
        ('/blog', '0.7', 'daily'),
        ('/search', '0.6', 'monthly'),
    ]
    
    for url, priority, changefreq in static_pages:
        xml_content.append(f'  <url>')
        xml_content.append(f'    <loc>{base_url}{url}</loc>')
        xml_content.append(f'    <lastmod>{format_date(None)}</lastmod>')
        xml_content.append(f'    <changefreq>{changefreq}</changefreq>')
        xml_content.append(f'    <priority>{priority}</priority>')
        xml_content.append(f'  </url>')
    
    # Category pages
    try:
        categories = Category.query.all()
        for category in categories:
            xml_content.append(f'  <url>')
            xml_content.append(f'    <loc>{base_url}/category/{category.slug}</loc>')
            xml_content.append(f'    <lastmod>{format_date(None)}</lastmod>')
            xml_content.append(f'    <changefreq>weekly</changefreq>')
            xml_content.append(f'    <priority>0.8</priority>')
            xml_content.append(f'  </url>')
    except Exception:
        pass
    
    # Country pages
    try:
        countries = Country.query.all()
        for country in countries:
            xml_content.append(f'  <url>')
            xml_content.append(f'    <loc>{base_url}/country/{country.slug}</loc>')
            xml_content.append(f'    <lastmod>{format_date(None)}</lastmod>')
            xml_content.append(f'    <changefreq>weekly</changefreq>')
            xml_content.append(f'    <priority>0.7</priority>')
            xml_content.append(f'  </url>')
    except Exception:
        pass
    
    # Language pages
    try:
        languages = Language.query.all()
        for language in languages:
            xml_content.append(f'  <url>')
            xml_content.append(f'    <loc>{base_url}/language/{language.slug}</loc>')
            xml_content.append(f'    <lastmod>{format_date(None)}</lastmod>')
            xml_content.append(f'    <changefreq>weekly</changefreq>')
            xml_content.append(f'    <priority>0.7</priority>')
            xml_content.append(f'  </url>')
    except Exception:
        pass
    
    # Tag pages
    try:
        tags = Tag.query.all()
        for tag in tags:
            xml_content.append(f'  <url>')
            xml_content.append(f'    <loc>{base_url}/tags/{tag.slug}</loc>')
            xml_content.append(f'    <lastmod>{format_date(getattr(tag, "created_at", None))}</lastmod>')
            xml_content.append(f'    <changefreq>weekly</changefreq>')
            xml_content.append(f'    <priority>0.6</priority>')
            xml_content.append(f'  </url>')
    except Exception:
        pass
    
    # Published blog posts
    try:
        posts = Post.query.filter_by(is_published=True).all()
        for post in posts:
            xml_content.append(f'  <url>')
            xml_content.append(f'    <loc>{base_url}/blog/{post.slug}</loc>')
            xml_content.append(f'    <lastmod>{format_date(getattr(post, "updated_at", None))}</lastmod>')
            xml_content.append(f'    <changefreq>monthly</changefreq>')
            xml_content.append(f'    <priority>0.6</priority>')
            xml_content.append(f'  </url>')
    except Exception:
        pass
    
    # Published static pages
    try:
        pages = Page.query.filter_by(is_published=True).all()
        for page in pages:
            xml_content.append(f'  <url>')
            xml_content.append(f'    <loc>{base_url}/page/{page.slug}</loc>')
            xml_content.append(f'    <lastmod>{format_date(getattr(page, "updated_at", None))}</lastmod>')
            xml_content.append(f'    <changefreq>monthly</changefreq>')
            xml_content.append(f'    <priority>0.5</priority>')
            xml_content.append(f'  </url>')
    except Exception:
        pass
    
    # Approved WhatsApp groups - detail pages
    try:
        groups = WhatsAppGroup.query.filter_by(status='approved').all()
        for group in groups:
            try:
                # Group detail page
                if group.category and group.slug:
                    xml_content.append(f'  <url>')
                    xml_content.append(f'    <loc>{base_url}/group/{group.category.slug}/{group.slug}</loc>')
                    xml_content.append(f'    <lastmod>{format_date(getattr(group, "updated_at", None))}</lastmod>')
                    xml_content.append(f'    <changefreq>weekly</changefreq>')
                    xml_content.append(f'    <priority>0.8</priority>')
                    xml_content.append(f'  </url>')
                
                # Group join page
                if getattr(group, 'invite_code', None):
                    xml_content.append(f'  <url>')
                    xml_content.append(f'    <loc>{base_url}/join/{group.invite_code}</loc>')
                    xml_content.append(f'    <lastmod>{format_date(getattr(group, "updated_at", None))}</lastmod>')
                    xml_content.append(f'    <changefreq>monthly</changefreq>')
                    xml_content.append(f'    <priority>0.9</priority>')
                    xml_content.append(f'  </url>')
            except Exception:
                continue
    except Exception:
        pass
    
    xml_content.append('</urlset>')
    
    # Return XML response with proper content type
    return Response('\n'.join(xml_content), mimetype='application/xml')


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    settings = get_site_settings()
    return render_template('404.html', settings=settings), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    settings = get_site_settings()
    return render_template('500.html', settings=settings), 500

# Template filters
@app.template_filter('truncate')
def truncate_filter(text, length=100):
    if text and len(text) > length:
        return text[:length-3] + '...'
    return text or ''

# Context processors
@app.context_processor
def inject_globals():
    return {
        'site_settings': get_site_settings(),
        'current_year': 2025,
        'categories': Category.query.order_by(Category.name).all(),
        'countries': Country.query.order_by(Country.name).all(),
        'languages': Language.query.order_by(Language.name).all(),
        'notifications': Notification.query.filter_by(is_active=True).all()
    }
