#!/usr/bin/env python3
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
