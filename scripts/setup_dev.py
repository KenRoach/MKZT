import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all required software is installed"""
    requirements = {
        "python": "3.8",
        "postgres": "14.0",
        "redis": "7.0",
        "docker": "20.0"
    }
    
    # Check Python version
    python_version = sys.version.split()[0]
    if python_version < requirements["python"]:
        print(f"Python {requirements['python']} or higher is required")
        sys.exit(1)
    
    # Check PostgreSQL
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("PostgreSQL is not installed")
            sys.exit(1)
    except FileNotFoundError:
        print("PostgreSQL is not installed")
        sys.exit(1)
    
    # Check Redis
    try:
        result = subprocess.run(["redis-cli", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Redis is not installed")
            sys.exit(1)
    except FileNotFoundError:
        print("Redis is not installed")
        sys.exit(1)

def setup_virtual_environment():
    """Set up Python virtual environment"""
    if not os.path.exists("venv"):
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Activate virtual environment
    if sys.platform == "win32":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "source venv/bin/activate"
    
    print(f"To activate virtual environment, run: {activate_script}")

def install_dependencies():
    """Install Python dependencies"""
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
    ])
    
    # Install spaCy language model
    subprocess.run([
        sys.executable, "-m", "spacy", "download", "es_core_news_md"
    ])

def setup_database():
    """Set up development database"""
    try:
        # Create database
        subprocess.run([
            "createdb", "mkzt_dev"
        ])
        
        # Run migrations
        subprocess.run([
            "alembic", "upgrade", "head"
        ])
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

def setup_pre_commit():
    """Set up pre-commit hooks"""
    subprocess.run(["pre-commit", "install"])

def create_env_file():
    """Create development environment file"""
    env_content = """
DEBUG=True
DATABASE_URL=postgresql://localhost:5432/mkzt_dev
REDIS_URL=redis://localhost:6379/0
WHATSAPP_API_KEY=your_test_api_key
JWT_SECRET_KEY=dev_secret_key
LOG_LEVEL=DEBUG
    """.strip()
    
    with open(".env.development", "w") as f:
        f.write(env_content)

def main():
    """Main setup function"""
    print("Setting up development environment...")
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    
    # Run setup steps
    check_requirements()
    setup_virtual_environment()
    install_dependencies()
    setup_database()
    setup_pre_commit()
    create_env_file()
    
    print("\nDevelopment environment setup complete!")
    print("\nNext steps:")
    print("1. Activate virtual environment")
    print("2. Configure .env.development with your settings")
    print("3. Run 'python -m uvicorn src.main:app --reload' to start development server")

if __name__ == "__main__":
    main() 