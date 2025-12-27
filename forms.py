from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email, Length, URL, Optional
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

class GroupSubmissionForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    invite_link = StringField('WhatsApp Invite Link', validators=[DataRequired(), URL()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    country_id = SelectField('Country', coerce=int, validators=[DataRequired()])
    language_id = SelectField('Language', coerce=int, validators=[DataRequired()])
    tags = StringField('Tags (comma separated)', validators=[Optional()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class GroupEditForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    invite_link = StringField('WhatsApp Invite Link', validators=[DataRequired(), URL()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    country_id = SelectField('Country', coerce=int, validators=[DataRequired()])
    language_id = SelectField('Language', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    featured = BooleanField('Featured')
    tags = StringField('Tags (comma separated)', validators=[Optional()])
    admin_notes = TextAreaField('Admin Notes', validators=[Optional()])
    meta_title = StringField('Meta Title', validators=[Optional(), Length(max=200)])
    meta_description = TextAreaField('Meta Description', validators=[Optional(), Length(max=300)])

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])

class TagForm(FlaskForm):
    name = StringField('Tag Name', validators=[DataRequired(), Length(min=2, max=50)])

class PageForm(FlaskForm):
    title = StringField('Page Title', validators=[DataRequired(), Length(min=2, max=200)])
    content = CKEditorField('Content')
    meta_title = StringField('Meta Title', validators=[Optional(), Length(max=200)])
    meta_description = TextAreaField('Meta Description', validators=[Optional(), Length(max=300)])
    is_published = BooleanField('Published', default=True)

class PostForm(FlaskForm):
    title = StringField('Post Title', validators=[DataRequired(), Length(min=2, max=200)])
    content = CKEditorField('Content')
    excerpt = TextAreaField('Excerpt', validators=[Optional(), Length(max=300)])
    featured_image = StringField('Featured Image URL', validators=[Optional(), URL()])
    meta_title = StringField('Meta Title', validators=[Optional(), Length(max=200)])
    meta_description = TextAreaField('Meta Description', validators=[Optional(), Length(max=300)])
    is_published = BooleanField('Published', default=True)

class SettingsForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired(), Length(min=2, max=100)])
    site_description = TextAreaField('Site Description', validators=[Optional()])
    site_logo = StringField('Site Logo URL', validators=[Optional(), URL()])
    favicon = StringField('Favicon URL', validators=[Optional(), URL()])
    google_analytics = TextAreaField('Google Analytics Code', validators=[Optional()])
    custom_head_code = TextAreaField('Custom Head Code', validators=[Optional()])
    custom_footer_code = TextAreaField('Custom Footer Code', validators=[Optional()])
    contact_email = StringField('Contact Email', validators=[Optional(), Email()])
    social_facebook = StringField('Facebook URL', validators=[Optional(), URL()])
    social_twitter = StringField('Twitter URL', validators=[Optional(), URL()])
    social_instagram = StringField('Instagram URL', validators=[Optional(), URL()])

class NotificationForm(FlaskForm):
    title = StringField('Notification Title', validators=[DataRequired(), Length(min=2, max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])
    notification_type = SelectField('Type', choices=[('info', 'Info'), ('success', 'Success'), ('warning', 'Warning'), ('error', 'Error')])
    is_active = BooleanField('Active', default=True)
