from pydantic import BaseSettings, Field
from typing import List, Optional, Dict
import yaml
from pathlib import Path


class AIConfig(BaseSettings):
    model_type: str = "local"
    model_name: str = "mistral-7b-instruct"
    quantization: str = "Q4_K_M"
    max_tokens: int = 200
    temperature: float = 0.8
    device: str = "cuda"
    
    class Config:
        env_prefix = "AI_"


class PersonalityConfig(BaseSettings):
    name: str = "AI Assistant"
    traits: List[str] = []
    backstory: str = ""
    speech_style: str = "neutral"
    
    class Config:
        env_prefix = "PERSONALITY_"


class VoiceConfig(BaseSettings):
    stt_engine: str = "faster-whisper"
    stt_model_size: str = "base"
    stt_language: str = "en"
    stt_device: str = "cuda"
    
    tts_engine: str = "coqui"
    tts_voice_id: str = "default"
    tts_speed: float = 1.0
    tts_pitch: float = 1.0
    
    class Config:
        env_prefix = "VOICE_"


class TwitchConfig(BaseSettings):
    username: str = ""
    oauth_token: str = Field(default="", env="TWITCH_OAUTH_TOKEN")
    client_id: str = Field(default="", env="TWITCH_CLIENT_ID")
    client_secret: str = Field(default="", env="TWITCH_CLIENT_SECRET")
    channel: str = ""
    command_prefix: str = "!"
    enabled_commands: List[str] = ["hello", "mood", "story"]
    
    class Config:
        env_prefix = "TWITCH_"


class VTubeStudioConfig(BaseSettings):
    enabled: bool = True
    host: str = "localhost"
    port: int = 8001
    auth_token: str = Field(default="", env="VTUBE_AUTH_TOKEN")
    model_id: str = ""
    expressions: Dict[str, str] = {}
    
    class Config:
        env_prefix = "VTUBE_"


class TrainingConfig(BaseSettings):
    auto_collect: bool = True
    min_interactions: int = 100
    batch_size: int = 32
    learning_rate: float = 1e-5
    positive_reactions: List[str] = ["PogChamp", "Pog", "LUL", "KEKW"]
    negative_reactions: List[str] = ["ResidentSleeper", "NotLikeThis"]
    
    class Config:
        env_prefix = "TRAINING_"


class SystemConfig(BaseSettings):
    log_level: str = "INFO"
    data_retention_days: int = 30
    backup_interval_hours: int = 24
    response_timeout_ms: int = 5000
    max_concurrent_requests: int = 10
    cache_responses: bool = True
    
    class Config:
        env_prefix = "SYSTEM_"


class Config:
    def __init__(self, config_path: Optional[Path] = None):
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
        else:
            config_data = {}
        
        self.ai = AIConfig(**config_data.get('ai', {}).get('model', {}))
        self.personality = PersonalityConfig(**config_data.get('ai', {}).get('personality', {}))
        self.voice = VoiceConfig(
            stt_engine=config_data.get('voice', {}).get('stt', {}).get('engine', 'faster-whisper'),
            stt_model_size=config_data.get('voice', {}).get('stt', {}).get('model_size', 'base'),
            stt_language=config_data.get('voice', {}).get('stt', {}).get('language', 'en'),
            stt_device=config_data.get('voice', {}).get('stt', {}).get('device', 'cuda'),
            tts_engine=config_data.get('voice', {}).get('tts', {}).get('engine', 'coqui'),
            tts_voice_id=config_data.get('voice', {}).get('tts', {}).get('voice_id', 'default'),
            tts_speed=config_data.get('voice', {}).get('tts', {}).get('speed', 1.0),
            tts_pitch=config_data.get('voice', {}).get('tts', {}).get('pitch', 1.0)
        )
        self.twitch = TwitchConfig(**config_data.get('twitch', {}))
        self.vtube_studio = VTubeStudioConfig(**config_data.get('vtube_studio', {}))
        self.training = TrainingConfig(**config_data.get('training', {}))
        self.system = SystemConfig(**config_data.get('system', {}))
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        if config_path:
            return cls(Path(config_path))
        
        # Look for config in standard locations
        for path in ["config.yaml", "config.yml", "../config.yaml"]:
            p = Path(path)
            if p.exists():
                return cls(p)
        
        # Return default config
        return cls()