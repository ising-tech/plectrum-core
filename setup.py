"""Setup script for Plectrum Core SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="plectrum-core",
    version="0.1.1",
    author="HaoJJCleas",
    author_email="haojj@ising.tech",
    description="A unified Python SDK for submitting optimization problems to cloud or local solvers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ising-tech/plectrum-core",
    project_urls={
        "Bug Tracker": "https://github.com/ising-tech/plectrum-core/issues",
        "Source": "https://github.com/ising-tech/plectrum-core",
    },
    packages=find_packages(exclude=["tests", "tests.*", "dev"]),
    keywords=[
        "optimization", "ising", "qubo", "quantum-annealing",
        "simulated-annealing", "solver", "sdk",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "twine>=3.4.0",
            "wheel>=0.37.0",
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
)
