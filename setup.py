"""Setup script for Plectrum Core SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="plectrum-core",
    version="0.1.0",
    author="Plectrum Team",
    author_email="info@plectrum.com",
    description="A unified SDK for submitting solving requests to cloud or local solvers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ising-tech/plectrum-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "numpy>=1.19.0",
    ],
)
