#!/usr/bin/env python3
"""Setup script for Rob-Bur- Robot Automation System"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rob-bur",
    version="1.0.0",
    author="David Adriano Ferrari dos Santos",
    author_email="david@example.com",
    description="Intelligent Robot Automation System with Local LLM AI Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davidadrianofe/Rob-Bur-",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Hardware",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rob-bur=src.main:main",
        ],
    },
)
