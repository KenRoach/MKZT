import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import time

class SetupEnvironment:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / ".venv"
        self.python_cmd = "python3" if platform.system() != "Windows" else "python"
        self.pip_cmd = str(self.venv_path / "bin" / "pip") if platform.system() != "Windows" else str(self.venv_path / "Scripts" / "pip")

    def run_command(self, command, description, error_message):
        """Run a command and handle its output"""
        print(f"\n📝 {description}...")
        try:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            print(f"✅ Success: {description}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {error_message}")
            print(f"Details: {e.stderr}")
            return None

    def setup_virtual_environment(self):
        """Set up Python virtual environment"""
        if not self.venv_path.exists():
            print("\n🔧 Creating virtual environment...")
            subprocess.run([self.python_cmd, "-m", "venv", ".venv"], check=True)
            print("✅ Virtual environment created")
        else:
            print("\n✅ Virtual environment already exists")

    def install_dependencies(self):
        """Install project dependencies"""
        commands = [
            (f"{self.pip_cmd} install --upgrade pip", "Upgrading pip"),
            (f"{self.pip_cmd} install -r requirements.txt", "Installing project dependencies"),
            (f"{self.pip_cmd} install spacy", "Installing spaCy"),
            (f"{self.python_cmd} -m spacy download es_core_news_md", "Downloading Spanish language model")
        ]

        for cmd, desc in commands:
            self.run_command(cmd, desc, f"Failed to {desc.lower()}")

    def setup_database(self):
        """Set up PostgreSQL databases"""
        commands = [
            ("createdb mkzt_dev", "Creating development database"),
            ("createdb mkzt_test", "Creating test database"),
            (f"{self.python_cmd} run_migrations.py", "Running database migrations")
        ]

        for cmd, desc in commands:
            self.run_command(cmd, desc, f"Failed to {desc.lower()}")

    def create_env_files(self):
        """Create environment files"""
        env_content = """
# Debug mode
DEBUG=True

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mkzt_dev
DATABASE_TEST_URL=postgresql://postgres:postgres@localhost:5432/mkzt_test

# Redis
REDIS_URL=redis://localhost:6379/0

# WhatsApp API (sandbox)
WHATSAPP_API_KEY=your_test_api_key
WHATSAPP_SANDBOX_NUMBER=+1234567890

# Security
JWT_SECRET_KEY=dev_secret_key
API_KEY_HEADER=X-API-Key

# Monitoring
ENABLE_METRICS=True
METRICS_PORT=9090

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/development.log
"""
        with open(".env.development", "w") as f:
            f.write(env_content.strip())
        print("\n✅ Created .env.development file")

    def setup_docker_services(self):
        """Start development Docker services"""
        self.run_command(
            "docker-compose -f docker-compose.dev.yml up -d",
            "Starting Docker services",
            "Failed to start Docker services"
        )

    def verify_installation(self):
        """Verify the installation"""
        verification_script = """
import sys
import subprocess
import pkg_resources
import psycopg2
import redis
import spacy

def check_component(name, check_func):
    try:
        check_func()
        print(f"✅ {name}: OK")
        return True
    except Exception as e:
        print(f"❌ {name}: Failed - {str(e)}")
        return False

def check_python_version():
    assert sys.version_info >= (3, 8), "Python 3.8+ is required"

def check_dependencies():
    requirements = pkg_resources.parse_requirements(open('requirements.txt'))
    pkg_resources.working_set.resolve(requirements)

def check_database():
    conn = psycopg2.connect("dbname=mkzt_dev user=postgres password=postgres")
    conn.close()

def check_redis():
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()

def check_spacy():
    nlp = spacy.load('es_core_news_md')

def main():
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Database", check_database),
        ("Redis", check_redis),
        ("SpaCy Model", check_spacy)
    ]
    
    results = [check_component(name, func) for name, func in checks]
    
    if all(results):
        print("\n✅ All components verified successfully!")
    else:
        print("\n❌ Some components failed verification")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
        with open("verify_setup.py", "w") as f:
            f.write(verification_script)
        
        self.run_command(
            f"{self.python_cmd} verify_setup.py",
            "Verifying installation",
            "Installation verification failed"
        )

    def run_tests(self):
        """Run test suite"""
        commands = [
            ("pytest tests/ -v", "Running test suite"),
            ("pytest tests/test_conversation_flow.py -v", "Running conversation flow tests"),
            ("pytest tests/test_whatsapp_handler.py -v", "Running WhatsApp handler tests")
        ]

        for cmd, desc in commands:
            self.run_command(cmd, desc, f"Failed to {desc.lower()}")

    def setup(self):
        """Run complete setup"""
        print("🚀 Starting development environment setup...")
        
        steps = [
            (self.setup_virtual_environment, "Setting up virtual environment"),
            (self.install_dependencies, "Installing dependencies"),
            (self.create_env_files, "Creating environment files"),
            (self.setup_database, "Setting up databases"),
            (self.setup_docker_services, "Starting Docker services"),
            (self.verify_installation, "Verifying installation"),
            (self.run_tests, "Running tests")
        ]

        for step_func, description in steps:
            print(f"\n📋 {description}...")
            try:
                step_func()
                print(f"✅ {description} completed")
            except Exception as e:
                print(f"❌ {description} failed: {str(e)}")
                print("\n❌ Setup failed. Please fix the errors and try again.")
                sys.exit(1)

        print("\n🎉 Development environment setup completed successfully!")
        print("\nNext steps:")
        print("1. Activate your virtual environment:")
        print("   source .venv/bin/activate  # On Unix/macOS")
        print("   .venv\\Scripts\\activate    # On Windows")
        print("2. Start the development server:")
        print("   python -m uvicorn src.main:app --reload")
        print("3. Visit http://localhost:8000/docs for API documentation")

if __name__ == "__main__":
    setup = SetupEnvironment()
    setup.setup() 