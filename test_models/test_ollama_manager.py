"""
Tests for the Ollama model manager.
"""

import json
from unittest.mock import patch, MagicMock, mock_open

import pytest
import requests

from getllm.models.ollama.manager import OllamaModelManager
from getllm.exceptions import ModelError, ModelInstallationError, ModelNotFoundError
from getllm.models.base import ModelMetadata, ModelSource, ModelType


@pytest.fixture
def ollama_manager(temp_cache_dir):
    """Create an OllamaModelManager instance with a temporary cache."""
    return OllamaModelManager(cache_dir=temp_cache_dir)


def test_ollama_manager_init(ollama_manager):
    """Test initializing the OllamaModelManager."""
    assert ollama_manager.cache_dir is not None
    assert isinstance(ollama_manager._models_cache, dict)
    assert ollama_manager.base_url == "http://localhost:11434"


def test_ollama_manager_init_with_custom_url():
    """Test initializing with a custom base URL."""
    manager = OllamaModelManager(base_url="http://custom-ollama:11434")
    assert manager.base_url == "http://custom-ollama:11434"


@patch('requests.get')
def test_check_server_running_success(mock_get, ollama_manager):
    """Test checking if the Ollama server is running."""
    # Mock a successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    assert ollama_manager.check_server_running() is True
    mock_get.assert_called_once_with("http://localhost:11434/api/version")


@patch('requests.get')
def test_check_server_running_error(mock_get, ollama_manager):
    """Test handling when the Ollama server is not running."""
    # Mock a connection error
    mock_get.side_effect = requests.ConnectionError()
    
    assert ollama_manager.check_server_running() is False


@patch('requests.get')
def test_fetch_model_info_success(mock_get, ollama_manager):
    """Test successfully fetching model info from Ollama."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "llama2",
        "model": "llama2:7b",
        "details": {
            "parameter_size": "7B",
            "quantization_level": "Q4_0"
        }
    }
    mock_get.return_value = mock_response
    
    # Call the method
    model_info = ollama_manager._fetch_model_info("llama2:7b")
    
    # Check the results
    assert model_info["name"] == "llama2"
    assert model_info["model"] == "llama2:7b"
    mock_get.assert_called_once_with(
        "http://localhost:11434/api/show",
        json={"name": "llama2:7b"}
    )


@patch('requests.get')
def test_fetch_model_info_not_found(mock_get, ollama_manager):
    """Test fetching info for a non-existent model."""
    # Mock a 404 response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    # Should raise ModelNotFoundError
    with pytest.raises(ModelNotFoundError):
        ollama_manager._fetch_model_info("nonexistent-model")


@patch('requests.get')
def test_fetch_model_info_error(mock_get, ollama_manager):
    """Test error handling when fetching model info."""
    # Mock a request exception
    mock_get.side_effect = requests.RequestException("API error")
    
    # Should raise ModelError
    with pytest.raises(ModelError, match="Failed to fetch model info"):
        ollama_manager._fetch_model_info("llama2:7b")


def test_model_dict_to_metadata(ollama_manager):
    """Test converting a model dict to ModelMetadata."""
    model_dict = {
        "name": "llama2",
        "model": "llama2:7b",
        "details": {
            "parameter_size": "7B",
            "quantization_level": "Q4_0"
        },
        "parameters": "7B",
        "size": 4000000000,
        "digest": "sha256:abc123"
    }
    
    metadata = ollama_manager._model_dict_to_metadata("llama2:7b", model_dict)
    
    assert metadata.id == "llama2:7b"
    assert metadata.name == "llama2"
    assert metadata.source == ModelSource.OLLAMA
    assert metadata.model_type == ModelType.TEXT
    assert metadata.size == 4000000000
    assert metadata.parameters == 7000000000  # 7B parameters
    assert "llm" in metadata.tags
    assert "ollama" in metadata.tags


@patch('requests.get')
def test_list_models_success(mock_get, ollama_manager):
    """Test listing models successfully."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [
            {"name": "llama2:7b"},
            {"name": "mistral:latest"}
        ]
    }
    mock_get.return_value = mock_response
    
    # Mock the _fetch_model_info method
    with patch.object(ollama_manager, '_fetch_model_info') as mock_fetch_info:
        mock_fetch_info.side_effect = [
            {
                "name": "llama2",
                "model": "llama2:7b",
                "details": {"parameter_size": "7B"},
                "size": 4000000000
            },
            {
                "name": "mistral",
                "model": "mistral:latest",
                "details": {"parameter_size": "7B"},
                "size": 4000000000
            }
        ]
        
        # Call the method
        models = ollama_manager.list_models()
    
    # Check the results
    assert len(models) == 2
    assert models[0].id == "llama2:7b"
    assert models[1].id == "mistral:latest"


