from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from urllib.parse import urlparse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import requests
from dotenv import load_dotenv
import secrets
import string
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)  # Extended to 7 days
app.config['JWT_ALGORITHM'] = 'HS256'

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')

jwt = JWTManager(app)

# Database configuration
if os.environ.get('DATABASE_URL'):
    # For production (Render)
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # For local development - using SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todoapp.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration with error handling
try:
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = os.getenv('MAIL_PORT', '587')
    app.config['MAIL_PORT'] = int(mail_port) if mail_port.isdigit() else 587
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    print("✅ Email configuration loaded successfully")
except Exception as e:
    print(f"⚠️ Email configuration error: {e}")
    # Set default values
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)
mail = Mail(app)

# Blacklist for JWT tokens (for logout)
blacklisted_tokens = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blacklisted_tokens

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for Google users
    google_id = db.Column(db.String(100), unique=True, nullable=True)  # Google user ID
    profile_picture = db.Column(db.String(200), nullable=True)  # Google profile picture
    auth_provider = db.Column(db.String(20), default='local')  # 'local' or 'google'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with todos
    todos = db.relationship('Todo', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        if password:  # Only set password for local auth
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:  # Google users don't have password
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profile_picture': self.profile_picture,
            'auth_provider': self.auth_provider,
            'created_at': self.created_at.isoformat()
        }

# Todo Model (Updated with user relationship)
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        }

