#!/usr/bin/env python3
"""
Run script for the Hybrid Text Compression System
This script initializes the database and starts the Flask application
"""
from dotenv import load_dotenv
load_dotenv()
import os
import sys
from app import app, db

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [app.config['UPLOAD_FOLDER'], app.config['COMPRESSED_FOLDER']]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def initialize_database():
    """Initialize the database with tables"""
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        sys.exit(1)

def check_environment():
    """Check if required environment variables are set for SQLite"""
    # Only need to check for SECRET_KEY now
    if not os.environ.get('SECRET_KEY'):
        print("Warning: The SECRET_KEY environment variable is not set.")
        print("Please create a .env file based on .env.example")
        response = input("\nContinue with a default SECRET_KEY? (y/N): ")
        if response.lower() != 'y':
            print("Exiting. Please set up your environment variables.")
            sys.exit(1)

def main():
    """Main function to set up and run the application"""
    print("Hybrid Text Compression System - Setup")
    print("=" * 40)
    
    # Check for SECRET_KEY
    check_environment()
    
    # Create necessary directories
    print("\n1. Creating directories...")
    create_directories()
    
    # Initialize database
    print("\n2. Initializing database...")
    initialize_database()
    
    # Start the application
    print("\n3. Starting the application...")
    print("=" * 40)
    print("🚀 Hybrid Text Compression System is running!")
    print("📍 Open your browser and go to: http://localhost:5001")
    print("⏹️ Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=app.config['DEBUG'] if 'DEBUG' in app.config else True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")

if __name__ == '__main__':
    main()