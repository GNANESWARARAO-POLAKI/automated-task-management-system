#!/usr/bin/env python3
"""
Startup script for Task Manager API
Handles environment setup, dependency installation, and service initialization
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class TaskManagerSetup:
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.credentials_dir = self.project_root / "credentials"
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
        return True
    
    def install_dependencies(self):
        """Install required Python packages"""
        print("📦 Installing dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, cwd=self.project_root)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            self.credentials_dir,
            self.project_root / "logs",
            self.project_root / "data"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    def check_credentials(self):
        """Check if Google API credentials are set up"""
        credential_files = [
            "gmail_credentials.json",
            "sheets_credentials.json", 
            "calendar_credentials.json"
        ]
        
        missing_files = []
        for file in credential_files:
            file_path = self.credentials_dir / file
            if not file_path.exists():
                missing_files.append(file)
        
        if missing_files:
            print("⚠️ Missing Google API credential files:")
            for file in missing_files:
                print(f"   - credentials/{file}")
            print("\n📘 Setup Guide:")
            print("1. Go to Google Cloud Console")
            print("2. Create/select a project")
            print("3. Enable Gmail API, Sheets API, Calendar API")
            print("4. Create OAuth 2.0 credentials")
            print("5. Download and place JSON files in credentials/ folder")
            print("6. See SETUP.md for detailed instructions")
            return False
        else:
            print("✅ All credential files found")
            return True
    
    def create_sample_env(self):
        """Create sample environment file"""
        env_content = """# Task Manager API Environment Variables
FLASK_ENV=development
FLASK_DEBUG=True
GOOGLE_CLOUD_PROJECT_ID=your-project-id
DATABASE_PATH=task_manager.db
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
"""
        
        env_file = self.project_root / ".env.example"
        with open(env_file, "w") as f:
            f.write(env_content)
        print(f"📄 Created sample environment file: {env_file}")
    
    def run_tests(self):
        """Run basic API tests"""
        print("🧪 Running basic tests...")
        try:
            # Import and run basic tests
            test_script = self.project_root / "test_api.py"
            if test_script.exists():
                print("Test script found, but skipping automated run.")
                print("Run 'python test_api.py' after starting the server to test.")
            else:
                print("No test script found")
        except Exception as e:
            print(f"⚠️ Could not run tests: {e}")
    
    def start_server(self):
        """Start the Flask development server"""
        print("🚀 Starting Task Manager API server...")
        print("Server will be available at: http://localhost:5000")
        print("API endpoints:")
        print("  - GET /health - Health check")
        print("  - GET /tasks - List tasks") 
        print("  - POST /tasks - Create task")
        print("  - GET /dashboard - Dashboard")
        print("  - GET /tasks/integrations - Integration status")
        print("\nPress Ctrl+C to stop the server\n")
        
        try:
            os.chdir(self.project_root)
            subprocess.run([sys.executable, "app.py"], check=True)
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
        except subprocess.CalledProcessError as e:
            print(f"❌ Server failed to start: {e}")
    
    def full_setup(self):
        """Run complete setup process"""
        print("🔧 Task Manager API Setup")
        print("=" * 40)
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Setup directories
        self.setup_directories()
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Create sample environment file
        self.create_sample_env()
        
        # Check credentials
        credentials_ok = self.check_credentials()
        
        print("\n" + "=" * 40)
        if credentials_ok:
            print("✅ Setup completed successfully!")
            print("🚀 Ready to start the server")
        else:
            print("⚠️ Setup completed with warnings")
            print("🔧 Please setup Google API credentials before starting")
        
        return True

def main():
    """Main entry point"""
    setup = TaskManagerSetup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup.full_setup()
        elif command == "start":
            setup.start_server()
        elif command == "test":
            setup.run_tests()
        elif command == "install":
            setup.install_dependencies()
        else:
            print("Available commands:")
            print("  setup  - Run full setup process")
            print("  start  - Start the development server")
            print("  test   - Run API tests")
            print("  install - Install dependencies only")
    else:
        print("🚀 Task Manager API Startup")
        print("\nAvailable commands:")
        print("  python run.py setup   - Initial setup")
        print("  python run.py start   - Start server")
        print("  python run.py test    - Run tests")
        print("  python run.py install - Install dependencies")
        
        # Auto-run setup if first time
        if not (setup.project_root / "requirements.txt").exists():
            print("\nFirst time setup detected, running setup...")
            setup.full_setup()
        else:
            choice = input("\nRun setup now? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                if setup.full_setup():
                    choice = input("\nStart server now? (y/n): ").lower().strip()
                    if choice in ['y', 'yes']:
                        setup.start_server()

if __name__ == "__main__":
    main()
