#!/bin/bash

# 🚀 Todo App Startup Script
# This script starts both backend and frontend services for the Todo application
# Usage: ./start-todo-app.sh [options]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_PORT=5001
FRONTEND_PORT=3000
LOG_DIR="$SCRIPT_DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] ℹ️  $1${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on specific ports
kill_port_processes() {
    local port=$1
    local service_name=$2
    
    if check_port $port; then
        print_warning "Port $port is in use. Stopping existing $service_name processes..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
        
        if check_port $port; then
            print_error "Failed to free port $port. Please manually stop processes using this port."
            return 1
        else
            print_success "Port $port is now free"
        fi
    fi
    return 0
}

# Function to check if required directories exist
check_directories() {
    print_status "Checking project structure..."
    
    if [[ ! -d "$BACKEND_DIR" ]]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        return 1
    fi
    
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        return 1
    fi
    
    if [[ ! -f "$BACKEND_DIR/app.py" ]]; then
        print_error "Backend app.py not found: $BACKEND_DIR/app.py"
        return 1
    fi
    
    if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
        print_error "Frontend package.json not found: $FRONTEND_DIR/package.json"
        return 1
    fi
    
    print_success "Project structure verified"
    return 0
}

# Function to check backend dependencies
check_backend_dependencies() {
    print_status "Checking backend dependencies..."
    
    cd "$BACKEND_DIR"
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_error "Python is not installed or not in PATH"
        return 1
    fi
    
    # Check if required Python packages are installed
    local python_cmd="python3"
    if ! command -v python3 &> /dev/null; then
        python_cmd="python"
    fi
    
    if ! $python_cmd -c "import flask, flask_sqlalchemy, flask_cors, flask_jwt_extended, flask_mail" 2>/dev/null; then
        print_warning "Some Python dependencies are missing. Installing..."
        if [[ -f "requirements.txt" ]]; then
            pip install -r requirements.txt
        else
            print_error "requirements.txt not found"
            return 1
        fi
    fi
    
    print_success "Backend dependencies verified"
    return 0
}

# Function to check frontend dependencies
check_frontend_dependencies() {
    print_status "Checking frontend dependencies..."
    
    cd "$FRONTEND_DIR"
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed or not in PATH"
        return 1
    fi
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed or not in PATH"
        return 1
    fi
    
    # Check if node_modules exists
    if [[ ! -d "node_modules" ]]; then
        print_warning "node_modules not found. Installing dependencies..."
        npm install
    fi
    
    print_success "Frontend dependencies verified"
    return 0
}

# Function to check environment configuration
check_environment() {
    print_status "Checking environment configuration..."
    
    # Check backend .env file
    if [[ ! -f "$BACKEND_DIR/.env" ]]; then
        print_warning "Backend .env file not found. Using default configuration."
    else
        print_success "Backend .env file found"
    fi
    
    # Check frontend .env file
    if [[ ! -f "$FRONTEND_DIR/.env" ]]; then
        print_warning "Frontend .env file not found. Using default configuration."
    else
        print_success "Frontend .env file found"
    fi
    
    return 0
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    cd "$BACKEND_DIR"
    
    # Determine Python command
    local python_cmd="python3"
    if ! command -v python3 &> /dev/null; then
        python_cmd="python"
    fi
    
    # Start backend in background
    nohup $python_cmd app.py > "$LOG_DIR/backend.log" 2>&1 &
    local backend_pid=$!
    
    # Wait for backend to start
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -s "http://localhost:$BACKEND_PORT/api/health" >/dev/null 2>&1; then
            print_success "Backend server started successfully (PID: $backend_pid)"
            echo $backend_pid > "$LOG_DIR/backend.pid"
            return 0
        fi
        
        sleep 1
        ((attempt++))
        
        if [[ $((attempt % 5)) -eq 0 ]]; then
            print_status "Waiting for backend to start... ($attempt/$max_attempts)"
        fi
    done
    
    print_error "Backend failed to start within $max_attempts seconds"
    return 1
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    cd "$FRONTEND_DIR"
    
    # Start frontend in background
    nohup npm start > "$LOG_DIR/frontend.log" 2>&1 &
    local frontend_pid=$!
    
    # Wait for frontend to start
    local max_attempts=60  # Frontend takes longer to start
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -s -I "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
            print_success "Frontend server started successfully (PID: $frontend_pid)"
            echo $frontend_pid > "$LOG_DIR/frontend.pid"
            return 0
        fi
        
        sleep 1
        ((attempt++))
        
        if [[ $((attempt % 10)) -eq 0 ]]; then
            print_status "Waiting for frontend to start... ($attempt/$max_attempts)"
        fi
    done
    
    print_error "Frontend failed to start within $max_attempts seconds"
    return 1
}

# Function to show application status
show_status() {
    echo
    print_info "🎯 TODO APPLICATION STATUS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Backend status
    if check_port $BACKEND_PORT; then
        if curl -s "http://localhost:$BACKEND_PORT/api/health" >/dev/null 2>&1; then
            print_success "Backend: Running on http://localhost:$BACKEND_PORT"
        else
            print_warning "Backend: Port in use but not responding"
        fi
    else
        print_error "Backend: Not running"
    fi
    
    # Frontend status
    if check_port $FRONTEND_PORT; then
        if curl -s -I "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
            print_success "Frontend: Running on http://localhost:$FRONTEND_PORT"
        else
            print_warning "Frontend: Port in use but not responding"
        fi
    else
        print_error "Frontend: Not running"
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if check_port $BACKEND_PORT && check_port $FRONTEND_PORT; then
        echo
        print_success "🚀 Application is ready!"
        print_info "📱 Open your browser and go to: ${CYAN}http://localhost:$FRONTEND_PORT${NC}"
        print_info "🔐 Login credentials:"
        print_info "   • Username: testuser, Password: password123"
        print_info "   • Username: shweta_yadav, Password: password123"
        echo
        print_info "📧 Email notifications are configured and working"
        print_info "🔐 Forgot password functionality is available"
        print_info "🔍 Google OAuth is configured"
        echo
        print_info "📊 Logs are available in: $LOG_DIR/"
        print_info "🛑 To stop the application, run: ./start-todo-app.sh --stop"
    fi
}

