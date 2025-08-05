# Todo App - Full Stack Assignment with JWT Authentication

A secure todo application built with Flask (Python) backend, React frontend, PostgreSQL database, and JWT authentication.

## Tech Stack

- **Backend**: Python Flask with SQLAlchemy and JWT authentication
- **Frontend**: React with Axios and Context API for state management
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: JWT tokens with login/logout functionality
- **Hosting**: Render (free tier)

## Features

- 🔐 **User Authentication**: Register, login, and logout with JWT tokens
- ✅ **Secure Todo Management**: Create, read, update, delete todos (user-specific)
- 🚀 **Token-based Security**: JWT tokens with blacklisting for logout
- 📱 **Responsive Design**: Clean, mobile-friendly interface
- 🔄 **Real-time Updates**: Automatic token validation and session management
- 🛡️ **Protected Routes**: All todo operations require authentication

## New Authentication Features

### Backend Authentication:
- **User Registration**: Create new accounts with username, email, and password
- **User Login**: Authenticate with username/email and password
- **JWT Token Generation**: Secure token-based authentication
- **Token Blacklisting**: Proper logout with token revocation
- **Password Hashing**: Secure password storage using Werkzeug
- **User-specific Data**: Todos are isolated per user

### Frontend Authentication:
- **Login/Register Forms**: Clean, responsive authentication UI
- **AuthContext**: React Context for global authentication state
- **Automatic Token Management**: Tokens stored in localStorage
- **Session Validation**: Automatic token validation on app load
- **Protected Components**: Todo app only accessible when authenticated
- **Logout Functionality**: Secure logout with token cleanup

## Project Structure

```
TO-DO_LIST/
├── backend/
│   ├── app.py              # Flask application with JWT auth
│   ├── requirements.txt    # Python dependencies (includes JWT)
│   ├── Dockerfile         # Docker configuration
│   └── .env.example       # Environment variables template
├── frontend/
│   ├── public/
│   │   └── index.html     # HTML template
│   ├── src/
│   │   ├── App.js         # Main React component with auth
│   │   ├── AuthContext.js # Authentication context provider
│   │   ├── Login.js       # Login component
│   │   ├── Register.js    # Registration component
│   │   ├── Auth.css       # Authentication styles
│   │   ├── App.css        # Main app styles
│   │   ├── index.js       # React entry point
│   │   └── index.css      # Global styles
│   ├── package.json       # Node dependencies
│   └── .env.example       # Frontend environment variables
├── render.yaml            # Render deployment config
└── README.md              # This file
```

## Local Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL (optional - SQLite used for development)
- Git

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your JWT secret key
   ```

5. Run the Flask app:
   ```bash
   python app.py
   ```

Backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   # REACT_APP_API_URL should point to your backend
   ```

4. Start the React app:
   ```bash
   npm start
   ```

Frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication Endpoints:
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/register` | Register new user | No |
| POST | `/api/login` | Login user | No |
| POST | `/api/logout` | Logout user | Yes |
| GET | `/api/me` | Get current user info | Yes |

### Todo Endpoints:
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/todos` | Get user's todos | Yes |
| POST | `/api/todos` | Create new todo | Yes |
| PUT | `/api/todos/:id` | Update todo | Yes |
| DELETE | `/api/todos/:id` | Delete todo | Yes |
| GET | `/api/health` | Health check | No |

### API Request Examples

**Register User:**
```json
POST /api/register
{
  "username": "john",
  "email": "john@example.com",
  "password": "password123"
}
```

**Login User:**
```json
POST /api/login
{
  "username": "john",
  "password": "password123"
}
```

**Create Todo (with JWT token):**
```bash
curl -X POST http://localhost:5000/api/todos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Learn React", "description": "Complete React tutorial"}'
```

## Authentication Flow

