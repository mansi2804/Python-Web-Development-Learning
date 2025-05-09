"""
Flask Forms Example

This module demonstrates how to handle forms in Flask using Flask-WTF.
Flask-WTF provides simple integration between Flask and WTForms,
including CSRF protection and file uploads.

Key Concepts:
- Creating form classes with Flask-WTF
- Form validation
- CSRF protection
- File uploads
- Flash messages
- Redirects after form submission
"""

from flask import Flask, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
import os

app = Flask(__name__)
# Secret key is required for CSRF protection and session cookies
app.config['SECRET_KEY'] = 'this-is-a-secret-key-for-development-only'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Login form using Flask-WTF
class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Invalid email format")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=6, message="Password must be at least 6 characters")
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Registration form with custom validation
class RegistrationForm(FlaskForm):
    """Form for user registration with custom validation."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register')
    
    # Custom validator method
    def validate_username(self, username):
        """Check if username is already taken (simulation)."""
        taken_usernames = ['admin', 'user', 'moderator']
        if username.data.lower() in taken_usernames:
            raise ValidationError(f"Username '{username.data}' is already taken.")

# Profile form with select fields and file upload
class ProfileForm(FlaskForm):
    """Profile form with various field types."""
    name = StringField('Full Name', validators=[DataRequired()])
    bio = TextAreaField('Biography', validators=[Length(max=200)])
    age = IntegerField('Age', validators=[
        NumberRange(min=18, max=120, message="Age must be between 18 and 120")
    ])
    occupation = StringField('Occupation')
    country = SelectField('Country', choices=[
        ('', 'Select Country'),
        ('us', 'United States'),
        ('ca', 'Canada'),
        ('uk', 'United Kingdom'),
        ('au', 'Australia'),
        ('other', 'Other')
    ])
    profile_pic = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Update Profile')

@app.route('/')
def index():
    """Render the index page with links to form examples."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle login form.
    - GET: Display the form
    - POST: Process form data and perform validation
    """
    form = LoginForm()
    
    # form.validate_on_submit() checks if it's a POST request and if validation passes
    if form.validate_on_submit():
        # In a real app, we would check the credentials against a database
        # For this example, we'll just simulate a successful login
        flash(f'Login successful for {form.email.data}', 'success')
        session['logged_in'] = True
        session['email'] = form.email.data
        return redirect(url_for('index'))
    
    # If it's a GET request or validation failed, render the form
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with more complex validation."""
    form = RegistrationForm()
    
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """Handle profile form with file upload."""
    form = ProfileForm()
    
    if form.validate_on_submit():
        # File handling example
        if form.profile_pic.data:
            filename = form.profile_pic.data.filename
            form.profile_pic.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f'Profile picture "{filename}" uploaded successfully', 'success')
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('profile.html', form=form)

@app.route('/logout')
def logout():
    """Simple logout route that clears the session."""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
