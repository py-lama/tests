"""
Tests for the Hugging Face model manager.
"""

import json
from unittest.mock import patch, MagicMock, mock_open

import pytest
import requests

from getllm.models.huggingface.manager import HuggingFaceModelManager
from getllm.exceptions import ModelError, ModelInstallationError, ModelNotFoundError
from getllm.models.base import ModelMetadata, ModelSource, ModelType


@pytest.fixture
def hf_manager(temp_cache_dir):
    """Create a HuggingFaceModelManager instance with a temporary cache."""
    return HuggingFaceModelManager(cache_dir=temp_cache_dir)


def test_hf_manager_init(hf_manager):
    """Test initializing the HuggingFaceModelManager."""
    assert hf_manager.cache_dir is not None
    assert isinstance(hf_manager._models_cache, dict)
    assert hf_manager.hf_token is None


def test_hf_manager_init_with_token():
    """Test initializing with a Hugging Face token."""
    manager = HuggingFaceModelManager(hf_token="test-token")
    assert manager.hf_token == "test-token"


@patch('requests.get')
def test_fetch_model_info_success(mock_get, hf_manager):
    """Test successfully fetching model info from Hugging Face Hub."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "modelId": "test/model",
        "tags": ["pytorch", "text-classification"],
        "siblings": [{"rfilename": "pytorch_model.bin"}],
        "config": {"num_parameters": 1000000}
    }
    mock_get.return_value = mock_response
    
    # Call the method
    model_info = hf_manager._fetch_model_info("test/model")
    
    # Check the results
    assert model_info["modelId"] == "test/model"
    assert "pytorch" in model_info["tags"]
    mock_get.assert_called_once()


@patch('requests.get')
def test_fetch_model_info_not_found(mock_get, hf_manager):
    """Test fetching info for a non-existent model."""
    # Mock a 404 response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    # Should raise ModelNotFoundError
    with pytest.raises(ModelNotFoundError):
        hf_manager._fetch_model_info("nonexistent/model")


@patch('requests.get')
def test_fetch_model_info_error(mock_get, hf_manager):
    """Test error handling when fetching model info."""
    # Mock a request exception
    mock_get.side_effect = requests.RequestException("API error")
    
    # Should raise ModelError
    with pytest.raises(ModelError, match="Failed to fetch model info"):
        hf_manager._fetch_model_info("test/model")


def test_model_dict_to_metadata(hf_manager):
    """Test converting a model dict to ModelMetadata."""
    model_dict = {
        "modelId": "test/model",
        "tags": ["pytorch", "text-classification"],
        "siblings": [
            {"rfilename": "model.safetensors", "size": 500000000}
        ],
        "cardData": {"description": "A test model"},
        "config": {"num_parameters": 1000000}
    }
    
    metadata = hf_manager._model_dict_to_metadata("test/model", model_dict)
    
    assert metadata.id == "test/model"
    assert metadata.name == "test/model"
    assert metadata.description == "A test model"
    assert metadata.source == ModelSource.HUGGINGFACE
    assert metadata.model_type == ModelType.TEXT
    assert metadata.size == 500000000
    assert metadata.parameters == 1000000
    assert "pytorch" in metadata.tags
    assert "text-classification" in metadata.tags


@patch('requests.get')
def test_list_models_success(mock_get, hf_manager):
    """Test listing models successfully."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "modelId": "test/model1",
            "tags": ["pytorch"],
            "siblings": [{"rfilename": "model.safetensors"}],
            "config": {}
        },
        {
            "modelId": "test/model2",
            "tags": ["tensorflow"],
            "siblings": [{"rfilename": "model.h5"}],
            "config": {}
        }
    ]
    mock_get.return_value = mock_response
    
    # Call the method
    models = hf_manager.list_models()
    
    # Check the results
    assert len(models) == 2
    assert models[0].id == "test/model1"
    assert models[1].id == "test/model2"


@patch('requests.get')
def test_list_models_error(mock_get, hf_manager):
    """Test error handling when listing models."""
    # Mock a request exception
    mock_get.side_effect = requests.RequestException("API error")
    
    # Should return an empty list and log the error
    models = hf_manager.list_models()
    assert models == []


@patch('transformers.AutoModel.from_pretrained')
@patch('transformers.AutoTokenizer.from_pretrained')
@patch.object(HuggingFaceModelManager, '_fetch_model_info')
def test_install_model_success(
    mock_fetch_info, 
    mock_tokenizer_from_pretrained, 
    mock_model_from_pretrained,
    hf_manager
):
    """Test successfully installing a model."""
    # Mock the model info response
    mock_fetch_info.return_value = {
        "modelId": "test/model",
        "tags": ["pytorch"],
        "siblings": [{"rfilename": "model.safetensors"}],
        "config": {}
    }
    
    # Mock the transformers methods
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    mock_tokenizer_from_pretrained.return_value = mock_tokenizer
    mock_model_from_pretrained.return_value = mock_model
    
    # Call the method
    result = hf_manager.install_model("test/model")
    
    # Check the results
    assert result is True
    mock_fetch_info.assert_called_once_with("test/model")
    mock_tokenizer_from_pretrained.assert_called_once()
    mock_model_from_pretrained.assert_called_once()
    
    # Check that the model was added to the cache
    assert "test/model" in hf_manager._models_cache


@patch.object(HuggingFaceModelManager, '_fetch_model_info')
def test_install_model_error(mock_fetch_info, hf_manager):
    """Test error handling during model installation."""
    # Mock an error when fetching model info
    mock_fetch_info.side_effect = ModelError("Failed to fetch model info")
    
    # Should raise ModelInstallationError
    with pytest.raises(ModelInstallationError):
        hf_manager.install_model("test/model")


def test_uninstall_model(hf_manager):
    """Test uninstalling a model."""
    # Add a model to the cache
    hf_manager._models_cache["test/model"] = {"modelId": "test/model"}
    
    # Call the method
    result = hf_manager.uninstall_model("test/model")
    
    # Check the results
    assert result is True
    assert "test/model" not in hf_manager._models_cache


def test_is_model_installed(hf_manager):
    """Test checking if a model is installed."""
    # Mock the transformers module
    with patch('transformers.AutoConfig.from_pretrained') as mock_from_pretrained:
        # Test when model is installed
        mock_from_pretrained.return_value = MagicMock()
        assert hf_manager.is_model_installed("test/model") is True
        
        # Test when model is not installed
        mock_from_pretrained.side_effect = OSError("Model not found")
        assert hf_manager.is_model_installed("nonexistent/model") is False
