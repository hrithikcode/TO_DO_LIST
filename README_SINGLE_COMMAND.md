# 🎯 Todo Application - Single Command Setup

## 🚀 **One-Time Setup**

Run this command once to set up the global `todo-app` command:

```bash
cd ~/workspace/TO-DO_LIST && ./quick-install.sh
```

After setup, restart your terminal or run:
```bash
source ~/.bashrc
```

## ⚡ **Single Command Usage**

### **Start the Application**
```bash
todo-app
```
This single command will:
- ✅ Check all dependencies
- ✅ Resolve port conflicts
- ✅ Start backend server (http://localhost:5001)
- ✅ Start frontend server (http://localhost:3000)
- ✅ Show application status
- ✅ Provide login credentials

### **Other Commands**
```bash
todo-app --stop      # Stop the application
todo-app --restart   # Restart the application
todo-app --status    # Check if running
todo-app --logs      # View application logs
todo-app --help      # Show all options
```

## 🌍 **Run From Anywhere**

Once installed, you can run `todo-app` from any directory:

```bash
# From home directory
cd ~
todo-app

# From any project directory
cd /path/to/any/project
todo-app

# From desktop
cd ~/Desktop
todo-app
```

## 🎯 **Complete Example**

```bash
# One-time setup (run once)
cd ~/workspace/TO-DO_LIST
./quick-install.sh
source ~/.bashrc

# Daily usage (run from anywhere)
todo-app                    # Start the app
# Open browser: http://localhost:3000
# Login: testuser / password123

todo-app --status          # Check if running
todo-app --stop            # Stop when done
```

## 🔐 **Login Credentials**

- **Username**: `testuser`, **Password**: `password123`
- **Username**: `shweta_yadav`, **Password**: `password123`
- **Google OAuth**: Click "Sign in with Google"

## ✨ **Features Available**

- 📝 **Todo Management**: Create, edit, delete, complete todos
- 📧 **Email Notifications**: Get emails when creating todos
- 🔐 **Forgot Password**: Reset password via email
- 🔍 **Google OAuth**: Sign in with Google account
- 📱 **Responsive Design**: Works on all devices
- 🎨 **Beautiful UI**: Modern, intuitive interface

## 🛠️ **Troubleshooting**

### **Command Not Found**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
# Or restart terminal
```

### **Services Won't Start**
```bash
todo-app --check    # Check system requirements
todo-app --logs     # View error logs
```

### **Port Conflicts**
The script automatically resolves port conflicts, but if needed:
```bash
todo-app --stop     # Stop all services
todo-app            # Start fresh
```

## 📊 **What Happens When You Run `todo-app`**

1. **System Check**: Verifies Python, Node.js, and dependencies
2. **Port Management**: Stops any conflicting processes
3. **Backend Start**: Launches Flask API server with email support
4. **Frontend Start**: Launches React development server
5. **Health Check**: Ensures both services are responding
6. **Status Display**: Shows URLs and login credentials

## 🎉 **That's It!**

Your Todo Application is now available as a single command that can be run from anywhere on your system!

```bash
todo-app  # 🚀 Start your Todo App!
```

Open http://localhost:3000 and enjoy your feature-rich Todo application with email notifications and forgot password functionality! ✨
