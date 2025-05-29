"""
Tests for the base model classes.
"""

import pytest

from getllm.models.base import (
    ModelSource,
    ModelType,
    ModelMetadata,
    BaseModel,
    BaseModelManager
)


def test_model_source_enum():
    """Test the ModelSource enum values."""
    assert ModelSource.HUGGINGFACE == "huggingface"
    assert ModelSource.OLLAMA == "ollama"
    assert ModelSource.LOCAL == "local"
    assert ModelSource.OTHER == "other"


def test_model_type_enum():
    """Test the ModelType enum values."""
    assert ModelType.TEXT == "text"
    assert ModelType.CODE == "code"
    assert ModelType.CHAT == "chat"
    assert ModelType.EMBEDDING == "embedding"
    assert ModelType.MULTIMODAL == "multimodal"


def test_model_metadata_creation(sample_model_metadata):
    """Test creating a ModelMetadata object."""
    assert sample_model_metadata.id == "test-model"
    assert sample_model_metadata.name == "Test Model"
    assert sample_model_metadata.description == "A test model"
    assert sample_model_metadata.source == ModelSource.OTHER
    assert sample_model_metadata.model_type == ModelType.TEXT
    assert sample_model_metadata.size == 1000000
    assert sample_model_metadata.parameters == 1000000
    assert sample_model_metadata.tags == ["test", "text"]
    assert sample_model_metadata.config == {"test": True}


def test_model_metadata_from_dict(mock_model_metadata):
    """Test creating a ModelMetadata object from a dictionary."""
    metadata = ModelMetadata(**mock_model_metadata)
    assert metadata.id == "test-model"
    assert metadata.name == "Test Model"
    assert metadata.description == "A test model"
    assert metadata.source == ModelSource.OTHER
    assert metadata.model_type == ModelType.TEXT
    assert metadata.size == 1000000
    assert metadata.parameters == 1000000
    assert metadata.tags == ["test", "text"]
    assert metadata.config == {"test": True}


def test_base_model_abstract_methods():
    """Test that BaseModel abstract methods raise NotImplementedError."""
    class TestModel(BaseModel):
        def load(self):
            pass
            
        def unload(self):
            pass
            
        def is_loaded(self):
            pass
    
    model = TestModel(ModelMetadata(id="test", name="Test"))
    with pytest.raises(NotImplementedError):
        model.load()
    with pytest.raises(NotImplementedError):
        model.unload()
    with pytest.raises(NotImplementedError):
        model.is_loaded()


def test_base_model_manager_abstract_methods():
    """Test that BaseModelManager abstract methods raise NotImplementedError."""
    manager = BaseModelManager()
    
    with pytest.raises(NotImplementedError):
        manager.list_models()
    
    with pytest.raises(NotImplementedError):
        manager.get_model("test")
    
    with pytest.raises(NotImplementedError):
        manager.install_model("test")
    
    with pytest.raises(NotImplementedError):
        manager.uninstall_model("test")
    
    with pytest.raises(NotImplementedError):
        manager.is_model_installed("test")
