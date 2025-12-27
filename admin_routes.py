from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from app import app, db
from models import *
from forms import *
from utils import process_tags, get_site_settings, update_tag_usage_counts
from whatsapp_api import get_group_info, verify_invite_link
from werkzeug.security import check_password_hash
import json
import functools

# Create admin blueprint
admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data) and user.is_admin:
            login_user(user)
            flash('Welcome to the admin panel!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials or insufficient privileges.', 'error')
    
    return render_template('admin/login.html', form=form)

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@admin.route('/')
@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_groups = WhatsAppGroup.query.count()
    approved_groups = WhatsAppGroup.query.filter_by(status='approved').count()
    pending_groups = WhatsAppGroup.query.filter_by(status='pending').count()
    rejected_groups = WhatsAppGroup.query.filter_by(status='rejected').count()
    total_categories = Category.query.count()
    total_countries = Country.query.count()
    total_languages = Language.query.count()
    total_tags = Tag.query.count()
    total_pages = Page.query.count()
    total_posts = Post.query.count()
    
    # Recent activity
    recent_groups = WhatsAppGroup.query.order_by(WhatsAppGroup.created_at.desc()).limit(5).all()
    pending_review = WhatsAppGroup.query.filter_by(status='pending').limit(5).all()
    
    stats = {
        'total_groups': total_groups,
        'approved_groups': approved_groups,
        'pending_groups': pending_groups,
        'rejected_groups': rejected_groups,
        'total_categories': total_categories,
        'total_countries': total_countries,
        'total_languages': total_languages,
        'total_tags': total_tags,
        'total_pages': total_pages,
        'total_posts': total_posts
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_groups=recent_groups,
                         pending_review=pending_review)

@admin.route('/groups')
@login_required
@admin_required
def groups():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    query = WhatsAppGroup.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if search:
        query = query.filter(WhatsAppGroup.name.contains(search))
    
    groups = query.order_by(WhatsAppGroup.created_at.desc())\
                  .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/groups.html', 
                         groups=groups, 
                         status_filter=status_filter,
                         search=search)

