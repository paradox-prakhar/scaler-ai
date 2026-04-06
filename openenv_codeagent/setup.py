"""
setup.py — minimal setup.py to allow pip install -e . for editable installs.
"""
from setuptools import setup, find_packages

setup(
    name="openenv-codeagent",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "ui": ["gradio>=4.0.0"],
        "agent": ["openai>=1.0.0"],
        "sandbox": ["RestrictedPython>=7.0"],
        "test": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
)
