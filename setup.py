#!/usr/bin/env python3
"""
Setup script for the spood package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="spood",
    version="0.2.0",
    description="A bridge between EESSI/EasyBuild and Spack",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Loris Ercole",
    author_email="loris.ercole@epfl.ch",
    url="https://github.com/lorisercole/spood",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "jsonschema>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="spack package-manager specs database easybuild eessi spood",
)
