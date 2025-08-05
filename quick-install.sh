#!/bin/bash

# 🚀 Quick Install Script for Todo App Global Command
# Run this once to set up the global 'todo-app' command

set -e

echo "🚀 Setting up Todo App global command..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Make scripts executable
chmod +x "$SCRIPT_DIR/start-todo-app.sh"
chmod +x "$SCRIPT_DIR/install-global-command.sh"

# Install global command
"$SCRIPT_DIR/install-global-command.sh"

# Add to current session PATH
export PATH="$HOME/.local/bin:$PATH"

echo
echo "✅ Setup complete! You can now run:"
echo "   todo-app              # Start the application"
echo "   todo-app --help       # Show all options"
echo
echo "🔄 If 'todo-app' command is not found, restart your terminal or run:"
echo "   source ~/.bashrc"
echo
echo "🎯 Ready to start your Todo App! 🚀"
