"""
Tests for the configuration system.
"""
import os
import tempfile
import yaml
import pytest
import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.config import (
    Config, 
    get_config, 
    reload_config,
    AIModelConfig,
    PersonalityConfig,
    VoiceConfig,
    TwitchConfig,
    VTubeStudioConfig,
    TrainingConfig,
    SystemConfig,
    CONFIG_SCHEMA_VERSION
)


class TestConfigurationLoading:
    """Test configuration loading from YAML files."""
    
    def test_load_default_config(self):
        """Test loading configuration with default values."""
        config = Config()
        
        # Test defaults
        assert config.schema_version == CONFIG_SCHEMA_VERSION
        assert config.ai.model.type == "local"
        assert config.ai.model.name == "mistral-7b-instruct"
        assert config.ai.personality.name == "AI Assistant"
        assert config.voice.stt.engine == "faster-whisper"
        assert config.twitch.username == ""
        assert config.system.log_level == "INFO"
    
    def test_load_from_yaml_file(self):
        """Test loading configuration from YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_content = {
                'schema_version': '1.0.0',
                'ai': {
                    'model': {
                        'type': 'api',
                        'name': 'gpt-4',
                        'max_tokens': 500,
                        'temperature': 0.7
                    },
                    'personality': {
                        'name': 'Aiko',
                        'traits': ['cheerful', 'curious'],
                        'backstory': 'A friendly AI companion'
                    }
                },
                'voice': {
                    'stt': {
                        'engine': 'whisper',
                        'model_size': 'large'
                    }
                },
                'twitch': {
                    'username': 'testuser',
                    'channel': 'testchannel'
                }
            }
            yaml.dump(yaml_content, f)
            f.flush()
            
            config = Config.load(f.name)
            
            assert config.ai.model.type == "api"
            assert config.ai.model.name == "gpt-4"
            assert config.ai.model.max_tokens == 500
            assert config.ai.personality.name == "Aiko"
            assert config.ai.personality.traits == ['cheerful', 'curious']
            assert config.voice.stt.engine == "whisper"
            assert config.twitch.username == "testuser"
            
            os.unlink(f.name)
    
    def test_find_config_file(self):
        """Test finding configuration file in standard locations."""
        # Test with no config file
        assert Config._find_config_file() is None
        
        # Test with config.yaml in current directory
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("schema_version: '1.0.0'\n")
            
            with patch('pathlib.Path.cwd', return_value=Path(tmpdir)):
                with patch('pathlib.Path.exists') as mock_exists:
                    def exists_side_effect(self):
                        return str(self) == str(config_path)
                    mock_exists.side_effect = exists_side_effect
                    
                    found = Config._find_config_file()
                    assert found is not None


class TestEnvironmentVariableOverrides:
    """Test environment variable override functionality."""
    
    def test_env_var_override_twitch(self):
        """Test environment variable overrides for Twitch config."""
        with patch.dict(os.environ, {
            'TWITCH_USERNAME': 'env_user',
            'TWITCH_OAUTH_TOKEN': 'oauth_123',
            'TWITCH_CLIENT_ID': 'client_123',
            'TWITCH_CHANNEL': 'env_channel'
        }):
            config = Config.load()
            
            assert config.twitch.username == "env_user"
            assert config.twitch.oauth_token == "oauth_123"
            assert config.twitch.client_id == "client_123"
            assert config.twitch.channel == "env_channel"
    
    def test_env_var_override_with_yaml(self):
        """Test that environment variables override YAML values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_content = {
                'twitch': {
                    'username': 'yaml_user',
                    'oauth_token': 'yaml_token'
                }
            }
            yaml.dump(yaml_content, f)
            f.flush()
            
            with patch.dict(os.environ, {
                'TWITCH_USERNAME': 'env_user',
                'TWITCH_OAUTH_TOKEN': 'env_token'
            }):
                config = Config.load(f.name)
                
                # Environment variables should override YAML
                assert config.twitch.username == "env_user"
                assert config.twitch.oauth_token == "env_token"
            
            os.unlink(f.name)
    
    def test_env_var_vtube_studio(self):
        """Test environment variable overrides for VTube Studio config."""
        with patch.dict(os.environ, {
            'VTUBE_AUTH_TOKEN': 'vtube_auth_123',
            'VTUBE_HOST': '192.168.1.100',
            'VTUBE_PORT': '9000'
        }):
            config = Config.load()
            
            assert config.vtube_studio.auth_token == "vtube_auth_123"
            assert config.vtube_studio.host == "192.168.1.100"
            assert config.vtube_studio.port == 9000


