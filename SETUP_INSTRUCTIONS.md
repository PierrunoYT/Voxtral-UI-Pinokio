# Voxtral Pinokio Package Setup Instructions

## Package Structure

This Pinokio package provides a complete installation for Voxtral, Mistral AI's state-of-the-art audio model with advanced speech understanding capabilities. The package automatically installs all dependencies and sets up both the vLLM inference server and Gradio web interface.

### 1. Package Files ✅ Complete

The package includes these core files:
- `pinokio.js` - Main configuration with Voxtral branding
- `install.js` - Installation script (installs vLLM, Voxtral dependencies)
- `start.js` - Startup script with vLLM server and Gradio frontend
- `torch.js` - PyTorch installation with latest optimizations
- `update.js` - Update script
- `reset.js` - Reset script
- `link.js` - Deduplication script for disk space optimization
- `app.py` - Gradio frontend for Voxtral interaction
- `requirements.txt` - Python dependencies for Voxtral
- `icon.png` - Audio/AI themed project icon

### 2. Installation Process

The installation process:
1. Installs PyTorch with GPU support (CUDA 12.8, DirectML, ROCm)
2. Installs UV package manager for faster dependency installation
3. Installs vLLM with audio support from nightly builds
4. Installs Voxtral dependencies (gradio>=4.0.0, mistral-common[audio], transformers>=4.46.0)
5. Installs additional audio processing dependencies
6. Creates installation completion marker

### 3. Voxtral Model Integration

The package uses Mistral AI's Voxtral models:
- **Default**: `mistralai/Voxtral-Mini-3B-2507` (faster, lower memory)
- **Alternative**: `mistralai/Voxtral-Small-24B-2507` (better performance, more memory)

This ensures:
- State-of-the-art audio understanding capabilities
- Proper audio transcription and translation
- Direct Q&A interactions with audio content
- Multi-language support
- Automatic model downloading via vLLM

### 4. Distribution Files

For the Pinokio package, distribute these files:
- `pinokio.js` - Main configuration
- `install.js` - Installation script (installs vLLM + Voxtral)
- `start.js` - Startup script with vLLM server monitoring
- `torch.js` - PyTorch installation
- `update.js` - Update script
- `reset.js` - Reset script
- `link.js` - Deduplication script
- `app.py` - Gradio frontend application
- `requirements.txt` - Voxtral dependencies
- `icon.png` - Audio/AI themed project icon
- `README.md` - Voxtral documentation
- `PINOKIO_PACKAGE_README.md` - Package documentation
- `PACKAGE_VALIDATION.md` - Validation checklist
- `SETUP_INSTRUCTIONS.md` - This file

### 5. How It Works

1. User installs the Pinokio package (files above)
2. When they click "Install", it:
   - Installs PyTorch with platform-specific optimizations
   - Installs vLLM with audio support
   - Installs Voxtral dependencies using UV package manager
   - Sets up the Python environment
   - Creates installation completion marker
3. User can then start the application through Pinokio interface
4. The startup process launches:
   - vLLM server with Voxtral model on port 8000
   - Gradio web interface on port 7860
5. Users can upload audio files and interact with the Voxtral model

### 6. Key Features

- **vLLM Backend**: High-performance inference server for Voxtral
- **Fast Installation**: Uses UV package manager for lightning-fast dependency installation
- **GPU Optimization**: Supports NVIDIA CUDA, AMD DirectML/ROCm, and CPU fallback
- **Cross-Platform**: Windows, macOS, and Linux support
- **Advanced Features**: XFormers, Triton, and SageAttention optimizations
- **Audio Intelligence**: Speech understanding, transcription, translation, and Q&A
- **Multi-Modal Processing**: Advanced audio comprehension capabilities
- **Deduplication Support**: Optional disk space optimization

### 7. Technical Details

**PyTorch Installation:**
- Windows NVIDIA: CUDA 12.8 + XFormers + Triton + SageAttention
- Windows AMD: DirectML support
- Linux NVIDIA: CUDA 12.8 + XFormers + SageAttention
- Linux AMD: ROCm 6.2.4 support
- macOS: CPU + Metal acceleration
- CPU fallback: Optimized CPU-only installation

**Voxtral-Specific Dependencies:**
- vLLM with audio support (nightly builds)
- mistral-common[audio] (audio processing)
- gradio>=4.0.0 (modern audio interface)
- transformers>=4.46.0 (latest for audio models)
- accelerate (GPU acceleration)
- peft>=0.14.0 (parameter-efficient fine-tuning)
- huggingface-hub (model downloading)

**Audio Model Features:**
- **Models**: mistralai/Voxtral-Mini-3B-2507 / Voxtral-Small-24B-2507
- **Capabilities**: Speech understanding, transcription, translation, Q&A
- **Backend**: vLLM inference server with OpenAI-compatible API
- **Frontend**: Gradio web interface with audio upload and microphone support
- **Performance**: GPU acceleration with automatic model downloading

### 8. System Requirements

**Minimum Requirements:**
- **RAM**: 16GB (32GB+ recommended)
- **Storage**: 15GB free space for models and dependencies
- **GPU**: 9GB+ VRAM recommended (CPU fallback available)
- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **Python**: 3.9+ (installed automatically in virtual environment)
- **Audio**: Microphone or audio files for input

**Recommended for Optimal Performance:**
- **GPU**: NVIDIA RTX 4070 or better with 12GB+ VRAM
- **RAM**: 32GB or more
- **Storage**: SSD with 20GB+ free space
- **Internet**: Stable connection for model downloads (~10GB)
- **Audio**: High-quality microphone or audio files

This approach ensures a robust, up-to-date installation that leverages Mistral AI's latest audio intelligence technology with high-performance vLLM backend and always has access to the most current Voxtral capabilities.