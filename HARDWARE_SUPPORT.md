# Hardware Support Guide

## GPU Compatibility

### NVIDIA GPUs (CUDA)
- **Primary Support**: CUDA 11.8+
- **Frameworks**: PyTorch with CUDA
- **Optimization**: TensorRT, Flash Attention

### AMD GPUs (ROCm)
- **Supported Cards**: 
  - RX 7900 XTX/XT
  - RX 6900 XT/6800 XT
  - MI250/MI210 (datacenter)
- **ROCm Version**: 5.6+
- **Frameworks**: PyTorch with ROCm support

### Intel GPUs (Coming Soon)
- **Arc Series**: Limited support via IPEX
- **Framework**: PyTorch with Intel Extension

## AMD GPU Setup

### 1. Install ROCm
```bash
# Ubuntu 22.04
wget https://repo.radeon.com/amdgpu-install/latest/ubuntu/jammy/amdgpu-install_5.7.50700-1_all.deb
sudo apt install ./amdgpu-install_5.7.50700-1_all.deb
sudo amdgpu-install --rocm
```

### 2. Install PyTorch for ROCm
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

### 3. Environment Variables
```bash
export HSA_OVERRIDE_GFX_VERSION=10.3.0  # For RX 7900 XTX
export PYTORCH_HIP_ALLOC_CONF=garbage_collection_threshold:0.9,max_split_size_mb:512
```

## Cross-Platform Model Support

### Inference Engines
1. **llama.cpp** - Works on all platforms
   - CPU, CUDA, ROCm, Metal
   - Excellent quantization support
   - Low memory usage

2. **ONNX Runtime** - Universal compatibility
   - Supports all major GPUs
   - Good for deployment

3. **MLX** - Apple Silicon
   - Optimized for M1/M2/M3

### Recommended Models by Platform

#### AMD GPUs
- **Mistral 7B GGUF Q4**: 4GB VRAM
- **LLaMA 2 7B GGUF Q5**: 5GB VRAM
- **Phi-2 GGUF**: 2GB VRAM

#### Low VRAM Solutions
- Use CPU offloading
- Implement model sharding
- Utilize system RAM

## Performance Tips

### AMD Specific
```python
# Force ROCm backend
import torch
torch.cuda.is_available()  # Should return True with ROCm

# Memory optimization
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.deterministic = False
```

### Universal Optimizations
- Use mixed precision (fp16/bf16)
- Enable memory efficient attention
- Implement gradient checkpointing
- Use quantized models (4-bit/8-bit)