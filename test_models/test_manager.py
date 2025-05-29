"""
Tests for the main ModelManager class.
"""

from unittest.mock import patch, MagicMock, ANY

import pytest

from getllm.models import ModelManager
from getllm.models.base import ModelMetadata, ModelSource, ModelType
from getllm.exceptions import ModelError, ModelInstallationError, ModelNotFoundError


@pytest.fixture
def model_manager():
    """Create a ModelManager instance with mocked sub-managers."""
    with patch('getllm.models.manager.HuggingFaceModelManager') as mock_hf, \
         patch('getllm.models.manager.OllamaModelManager') as mock_ollama:
        
        # Set up mock managers
        mock_hf.return_value.list_models.return_value = [
            ModelMetadata(
                id="hf/test-model",
                name="Test Model",
                source=ModelSource.HUGGINGFACE,
                model_type=ModelType.TEXT
            )
        ]
        
        mock_ollama.return_value.list_models.return_value = [
            ModelMetadata(
                id="ollama/llama2:7b",
                name="Llama 2",
                source=ModelSource.OLLAMA,
                model_type=ModelType.TEXT
            )
        ]
        
        yield ModelManager()


def test_model_manager_init(model_manager):
    """Test initializing the ModelManager."""
    assert hasattr(model_manager, '_hf_manager')
    assert hasattr(model_manager, '_ollama_manager')
    assert model_manager._models == {}


def test_list_models(model_manager):
    """Test listing all models from all sources."""
    models = model_manager.list_models()
    
    # Should return models from both sources
    assert len(models) == 2
    assert any(m.id == "hf/test-model" for m in models)
    assert any(m.id == "ollama/llama2:7b" for m in models)


def test_list_models_with_source_filter(model_manager):
    """Test listing models filtered by source."""
    # Test with Hugging Face filter
    hf_models = model_manager.list_models(source=ModelSource.HUGGINGFACE)
    assert len(hf_models) == 1
    assert hf_models[0].id == "hf/test-model"
    
    # Test with Ollama filter
    ollama_models = model_manager.list_models(source=ModelSource.OLLAMA)
    assert len(ollama_models) == 1
    assert ollama_models[0].id == "ollama/llama2:7b"


def test_list_models_with_search(model_manager):
    """Test searching for models with a query."""
    # Set up mock search results
    model_manager._hf_manager.search_models.return_value = [
        ModelMetadata(
            id="hf/test-model",
            name="Test Model",
            source=ModelSource.HUGGINGFACE,
            model_type=ModelType.TEXT
        )
    ]
    
    model_manager._ollama_manager.search_models.return_value = [
        ModelMetadata(
            id="ollama/llama2:7b",
            name="Llama 2",
            source=ModelSource.OLLAMA,
            model_type=ModelType.TEXT
        )
    ]
    
    # Test search
    results = model_manager.search_models("test")
    assert len(results) == 2
    
    # Test search with source filter
    hf_results = model_manager.search_models("test", source=ModelSource.HUGGINGFACE)
    assert len(hf_results) == 1
    assert hf_results[0].id == "hf/test-model"


def test_get_model(model_manager):
    """Test getting a model by ID."""
    # Set up mock get_model responses
    hf_model = ModelMetadata(
        id="hf/test-model",
        name="Test Model",
        source=ModelSource.HUGGINGFACE,
        model_type=ModelType.TEXT
    )
    
    ollama_model = ModelMetadata(
        id="ollama/llama2:7b",
        name="Llama 2",
        source=ModelSource.OLLAMA,
        model_type=ModelType.TEXT
    )
    
    model_manager._hf_manager.get_model.return_value = hf_model
    model_manager._ollama_manager.get_model.return_value = ollama_model
    
    # Test getting a Hugging Face model
    result = model_manager.get_model("hf/test-model")
    assert result == hf_model
    
    # Test getting an Ollama model
    result = model_manager.get_model("ollama/llama2:7b")
    assert result == ollama_model
    
    # Test getting a non-existent model
    model_manager._hf_manager.get_model.return_value = None
    model_manager._ollama_manager.get_model.return_value = None
    assert model_manager.get_model("nonexistent/model") is None


