#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path


def detect_gpu():
    """Detect available GPU and return type"""
    try:
        # Check for NVIDIA
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'cuda'
    except FileNotFoundError:
        pass
    
    try:
        # Check for AMD
        result = subprocess.run(['rocm-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'rocm'
    except FileNotFoundError:
        pass
    
    # Check for Apple Silicon
    if sys.platform == 'darwin':
        result = subprocess.run(['sysctl', '-n', 'hw.optional.arm64'], capture_output=True, text=True)
        if result.stdout.strip() == '1':
            return 'metal'
    
    return 'cpu'


def setup_environment():
    """Set up the AI VTuber environment"""
    print("🤖 AI VTuber Companion Setup")
    print("=" * 50)
    
    # Detect GPU
    gpu_type = detect_gpu()
    print(f"✓ Detected GPU type: {gpu_type}")
    
    # Create necessary directories
    dirs = [
        'models/base',
        'models/fine-tuned',
        'models/voices',
        'data/conversations',
        'data/training',
        'logs'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✓ Created directory structure")
    
    # Create .gitkeep files
    for dir_path in dirs:
        (Path(dir_path) / '.gitkeep').touch()
    
    # Install appropriate requirements
    print("\n📦 Installing dependencies...")
    if gpu_type == 'rocm':
        print("Installing PyTorch for AMD ROCm...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            'torch', 'torchvision', 'torchaudio',
            '--index-url', 'https://download.pytorch.org/whl/rocm5.7'
        ])
        req_file = 'requirements-rocm.txt'
    else:
        req_file = 'requirements.txt'
    
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_file])
    
    # Create config from example
    if not Path('config.yaml').exists() and Path('config.example.yaml').exists():
        import shutil
        shutil.copy('config.example.yaml', 'config.yaml')
        print("✓ Created config.yaml from example")
    
    # Download a small model for testing
    print("\n🤖 Downloading test model...")
    print("Would you like to download a small test model? (y/n): ", end='')
    if input().lower() == 'y':
        download_test_model(gpu_type)
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit config.yaml with your API keys and preferences")
    print("2. Download your preferred AI model")
    print("3. Configure VTube Studio connection")
    print("4. Run: python src/main.py")


def download_test_model(gpu_type):
    """Download a small test model"""
    try:
        from huggingface_hub import hf_hub_download
        
        if gpu_type in ['cuda', 'rocm', 'metal']:
            # Download quantized Phi-2 for testing
            print("Downloading Phi-2 GGUF (2.7B model)...")
            hf_hub_download(
                repo_id="TheBloke/phi-2-GGUF",
                filename="phi-2.Q4_K_M.gguf",
                local_dir="models/base",
                local_dir_use_symlinks=False
            )
        else:
            print("CPU mode - skipping model download to save space")
            print("You can manually download models later")
            
    except ImportError:
        print("Please install huggingface-hub to download models:")
        print("pip install huggingface-hub")


if __name__ == "__main__":
    setup_environment()