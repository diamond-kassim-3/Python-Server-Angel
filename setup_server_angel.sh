#!/bin/bash
# Server Angel Setup Script v2.01
# Usage: ./setup_server_angel.sh

set -e

echo "👼 Welcome to Server Angel v2.01 Setup"
echo "======================================="

# Function to prompt for input with default
prompt() {
    local var_name=$1
    local prompt_text=$2
    local default_val=$3
    read -p "$prompt_text [$default_val]: " input
    echo "${input:-$default_val}"
}

# 1. Gather Configuration
CURRENT_DIR=$(pwd)
PROJECT_ROOT=$(prompt "PROJECT_ROOT" "Enter absolute path to Server Angel directory" "$CURRENT_DIR")
VENV_PATH=$(prompt "VENV_PATH" "Enter absolute path to Python Virtual Environment" "$CURRENT_DIR/venv")
SERVICE_USER=$(prompt "SERVICE_USER" "Enter system user to run services" "$(whoami)")

echo ""
echo "📝 Configuration:"
echo "   Project Root: $PROJECT_ROOT"
echo "   Venv Path:    $VENV_PATH"
echo "   User:         $SERVICE_USER"
echo ""
read -p "Is this correct? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# 2. Check Dependencies
echo "📦 Installing Python dependencies..."
if [ -f "$VENV_PATH/bin/pip" ]; then
    "$VENV_PATH/bin/pip" install -r requirements.txt
else
    echo "⚠️  Virtual environment not found at $VENV_PATH. Installing dependencies globally (not recommended)..."
    pip3 install -r requirements.txt
fi

# 3. Create .env if missing
if [ ! -f .env ]; then
    echo "⚠️  .env file missing. Creating from example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env. PLEASE EDIT IT with your API keys!"
    else
        echo "❌ .env.example not found!"
    fi
fi

# 4. Prepare Systemd Services
echo "⚙️  Configuring Systemd services..."
SERVICE_DIR="/etc/systemd/system"

# List of services to setup
SERVICES=("server-angel-health" "server-angel-git")

for SERVICE in "${SERVICES[@]}"; do
    TEMPLATE="systemd/${SERVICE}.service"
    TARGET="$SERVICE_DIR/${SERVICE}.service"
    TIMER_TEMPLATE="systemd/${SERVICE}.timer"
    TIMER_TARGET="$SERVICE_DIR/${SERVICE}.timer"

    if [ -f "$TEMPLATE" ]; then
        echo "   Processing $SERVICE..."
        
        # Create a temporary file with replaced values
        TEMP_FILE=$(mktemp)
        cp "$TEMPLATE" "$TEMP_FILE"
        
        # Replace placeholders using sed
        # Use | delimiter to avoid issues with / in paths
        sed -i "s|<PROJECT_ROOT>|$PROJECT_ROOT|g" "$TEMP_FILE"
        sed -i "s|<VENV_PATH>|$VENV_PATH|g" "$TEMP_FILE"
        sed -i "s|<USER>|$SERVICE_USER|g" "$TEMP_FILE"
        
        # Install Service
        echo "   Installing to $TARGET..."
        sudo cp "$TEMP_FILE" "$TARGET"
        sudo chmod 644 "$TARGET"
        rm "$TEMP_FILE"
        
        # Install Timer if it exists
        if [ -f "$TIMER_TEMPLATE" ]; then
             echo "   Installing timer to $TIMER_TARGET..."
             sudo cp "$TIMER_TEMPLATE" "$TIMER_TARGET"
             sudo chmod 644 "$TIMER_TARGET"
             sudo systemctl enable "${SERVICE}.timer"
             sudo systemctl start "${SERVICE}.timer"
        fi
    else
        echo "⚠️  Template $TEMPLATE not found."
    fi
done

# 5. Reload and Check
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

echo ""
echo "✅ Server Angel v2.01 Setup Complete!"
echo "   - Dependencies installed."
echo "   - Systemd services configured and timers started."
echo "   - Don't forget to edit .env with your SMTP/Redis credentials."
echo ""
echo "To check status: systemctl list-timers --all | grep server-angel"
