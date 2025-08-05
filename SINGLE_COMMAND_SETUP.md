# 🚀 Single Command Setup - Todo Application

## 🎯 **Overview**
Run your complete Todo Application with a single command from anywhere on your system!

## ⚡ **Quick Start**

### **Option 1: Global Command (Recommended)**
```bash
# Install the global command (run once)
cd ~/workspace/TO-DO_LIST
./install-global-command.sh

# Restart your terminal or run:
source ~/.bashrc

# Now you can run from anywhere:
todo-app
```

### **Option 2: Direct Script**
```bash
# From the project directory:
cd ~/workspace/TO-DO_LIST
./start-todo-app.sh
```

## 🎮 **Available Commands**

### **Start Application**
```bash
todo-app                # Start both backend and frontend
todo-app --start        # Same as above
```

### **Stop Application**
```bash
todo-app --stop         # Stop both services gracefully
```

### **Restart Application**
```bash
todo-app --restart      # Stop and start again
```

### **Check Status**
```bash
todo-app --status       # Show current application status
```

### **View Logs**
```bash
todo-app --logs         # Show all logs
todo-app --logs backend # Show only backend logs
todo-app --logs frontend # Show only frontend logs
```

### **System Check**
```bash
todo-app --check        # Verify all dependencies and configuration
```

### **Help**
```bash
todo-app --help         # Show all available options
```

## 🔧 **What the Script Does**

### **Automatic Checks**
- ✅ **Project Structure**: Verifies all required files exist
- ✅ **Dependencies**: Checks Python packages and Node.js modules
- ✅ **Environment**: Validates configuration files
- ✅ **Port Conflicts**: Resolves port conflicts automatically
- ✅ **Health Monitoring**: Ensures services start correctly

### **Smart Features**
- 🔄 **Auto-restart**: Kills existing processes before starting
- 📊 **Health Checks**: Waits for services to be fully ready
- 📝 **Comprehensive Logging**: Separate logs for backend and frontend
- 🎨 **Colored Output**: Beautiful terminal output with status indicators
- ⚡ **Fast Startup**: Optimized startup sequence

### **Error Handling**
- 🛡️ **Graceful Failures**: Clear error messages with solutions
- 🔍 **Dependency Detection**: Automatic installation of missing packages
- 🚨 **Port Management**: Automatic resolution of port conflicts
- 📋 **System Requirements**: Validates all prerequisites

## 📊 **Application Services**

### **Backend Service**
- **URL**: http://localhost:5001
- **Health Check**: `/api/health`
- **Features**: REST API, JWT Auth, Email notifications, Password reset
- **Log File**: `logs/backend.log`

### **Frontend Service**
- **URL**: http://localhost:3000
- **Features**: React SPA, Google OAuth, Responsive design
- **Log File**: `logs/frontend.log`

## 🎯 **Usage Examples**

### **Daily Usage**
```bash
# Start your todo app
todo-app

# Check if it's running
todo-app --status

# Stop when done
todo-app --stop
```

### **Development Workflow**
```bash
# Start the app
todo-app

# Make changes to code...

# Restart to see changes
todo-app --restart

# Check logs if issues
todo-app --logs backend
```

### **Troubleshooting**
```bash
# Check system requirements
todo-app --check

# View recent logs
todo-app --logs

# Stop and clean restart
todo-app --stop
sleep 5
todo-app
```

## 🔐 **Login Credentials**

### **Local Authentication**
- **Username**: `testuser`
- **Password**: `password123`
- **Email**: `shwetay1508+test@gmail.com` (for password reset)

- **Username**: `shweta_yadav`
- **Password**: `password123`
- **Email**: `shwetay1508@gmail.com`

### **Google OAuth**
- Click "Sign in with Google" button
- Use any Google account

## 📧 **Email Features Available**

### **Todo Creation Notifications**
- ✅ Automatic email when creating todos
- ✅ Beautiful HTML templates
- ✅ List of all active tasks
- ✅ Task summary statistics