def test_install_model(model_manager):
    """Test installing a model."""
    # Set up mock install responses
    model_manager._hf_manager.install_model.return_value = True
    model_manager._ollama_manager.install_model.return_value = True
    
    # Test installing a Hugging Face model
    assert model_manager.install_model("hf/test-model") is True
    model_manager._hf_manager.install_model.assert_called_once_with("test-model")
    
    # Test installing an Ollama model
    assert model_manager.install_model("ollama/llama2:7b") is True
    model_manager._ollama_manager.install_model.assert_called_once_with("llama2:7b")
    
    # Test installing with an invalid source
    with pytest.raises(ValueError, match="Unknown model source"):
        model_manager.install_model("invalid/model")


def test_uninstall_model(model_manager):
    """Test uninstalling a model."""
    # Set up mock uninstall responses
    model_manager._hf_manager.uninstall_model.return_value = True
    model_manager._ollama_manager.uninstall_model.return_value = True
    
    # Test uninstalling a Hugging Face model
    assert model_manager.uninstall_model("hf/test-model") is True
    model_manager._hf_manager.uninstall_model.assert_called_once_with("test-model")
    
    # Test uninstalling an Ollama model
    assert model_manager.uninstall_model("ollama/llama2:7b") is True
    model_manager._ollama_manager.uninstall_model.assert_called_once_with("llama2:7b")
    
    # Test uninstalling with an invalid source
    with pytest.raises(ValueError, match="Unknown model source"):
        model_manager.uninstall_model("invalid/model")


def test_is_model_installed(model_manager):
    """Test checking if a model is installed."""
    # Set up mock responses
    model_manager._hf_manager.is_model_installed.return_value = True
    model_manager._ollama_manager.is_model_installed.return_value = False
    
    # Test checking a Hugging Face model
    assert model_manager.is_model_installed("hf/test-model") is True
    model_manager._hf_manager.is_model_installed.assert_called_once_with("test-model")
    
    # Test checking an Ollama model
    assert model_manager.is_model_installed("ollama/llama2:7b") is False
    model_manager._ollama_manager.is_model_installed.assert_called_once_with("llama2:7b")
    
    # Test checking with an invalid source
    with pytest.raises(ValueError, match="Unknown model source"):
        model_manager.is_model_installed("invalid/model")


def test_get_default_model(model_manager):
    """Test getting the default model."""
    # Test when no default model is set
    assert model_manager.get_default_model() is None
    
    # Test when a default model is set
    model_manager.set_default_model("hf/test-model")
    assert model_manager.get_default_model() == "hf/test-model"


def test_set_default_model(model_manager):
    """Test setting the default model."""
    # Test setting a valid model
    model_manager._hf_manager.is_model_installed.return_value = True
    model_manager.set_default_model("hf/test-model")
    assert model_manager._default_model == "hf/test-model"
    
    # Test setting a non-existent model
    model_manager._hf_manager.is_model_installed.return_value = False
    with pytest.raises(ValueError, match="Model not found or not installed"):
        model_manager.set_default_model("hf/nonexistent-model")
    
    # Test setting an invalid model ID
    with pytest.raises(ValueError, match="Invalid model ID format"):
        model_manager.set_default_model("invalid-format")


def test_update_models_cache(model_manager):
    """Test updating the models cache."""
    # Set up mock responses
    model_manager._hf_manager.list_models.return_value = [
        ModelMetadata(
            id="hf/test-model",
            name="Test Model",
            source=ModelSource.HUGGINGFACE,
            model_type=ModelType.TEXT
        )
    ]
    
    model_manager._ollama_manager.list_models.return_value = [
        ModelMetadata(
            id="ollama/llama2:7b",
            name="Llama 2",
            source=ModelSource.OLLAMA,
            model_type=ModelType.TEXT
        )
    ]
    
    # Call the method
    model_manager.update_models_cache()
    
    # Check that the cache was updated
    assert len(model_manager._models) == 2
    assert "hf/test-model" in model_manager._models
    assert "ollama/llama2:7b" in model_manager._models
    
    # Check that the managers' list_models methods were called
    model_manager._hf_manager.list_models.assert_called_once()
    model_manager._ollama_manager.list_models.assert_called_once()