1. **Registration/Login**: User provides credentials
2. **Token Generation**: Server creates JWT token
3. **Token Storage**: Frontend stores token in localStorage
4. **Request Authentication**: Token sent in Authorization header
5. **Token Validation**: Server validates token for protected routes
6. **Logout**: Token added to blacklist and removed from client

## Deployment on Render

### Option 1: Using render.yaml (Recommended)

1. Fork/clone this repository to your GitHub account

2. Connect your GitHub repository to Render

3. Render will automatically detect the `render.yaml` file and deploy both services

4. The deployment will create:
   - PostgreSQL database
   - Backend API service with JWT authentication
   - Frontend web service with authentication UI

### Option 2: Manual Deployment

#### Deploy Backend:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Environment**: Python 3

4. Add environment variables:
   - `FLASK_ENV=production`
   - `JWT_SECRET_KEY=your-super-secret-key-here`
   - `DATABASE_URL` (from your PostgreSQL service)

#### Deploy Frontend:

1. Create another Web Service on Render
2. Configure:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Start Command**: `cd frontend && npx serve -s build -l $PORT`
   - **Environment**: Node

3. Add environment variable:
   - `REACT_APP_API_URL` (your backend service URL)

#### Create Database:

1. Create a PostgreSQL database on Render
2. Note the connection string for the backend service

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://username:password@host:port/database
FLASK_ENV=development
FLASK_DEBUG=True
JWT_SECRET_KEY=your-super-secret-key-change-in-production
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:5000
```

## Testing the Application

### Authentication Testing:
1. Open the frontend URL in your browser (`http://localhost:3000`)
2. Register a new account using the signup form
3. Login with your credentials
4. Verify you can access the todo interface
5. Test logout functionality
6. Verify you're redirected to login after logout

### Todo Testing:
1. After logging in, add a new todo using the form
2. Mark todos as complete/incomplete
3. Delete todos
4. Verify data persists after page refresh
5. Test that todos are user-specific (create another account)

## Security Features

- **Password Hashing**: Passwords are hashed using Werkzeug's security functions
- **JWT Tokens**: Secure token-based authentication with expiration
- **Token Blacklisting**: Proper logout implementation with token revocation
- **CORS Protection**: Configured for cross-origin requests
- **User Isolation**: Each user can only access their own todos
- **Input Validation**: Server-side validation for all inputs

## Troubleshooting

### Common Issues:

1. **Authentication Errors**: Check JWT_SECRET_KEY is set consistently
2. **Token Expired**: Tokens expire after 24 hours, login again
3. **CORS Errors**: Ensure Flask-CORS is installed and configured
4. **Database Connection**: Check DATABASE_URL format and credentials
5. **API Not Found**: Verify backend is running and REACT_APP_API_URL is correct

### Development Tips:

- Use browser developer tools to inspect JWT tokens
- Check Network tab for authentication headers
- Monitor backend logs for authentication errors
- Verify tokens are stored in localStorage
- Test authentication flow with different users

## Assignment Completion Checklist

- ✅ Flask backend with REST API
- ✅ React frontend with modern hooks
- ✅ PostgreSQL database integration
- ✅ **JWT Authentication System**
- ✅ **User Registration and Login**
- ✅ **Secure Password Handling**
- ✅ **Token-based Authorization**
- ✅ **Logout with Token Blacklisting**
- ✅ **User-specific Data Isolation**
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Responsive design with authentication UI
- ✅ Error handling and validation
- ✅ Environment configuration
- ✅ Deployment configuration for Render
- ✅ Comprehensive documentation

## Next Steps / Enhancements

- Add password reset functionality
- Implement refresh tokens for better security
- Add user profile management
- Implement todo categories/tags with user permissions
- Add due dates and reminders
- Implement search and filtering
- Add unit tests for authentication
- Set up CI/CD pipeline
- Add rate limiting for authentication endpoints
- Implement two-factor authentication (2FA)

## License

This project is created for educational purposes as part of a coding assignment.
