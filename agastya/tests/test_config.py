import pytest
import yaml
from pathlib import Path
from agastya.core.config import ConfigLoader, AgastyaConfig, Profile, FeaturesConfig

@pytest.fixture
def temp_config_dir(tmp_path):
    """Provides a temporary directory simulating ~/.agastya"""
    return tmp_path

def test_default_config_path(monkeypatch, tmp_path):
    # Mock Path.home() to return our tmp_path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    loader = ConfigLoader()
    assert loader.get_default_config_dir() == tmp_path / ".agastya"

def test_load_config_missing_file(temp_config_dir):
    loader = ConfigLoader(config_dir=temp_config_dir)
    config = loader.load()
    
    assert isinstance(config, AgastyaConfig)
    assert config.default_profile == "local"
    assert "local" in config.profiles
    assert getattr(config.profiles["local"], "provider") == "ollama"
    assert config.features.blog_generation is False
    assert config.features.tweet_generation is False

def test_load_config_from_yaml(temp_config_dir):
    config_file = temp_config_dir / "config.yaml"
    yaml_content = {
        "default_profile": "deep",
        "profiles": {
            "deep": {
                "provider": "anthropic",
                "model": "claude-3-opus-20240229",
                "description": "Deep thinking"
            }
        },
        "features": {
            "blog_generation": True,
            "tweet_generation": True,
            "tweet_generation_locked": True
        }
    }
    with open(config_file, "w") as f:
        yaml.dump(yaml_content, f)
        
    loader = ConfigLoader(config_dir=temp_config_dir)
    config = loader.load()
    
    assert config.default_profile == "deep"
    assert "deep" in config.profiles
    assert config.profiles["deep"].provider == "anthropic"
    assert config.profiles["deep"].model == "claude-3-opus-20240229"
    assert config.profiles["deep"].base_url is None
    
    assert config.features.blog_generation is True
    assert config.features.tweet_generation is True
    assert config.features.tweet_generation_locked is True

def test_config_merge_with_defaults(temp_config_dir):
    # Only providing one partial override
    config_file = temp_config_dir / "config.yaml"
    yaml_content = {
        "features": {
            "blog_generation": True
        }
    }
    with open(config_file, "w") as f:
        yaml.dump(yaml_content, f)
        
    loader = ConfigLoader(config_dir=temp_config_dir)
    config = loader.load()
    
    # Should merge with default 'local' profile
    assert config.default_profile == "local"
    assert "local" in config.profiles
    assert config.features.blog_generation is True
    assert config.features.tweet_generation is False

def test_config_invalid_yaml(temp_config_dir):
    config_file = temp_config_dir / "config.yaml"
    with open(config_file, "w") as f:
        f.write("invalid: [\nyaml:")
        
    loader = ConfigLoader(config_dir=temp_config_dir)
    with pytest.raises(ValueError, match="Failed to parse config.yaml"):
        loader.load()

def test_config_manas_registry_path(temp_config_dir):
    loader = ConfigLoader(config_dir=temp_config_dir)
    assert loader.get_manas_registry_path() == temp_config_dir / "manas.yaml"