class TestValidation:
    """Test configuration validation."""
    
    def test_field_validation_ai_model(self):
        """Test AI model field validation."""
        # Valid configuration
        config = AIModelConfig(type="local", device="cuda", temperature=1.5)
        assert config.type == "local"
        
        # Invalid type
        with pytest.raises(ValueError, match="Model type must be one of"):
            AIModelConfig(type="invalid")
        
        # Invalid device
        with pytest.raises(ValueError, match="Device must be one of"):
            AIModelConfig(device="invalid")
        
        # Invalid temperature range
        with pytest.raises(ValueError):
            AIModelConfig(temperature=3.0)
    
    def test_field_validation_numeric_ranges(self):
        """Test numeric field validation."""
        # Test max_tokens range
        with pytest.raises(ValueError):
            AIModelConfig(max_tokens=0)
        
        with pytest.raises(ValueError):
            AIModelConfig(max_tokens=5000)
        
        # Test port range
        with pytest.raises(ValueError):
            VTubeStudioConfig(port=0)
        
        with pytest.raises(ValueError):
            VTubeStudioConfig(port=70000)
    
    def test_log_level_validation(self):
        """Test log level validation and case normalization."""
        # Valid log levels
        config = SystemConfig(log_level="info")
        assert config.log_level == "INFO"
        
        config = SystemConfig(log_level="DEBUG")
        assert config.log_level == "DEBUG"
        
        # Invalid log level
        with pytest.raises(ValueError, match="Log level must be one of"):
            SystemConfig(log_level="INVALID")
    
    def test_required_fields_validation(self):
        """Test validation of required fields."""
        config = Config()
        
        # No errors with default config
        errors = config.validate_required_fields()
        assert len(errors) == 0
        
        # Error when username set but no oauth token
        config.twitch.username = "testuser"
        errors = config.validate_required_fields()
        assert len(errors) == 1
        assert "OAuth token is required" in errors[0]
        
        # Error when VTube Studio enabled but no auth token
        config.vtube_studio.enabled = True
        errors = config.validate_required_fields()
        assert len(errors) == 2
        assert any("VTube Studio auth token" in e for e in errors)
    
    def test_schema_version_validation(self):
        """Test schema version validation."""
        # Valid schema version
        config = Config(schema_version=CONFIG_SCHEMA_VERSION)
        assert config.schema_version == CONFIG_SCHEMA_VERSION
        
        # Invalid schema version
        with pytest.raises(ValueError, match="Configuration schema version mismatch"):
            Config(schema_version="0.9.0")