### **Forgot Password**
- ✅ Secure password reset via email
- ✅ Time-limited reset tokens (1 hour)
- ✅ Professional email templates
- ✅ Security notices and warnings

### **On-Demand Email Summary**
- ✅ "Send Email Summary" button in app
- ✅ Current task overview
- ✅ Progress statistics

## 🎨 **Script Output Examples**

### **Starting Application**
```
╔══════════════════════════════════════════════════════════════╗
║                    🎯 TODO APPLICATION                       ║
║                     Startup Script                           ║
╚══════════════════════════════════════════════════════════════╝

[23:50:41] Starting Todo Application...
[23:50:41] ✅ Project structure verified
[23:50:41] ✅ Backend dependencies verified
[23:50:41] ✅ Frontend dependencies verified
[23:50:48] ✅ Backend server started successfully (PID: 79216)
[23:50:51] ✅ Frontend server started successfully (PID: 79230)

🎯 TODO APPLICATION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Backend: Running on http://localhost:5001
✅ Frontend: Running on http://localhost:3000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 🚀 Application is ready!
📱 Open your browser and go to: http://localhost:3000
```

### **Status Check**
```
🎯 TODO APPLICATION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Backend: Running on http://localhost:5001
✅ Frontend: Running on http://localhost:3000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Application is ready!
📱 Open your browser and go to: http://localhost:3000
```

## 📁 **File Structure**

```
~/workspace/TO-DO_LIST/
├── start-todo-app.sh           # Main startup script
├── install-global-command.sh   # Global command installer
├── logs/                       # Application logs
│   ├── backend.log            # Backend service logs
│   ├── frontend.log           # Frontend service logs
│   ├── backend.pid            # Backend process ID
│   └── frontend.pid           # Frontend process ID
├── backend/                    # Backend service
└── frontend/                   # Frontend service
```

## 🔧 **Advanced Configuration**

### **Custom Ports**
Edit the script variables:
```bash
BACKEND_PORT=5001
FRONTEND_PORT=3000
```

### **Custom Log Directory**
```bash
LOG_DIR="$SCRIPT_DIR/logs"
```

### **Startup Timeout**
```bash
# Backend startup timeout (seconds)
max_attempts=30

# Frontend startup timeout (seconds)
max_attempts=60
```

## 🛠️ **Troubleshooting**

### **Command Not Found**
```bash
# Add to PATH manually
export PATH="$HOME/.local/bin:$PATH"

# Or restart terminal
source ~/.bashrc
```

### **Port Already in Use**
```bash
# The script automatically handles this, but manually:
lsof -ti:3000 | xargs kill -9  # Kill frontend
lsof -ti:5001 | xargs kill -9  # Kill backend
```

### **Dependencies Missing**
```bash
# Check what's missing
todo-app --check

# Install backend dependencies
cd ~/workspace/TO-DO_LIST/backend
pip install -r requirements.txt

# Install frontend dependencies
cd ~/workspace/TO-DO_LIST/frontend
npm install
```

### **Services Won't Start**
```bash
# Check logs for errors
todo-app --logs backend
todo-app --logs frontend

# Try clean restart
todo-app --stop
sleep 5
todo-app
```

## 🎯 **Quick Reference**

| Command | Description |
|---------|-------------|
| `todo-app` | Start the application |
| `todo-app --stop` | Stop the application |
| `todo-app --restart` | Restart the application |
| `todo-app --status` | Check if running |
| `todo-app --logs` | View logs |
| `todo-app --check` | System check |
| `todo-app --help` | Show help |

## 🚀 **Installation Summary**

1. **Install Global Command** (one-time setup):
   ```bash
   cd ~/workspace/TO-DO_LIST
   ./install-global-command.sh
   source ~/.bashrc
   ```

2. **Start Application** (anytime, anywhere):
   ```bash
   todo-app
   ```

3. **Access Application**:
   - Open browser: http://localhost:3000
   - Login with provided credentials
   - Enjoy your Todo App with email notifications! 🎉

The single command setup is now complete and ready for use! 🚀✨
