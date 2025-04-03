"""
Setup script for EI-harness-lite.
"""

from setuptools import setup, find_packages

# Read requirements
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Read README for long description
try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "EI-harness-lite: A lightweight harness for using the MHH EI superprompt with various LLMs."

setup(
    name="ei-harness-lite",
    version="0.1.0",
    description="A lightweight harness for using the MHH EI superprompt with various LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MindHackingHappiness",
    author_email="info@mindhackinghappiness.com",
    url="https://github.com/MindHackingHappiness/EI-harness-lite",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ei-harness-lite=ei_harness.cli:main",
        ],
    },
)
