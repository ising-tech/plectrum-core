"""Setup script for Plectrum Core SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="plectrum-core",
    version="0.1.0",
    author="HaoJJCleas",
    author_email="haojj@ising.tech",
    description="A unified SDK for submitting solving requests to cloud or local solvers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ising-tech/plectrum-core",
    project_urls={
        "Bug Tracker": "https://github.com/ising-tech/plectrum-core/issues",
        "Source": "https://github.com/ising-tech/plectrum-core",
    },
    packages=["plectrum", "plectrum.client", "plectrum.matrix", "plectrum.task"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
        ],
    },
)
