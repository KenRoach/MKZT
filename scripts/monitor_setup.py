import subprocess
import sys
import time
import psutil
import os
from pathlib import Path

class SetupMonitor:
    def __init__(self):
        self.log_file = Path("logs/setup.log")
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        print(log_message, end="")
        with open(self.log_file, "a") as f:
            f.write(log_message)

    def check_system_requirements(self):
        self.log("Checking system requirements...")
        
        # Check Python version
        python_version = sys.version.split()[0]
        self.log(f"Python version: {python_version}")
        if not (sys.version_info.major == 3 and sys.version_info.minor >= 8):
            raise Exception("Python 3.8+ is required")

        # Check available memory
        memory = psutil.virtual_memory()
        self.log(f"Available memory: {memory.available / (1024 * 1024 * 1024):.2f} GB")
        if memory.available < 2 * 1024 * 1024 * 1024:  # 2GB
            raise Exception("At least 2GB of available memory is required")

        # Check disk space
        disk = psutil.disk_usage('/')
        self.log(f"Available disk space: {disk.free / (1024 * 1024 * 1024):.2f} GB")
        if disk.free < 5 * 1024 * 1024 * 1024:  # 5GB
            raise Exception("At least 5GB of free disk space is required")

        self.log("System requirements check passed ✅")

    def check_docker(self):
        self.log("Checking Docker installation...")
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
            self.log("Docker installation check passed ✅")
        except subprocess.CalledProcessError:
            raise Exception("Docker or docker-compose not installed properly")
        except FileNotFoundError:
            raise Exception("Docker or docker-compose not found")

    def check_database(self):
        self.log("Checking database connection...")
        try:
            import psycopg2
            conn = psycopg2.connect(
                dbname="mkzt_dev",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            )
            conn.close()
            self.log("Database connection check passed ✅")
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")

    def check_redis(self):
        self.log("Checking Redis connection...")
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            self.log("Redis connection check passed ✅")
        except Exception as e:
            raise Exception(f"Redis connection failed: {str(e)}")

    def monitor_setup(self):
        try:
            self.log("Starting setup monitoring...")
            
            # Check system requirements
            self.check_system_requirements()
            
            # Check Docker
            self.check_docker()
            
            # Run setup script
            self.log("Running setup script...")
            setup_process = subprocess.Popen(
                ["python", "scripts/setup_environment.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Monitor setup process
            while True:
                output = setup_process.stdout.readline()
                if output == '' and setup_process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())

            # Check exit code
            if setup_process.returncode != 0:
                raise Exception("Setup script failed")

            # Verify services
            self.check_database()
            self.check_redis()

            self.log("Setup completed successfully! 🎉")
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.log("Setup failed. Please check the logs for details.")
            sys.exit(1)

if __name__ == "__main__":
    monitor = SetupMonitor()
    monitor.monitor_setup() 