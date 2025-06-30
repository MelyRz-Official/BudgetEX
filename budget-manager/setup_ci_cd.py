#!/usr/bin/env python3
"""
Setup script to create CI/CD files for Budget Manager.
This script will create all necessary CI/CD configuration files.
"""

import os
from pathlib import Path

def create_directory_structure():
    """Create necessary directories for CI/CD."""
    directories = [
        '.github/workflows',
        'docs',
        'scripts'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_requirements_txt():
    """Create requirements.txt file."""
    content = """# Production dependencies for Budget Manager
# Install with: pip install -r requirements.txt

# GUI Framework and Theming
sv-ttk>=2.6.0              # Sun Valley theme for tkinter

# Data Visualization
matplotlib>=3.5.0          # Charts and graphs

# Data Processing (optional, for future enhancements)
# pandas>=1.5.0            # Data analysis (uncomment if needed)
# numpy>=1.21.0            # Numerical computing (uncomment if needed)

# Database (built-in with Python)
# sqlite3 is included with Python standard library

# Configuration and Data Handling
# json, pathlib, datetime are included with Python standard library

# Minimal dependencies for core functionality
# The app is designed to work with Python standard library + minimal external deps
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(content)
    print("✅ Created requirements.txt")

def create_requirements_dev_txt():
    """Create requirements-dev.txt file."""
    content = """# Development dependencies for Budget Manager
# Install with: pip install -r requirements-dev.txt

# Include production dependencies
-r requirements.txt

# Testing Framework
pytest>=7.0.0
pytest-cov>=4.0.0          # Coverage reporting
pytest-mock>=3.10.0        # Mocking utilities
pytest-timeout>=2.1.0      # Test timeout handling
pytest-html>=3.1.0         # HTML test reports
pytest-benchmark>=4.0.0    # Performance benchmarking

# Code Quality Tools
black>=23.0.0              # Code formatting
isort>=5.12.0              # Import sorting
flake8>=6.0.0              # Style guide enforcement
mypy>=1.0.0                # Static type checking

# Security Tools
bandit>=1.7.0              # Security linting
safety>=2.0.0              # Dependency vulnerability scanning

# Development Utilities
pre-commit>=3.0.0          # Git hooks
bump2version>=1.0.0        # Version management

# Documentation
mkdocs>=1.4.0              # Documentation generator
mkdocs-material>=8.0.0     # Material theme for docs

# Build Tools
build>=0.10.0              # Python package building
twine>=4.0.0               # Package uploading
wheel>=0.40.0              # Wheel format support

# Time mocking for tests
freezegun>=1.2.0           # Time mocking for tests

# Optional: GUI development tools
# tkinter is included with Python
# For advanced GUI development:
# customtkinter>=5.0.0     # Modern tkinter widgets
# pillow>=9.0.0            # Image processing
"""
    
    with open('requirements-dev.txt', 'w') as f:
        f.write(content)
    print("✅ Created requirements-dev.txt")

def create_basic_setup_py():
    """Create a basic setup.py file."""
    content = '''#!/usr/bin/env python3
"""
Setup script for Budget Manager application.
"""

from setuptools import setup, find_packages

setup(
    name="budget-manager",
    version="1.0.0",
    author="Melissa Ruiz",
    author_email="your-email@example.com",  # Update this!
    description="A professional personal finance management application",
    long_description="A comprehensive budget management application with modern architecture",
    url="https://github.com/MellyRz-Official/BudgetEX",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "sv-ttk>=2.6.0",
        "matplotlib>=3.5.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
'''
    
    with open('setup.py', 'w') as f:
        f.write(content)
    print("✅ Created setup.py")

def create_basic_ci_yml():
    """Create a basic CI workflow."""
    content = """name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest

    - name: Create necessary directories
      run: |
        mkdir -p backups
        mkdir -p exports

    - name: Run tests
      run: python run_tests.py

  lint:
    name: Code Quality
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install linting tools
      run: |
        python -m pip install --upgrade pip
        pip install black flake8

    - name: Run Black (code formatting check)
      run: |
        black --check --diff models/ controllers/ config.py *.py
      continue-on-error: true

    - name: Run flake8 (linting)
      run: |
        flake8 models/ controllers/ config.py --max-line-length=100 --ignore=E203,W503
      continue-on-error: true
"""
    
    with open('.github/workflows/ci.yml', 'w') as f:
        f.write(content)
    print("✅ Created .github/workflows/ci.yml")

def create_license():
    """Create MIT License file."""
    content = """MIT License

Copyright (c) 2024 Melissa Ruiz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    with open('LICENSE', 'w') as f:
        f.write(content)
    print("✅ Created LICENSE")

def update_gitignore():
    """Update .gitignore with CI/CD specific entries."""
    additional_entries = """
# CI/CD artifacts
.github/badges/
*-report.json
*-report.html
coverage.xml
.coverage

# Build artifacts
build/
dist/
*.egg-info/

# Documentation builds
docs/_build/
site/

# Pre-commit
.pre-commit-config.yaml.backup
"""
    
    try:
        with open('.gitignore', 'a') as f:
            f.write(additional_entries)
        print("✅ Updated .gitignore")
    except FileNotFoundError:
        print("⚠️ .gitignore not found, skipping update")

def main():
    """Main setup function."""
    print("🚀 Setting up CI/CD for Budget Manager")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('config.py').exists():
        print("❌ Error: config.py not found. Make sure you're in the budget-manager directory.")
        return
    
    # Create directory structure
    create_directory_structure()
    
    # Create configuration files
    create_requirements_txt()
    create_requirements_dev_txt()
    create_basic_setup_py()
    create_basic_ci_yml()
    create_license()
    update_gitignore()
    
    print("\n" + "=" * 50)
    print("✅ CI/CD setup completed!")
    print("\n📋 Next steps:")
    print("1. Update setup.py with your email address")
    print("2. Commit and push to GitHub:")
    print("   git add .")
    print("   git commit -m 'feat: add CI/CD pipeline'")
    print("   git push origin main")
    print("3. Check GitHub Actions tab to see workflows running")
    print("4. Create a release tag to test the release workflow:")
    print("   git tag v1.0.0")
    print("   git push origin v1.0.0")
    
    print("\n🎉 Your repository will now have professional CI/CD!")

if __name__ == "__main__":
    main()