# Email Notification Functions
def send_email_sync(msg):
    """Send email synchronously"""
    try:
        mail.send(msg)
        print(f"✅ Email sent successfully to {msg.recipients}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

def send_todo_creation_email(user_email, username, todo_title, todo_description=None, user_id=None):
    """Send email notification when a new todo is created with list of all active tasks"""
    
    # Check if email notifications are enabled
    if not os.getenv('SEND_EMAIL_NOTIFICATIONS', 'True').lower() == 'true':
        print("Email notifications are disabled")
        return False
    
    # Check if email configuration is set up
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("Email configuration not set up - skipping email notification")
        return False
    
    try:
        # Get all active (incomplete) todos for the user
        active_todos = []
        if user_id:
            active_todos = Todo.query.filter_by(user_id=user_id, completed=False).order_by(Todo.created_at.desc()).all()
        
        # Create email message
        subject = f"🎯 New Todo Added: {todo_title} | {len(active_todos)} Active Tasks"
        
        # Build active tasks list for HTML
        active_tasks_html = ""
        if active_todos:
            active_tasks_html = "<h3>📋 Your Current Active Tasks:</h3>"
            for i, task in enumerate(active_todos, 1):
                task_description = f"<br><small style='color: #666;'>{task.description}</small>" if task.description else ""
                task_date = task.created_at.strftime('%b %d, %Y')
                
                # Highlight the newly created task
                if task.title == todo_title and task.description == todo_description:
                    active_tasks_html += f"""
                    <div style="background: #e8f5e8; padding: 12px; border-radius: 6px; border-left: 4px solid #28a745; margin: 8px 0;">
                        <strong style="color: #28a745;">🆕 {i}. {task.title}</strong> <span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">NEW</span>
                        {task_description}
                        <br><small style="color: #666;">📅 Created: {task_date}</small>
                    </div>
                    """
                else:
                    active_tasks_html += f"""
                    <div style="background: white; padding: 12px; border-radius: 6px; border-left: 4px solid #667eea; margin: 8px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <strong>📌 {i}. {task.title}</strong>
                        {task_description}
                        <br><small style="color: #666;">📅 Created: {task_date}</small>
                    </div>
                    """
        else:
            active_tasks_html = "<p style='color: #666; font-style: italic;'>🎉 This is your first active task!</p>"
        
        # Build active tasks list for plain text
        active_tasks_text = ""
        if active_todos:
            active_tasks_text = f"\n📋 Your Current Active Tasks ({len(active_todos)} total):\n" + "="*50 + "\n"
            for i, task in enumerate(active_todos, 1):
                task_description = f"\n   📝 {task.description}" if task.description else ""
                task_date = task.created_at.strftime('%b %d, %Y')
                
                # Highlight the newly created task
                if task.title == todo_title and task.description == todo_description:
                    active_tasks_text += f"\n🆕 {i}. {task.title} [NEW TASK]{task_description}\n   📅 Created: {task_date}\n"
                else:
                    active_tasks_text += f"\n📌 {i}. {task.title}{task_description}\n   📅 Created: {task_date}\n"
        else:
            active_tasks_text = "\n🎉 This is your first active task!"
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                .new-todo-card {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .stats-bar {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin: 15px 0; text-align: center; }}
                .tasks-container {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; max-height: 400px; overflow-y: auto; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
                .btn-success {{ background: #28a745; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📝 Todo App Notification</h1>
                    <p>New Task Added Successfully!</p>
                </div>
                <div class="content">
                    <h2>Hello {username}! 👋</h2>
                    <p>You've successfully added a new task to your todo list:</p>
                    
                    <div class="new-todo-card">
                        <h3>🆕 {todo_title}</h3>
                        {f'<p><strong>Description:</strong> {todo_description}</p>' if todo_description else ''}
                        <p><strong>Status:</strong> ⭕ Active</p>
                        <p><strong>Added:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                    
                    <div class="stats-bar">
                        <h3>📊 Your Task Summary</h3>
                        <p><strong>{len(active_todos)} Active Tasks</strong> • Ready to tackle!</p>
                    </div>
                    
                    <div class="tasks-container">
                        {active_tasks_html}
                    </div>
                    
                    <p>🎯 <strong>Quick Actions:</strong></p>
                    <ul>
                        <li>✏️ Click edit to modify any task</li>
                        <li>✅ Click status to mark tasks complete</li>
                        <li>🗑️ Click delete to remove tasks</li>
                        <li>🔍 Use filters to organize your view</li>
                        <li>📊 Check your progress statistics</li>
                    </ul>
                    
                    <div style="text-align: center;">
                        <a href="http://localhost:3000" class="btn">🚀 Open Todo App</a>
                        <a href="http://localhost:3000" class="btn btn-success">✅ Manage Tasks</a>
                    </div>
                </div>
                <div class="footer">
                    <p>📱 This email was sent from your Todo App</p>
                    <p>🔧 You receive this email whenever you add a new task</p>
                    <p>📊 Total Active Tasks: {len(active_todos)} | Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        Hello {username}!
        
        🆕 NEW TASK ADDED SUCCESSFULLY!
        
        📌 Title: {todo_title}
        {f'📝 Description: {todo_description}' if todo_description else ''}
        ⭕ Status: Active
        📅 Added: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        📊 TASK SUMMARY:
        • Total Active Tasks: {len(active_todos)}
        • Status: Ready to tackle!
        {active_tasks_text}
        
        🚀 Open your Todo App: http://localhost:3000
        
        🎯 Quick Actions:
        • ✏️ Edit tasks by clicking the edit button
        • ✅ Mark complete by clicking the status button
        • 🗑️ Delete tasks by clicking the delete button
        • 🔍 Use filters to organize your view
        • 📊 Check your progress statistics
        
        📱 This email was sent from your Todo App
        🔧 You receive this email whenever you add a new task
        📊 Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body,
            body=text_body
        )
        
        # Send email synchronously
        success = send_email_sync(msg)
        
        if success:
            print(f"📧 Email notification with {len(active_todos)} active tasks sent successfully to {user_email}")
        else:
            print(f"❌ Failed to send email notification to {user_email}")
        
        return success
        
    except Exception as e:
        print(f"Error creating email notification: {str(e)}")
        return False

# Password Reset Functions
def generate_password_reset_token(email):
    """Generate a signed token for password reset"""
    serializer = URLSafeTimedSerializer(app.config['JWT_SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_password_reset_token(token, expiration=3600):
    """Verify password reset token (expires in 1 hour by default)"""
    serializer = URLSafeTimedSerializer(app.config['JWT_SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None

def send_password_reset_email(user_email, username, reset_token):
    """Send password reset email with reset link"""
    
    # Check if email notifications are enabled
    if not os.getenv('SEND_EMAIL_NOTIFICATIONS', 'True').lower() == 'true':
        print("Email notifications are disabled")
        return False
    
    # Check if email configuration is set up
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("Email configuration not set up - skipping password reset email")
        return False
    
    try:
        # Create reset link
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        
        # Create email subject
        subject = "🔐 Password Reset Request - Todo App"
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                .reset-card {{ background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 15px; border-radius: 8px; margin: 15px 0; text-align: center; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
                .btn-danger {{ background: #ff6b6b; }}
                .warning {{ background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #ffc107; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                    <p>Todo App Security</p>
                </div>
                <div class="content">
                    <h2>Hello {username}! 👋</h2>
                    <p>We received a request to reset your password for your Todo App account.</p>
                    
                    <div class="reset-card">
                        <h3>🔑 Password Reset Requested</h3>
                        <p><strong>Account:</strong> {user_email}</p>
                        <p><strong>Requested:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                    
                    <p>Click the button below to reset your password:</p>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{reset_link}" class="btn btn-danger">🔐 Reset Password</a>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul>
                            <li>This link will expire in <strong>1 hour</strong></li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>Your password will remain unchanged until you create a new one</li>
                            <li>For security, this link can only be used once</li>
                        </ul>
                    </div>
                    
                    <p><strong>Can't click the button?</strong> Copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px; font-family: monospace;">
                        {reset_link}
                    </p>
                    
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://localhost:3000" class="btn">🚀 Back to Todo App</a>
                    </div>
                </div>
                <div class="footer">
                    <p>🔒 This is a security email from your Todo App</p>
                    <p>📧 If you have questions, please contact support</p>
                    <p>🕒 Reset link expires: {(datetime.now() + timedelta(hours=1)).strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        Hello {username}!
        
        🔐 PASSWORD RESET REQUEST
        
        We received a request to reset your password for your Todo App account.
        
        Account: {user_email}
        Requested: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        To reset your password, click this link:
        {reset_link}
        
        ⚠️ SECURITY NOTICE:
        • This link will expire in 1 hour
        • If you didn't request this reset, please ignore this email
        • Your password will remain unchanged until you create a new one
        • For security, this link can only be used once
        
        If you can't click the link, copy and paste it into your browser.
        
        🚀 Back to Todo App: http://localhost:3000
        
        🔒 This is a security email from your Todo App
        📧 If you have questions, please contact support
        🕒 Reset link expires: {(datetime.now() + timedelta(hours=1)).strftime('%B %d, %Y at %I:%M %p')}
        """
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body,
            body=text_body
        )
        
        # Send email synchronously
        success = send_email_sync(msg)
        
        if success:
            print(f"🔐 Password reset email sent successfully to {user_email}")
        else:
            print(f"❌ Failed to send password reset email to {user_email}")
        
        return success
        
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create access token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklisted_tokens.add(jti)
    return jsonify({'message': 'Successfully logged out'}), 200

# Password Reset Routes
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # For security, don't reveal if email exists or not
            return jsonify({
                'message': 'If an account with that email exists, a password reset link has been sent.',
                'email_sent': False
            }), 200
        
        # Check if user uses local authentication
        if user.auth_provider != 'local':
            return jsonify({
                'error': f'This account uses {user.auth_provider} authentication. Please use {user.auth_provider} to sign in.',
                'email_sent': False
            }), 400
        
        # Generate reset token
        reset_token = generate_password_reset_token(user.email)
        
        # Send password reset email
        email_sent = send_password_reset_email(user.email, user.username, reset_token)
        
        return jsonify({
            'message': 'If an account with that email exists, a password reset link has been sent.',
            'email_sent': email_sent
        }), 200
        
    except Exception as e:
        print(f"Error in forgot_password: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Verify reset token
        email = verify_password_reset_token(token)
        
        if not email:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user uses local authentication
        if user.auth_provider != 'local':
            return jsonify({
                'error': f'This account uses {user.auth_provider} authentication. Password cannot be reset.'
            }), 400
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        print(f"🔐 Password reset successful for user: {user.username}")
        
        return jsonify({
            'message': 'Password has been reset successfully. You can now login with your new password.',
            'success': True
        }), 200
        
    except Exception as e:
        print(f"Error in reset_password: {str(e)}")
        return jsonify({'error': 'An error occurred while resetting your password'}), 500

@app.route('/api/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Verify if reset token is valid"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        # Verify reset token
        email = verify_password_reset_token(token)
        
        if not email:
            return jsonify({
                'valid': False,
                'error': 'Invalid or expired reset token'
            }), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'valid': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'valid': True,
            'email': email,
            'username': user.username
        }), 200
        
    except Exception as e:
        print(f"Error in verify_reset_token: {str(e)}")
        return jsonify({
            'valid': False,
            'error': 'An error occurred while verifying the token'
        }), 500

# Google OAuth Routes
@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """Handle Google OAuth authentication"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Google token is required'}), 400
        
        # Verify the Google token
        try:
            # For development, we'll use a simpler approach
            # In production, you should verify the token properly
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            
            # Get user info from Google
            google_id = idinfo['sub']
            email = idinfo['email']
            name = idinfo.get('name', email.split('@')[0])
            picture = idinfo.get('picture', '')
            
        except ValueError as e:
            # For development, let's also try a direct API call approach
            try:
                response = requests.get(f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}')
                if response.status_code == 200:
                    token_info = response.json()
                    # Get user profile
                    profile_response = requests.get(f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}')
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        google_id = profile_data['id']
                        email = profile_data['email']
                        name = profile_data.get('name', email.split('@')[0])
                        picture = profile_data.get('picture', '')
                    else:
                        return jsonify({'error': 'Failed to get user profile from Google'}), 400
                else:
                    return jsonify({'error': 'Invalid Google token'}), 400
            except Exception as api_error:
                return jsonify({'error': f'Google authentication failed: {str(api_error)}'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(google_id=google_id).first()
        if existing_user:
            # User exists, log them in
            access_token = create_access_token(identity=str(existing_user.id))
            return jsonify({
                'access_token': access_token,
                'user': existing_user.to_dict(),
                'message': 'Login successful'
            }), 200
        
        # Check if email is already used by local account
        email_user = User.query.filter_by(email=email).first()
        if email_user and email_user.auth_provider == 'local':
            return jsonify({
                'error': 'An account with this email already exists. Please login with your password.'
            }), 400
        
        # Create new user
        # Generate unique username if needed
        base_username = name.lower().replace(' ', '_')
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{counter}"
            counter += 1
        
        new_user = User(
            username=username,
            email=email,
            google_id=google_id,
            profile_picture=picture,
            auth_provider='google'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(new_user.id))
        
        return jsonify({
            'access_token': access_token,
            'user': new_user.to_dict(),
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Authentication failed: {str(e)}'}), 500

@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

# Todo Routes (Updated with authentication)
@app.route('/api/todos', methods=['GET'])
@jwt_required()
def get_todos():
    current_user_id = int(get_jwt_identity())
    todos = Todo.query.filter_by(user_id=current_user_id).order_by(Todo.created_at.desc()).all()
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/api/send-email-summary', methods=['POST'])
@jwt_required()
def send_email_summary():
    """Send email summary of active tasks on demand"""
    current_user_id = int(get_jwt_identity())
    
    # Get user information
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if email configuration is set up
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        return jsonify({
            'error': 'Email configuration not set up',
            'message': 'Please configure email settings to send notifications'
        }), 400
    
    try:
        # Get all active todos for the user
        active_todos = Todo.query.filter_by(user_id=current_user_id, completed=False).order_by(Todo.created_at.desc()).all()
        
        # Create email subject
        subject = f"📊 Todo Summary: {len(active_todos)} Active Tasks | Sent on Demand"
        
        # Build active tasks list for HTML
        active_tasks_html = ""
        if active_todos:
            active_tasks_html = "<h3>📋 Your Current Active Tasks:</h3>"
            for i, task in enumerate(active_todos, 1):
                task_description = f"<br><small style='color: #666;'>{task.description}</small>" if task.description else ""
                task_date = task.created_at.strftime('%b %d, %Y')
                
                active_tasks_html += f"""
                <div style="background: white; padding: 12px; border-radius: 6px; border-left: 4px solid #667eea; margin: 8px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <strong>📌 {i}. {task.title}</strong>
                    {task_description}
                    <br><small style="color: #666;">📅 Created: {task_date}</small>
                </div>
                """
        else:
            active_tasks_html = "<p style='color: #666; font-style: italic;'>🎉 No active tasks! You're all caught up!</p>"
        
        # Build active tasks list for plain text
        active_tasks_text = ""
        if active_todos:
            active_tasks_text = f"\n📋 Your Current Active Tasks ({len(active_todos)} total):\n" + "="*50 + "\n"
            for i, task in enumerate(active_todos, 1):
                task_description = f"\n   📝 {task.description}" if task.description else ""
                task_date = task.created_at.strftime('%b %d, %Y')
                active_tasks_text += f"\n📌 {i}. {task.title}{task_description}\n   📅 Created: {task_date}\n"
        else:
            active_tasks_text = "\n🎉 No active tasks! You're all caught up!"
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                .stats-bar {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 15px; border-radius: 8px; margin: 15px 0; text-align: center; }}
                .tasks-container {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; max-height: 400px; overflow-y: auto; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
                .btn-success {{ background: #28a745; }}
                .on-demand-badge {{ background: #ffc107; color: #212529; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Todo App Summary</h1>
                    <p>On-Demand Task Summary</p>
                    <span class="on-demand-badge">📧 SENT ON DEMAND</span>
                </div>
                <div class="content">
                    <h2>Hello {user.username}! 👋</h2>
                    <p>Here's your current task summary as requested:</p>
                    
                    <div class="stats-bar">
                        <h3>📊 Your Task Summary</h3>
                        <p><strong>{len(active_todos)} Active Tasks</strong> • {'Ready to tackle!' if active_todos else 'All caught up!'}</p>
                    </div>
                    
                    <div class="tasks-container">
                        {active_tasks_html}
                    </div>
                    
                    <p>🎯 <strong>Quick Actions:</strong></p>
                    <ul>
                        <li>✏️ Click edit to modify any task</li>
                        <li>✅ Click status to mark tasks complete</li>
                        <li>🗑️ Click delete to remove tasks</li>
                        <li>🔍 Use filters to organize your view</li>
                        <li>📊 Check your progress statistics</li>
                        <li>📧 Use the "Send Email Summary" button for on-demand updates</li>
                    </ul>
                    
                    <div style="text-align: center;">
                        <a href="http://localhost:3000" class="btn">🚀 Open Todo App</a>
                        <a href="http://localhost:3000" class="btn btn-success">✅ Manage Tasks</a>
                    </div>
                </div>
                <div class="footer">
                    <p>📱 This email was sent on-demand from your Todo App</p>
                    <p>🔧 You requested this summary using the "Send Email Summary" button</p>
                    <p>📊 Total Active Tasks: {len(active_todos)} | Sent: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        Hello {user.username}!
        
        📊 ON-DEMAND TASK SUMMARY
        
        Here's your current task summary as requested:
        
        📊 TASK SUMMARY:
        • Total Active Tasks: {len(active_todos)}
        • Status: {'Ready to tackle!' if active_todos else 'All caught up!'}
        {active_tasks_text}
        
        🚀 Open your Todo App: http://localhost:3000
        
        🎯 Quick Actions:
        • ✏️ Edit tasks by clicking the edit button
        • ✅ Mark complete by clicking the status button
        • 🗑️ Delete tasks by clicking the delete button
        • 🔍 Use filters to organize your view
        • 📊 Check your progress statistics
        • 📧 Use the "Send Email Summary" button for on-demand updates
        
        📱 This email was sent on-demand from your Todo App
        🔧 You requested this summary using the "Send Email Summary" button
        📊 Sent: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            body=text_body
        )
        
        # Send email synchronously
        success = send_email_sync(msg)
        
        if success:
            return jsonify({
                'message': 'Email summary sent successfully',
                'email': user.email,
                'active_tasks_count': len(active_todos),
                'sent_at': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send email',
                'message': 'Please check email configuration and try again'
            }), 500
            
    except Exception as e:
        print(f"Error sending email summary: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to send email summary'
        }), 500

@app.route('/api/todos', methods=['POST'])
@jwt_required()
def create_todo():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    # Get user information for email
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    todo = Todo(
        title=data['title'],
        description=data.get('description', ''),
        user_id=current_user_id
    )
    
    db.session.add(todo)
    db.session.commit()
    
    # Send email notification synchronously (if enabled)
    email_sent = False
    email_error = None
    
    try:
        email_sent = send_todo_creation_email(
            user_email=user.email,
            username=user.username,
            todo_title=todo.title,
            todo_description=todo.description,
            user_id=current_user_id
        )
        if email_sent:
            print(f"📧 Email notification sent successfully for todo creation: {todo.title}")
        else:
            print(f"📧 Email notification failed for todo creation: {todo.title}")
    except Exception as e:
        email_error = str(e)
        print(f"❌ Failed to send email notification: {email_error}")
    
    # Return todo data with email status
    response_data = todo.to_dict()
    response_data['email_sent'] = email_sent
    if email_error:
        response_data['email_error'] = email_error
    
    return jsonify(response_data), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    current_user_id = int(get_jwt_identity())
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user_id).first()
    
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'completed' in data:
        todo.completed = data['completed']
    
    todo.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(todo.to_dict())

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    current_user_id = int(get_jwt_identity())
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user_id).first()
    
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify({'message': 'Todo deleted successfully'})

@app.route('/api/debug/token', methods=['GET'])
@jwt_required()
def debug_token():
    from flask_jwt_extended import get_jwt
    current_user_id = int(get_jwt_identity())
    token_data = get_jwt()
    
    return jsonify({
        'user_id': current_user_id,
        'token_jti': token_data.get('jti'),
        'token_exp': token_data.get('exp'),
        'token_iat': token_data.get('iat'),
        'is_blacklisted': token_data.get('jti') in blacklisted_tokens
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

# Serve React frontend (for single service deployment)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    from flask import send_from_directory, send_file
    import os
    
    # If it's an API route, let Flask handle it normally
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    
    # Path to your built React app
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build')
    
    # Debug: Check if frontend directory exists
    if not os.path.exists(frontend_dir):
        return jsonify({
            'error': 'Frontend build directory not found',
            'expected_path': frontend_dir,
            'current_dir': os.path.dirname(__file__)
        }), 500
    
    # Serve static files
    if path != "":
        file_path = os.path.join(frontend_dir, path)
        if os.path.exists(file_path):
            return send_from_directory(frontend_dir, path)
    
    # For React Router - serve index.html for all non-API routes
    index_path = os.path.join(frontend_dir, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    else:
        return jsonify({
            'error': 'index.html not found',
            'frontend_dir': frontend_dir,
            'files': os.listdir(frontend_dir) if os.path.exists(frontend_dir) else 'Directory does not exist'
        }), 500

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
