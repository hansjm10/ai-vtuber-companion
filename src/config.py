"""
Configuration system with YAML support, environment variable overrides, and hot-reload capability.
"""
import os
import yaml
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from pydantic import (
    BaseModel, 
    Field, 
    field_validator,
    model_validator,
    ConfigDict
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# Schema version for configuration compatibility
CONFIG_SCHEMA_VERSION = "1.0.0"


class AIModelConfig(BaseModel):
    """AI model configuration."""
    type: str = Field(default="local", description="Model type: local or api")
    name: str = Field(default="mistral-7b-instruct", description="Model name")
    quantization: Optional[str] = Field(default="Q4_K_M", description="Quantization for GGUF models")
    max_tokens: int = Field(default=200, ge=1, le=4096, description="Maximum tokens to generate")
    temperature: float = Field(default=0.8, ge=0.0, le=2.0, description="Sampling temperature")
    device: str = Field(default="cuda", description="Device: cuda, rocm, cpu, metal")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = ["local", "api"]
        if v not in allowed:
            raise ValueError(f"Model type must be one of: {allowed}")
        return v
    
    @field_validator('device')
    @classmethod
    def validate_device(cls, v: str) -> str:
        allowed = ["cuda", "rocm", "cpu", "metal"]
        if v not in allowed:
            raise ValueError(f"Device must be one of: {allowed}")
        return v


class PersonalityConfig(BaseModel):
    """AI personality configuration."""
    name: str = Field(default="AI Assistant", description="AI personality name")
    traits: List[str] = Field(default_factory=lambda: ["helpful", "friendly"], description="Personality traits")
    backstory: str = Field(default="A helpful AI assistant", description="Character backstory")
    speech_style: str = Field(default="neutral", description="Speech style")


class AIConfig(BaseModel):
    """Complete AI configuration."""
    model: AIModelConfig = Field(default_factory=AIModelConfig)
    personality: PersonalityConfig = Field(default_factory=PersonalityConfig)


class STTConfig(BaseModel):
    """Speech-to-text configuration."""
    engine: str = Field(default="faster-whisper", description="STT engine")
    model_size: str = Field(default="base", description="Model size")
    language: str = Field(default="en", description="Language code")
    device: str = Field(default="cuda", description="Device for STT")
    
    @field_validator('engine')
    @classmethod
    def validate_engine(cls, v: str) -> str:
        allowed = ["faster-whisper", "whisper", "azure", "google"]
        if v not in allowed:
            raise ValueError(f"STT engine must be one of: {allowed}")
        return v


class TTSConfig(BaseModel):
    """Text-to-speech configuration."""
    engine: str = Field(default="coqui", description="TTS engine")
    voice_id: str = Field(default="default", description="Voice ID")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")
    pitch: float = Field(default=1.0, ge=0.5, le=2.0, description="Voice pitch")
    
    @field_validator('engine')
    @classmethod
    def validate_engine(cls, v: str) -> str:
        allowed = ["coqui", "elevenlabs", "azure", "google"]
        if v not in allowed:
            raise ValueError(f"TTS engine must be one of: {allowed}")
        return v


class VoiceConfig(BaseModel):
    """Voice processing configuration."""
    stt: STTConfig = Field(default_factory=STTConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)


class TwitchCommandsConfig(BaseModel):
    """Twitch commands configuration."""
    prefix: str = Field(default="!", description="Command prefix")
    enabled: List[str] = Field(default_factory=lambda: ["hello", "mood", "story"], description="Enabled commands")


class TwitchConfig(BaseSettings):
    """Twitch integration configuration."""
    model_config = SettingsConfigDict(env_prefix="TWITCH_")
    
    username: str = Field(default="", description="Twitch username")
    oauth_token: str = Field(default="", description="OAuth token from twitchapps.com/tmi/")
    client_id: str = Field(default="", description="Twitch client ID")
    client_secret: str = Field(default="", description="Twitch client secret")
    channel: str = Field(default="", description="Twitch channel name")
    commands: TwitchCommandsConfig = Field(default_factory=TwitchCommandsConfig)
    
    @field_validator('channel')
    @classmethod
    def validate_channel(cls, v: str, info) -> str:
        # If channel is empty, use username
        if not v and 'username' in info.data:
            return info.data['username']
        return v


class VTubeStudioConfig(BaseSettings):
    """VTube Studio integration configuration."""
    model_config = SettingsConfigDict(env_prefix="VTUBE_")
    
    enabled: bool = Field(default=True, description="Enable VTube Studio integration")
    host: str = Field(default="localhost", description="VTube Studio host")
    port: int = Field(default=8001, ge=1, le=65535, description="VTube Studio port")
    auth_token: str = Field(default="", description="Authentication token")
    model_id: str = Field(default="", description="VTuber model ID")
    expressions: Dict[str, str] = Field(default_factory=dict, description="Expression mappings")


class TrainingFeedbackConfig(BaseModel):
    """Training feedback configuration."""
    positive_reactions: List[str] = Field(
        default_factory=lambda: ["PogChamp", "Pog", "LUL", "KEKW"],
        description="Positive reaction emotes"
    )
    negative_reactions: List[str] = Field(
        default_factory=lambda: ["ResidentSleeper", "NotLikeThis"],
        description="Negative reaction emotes"
    )


class TrainingConfig(BaseSettings):
    """Training configuration."""
    model_config = SettingsConfigDict(env_prefix="TRAINING_")
    
    auto_collect: bool = Field(default=True, description="Auto-collect training data")
    min_interactions: int = Field(default=100, ge=10, description="Minimum interactions for training")
    batch_size: int = Field(default=32, ge=1, description="Training batch size")
    learning_rate: float = Field(default=1e-5, ge=1e-8, le=1e-2, description="Learning rate")
    feedback: TrainingFeedbackConfig = Field(default_factory=TrainingFeedbackConfig)


class PerformanceConfig(BaseModel):
    """System performance configuration."""
    response_timeout_ms: int = Field(default=5000, ge=100, le=30000, description="Response timeout in ms")
    max_concurrent_requests: int = Field(default=10, ge=1, le=100, description="Max concurrent requests")
    cache_responses: bool = Field(default=True, description="Enable response caching")


class SystemConfig(BaseSettings):
    """System configuration."""
    model_config = SettingsConfigDict(env_prefix="SYSTEM_")
    
    log_level: str = Field(default="INFO", description="Logging level")
    data_retention_days: int = Field(default=30, ge=1, description="Data retention period")
    backup_interval_hours: int = Field(default=24, ge=1, description="Backup interval")
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v


class Config(BaseModel):
    """Main configuration class."""
    model_config = ConfigDict(validate_assignment=True)
    
    schema_version: str = Field(default=CONFIG_SCHEMA_VERSION, description="Configuration schema version")
    ai: AIConfig = Field(default_factory=AIConfig)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    twitch: TwitchConfig = Field(default_factory=TwitchConfig)
    vtube_studio: VTubeStudioConfig = Field(default_factory=VTubeStudioConfig)
    training: TrainingConfig = Field(default_factory=TrainingConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)
    
    _config_file: Optional[Path] = None
    _file_observer: Optional[Observer] = None
    _reload_callbacks: List[callable] = []
    _lock: threading.Lock = threading.Lock()
    
    @model_validator(mode='after')
    def validate_schema_version(self) -> 'Config':
        """Validate configuration schema version compatibility."""
        if self.schema_version != CONFIG_SCHEMA_VERSION:
            # In the future, add migration logic here
            raise ValueError(
                f"Configuration schema version mismatch. "
                f"Expected: {CONFIG_SCHEMA_VERSION}, Got: {self.schema_version}"
            )
        return self
    
    @classmethod
    def load(cls, config_path: Optional[Union[str, Path]] = None) -> 'Config':
        """
        Load configuration from YAML file with environment variable overrides.
        
        Args:
            config_path: Path to configuration file. If None, searches standard locations.
            
        Returns:
            Loaded configuration instance.
        """
        # Find config file
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = cls._find_config_file()
        
        # Load YAML data
        yaml_data = {}
        if config_file and config_file.exists():
            with open(config_file, 'r') as f:
                yaml_data = yaml.safe_load(f) or {}
        
        # Create nested config objects with environment overrides
        config_data = {
            'schema_version': yaml_data.get('schema_version', CONFIG_SCHEMA_VERSION),
            'ai': AIConfig(**yaml_data.get('ai', {})),
            'voice': VoiceConfig(**yaml_data.get('voice', {})),
            'twitch': TwitchConfig(**cls._merge_with_env(yaml_data.get('twitch', {}), 'TWITCH_')),
            'vtube_studio': VTubeStudioConfig(**cls._merge_with_env(yaml_data.get('vtube_studio', {}), 'VTUBE_')),
            'training': TrainingConfig(**cls._merge_with_env(yaml_data.get('training', {}), 'TRAINING_')),
            'system': SystemConfig(**cls._merge_with_env(yaml_data.get('system', {}), 'SYSTEM_'))
        }
        
        config = cls(**config_data)
        config._config_file = config_file
        return config
    
    @staticmethod
    def _find_config_file() -> Optional[Path]:
        """Find configuration file in standard locations."""
        search_paths = [
            Path("config.yaml"),
            Path("config.yml"),
            Path("config/config.yaml"),
            Path("config/config.yml"),
            Path("../config.yaml"),
            Path("../config.yml"),
            Path.home() / ".ai-vtuber" / "config.yaml",
            Path("/etc/ai-vtuber/config.yaml"),
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        return None
    
    @staticmethod
    def _merge_with_env(yaml_data: dict, env_prefix: str) -> dict:
        """Merge YAML data with environment variables."""
        result = yaml_data.copy()
        
        # Check for environment variables with the prefix
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                # Convert TWITCH_OAUTH_TOKEN to oauth_token
                config_key = key[len(env_prefix):].lower()
                result[config_key] = value
        
        return result
    
    def enable_hot_reload(self, callback: Optional[callable] = None):
        """
        Enable configuration hot-reload.
        
        Args:
            callback: Optional callback function to call on config reload.
        """
        if not self._config_file:
            raise RuntimeError("Cannot enable hot-reload without a config file")
        
        if callback:
            self._reload_callbacks.append(callback)
        
        class ConfigFileHandler(FileSystemEventHandler):
            def __init__(self, config_instance):
                self.config = config_instance
            
            def on_modified(self, event):
                if isinstance(event, FileModifiedEvent) and event.src_path == str(self.config._config_file):
                    self.config._reload()
        
        self._file_observer = Observer()
        self._file_observer.schedule(
            ConfigFileHandler(self),
            str(self._config_file.parent),
            recursive=False
        )
        self._file_observer.start()
    
    def disable_hot_reload(self):
        """Disable configuration hot-reload."""
        if self._file_observer:
            self._file_observer.stop()
            self._file_observer.join()
            self._file_observer = None
    
    def _reload(self):
        """Reload configuration from file."""
        with self._lock:
            try:
                new_config = self.load(self._config_file)
                
                # Update current instance with new values
                self.schema_version = new_config.schema_version
                self.ai = new_config.ai
                self.voice = new_config.voice
                self.twitch = new_config.twitch
                self.vtube_studio = new_config.vtube_studio
                self.training = new_config.training
                self.system = new_config.system
                
                # Call reload callbacks
                for callback in self._reload_callbacks:
                    callback(self)
                
                print(f"Configuration reloaded at {datetime.now()}")
            except Exception as e:
                print(f"Error reloading configuration: {e}")
    
    def save(self, config_path: Optional[Union[str, Path]] = None):
        """
        Save configuration to YAML file.
        
        Args:
            config_path: Path to save configuration. Uses loaded path if not specified.
        """
        save_path = Path(config_path) if config_path else self._config_file
        if not save_path:
            raise ValueError("No configuration file path specified")
        
        # Convert to dict and save
        with open(save_path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)
    
    def validate_required_fields(self) -> List[str]:
        """
        Validate that all required fields are set.
        
        Returns:
            List of validation errors.
        """
        errors = []
        
        # Check required Twitch fields if Twitch is being used
        if self.twitch.username and not self.twitch.oauth_token:
            errors.append("Twitch OAuth token is required when username is set")
        
        # Check VTube Studio auth if enabled
        if self.vtube_studio.enabled and not self.vtube_studio.auth_token:
            errors.append("VTube Studio auth token is required when enabled")
        
        # Add more validation as needed
        
        return errors


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config():
    """Reload the global configuration."""
    global _config
    _config = Config.load()
    return _config