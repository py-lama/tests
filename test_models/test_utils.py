"""
Tests for the model utility functions.
"""

import os
import json
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from getllm.models import utils
from getllm.exceptions import ModelError


def test_get_models_dir():
    """Test getting the models directory."""
    models_dir = utils.get_models_dir()
    assert isinstance(models_dir, str)
    assert "getllm" in models_dir
    assert "models" in models_dir


def test_get_model_dir():
    """Test getting a model directory."""
    model_dir = utils.get_model_dir("test-model")
    assert "test-model" in model_dir
    assert "getllm" in model_dir


def test_ensure_model_dir_exists():
    """Test ensuring a model directory exists."""
    with patch('os.makedirs') as mock_makedirs:
        model_dir = utils.ensure_model_dir_exists("test-model")
        assert "test-model" in model_dir
        mock_makedirs.assert_called_once()


def test_load_model_metadata_file_not_found():
    """Test loading non-existent model metadata."""
    with patch('os.path.exists', return_value=False):
        with pytest.raises(ModelError, match="Metadata not found"):
            utils.load_model_metadata("nonexistent-model")


def test_load_model_metadata_invalid_json():
    """Test loading invalid JSON metadata."""
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with pytest.raises(ModelError, match="Failed to load metadata"):
                utils.load_model_metadata("invalid-model")


def test_save_model_metadata():
    """Test saving model metadata."""
    metadata = {"name": "test-model", "description": "A test model"}
    
    with patch('os.makedirs'), \
         patch('builtins.open', mock_open()) as mock_file:
        utils.save_model_metadata("test-model", metadata)
        
        # Check that the file was opened in write mode
        mock_file.assert_called_once()
        
        # Check that json.dump was called with the metadata
        file_handle = mock_file()
        file_handle.__enter__.return_value.write.assert_called_once()


def test_get_model_size_nonexistent():
    """Test getting size of a non-existent model."""
    with patch('os.path.exists', return_value=False):
        assert utils.get_model_size("nonexistent-model") is None


def test_format_model_size():
    """Test formatting model sizes."""
    assert utils.format_model_size(0) == "0.0 B"
    assert utils.format_model_size(1024) == "1.0 KB"
    assert utils.format_model_size(1024 * 1024) == "1.0 MB"
    assert utils.format_model_size(1024 * 1024 * 1024) == "1.0 GB"
    assert utils.format_model_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"
    assert utils.format_model_size(None) == "Unknown"


def test_get_available_models():
    """Test getting available models."""
    with patch('os.listdir', return_value=["model1", "model2"]), \
         patch('os.path.isdir', return_value=True):
        models = utils.get_available_models()
        assert models == ["model1", "model2"]


def test_is_model_installed():
    """Test checking if a model is installed."""
    with patch('os.path.exists', return_value=True), \
         patch('os.path.isdir', return_value=True):
        assert utils.is_model_installed("test-model") is True
    
    with patch('os.path.exists', return_value=False):
        assert utils.is_model_installed("nonexistent-model") is False


def test_delete_model():
    """Test deleting a model."""
    with patch('shutil.rmtree') as mock_rmtree, \
         patch('os.path.exists', return_value=True):
        assert utils.delete_model("test-model") is True
        mock_rmtree.assert_called_once()
    
    # Test when model doesn't exist
    with patch('os.path.exists', return_value=False):
        assert utils.delete_model("nonexistent-model") is False
