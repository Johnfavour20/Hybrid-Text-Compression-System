#!/bin/bash

# Hybrid Text Compression System Setup Script
# This script automates the setup process for the application

echo "🚀 Hybrid Text Compression System Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "❌ MySQL is not installed. Please install MySQL server."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your database credentials."
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating upload directories..."
mkdir -p uploads compressed
echo "✅ Directories created"

# Database setup prompt
echo ""
echo "🗄️  Database Setup"
echo "=================="
echo "Please ensure you have:"
echo "1. MySQL server running"
echo "2. Created a database named 'compression_db'"
echo "3. Updated .env file with your database credentials"
echo ""

read -p "Have you completed the database setup? (y/N): " db_setup
if [ "$db_setup" != "y" ] && [ "$db_setup" != "Y" ]; then
    echo ""
    echo "📝 To complete database setup:"
    echo "1. Start MySQL: sudo service mysql start"
    echo "2. Login to MySQL: mysql -u root -p"
    echo "3. Create database: CREATE DATABASE compression_db;"
    echo "4. Edit .env file with your credentials"
    echo ""
    echo "Then run: python run.py"
    exit 0
fi

# Test database connection
echo "🔍 Testing database connection..."
python3 -c "
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'compression_db')
    )
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Please check your .env file."
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo "================================="
echo ""
echo "To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the application: python run.py"
echo ""
echo "Or simply run: python run.py (it will handle activation)"
echo ""
echo "The application will be available at: http://localhost:5000"

# Ask if user wants to start the application now
echo ""
read -p "Would you like to start the application now? (y/N): " start_now
if [ "$start_now" = "y" ] || [ "$start_now" = "Y" ]; then
    echo ""
    echo "🚀 Starting Hybrid Text Compression System..."
    python run.py
fi