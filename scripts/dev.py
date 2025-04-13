#!/usr/bin/env python3
import click
import subprocess
import os
import sys
from typing import List

@click.group()
def cli():
    """Development tools for WhatsApp AI Ordering Bot"""
    pass

@cli.command()
def setup():
    """Setup development environment"""
    click.echo("Setting up development environment...")
    
    # Install pre-commit hooks
    subprocess.run(["pre-commit", "install"], check=True)
    
    # Install dependencies
    subprocess.run(["poetry", "install"], check=True)
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    
    click.echo("Development environment setup complete!")

@cli.command()
def test():
    """Run tests"""
    click.echo("Running tests...")
    subprocess.run(["pytest", "--cov=src", "--cov-report=term-missing"], check=True)

@cli.command()
def lint():
    """Run linters"""
    click.echo("Running linters...")
    subprocess.run(["flake8", "src"], check=True)
    subprocess.run(["mypy", "src"], check=True)
    subprocess.run(["black", "--check", "src"], check=True)
    subprocess.run(["isort", "--check-only", "src"], check=True)

@cli.command()
def format():
    """Format code"""
    click.echo("Formatting code...")
    subprocess.run(["black", "src"], check=True)
    subprocess.run(["isort", "src"], check=True)

@cli.command()
def migrate():
    """Run database migrations"""
    click.echo("Running database migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)

@cli.command()
def rollback():
    """Rollback last database migration"""
    click.echo("Rolling back last migration...")
    subprocess.run(["alembic", "downgrade", "-1"], check=True)

@cli.command()
def shell():
    """Start Python shell with application context"""
    click.echo("Starting Python shell...")
    subprocess.run(["poetry", "run", "python", "-i", "-c", """
from src.utils.database import SessionLocal
from src.utils.customer_handler import CustomerHandler
from src.utils.order_handler import OrderHandler
from src.utils.message_handler import MessageHandler
from src.whatsapp.handler import WhatsAppHandler

db = SessionLocal()
customer_handler = CustomerHandler(db)
order_handler = OrderHandler(db)
message_handler = MessageHandler(db)
whatsapp_handler = WhatsAppHandler()
"""], check=True)

if __name__ == "__main__":
    cli() 