@admin.route('/groups/<int:group_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_group(group_id):
    group = WhatsAppGroup.query.get_or_404(group_id)
    form = GroupEditForm(obj=group)
    
    # Populate form choices
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    form.country_id.choices = [(c.id, c.name) for c in Country.query.order_by(Country.name).all()]
    form.language_id.choices = [(l.id, l.name) for l in Language.query.order_by(Language.name).all()]
    
    # Set current tags
    if request.method == 'GET':
        form.tags.data = ', '.join([tag.name for tag in group.tags])
    
    if form.validate_on_submit():
        group.name = form.name.data
        group.description = form.description.data
        group.invite_link = form.invite_link.data
        group.category_id = form.category_id.data
        group.country_id = form.country_id.data
        group.language_id = form.language_id.data
        group.status = form.status.data
        group.featured = form.featured.data
        group.admin_notes = form.admin_notes.data
        group.meta_title = form.meta_title.data
        group.meta_description = form.meta_description.data
        
        # Update slug if name changed
        from slugify import slugify
        group.slug = slugify(group.name)
        
        # Process tags
        group.tags.clear()
        if form.tags.data:
            tags = process_tags(form.tags.data)
            group.tags = tags
        
        # Update invite code
        group.invite_code = group._extract_invite_code(group.invite_link)
        
        # Try to update image if link changed
        if form.invite_link.data != group.invite_link:
            try:
                group_info = get_group_info(form.invite_link.data)
                if group_info and group_info.get('image_url'):
                    group.image_url = group_info['image_url']
            except Exception as e:
                app.logger.warning(f"Could not update group image: {e}")
        
        db.session.commit()
        flash(f'Group "{group.name}" has been updated.', 'success')
        return redirect(url_for('admin.groups'))
    
    return render_template('admin/group_edit.html', form=form, group=group)

@admin.route('/groups/<int:group_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_group(group_id):
    group = WhatsAppGroup.query.get_or_404(group_id)
    group_name = group.name
    
    db.session.delete(group)
    db.session.commit()
    
    flash(f'Group "{group_name}" has been deleted.', 'success')
    return redirect(url_for('admin.groups'))

@admin.route('/groups/bulk-action', methods=['POST'])
@login_required
@admin_required
def bulk_group_action():
    action = request.form.get('action')
    group_ids = request.form.getlist('group_ids')
    
    if not action or not group_ids:
        flash('No action or groups selected.', 'warning')
        return redirect(url_for('admin.groups'))
    
    groups = WhatsAppGroup.query.filter(WhatsAppGroup.id.in_(group_ids)).all()
    
    if action == 'approve':
        for group in groups:
            group.status = 'approved'
        flash(f'{len(groups)} groups have been approved.', 'success')
    elif action == 'reject':
        for group in groups:
            group.status = 'rejected'
        flash(f'{len(groups)} groups have been rejected.', 'success')
    elif action == 'delete':
        for group in groups:
            db.session.delete(group)
        flash(f'{len(groups)} groups have been deleted.', 'success')
    elif action == 'feature':
        for group in groups:
            group.featured = True
        flash(f'{len(groups)} groups have been featured.', 'success')
    elif action == 'unfeature':
        for group in groups:
            group.featured = False
        flash(f'{len(groups)} groups have been unfeatured.', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.groups'))

@admin.route('/categories')
@login_required
@admin_required
def categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data)
        db.session.add(category)
        db.session.commit()
        flash(f'Category "{category.name}" has been created.', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_edit.html', form=form, category=None)

@admin.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.slug = slugify(category.name)
        db.session.commit()
        flash(f'Category "{category.name}" has been updated.', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_edit.html', form=form, category=category)

@admin.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Check if category has groups
    if category.groups:
        flash(f'Cannot delete category "{category.name}" because it has {len(category.groups)} groups.', 'error')
        return redirect(url_for('admin.categories'))
    
    category_name = category.name
    db.session.delete(category)
    db.session.commit()
    
    flash(f'Category "{category_name}" has been deleted.', 'success')
    return redirect(url_for('admin.categories'))

@admin.route('/update-tag-counts')
@login_required
@admin_required
def update_tag_counts():
    """Update tag usage counts"""
    try:
        update_tag_usage_counts()
        flash('Tag usage counts updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating tag counts: {str(e)}', 'error')
    return redirect(url_for('admin.tags'))

@admin.route('/tags')
@login_required
@admin_required
def tags():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Tag.query
    if search:
        query = query.filter(Tag.name.contains(search))
    
    tags = query.order_by(Tag.usage_count.desc(), Tag.name)\
               .paginate(page=page, per_page=50, error_out=False)
    
    return render_template('admin/tags.html', tags=tags, search=search)

@admin.route('/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    tag_name = tag.name
    
    db.session.delete(tag)
    db.session.commit()
    
    flash(f'Tag "{tag_name}" has been deleted.', 'success')
    return redirect(url_for('admin.tags'))

@admin.route('/tags/cleanup-unused', methods=['POST'])
@login_required
@admin_required
def cleanup_unused_tags():
    # Find tags that are not associated with any groups
    unused_tags = Tag.query.filter(~Tag.groups.any()).all()
    
    if not unused_tags:
        flash('No unused tags found.', 'info')
    else:
        count = len(unused_tags)
        for tag in unused_tags:
            db.session.delete(tag)
        db.session.commit()
        flash(f'Successfully deleted {count} unused tags.', 'success')
    
    return redirect(url_for('admin.tags'))

@admin.route('/pages')
@login_required
@admin_required
def pages():
    pages = Page.query.order_by(Page.created_at.desc()).all()
    return render_template('admin/pages.html', pages=pages)

@admin.route('/pages/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_page():
    form = PageForm()
    if form.validate_on_submit():
        page = Page(title=form.title.data, content=form.content.data)
        page.meta_title = form.meta_title.data
        page.meta_description = form.meta_description.data
        page.is_published = form.is_published.data
        
        db.session.add(page)
        db.session.commit()
        flash(f'Page "{page.title}" has been created.', 'success')
        return redirect(url_for('admin.pages'))
    
    return render_template('admin/page_edit.html', form=form, page=None)

@admin.route('/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_page(page_id):
    page = Page.query.get_or_404(page_id)
    form = PageForm(obj=page)
    
    if form.validate_on_submit():
        page.title = form.title.data
        page.content = form.content.data
        page.meta_title = form.meta_title.data
        page.meta_description = form.meta_description.data
        page.is_published = form.is_published.data
        page.slug = slugify(page.title)
        
        db.session.commit()
        flash(f'Page "{page.title}" has been updated.', 'success')
        return redirect(url_for('admin.pages'))
    
    return render_template('admin/page_edit.html', form=form, page=page)

@admin.route('/pages/<int:page_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_page(page_id):
    page = Page.query.get_or_404(page_id)
    page_title = page.title
    
    db.session.delete(page)
    db.session.commit()
    
    flash(f'Page "{page_title}" has been deleted.', 'success')
    return redirect(url_for('admin.pages'))

@admin.route('/posts')
@login_required
@admin_required
def posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts)

@admin.route('/posts/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data)
        post.excerpt = form.excerpt.data
        post.featured_image = form.featured_image.data
        post.meta_title = form.meta_title.data
        post.meta_description = form.meta_description.data
        post.is_published = form.is_published.data
        
        db.session.add(post)
        db.session.commit()
        flash(f'Post "{post.title}" has been created.', 'success')
        return redirect(url_for('admin.posts'))
    
    return render_template('admin/post_edit.html', form=form, post=None)

@admin.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.featured_image = form.featured_image.data
        post.meta_title = form.meta_title.data
        post.meta_description = form.meta_description.data
        post.is_published = form.is_published.data
        post.slug = slugify(post.title)
        
        db.session.commit()
        flash(f'Post "{post.title}" has been updated.', 'success')
        return redirect(url_for('admin.posts'))
    
    return render_template('admin/post_edit.html', form=form, post=post)

@admin.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    post_title = post.title
    
    db.session.delete(post)
    db.session.commit()
    
    flash(f'Post "{post_title}" has been deleted.', 'success')
    return redirect(url_for('admin.posts'))

@admin.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    settings = get_site_settings()
    form = SettingsForm(obj=settings)
    
    if form.validate_on_submit():
        settings.site_name = form.site_name.data
        settings.site_description = form.site_description.data
        settings.site_logo = form.site_logo.data
        settings.favicon = form.favicon.data
        settings.google_analytics = form.google_analytics.data
        settings.custom_head_code = form.custom_head_code.data
        settings.custom_footer_code = form.custom_footer_code.data
        settings.contact_email = form.contact_email.data
        settings.social_facebook = form.social_facebook.data
        settings.social_twitter = form.social_twitter.data
        settings.social_instagram = form.social_instagram.data
        
        db.session.commit()
        flash('Settings have been updated.', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', form=form)

@admin.route('/notifications')
@login_required
@admin_required
def notifications():
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('admin/notifications.html', notifications=notifications)

@admin.route('/notifications/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_notification():
    form = NotificationForm()
    if form.validate_on_submit():
        notification = Notification(
            title=form.title.data,
            message=form.message.data,
            notification_type=form.notification_type.data,
            is_active=form.is_active.data
        )
        
        db.session.add(notification)
        db.session.commit()
        flash(f'Notification "{notification.title}" has been created.', 'success')
        return redirect(url_for('admin.notifications'))
    
    return render_template('admin/notification_edit.html', form=form, notification=None)

@admin.route('/notifications/<int:notification_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    form = NotificationForm(obj=notification)
    
    if form.validate_on_submit():
        notification.title = form.title.data
        notification.message = form.message.data
        notification.notification_type = form.notification_type.data
        notification.is_active = form.is_active.data
        
        db.session.commit()
        flash(f'Notification "{notification.title}" has been updated.', 'success')
        return redirect(url_for('admin.notifications'))
    
    return render_template('admin/notification_edit.html', form=form, notification=notification)

@admin.route('/notifications/<int:notification_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification_title = notification.title
    
    db.session.delete(notification)
    db.session.commit()
    
    flash(f'Notification "{notification_title}" has been deleted.', 'success')
    return redirect(url_for('admin.notifications'))

# Initialize default data
@admin.route('/init-data')
@login_required
@admin_required
def init_data():
    """Initialize default categories, countries, and languages"""
    
    # Categories
    categories_data = [
        'Adult/18+/Hot', 'Art/Design/Photography', 'Auto/Vehicle', 'Business/Advertising/Marketing',
        'Comedy/Funny', 'Dating/Flirting/Chatting', 'Education/School', 'Entertainment/Masti',
        'Family/Relationships', 'Fan Club/Celebrities', 'Fashion/Style/Clothing', 'Film/Animation',
        'Food/Drinks', 'Gaming/Apps', 'Health/Beauty/Fitness', 'Jobs/Career', 'Money/Earning',
        'Music/Audio/Songs', 'News/Magazines/Politics', 'Pets/Animals/Nature', 'Roleplay/Comics',
        'Science/Technology', 'Shopping/Buy/Sell', 'Social/Friendship/Community', 'Spiritual/Devotional',
        'Sports/Games', 'Thoughts/Quotes/Jokes', 'Travel/Local/Place'
    ]
    
    for cat_name in categories_data:
        if not Category.query.filter_by(name=cat_name).first():
            category = Category(name=cat_name)
            db.session.add(category)
    
    # Countries
    countries_data = [
        'Algeria', 'Argentina', 'Australia', 'Austria', 'Azerbaijan', 'Bahrain', 'Bangladesh',
        'Belarus', 'Belgium', 'Bolivia', 'Bosnia and Herzegovina', 'Brazil', 'Bulgaria',
        'Canada', 'Chile', 'China', 'Colombia', 'Croatia', 'Czechia', 'Denmark', 'Egypt',
        'Estonia', 'Ethiopia', 'Finland', 'France', 'Georgia', 'Germany', 'Ghana', 'Greece',
        'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iraq', 'Ireland', 'Israel',
        'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kuwait', 'Latvia',
        'Lebanon', 'Libya', 'Lithuania', 'Luxembourg', 'Macedonia', 'Malawi', 'Malaysia',
        'Mexico', 'Montenegro', 'Morocco', 'Mozambique', 'Nepal', 'Netherlands', 'New Zealand',
        'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Panama', 'Peru', 'Philippines', 'Poland',
        'Portugal', 'Puerto Rico', 'Qatar', 'Romania', 'Russia', 'Saudi Arabia', 'Senegal',
        'Serbia', 'Singapore', 'Slovakia', 'Slovenia', 'South Africa', 'South Korea', 'Spain',
        'Sri Lanka', 'Sweden', 'Switzerland', 'Taiwan', 'Tanzania', 'Thailand', 'Togo',
        'Tunisia', 'Turkey', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom',
        'United States', 'Venezuela', 'Vietnam', 'Yemen', 'Zimbabwe'
    ]
    
    for country_name in countries_data:
        if not Country.query.filter_by(name=country_name).first():
            country = Country(name=country_name)
            db.session.add(country)
    
    # Languages
    languages_data = [
        'Afrikaans', 'Albanian', 'Amharic', 'Arabic', 'Armenian', 'Azerbaijani', 'Bangla',
        'Basque', 'Belarusian', 'Bosnian', 'Bulgarian', 'Catalan', 'Chinese', 'Croatian',
        'Czech', 'Danish', 'Dutch', 'English', 'Estonian', 'Filipino', 'Finnish', 'French',
        'Galician', 'Georgian', 'German', 'Greek', 'Gujarati', 'Hebrew', 'Hindi', 'Hungarian',
        'Icelandic', 'Indonesian', 'Italian', 'Japanese', 'Kannada', 'Kazakh', 'Khmer',
        'Korean', 'Kyrgyz', 'Lao', 'Latvian', 'Lithuanian', 'Macedonian', 'Malay',
        'Malayalam', 'Marathi', 'Mongolian', 'Myanmar', 'Nepali', 'Norwegian', 'Persian',
        'Polish', 'Portuguese', 'Punjabi', 'Romanian', 'Russian', 'Serbian', 'Sinhala',
        'Slovak', 'Slovenian', 'Spanish', 'Swahili', 'Swedish', 'Tamil', 'Telugu', 'Thai',
        'Turkish', 'Ukrainian', 'Urdu', 'Uzbek', 'Vietnamese', 'Zulu'
    ]
    
    for lang_name in languages_data:
        if not Language.query.filter_by(name=lang_name).first():
            language = Language(name=lang_name)
            db.session.add(language)
    
    db.session.commit()
    flash('Default data has been initialized successfully!', 'success')
    return redirect(url_for('admin.dashboard'))
