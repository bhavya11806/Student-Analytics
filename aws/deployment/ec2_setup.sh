#!/usr/bin/env bash
# =====================================================================
# AWS EC2 Provisioning & Deployment Script for Ubuntu 22.04 / 24.04 LTS
# Application: Student Attendance & Performance Analytics Cloud
# =====================================================================

set -e

echo ">>> [1/7] Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

echo ">>> [2/7] Installing runtime dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv git nginx libmysqlclient-dev pkg-config curl

APP_DIR="/var/www/student_analytics"
echo ">>> [3/7] Setting up application directory at ${APP_DIR}..."
sudo mkdir -p ${APP_DIR}
sudo chown -R ubuntu:ubuntu ${APP_DIR}

# Copy code or clone repository
# git clone <your-repo-url> ${APP_DIR}
cd ${APP_DIR}

echo ">>> [4/7] Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo ">>> [5/7] Configuring systemd service..."
sudo cp aws/deployment/student_analytics.service /etc/systemd/system/student_analytics.service
sudo systemctl daemon-reload
sudo systemctl enable student_analytics
sudo systemctl restart student_analytics

echo ">>> [6/7] Configuring Nginx reverse proxy..."
sudo cp aws/deployment/nginx.conf /etc/nginx/sites-available/student_analytics
sudo ln -sf /etc/nginx/sites-available/student_analytics /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo ">>> [7/7] Deployment complete! Application is running on port 80."
