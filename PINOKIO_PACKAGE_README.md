# Voxtral - Pinokio Package

This directory contains a complete Pinokio installer package for Voxtral, Mistral AI's state-of-the-art audio model with a beautiful Gradio web interface for audio understanding and interaction.

## Package Contents

### Core Pinokio Files
- **`pinokio.js`** - Main configuration and dynamic menu system
- **`install.js`** - Complete installation workflow with vLLM and Voxtral setup
- **`start.js`** - Application startup script with vLLM server and Gradio frontend
- **`torch.js`** - Cross-platform PyTorch installation with latest optimizations
- **`update.js`** - Update workflow for package and dependencies
- **`reset.js`** - Clean removal and reset functionality
- **`link.js`** - Deduplication workflow to save disk space
- **`app.py`** - Gradio frontend application for Voxtral interaction
- **`requirements.txt`** - Python dependencies for Voxtral
- **`icon.png`** - Project icon (512x512px audio/AI design)

### Additional Files
- **`PINOKIO_SCRIPT_GUIDE.md`** - Comprehensive guide for creating Pinokio scripts
- **`PINOKIO_PACKAGE_README.md`** - This documentation file
- **`PACKAGE_VALIDATION.md`** - Package validation and testing documentation
- **`SETUP_INSTRUCTIONS.md`** - Detailed setup and usage instructions

## Installation Process

The Pinokio installer will:

1. **Install PyTorch**: Platform and GPU-specific PyTorch installation with CUDA 12.8
2. **Install vLLM**: High-performance inference server with audio support
3. **Install Dependencies**: Installs gradio, mistral-common[audio], transformers, and supporting packages
4. **Setup Environment**: Creates virtual environment with all dependencies
5. **Model Download**: Voxtral models download automatically via vLLM on first use
6. **Verification**: Tests all components for proper installation

## Features

### Smart Menu System
- **Dynamic State Detection**: Shows appropriate options based on installation status
- **Running Process Awareness**: Detects if installation/startup is in progress
- **Direct Web Access**: "Open Web UI" button when application is running
- **Terminal Access**: View logs and output during operation
- **Deduplication Support**: Save disk space with library file deduplication

### Cross-Platform Support
- **Windows**: Full support with CUDA/DirectML/CPU modes
- **macOS**: Native support for Intel and Apple Silicon with Metal acceleration
- **Linux**: Ubuntu/Debian and other distributions with CUDA/ROCm support

### GPU Optimization
- **NVIDIA CUDA**: Automatic detection and installation of CUDA 12.8 with XFormers
- **AMD Support**: DirectML on Windows, ROCm 6.2.4 on Linux
- **CPU Fallback**: Graceful fallback to CPU-only mode with optimizations
- **Memory Management**: Automatic FP16/FP32 precision selection
- **Advanced Optimizations**: Optional Triton (Windows) and SageAttention support

### Audio Intelligence Features
- **Voxtral Model**: Mistral AI's audio model for advanced speech understanding
- **Multi-Modal Processing**: Speech, audio transcription, translation, and Q&A
- **Audio Upload**: Support for various audio formats (WAV, MP3, FLAC, OGG, M4A)
- **Microphone Input**: Real-time audio recording and processing
- **Multi-Language**: Support for multiple languages and translation
- **vLLM Backend**: High-performance inference with OpenAI-compatible API
- **Gradio Frontend**: Professional web interface for audio interaction

### Robust Installation
- **Error Handling**: Graceful handling of installation failures
- **Dependency Management**: Proper virtual environment isolation
- **Update Support**: Easy updates without full reinstallation
- **Clean Reset**: Complete removal for fresh starts
- **UV Package Manager**: Lightning-fast dependency installation
- **Deduplication**: Optional disk space optimization

## Usage Instructions

### For End Users
1. Copy this entire directory to your Pinokio packages folder
2. Launch Pinokio and find "Voxtral" in your packages
3. Click "Install" to begin the installation process
4. After installation, click "Start" to launch the application (starts vLLM server + Gradio)
5. Click "Open Web UI" to access the Gradio interface
6. Upload audio files or use microphone input to interact with Voxtral

### For Developers
1. Ensure all source files are in the same directory as the Pinokio scripts
2. Test the installation process in a clean environment
3. Verify cross-platform compatibility
4. Update version numbers in `pinokio.js` as needed

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **RAM**: 16GB (32GB+ recommended)
- **Storage**: 20GB free space
- **Python**: 3.9+ (installed automatically in virtual environment)

### Recommended for Optimal Performance
- **GPU**: NVIDIA RTX 4070 or better with 12GB+ VRAM
- **RAM**: 32GB or more
- **Storage**: SSD with 25GB+ free space
- **Internet**: Stable connection for model downloads (~10GB)
- **Audio**: Microphone or audio files for input

## Model Information

The application uses Mistral AI's Voxtral models:
- **Default Model**: mistralai/Voxtral-Mini-3B-2507
- **Alternative**: mistralai/Voxtral-Small-24B-2507 (better performance, more memory)
- **Type**: Large Audio-Language Model
- **Capabilities**: Speech understanding, transcription, translation, Q&A
- **Backend**: vLLM inference server
- **Download**: Automatic during first use (~10GB)

## Troubleshooting

### Common Issues
1. **Installation Fails**: Check internet connection and disk space (20GB+ required)
2. **PyTorch Issues**: Verify CUDA compatibility or use CPU mode
3. **vLLM Server Issues**: Check port 8000 availability and GPU compatibility
4. **Model Download Fails**: Check internet connection, large model download required
5. **Memory Issues**: Use shorter audio clips or consider more RAM/VRAM
6. **Audio Upload Errors**: Check supported formats (WAV, MP3, FLAC, etc.)

### Debug Information
- Installation logs are available in Pinokio terminal
- Application logs shown during startup
- Error messages include helpful troubleshooting hints
- Reset option available for clean reinstallation

## Technical Details

### Virtual Environment
- Isolated Python environment in `env/`
- All dependencies installed within virtual environment
- No conflicts with system Python installation

### Model Management
- Voxtral models downloaded automatically during first use via vLLM
- Cached locally in vLLM's model cache
- Approximately 10GB download during setup
- Uses vLLM for high-performance inference

### Port Management
- vLLM server runs on port 8000
- Gradio frontend runs on port 7860
- Automatic port detection and assignment
- Accessible via localhost and network interfaces

### GPU Support Matrix

| Platform | NVIDIA | AMD | CPU |
|----------|--------|-----|-----|
| Windows | CUDA 12.8 + XFormers + Triton | DirectML | CPU-only |
| Linux | CUDA 12.8 + XFormers + SageAttention | ROCm 6.2.4 | CPU-only |
| macOS | N/A | N/A | CPU + Metal |

## Version History

- **v1.0.0**: Initial Pinokio package release
  - Complete installation workflow for Voxtral
  - Cross-platform PyTorch support with latest optimizations
  - Dynamic menu system with deduplication support
  - Professional Gradio interface for audio interaction
  - vLLM backend for high-performance inference
  - Advanced audio model monitoring and startup detection

## Support

For issues related to:
- **Pinokio Package**: Check this documentation and Pinokio logs
- **Voxtral Model**: Visit [Mistral AI documentation](https://docs.mistral.ai/)
- **Installation Problems**: Use the Reset option and try reinstalling
- **Performance Issues**: Check system requirements and GPU compatibility
- **Audio Processing**: Ensure supported audio formats and sufficient memory
- **vLLM Issues**: Check vLLM documentation and server logs

## License

This package is provided under the MIT License. The Voxtral model is subject to Mistral AI's licensing terms.