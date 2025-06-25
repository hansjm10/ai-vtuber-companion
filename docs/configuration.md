# Configuration System Documentation

The AI VTuber Companion uses a robust configuration system that supports YAML files, environment variable overrides, validation, and hot-reload capabilities.

## Features

- **YAML Configuration**: Easy-to-read configuration files
- **Environment Variable Overrides**: Override any config value via environment variables
- **Validation**: Built-in validation for all configuration fields
- **Default Values**: Sensible defaults for all optional fields
- **Hot-Reload**: Automatically reload configuration when files change
- **Schema Versioning**: Configuration schema version tracking for compatibility
- **Multiple File Locations**: Searches standard locations for config files

## Configuration Structure

```yaml
schema_version: "1.0.0"  # Required for version compatibility

ai:
  model:
    type: "local"          # local or api
    name: "mistral-7b-instruct"
    quantization: "Q4_K_M"
    max_tokens: 200
    temperature: 0.8
    device: "cuda"         # cuda, rocm, cpu, metal
    
  personality:
    name: "Aiko"
    traits:
      - cheerful
      - curious
      - supportive
    backstory: "A digital entity learning about human culture"
    speech_style: "casual and friendly"

voice:
  stt:
    engine: "faster-whisper"
    model_size: "base"
    language: "en"
    device: "cuda"
    
  tts:
    engine: "coqui"
    voice_id: "default"
    speed: 1.0
    pitch: 1.0

twitch:
  username: ""
  oauth_token: ""
  client_id: ""
  client_secret: ""
  channel: ""
  commands:
    prefix: "!"
    enabled:
      - hello
      - mood
      - story

vtube_studio:
  enabled: true
  host: "localhost"
  port: 8001
  auth_token: ""
  model_id: ""
  expressions:
    happy: "expression_1"
    sad: "expression_2"

training:
  auto_collect: true
  min_interactions: 100
  batch_size: 32
  learning_rate: 1e-5
  feedback:
    positive_reactions: ["PogChamp", "Pog", "LUL", "KEKW"]
    negative_reactions: ["ResidentSleeper", "NotLikeThis"]

system:
  log_level: "INFO"
  data_retention_days: 30
  backup_interval_hours: 24
  performance:
    response_timeout_ms: 5000
    max_concurrent_requests: 10
    cache_responses: true
```

## Usage

### Basic Usage

```python
from src.config import Config, get_config

# Load configuration
config = Config.load()  # Searches standard locations
# or
config = Config.load("path/to/config.yaml")  # Specific file

# Access values
print(config.ai.model.name)
print(config.twitch.username)

# Global singleton
config = get_config()  # Get global instance
```

### Environment Variable Overrides

Environment variables override YAML values. The format is `PREFIX_FIELD`:

```bash
# Twitch configuration
export TWITCH_USERNAME="my_stream"
export TWITCH_OAUTH_TOKEN="oauth:abc123"
export TWITCH_CLIENT_ID="client123"

# System configuration
export SYSTEM_LOG_LEVEL="DEBUG"

# VTube Studio
export VTUBE_AUTH_TOKEN="auth123"
export VTUBE_PORT="9000"

# Training
export TRAINING_BATCH_SIZE="64"
```

### Configuration File Locations

The system searches for configuration files in this order:

1. `config.yaml`
2. `config.yml`
3. `config/config.yaml`
4. `config/config.yml`
5. `../config.yaml`
6. `../config.yml`
7. `~/.ai-vtuber/config.yaml`
8. `/etc/ai-vtuber/config.yaml`

### Hot-Reload

Enable automatic configuration reload when files change:

```python
# Enable hot-reload
def on_config_change(new_config):
    print("Configuration reloaded!")
    # Update your application state

config.enable_hot_reload(on_config_change)

# Later, disable if needed
config.disable_hot_reload()
```

### Validation

The configuration system provides built-in validation:

```python
# Validate required fields
errors = config.validate_required_fields()
if errors:
    for error in errors:
        print(f"Configuration error: {error}")
```

Common validation rules:
- Twitch OAuth token required when username is set
- VTube Studio auth token required when enabled
- Numeric fields have min/max ranges
- Enum fields have allowed values

### Saving Configuration

Save configuration back to file:

```python
# Modify configuration
config.ai.model.name = "llama-2-7b"
config.twitch.username = "my_vtuber"

# Save to file
config.save()  # Save to original location
# or
config.save("new_config.yaml")  # Save to new file
```

## Migration Guide

If you're upgrading from the old configuration system:

1. Add `schema_version: "1.0.0"` to your config file
2. Update imports from `from src.config import Config` 
3. Environment variables now use prefixes: `TWITCH_`, `VTUBE_`, `SYSTEM_`, `TRAINING_`
4. Access nested config with dot notation: `config.ai.model.name`

## Troubleshooting

### Missing Dependencies

Install required packages:
```bash
pip install pydantic==2.5.0 pydantic-settings==2.1.0 watchdog==3.0.0 pyyaml
```

### Configuration Not Loading

1. Check file exists in standard locations
2. Verify YAML syntax is valid
3. Check schema_version is correct
4. Review validation errors

### Environment Variables Not Working

1. Ensure correct prefix (TWITCH_, SYSTEM_, etc.)
2. Variable names are uppercase
3. Export variables before running application

## Best Practices

1. **Use Environment Variables for Secrets**: Never commit OAuth tokens or API keys
2. **Version Control**: Commit `config.example.yaml`, not actual config files
3. **Validation**: Always check validation errors on startup
4. **Hot-Reload**: Use for development, disable in production
5. **Schema Version**: Always include schema_version in config files