class TestHotReload:
    """Test configuration hot-reload functionality."""
    
    def test_hot_reload_basic(self):
        """Test basic hot-reload functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            initial_content = {
                'ai': {
                    'model': {
                        'name': 'initial-model'
                    }
                }
            }
            yaml.dump(initial_content, f)
            f.flush()
            
            config = Config.load(f.name)
            assert config.ai.model.name == "initial-model"
            
            # Track reload
            reload_called = threading.Event()
            
            def on_reload(cfg):
                reload_called.set()
            
            # Enable hot reload
            config.enable_hot_reload(on_reload)
            
            # Update the file
            updated_content = {
                'ai': {
                    'model': {
                        'name': 'updated-model'
                    }
                }
            }
            with open(f.name, 'w') as update_f:
                yaml.dump(updated_content, update_f)
            
            # Wait for reload
            assert reload_called.wait(timeout=2)
            
            # Check updated value
            assert config.ai.model.name == "updated-model"
            
            # Cleanup
            config.disable_hot_reload()
            os.unlink(f.name)
    
    def test_hot_reload_error_handling(self):
        """Test hot-reload error handling."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'ai': {'model': {'name': 'test'}}}, f)
            f.flush()
            
            config = Config.load(f.name)
            config.enable_hot_reload()
            
            # Write invalid YAML
            with open(f.name, 'w') as update_f:
                update_f.write("invalid: yaml: content:")
            
            # Give time for reload attempt
            time.sleep(0.5)
            
            # Config should remain unchanged
            assert config.ai.model.name == "test"
            
            config.disable_hot_reload()
            os.unlink(f.name)


class TestConfigSaving:
    """Test configuration saving functionality."""
    
    def test_save_config(self):
        """Test saving configuration to file."""
        config = Config()
        config.ai.model.name = "custom-model"
        config.twitch.username = "testuser"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config.save(f.name)
            
            # Load saved config
            loaded_config = Config.load(f.name)
            
            assert loaded_config.ai.model.name == "custom-model"
            assert loaded_config.twitch.username == "testuser"
            assert loaded_config.schema_version == CONFIG_SCHEMA_VERSION
            
            os.unlink(f.name)
    
    def test_save_without_path(self):
        """Test saving without specifying path."""
        config = Config()
        
        # Should raise error when no path specified
        with pytest.raises(ValueError, match="No configuration file path"):
            config.save()


class TestGlobalConfig:
    """Test global configuration instance."""
    
    def test_get_config_singleton(self):
        """Test that get_config returns singleton instance."""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_reload_config(self):
        """Test reloading global configuration."""
        with patch('src.config.Config.load') as mock_load:
            mock_config = MagicMock()
            mock_load.return_value = mock_config
            
            reloaded = reload_config()
            
            assert mock_load.called
            assert reloaded is mock_config


class TestComplexScenarios:
    """Test complex configuration scenarios."""
    
    def test_nested_config_structure(self):
        """Test deeply nested configuration structure."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_content = {
                'training': {
                    'feedback': {
                        'positive_reactions': ['Custom1', 'Custom2'],
                        'negative_reactions': ['Bad1', 'Bad2']
                    }
                },
                'system': {
                    'performance': {
                        'response_timeout_ms': 3000,
                        'max_concurrent_requests': 5,
                        'cache_responses': False
                    }
                }
            }
            yaml.dump(yaml_content, f)
            f.flush()
            
            config = Config.load(f.name)
            
            assert config.training.feedback.positive_reactions == ['Custom1', 'Custom2']
            assert config.system.performance.response_timeout_ms == 3000
            assert config.system.performance.cache_responses is False
            
            os.unlink(f.name)
    
    def test_channel_defaults_to_username(self):
        """Test that Twitch channel defaults to username if not specified."""
        config = TwitchConfig(username="myuser")
        assert config.channel == "myuser"
        
        config = TwitchConfig(username="myuser", channel="mychannel")
        assert config.channel == "mychannel"
    
    def test_partial_config_loading(self):
        """Test loading partial configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # Only specify some fields
            yaml_content = {
                'ai': {
                    'model': {
                        'name': 'custom-model'
                    }
                    # personality not specified, should use defaults
                }
                # other sections not specified
            }
            yaml.dump(yaml_content, f)
            f.flush()
            
            config = Config.load(f.name)
            
            # Specified value
            assert config.ai.model.name == "custom-model"
            
            # Default values
            assert config.ai.model.temperature == 0.8
            assert config.ai.personality.name == "AI Assistant"
            assert config.voice.stt.engine == "faster-whisper"
            
            os.unlink(f.name)