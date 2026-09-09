"""Shared test fixtures."""
import pytest
from pathlib import Path


@pytest.fixture
def project_root(tmp_path):
    """A clean temporary project directory."""
    return tmp_path
