#!/bin/bash
# echo "Setting up Marsh x NUS Marsh_Cyber_Content_Tool Backend server..."

# # Update system packages
# sudo apt update && sudo apt upgrade -y

# # Install any missing packages
# sudo apt install -y git curl

# # Navigate to home directory
# cd /home/ubuntu

# # Check if repository already exists
# if [ -d "Marsh_Cyber_Content_Tool" ]; then
#     echo "Repository already exists, pulling latest changes..."
#     cd Marsh_Cyber_Content_Tool
#     git pull origin frontend
# else
#     echo "Cloning repository..."
#     git clone -b frontend https://github.com/ramanenb/Marsh_Cyber_Content_Tool.git
#     cd Marsh_Cyber_Content_Tool
# fi

# # Navigate to backend directory
# cd backend

# # Check if virtual environment exists
# if [ ! -d "venv" ]; then
#     echo "Creating virtual environment..."
#     python3 -m venv venv
# fi

# # Activate virtual environment and install/update dependencies
# echo "Installing Python dependencies..."
# source venv/bin/activate
# pip install --upgrade pip
# pip install -r requirements.txt

# # Create systemd service for automatic startup
# echo "Setting up systemd service..."
# sudo tee /etc/systemd/system/marsh-backend.service > /dev/null <<EOF
# [Unit]
# Description=Marsh Cyber Content Tool Backend
# After=network.target

# [Service]
# Type=simple
# User=ubuntu
# WorkingDirectory=/home/ubuntu/Marsh_Cyber_Content_Tool/backend
# Environment=PATH=/home/ubuntu/Marsh_Cyber_Content_Tool/backend/venv/bin
# Environment=PYTHONPATH=/home/ubuntu/Marsh_Cyber_Content_Tool/backend
# Environment=ENVIRONMENT=UAT
# ExecStart=/home/ubuntu/Marsh_Cyber_Content_Tool/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
# Restart=always
# RestartSec=3

# [Install]
# WantedBy=multi-user.target
# EOF

# # Reload systemd and start service
# sudo systemctl daemon-reload
# sudo systemctl stop marsh-backend 2>/dev/null || true
# sudo systemctl start marsh-backend
# sudo systemctl enable marsh-backend

# # Check service status
# echo "Checking service status..."
# sleep 2
# sudo systemctl status marsh-backend --no-pager

#!/bin/bash
echo "Setting up Marsh Backend server..."

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install any missing packages (git might already be installed)
sudo apt install -y git curl

# Navigate to home directory
cd /home/ubuntu

# Check if repository already exists
if [ -d "Marsh_Cyber_Content_Tool" ]; then
    echo "Repository already exists, backing up config files..."
    cd Marsh_Cyber_Content_Tool
    
    # Backup existing config files if they exist
    if [ -f "backend/app/config/settings.py" ]; then
        echo "Backing up settings.py..."
        cp backend/app/config/settings.py /tmp/settings.py.backup
    fi
    
    # Pull latest changes
    git pull origin frontend
    
    # Restore backed up files (overwrite any changes from git)
    if [ -f "/tmp/settings.py.backup" ]; then
        echo "Restoring settings.py..."
        cp /tmp/settings.py.backup backend/app/config/settings.py
    fi
    
else
    echo "Cloning repository..."
    git clone -b frontend https://github.com/ramanenb/Marsh_Cyber_Content_Tool.git
    cd Marsh_Cyber_Content_Tool
fi

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install/update dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service for automatic startup
echo "Setting up systemd service..."
sudo tee /etc/systemd/system/marsh-backend.service > /dev/null <<EOF
[Unit]
Description=Marsh Cyber Content Tool Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Marsh_Cyber_Content_Tool/backend
Environment=PATH=/home/ubuntu/Marsh_Cyber_Content_Tool/backend/venv/bin
Environment=PYTHONPATH=/home/ubuntu/Marsh_Cyber_Content_Tool/backend
Environment=ENVIRONMENT=UAT
ExecStart=/home/ubuntu/Marsh_Cyber_Content_Tool/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl stop marsh-backend 2>/dev/null || true
sudo systemctl start marsh-backend
sudo systemctl enable marsh-backend

# Check service status
echo "Checking service status..."
sleep 2
sudo systemctl status marsh-backend --no-pager