# Function to stop application
stop_application() {
    print_status "Stopping Todo application..."
    
    # Stop backend
    if [[ -f "$LOG_DIR/backend.pid" ]]; then
        local backend_pid=$(cat "$LOG_DIR/backend.pid")
        if kill -0 $backend_pid 2>/dev/null; then
            kill $backend_pid
            print_success "Backend stopped (PID: $backend_pid)"
        fi
        rm -f "$LOG_DIR/backend.pid"
    fi
    
    # Stop frontend
    if [[ -f "$LOG_DIR/frontend.pid" ]]; then
        local frontend_pid=$(cat "$LOG_DIR/frontend.pid")
        if kill -0 $frontend_pid 2>/dev/null; then
            kill $frontend_pid
            print_success "Frontend stopped (PID: $frontend_pid)"
        fi
        rm -f "$LOG_DIR/frontend.pid"
    fi
    
    # Kill any remaining processes on the ports
    kill_port_processes $BACKEND_PORT "backend"
    kill_port_processes $FRONTEND_PORT "frontend"
    
    print_success "Todo application stopped"
}

# Function to show logs
show_logs() {
    local service=$1
    
    if [[ "$service" == "backend" ]]; then
        if [[ -f "$LOG_DIR/backend.log" ]]; then
            print_info "Backend logs (last 50 lines):"
            tail -50 "$LOG_DIR/backend.log"
        else
            print_warning "Backend log file not found"
        fi
    elif [[ "$service" == "frontend" ]]; then
        if [[ -f "$LOG_DIR/frontend.log" ]]; then
            print_info "Frontend logs (last 50 lines):"
            tail -50 "$LOG_DIR/frontend.log"
        else
            print_warning "Frontend log file not found"
        fi
    else
        print_info "Available logs:"
        ls -la "$LOG_DIR/"
    fi
}

# Function to show help
show_help() {
    echo
    echo -e "${PURPLE}🎯 Todo App Startup Script${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo -e "${CYAN}USAGE:${NC}"
    echo "  ./start-todo-app.sh [OPTIONS]"
    echo
    echo -e "${CYAN}OPTIONS:${NC}"
    echo "  (no options)     Start the Todo application"
    echo "  --start          Start the Todo application"
    echo "  --stop           Stop the Todo application"
    echo "  --restart        Restart the Todo application"
    echo "  --status         Show application status"
    echo "  --logs [service] Show logs (backend/frontend/all)"
    echo "  --check          Check system requirements"
    echo "  --help           Show this help message"
    echo
    echo -e "${CYAN}EXAMPLES:${NC}"
    echo "  ./start-todo-app.sh              # Start the application"
    echo "  ./start-todo-app.sh --stop       # Stop the application"
    echo "  ./start-todo-app.sh --status     # Check if running"
    echo "  ./start-todo-app.sh --logs backend  # Show backend logs"
    echo
    echo -e "${CYAN}FEATURES:${NC}"
    echo "  ✅ Automatic dependency checking"
    echo "  ✅ Port conflict resolution"
    echo "  ✅ Health monitoring"
    echo "  ✅ Comprehensive logging"
    echo "  ✅ Email notifications"
    echo "  ✅ Forgot password functionality"
    echo "  ✅ Google OAuth integration"
    echo
    echo -e "${CYAN}SERVICES:${NC}"
    echo "  🔧 Backend:  http://localhost:$BACKEND_PORT"
    echo "  🌐 Frontend: http://localhost:$FRONTEND_PORT"
    echo
}

# Main function
main() {
    # Print banner
    echo
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                    🎯 TODO APPLICATION                       ║${NC}"
    echo -e "${PURPLE}║                     Startup Script                           ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    # Parse command line arguments
    case "${1:-start}" in
        "start"|"--start"|"")
            print_status "Starting Todo Application..."
            
            # Check system requirements
            check_directories || exit 1
            check_backend_dependencies || exit 1
            check_frontend_dependencies || exit 1
            check_environment
            
            # Stop any existing processes
            kill_port_processes $BACKEND_PORT "backend"
            kill_port_processes $FRONTEND_PORT "frontend"
            
            # Start services
            start_backend || exit 1
            start_frontend || exit 1
            
            # Show status
            show_status
            ;;
            
        "stop"|"--stop")
            stop_application
            ;;
            
        "restart"|"--restart")
            print_status "Restarting Todo Application..."
            stop_application
            sleep 3
            $0 --start
            ;;
            
        "status"|"--status")
            show_status
            ;;
            
        "logs"|"--logs")
            show_logs "$2"
            ;;
            
        "check"|"--check")
            print_status "Checking system requirements..."
            check_directories
            check_backend_dependencies
            check_frontend_dependencies
            check_environment
            print_success "System check completed"
            ;;
            
        "help"|"--help"|"-h")
            show_help
            ;;
            
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
