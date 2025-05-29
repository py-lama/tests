"""
Pytest configuration and fixtures for model tests.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any

import pytest

from getllm.models import ModelManager
from getllm.models.base import ModelMetadata, ModelSource, ModelType


@pytest.fixture(scope="session")
def temp_cache_dir() -> Generator[str, None, None]:
    """Create a temporary cache directory for tests."""
    temp_dir = tempfile.mkdtemp(prefix="getllm_test_cache_")
    yield temp_dir
    # Cleanup after tests
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_model_metadata() -> Dict[str, Any]:
    """Create a sample model metadata dictionary."""
    return {
        "id": "test-model",
        "name": "Test Model",
        "description": "A test model",
        "source": "test",
        "model_type": "text",
        "size": 1000000,
        "parameters": 1000000,
        "tags": ["test", "text"],
        "config": {"test": True}
    }

@pytest.fixture
def sample_model_metadata() -> ModelMetadata:
    """Create a sample ModelMetadata object."""
    return ModelMetadata(
        id="test-model",
        name="Test Model",
        description="A test model",
        source=ModelSource.OTHER,
        model_type=ModelType.TEXT,
        size=1000000,
        parameters=1000000,
        tags=["test", "text"],
        config={"test": True}
    )

@pytest.fixture
def model_manager(temp_cache_dir: str) -> ModelManager:
    """Create a ModelManager instance with a temporary cache directory."""
    return ModelManager(cache_dir=temp_cache_dir)
