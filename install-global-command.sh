#!/bin/bash

# 🌍 Global Command Installer for Todo App
# This script creates a global command 'todo-app' that can be run from anywhere

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STARTUP_SCRIPT="$SCRIPT_DIR/start-todo-app.sh"

# Check if startup script exists
if [[ ! -f "$STARTUP_SCRIPT" ]]; then
    print_error "Startup script not found: $STARTUP_SCRIPT"
    exit 1
fi

# Determine the best location for the global command
if [[ -d "/usr/local/bin" ]] && [[ -w "/usr/local/bin" ]]; then
    INSTALL_DIR="/usr/local/bin"
elif [[ -d "$HOME/.local/bin" ]]; then
    INSTALL_DIR="$HOME/.local/bin"
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
        print_warning "Added $HOME/.local/bin to PATH. Please restart your terminal or run: source ~/.bashrc"
    fi
else
    # Create ~/.local/bin if it doesn't exist
    mkdir -p "$HOME/.local/bin"
    INSTALL_DIR="$HOME/.local/bin"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
    print_warning "Created $HOME/.local/bin and added to PATH. Please restart your terminal or run: source ~/.bashrc"
fi

GLOBAL_COMMAND="$INSTALL_DIR/todo-app"

# Create the global command script
cat > "$GLOBAL_COMMAND" << EOF
#!/bin/bash
# Global Todo App Command
# This script calls the actual startup script from anywhere

# Get the directory where the original script is located
ORIGINAL_SCRIPT="$STARTUP_SCRIPT"

# Check if the original script exists
if [[ ! -f "\$ORIGINAL_SCRIPT" ]]; then
    echo "❌ Todo App startup script not found: \$ORIGINAL_SCRIPT"
    echo "ℹ️  Please ensure the Todo App is installed in the correct location."
    exit 1
fi

# Execute the original script with all arguments
exec "\$ORIGINAL_SCRIPT" "\$@"
EOF

# Make the global command executable
chmod +x "$GLOBAL_COMMAND"

print_success "Global command installed successfully!"
print_info "Command location: $GLOBAL_COMMAND"
print_info "You can now run 'todo-app' from anywhere!"

echo
echo "🎯 USAGE EXAMPLES:"
echo "  todo-app              # Start the Todo application"
echo "  todo-app --stop       # Stop the application"
echo "  todo-app --status     # Check application status"
echo "  todo-app --restart    # Restart the application"
echo "  todo-app --logs       # Show application logs"
echo "  todo-app --help       # Show help message"

echo
if [[ "$INSTALL_DIR" == "$HOME/.local/bin" ]]; then
    print_warning "If 'todo-app' command is not found, please restart your terminal or run:"
    echo "  source ~/.bashrc"
fi

print_success "Installation completed! 🚀"
