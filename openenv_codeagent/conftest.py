"""
conftest.py — pytest configuration for OpenEnv CodeAgent.
Adds the project root to sys.path so all imports resolve correctly.
"""
import sys
from pathlib import Path

# Add project root to path for all tests
sys.path.insert(0, str(Path(__file__).resolve().parent))