@patch('requests.get')
def test_list_models_error(mock_get, ollama_manager):
    """Test error handling when listing models."""
    # Mock a request exception
    mock_get.side_effect = requests.RequestException("API error")
    
    # Should return an empty list and log the error
    models = ollama_manager.list_models()
    assert models == []


@patch('requests.post')
@patch.object(OllamaModelManager, '_fetch_model_info')
def test_install_model_success(
    mock_fetch_info, 
    mock_post,
    ollama_manager
):
    """Test successfully installing a model."""
    # Mock the model info response
    mock_fetch_info.return_value = {
        "name": "llama2",
        "model": "llama2:7b",
        "details": {"parameter_size": "7B"},
        "size": 4000000000
    }
    
    # Mock the pull response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    
    # Call the method
    result = ollama_manager.install_model("llama2:7b")
    
    # Check the results
    assert result is True
    mock_post.assert_called_once_with(
        "http://localhost:11434/api/pull",
        json={"name": "llama2:7b"},
        stream=True
    )
    
    # Check that the model was added to the cache
    assert "llama2:7b" in ollama_manager._models_cache


@patch('requests.post')
@patch.object(OllamaModelManager, '_fetch_model_info')
def test_install_model_error(mock_fetch_info, mock_post, ollama_manager):
    """Test error handling during model installation."""
    # Mock the model info response
    mock_fetch_info.return_value = {
        "name": "llama2",
        "model": "llama2:7b",
        "details": {"parameter_size": "7B"},
        "size": 4000000000
    }
    
    # Mock a request exception
    mock_post.side_effect = requests.RequestException("API error")
    
    # Should raise ModelInstallationError
    with pytest.raises(ModelInstallationError):
        ollama_manager.install_model("llama2:7b")


@patch('requests.delete')
def test_uninstall_model_success(mock_delete, ollama_manager):
    """Test successfully uninstalling a model."""
    # Add a model to the cache
    ollama_manager._models_cache["llama2:7b"] = {"model": "llama2:7b"}
    
    # Mock the delete response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_delete.return_value = mock_response
    
    # Call the method
    result = ollama_manager.uninstall_model("llama2:7b")
    
    # Check the results
    assert result is True
    mock_delete.assert_called_once_with(
        "http://localhost:11434/api/delete",
        json={"name": "llama2:7b"}
    )
    
    # Check that the model was removed from the cache
    assert "llama2:7b" not in ollama_manager._models_cache


@patch('requests.delete')
def test_uninstall_model_error(mock_delete, ollama_manager):
    """Test error handling during model uninstallation."""
    # Add a model to the cache
    ollama_manager._models_cache["llama2:7b"] = {"model": "llama2:7b"}
    
    # Mock a request exception
    mock_delete.side_effect = requests.RequestException("API error")
    
    # Should return False
    assert ollama_manager.uninstall_model("llama2:7b") is False
    
    # The model should still be in the cache
    assert "llama2:7b" in ollama_manager._models_cache


def test_is_model_installed(ollama_manager):
    """Test checking if a model is installed."""
    # Add a model to the cache
    ollama_manager._models_cache["llama2:7b"] = {"model": "llama2:7b"}
    
    # Should return True for installed model
    assert ollama_manager.is_model_installed("llama2:7b") is True
    
    # Should return False for non-installed model
    assert ollama_manager.is_model_installed("nonexistent-model") is False
