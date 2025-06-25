"""
Example usage of the configuration system.
"""
import os
from src.config import Config, get_config


def basic_usage():
    """Basic configuration usage."""
    # Load configuration from default locations
    config = Config.load()
    
    # Access configuration values
    print(f"AI Model: {config.ai.model.name}")
    print(f"Device: {config.ai.model.device}")
    print(f"Personality: {config.ai.personality.name}")
    print(f"TTS Engine: {config.voice.tts.engine}")
    
    # Validate required fields
    errors = config.validate_required_fields()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")


def environment_override():
    """Demonstrate environment variable overrides."""
    # Set environment variables
    os.environ['TWITCH_USERNAME'] = 'my_stream'
    os.environ['TWITCH_OAUTH_TOKEN'] = 'oauth:abc123'
    os.environ['SYSTEM_LOG_LEVEL'] = 'DEBUG'
    
    # Load configuration - env vars will override YAML
    config = Config.load()
    
    print(f"Twitch Username: {config.twitch.username}")
    print(f"Log Level: {config.system.log_level}")


def hot_reload_example():
    """Demonstrate hot-reload functionality."""
    # Load configuration
    config = Config.load("config.yaml")
    
    # Define callback for config changes
    def on_config_reload(new_config):
        print(f"Configuration reloaded!")
        print(f"New AI model: {new_config.ai.model.name}")
    
    # Enable hot-reload
    config.enable_hot_reload(on_config_reload)
    
    print("Hot-reload enabled. Edit config.yaml to see changes.")
    print("Press Ctrl+C to exit...")
    
    try:
        # Keep running to watch for changes
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        config.disable_hot_reload()
        print("Hot-reload disabled.")


def custom_config_location():
    """Load configuration from custom location."""
    # Load from specific file
    config = Config.load("/path/to/custom/config.yaml")
    
    # Or search multiple locations
    for path in ["config.yaml", "config/app.yaml", "../config.yaml"]:
        try:
            config = Config.load(path)
            print(f"Loaded configuration from: {path}")
            break
        except:
            continue


def save_configuration():
    """Save configuration to file."""
    # Create configuration
    config = Config()
    
    # Modify values
    config.ai.model.name = "llama-2-7b"
    config.ai.personality.name = "Sakura"
    config.ai.personality.traits = ["cheerful", "energetic", "helpful"]
    config.twitch.username = "my_vtuber_stream"
    
    # Save to file
    config.save("my_config.yaml")
    print("Configuration saved to my_config.yaml")


def global_config_usage():
    """Use global configuration instance."""
    # Get global config (singleton)
    config = get_config()
    
    print(f"Global config AI model: {config.ai.model.name}")
    
    # Access from anywhere in the application
    from src.config import get_config
    config2 = get_config()
    assert config is config2  # Same instance


def validation_example():
    """Demonstrate configuration validation."""
    from pydantic import ValidationError
    
    try:
        # This will fail validation
        config = Config()
        config.ai.model.temperature = 3.0  # Out of range
    except ValidationError as e:
        print(f"Validation error: {e}")
    
    # Validate specific fields
    config = Config()
    config.twitch.username = "streamer"
    # Missing oauth_token
    
    errors = config.validate_required_fields()
    if errors:
        print("Missing required fields:")
        for error in errors:
            print(f"  - {error}")


if __name__ == "__main__":
    print("=== Basic Usage ===")
    basic_usage()
    
    print("\n=== Environment Overrides ===")
    environment_override()
    
    print("\n=== Validation Example ===")
    validation_example()
    
    # Uncomment to test hot-reload
    # print("\n=== Hot Reload ===")
    # hot_reload_example()