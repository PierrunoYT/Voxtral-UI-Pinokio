# Voxtral UI Pinokio

A complete Pinokio installation package for running Mistral AI's Voxtral locally with a beautiful Gradio web interface.

## 🚀 Features

- **🎵 Voxtral Model**: Mistral AI's state-of-the-art audio model with advanced speech understanding capabilities
- **🔊 Multi-Modal Understanding**: Process speech, audio transcription, translation, and direct Q&A interactions
- **🧠 Audio Intelligence**: Advanced audio comprehension and analysis capabilities
- **💬 Gradio Interface**: Clean, professional web interface for audio interaction
- **⚡ GPU Acceleration**: Automatic CUDA support when available with vLLM backend
- **🔒 Complete Privacy**: Runs entirely offline, no data sent externally
- **🌐 Cross-Platform**: Windows, macOS, and Linux support

## 📋 Requirements

- **RAM**: 16GB+ (32GB+ recommended for optimal performance)
- **Storage**: ~10GB for model files (downloaded automatically)
- **GPU**: Highly recommended (9GB+ VRAM for best performance)
- **OS**: Windows 10/11, macOS, or Linux
- **Audio**: Microphone or audio files for input

## 🛠️ Installation

### Via Pinokio (Recommended)

1. Install [Pinokio](https://pinokio.computer/)
2. Open Pinokio and navigate to "Discover"
3. Search for "Voxtral UI" or paste this repository URL
4. Click "Install" and wait for the installation to complete
5. Click "Start" to launch Voxtral
6. Open the web interface when it becomes available

### Manual Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/Voxtral-UI-Pinokio.git
   cd Voxtral-UI-Pinokio
   ```

2. Install Pinokio and run the installation script through the Pinokio interface

## 🎯 Usage

1. **Start the Application**: Click "Start" in Pinokio (this starts both vLLM server and Gradio interface)
2. **Open Web Interface**: Click "Open Web UI" when available
3. **Audio Input**: Upload audio files or use microphone input
4. **Interact**: Ask questions about the audio content
5. **Advanced Features**:
   - Audio transcription
   - Audio translation
   - Direct Q&A with audio content
   - Multi-language support

## 🏗️ Project Structure

```
Voxtral-UI-Pinokio/
├── pinokio.js              # Main Pinokio configuration
├── install.js              # Installation workflow
├── start.js                # Application startup (vLLM + Gradio)
├── update.js               # Update workflow
├── reset.js                # Reset/cleanup workflow
├── link.js                 # Deduplication workflow
├── torch.js                # PyTorch installation
├── app.py                  # Main Gradio application
├── requirements.txt        # Python dependencies
├── icon.png                # Project icon
├── README.md               # This file
└── env/                    # Created during installation
    └── ...                 # Python virtual environment
```

## 🔧 Technical Details

### Model Information
- **Model**: mistralai/Voxtral-Mini-3B-2507 (default)
- **Alternative**: mistralai/Voxtral-Small-24B-2507 (for better performance)
- **Type**: Large Audio-Language Model
- **Capabilities**: Speech understanding, transcription, translation, Q&A

### Backend Architecture
- **vLLM Server**: High-performance inference server running on port 8000
- **Gradio Frontend**: Web interface running on port 7860
- **Communication**: OpenAI-compatible API between frontend and backend

### Dependencies
- PyTorch with CUDA support
- vLLM with audio support
- Gradio 4.0.0+
- mistral-common with audio support
- Transformers, Accelerate, PEFT

### GPU Support Matrix

| Platform | NVIDIA | AMD | CPU |
|----------|--------|-----|-----|
| Windows | CUDA 12.8 + XFormers + Triton | DirectML | CPU-only |
| Linux | CUDA 12.8 + XFormers + SageAttention | ROCm 6.2.4 | CPU-only |
| macOS | N/A | N/A | CPU + Metal |

## 🚨 Troubleshooting

### Common Issues

**Slow responses on CPU**
- This is normal - CPU inference is much slower than GPU
- Audio models are particularly compute-intensive
- Consider using a GPU with 9GB+ VRAM for optimal performance

**Out of memory errors**
- Audio models require significant memory
- Close other applications to free RAM/VRAM
- Use shorter audio clips
- Consider CPU mode if GPU memory is insufficient

**Model download fails**
- Check internet connection
- Model files download automatically on first use via vLLM
- Ensure sufficient disk space (~10GB)

**vLLM server fails to start**
- Check if port 8000 is available
- Verify CUDA installation for GPU usage
- Check vLLM logs in the terminal

**Audio upload errors**
- Supported formats: WAV, MP3, FLAC, OGG, M4A
- Try converting to WAV format if issues persist
- Check file size limitations

### Performance Tips

- **GPU Users**: Use NVIDIA GPU with 9GB+ VRAM for best experience
- **CPU Users**: Use shorter audio clips and be patient with processing
- **Memory**: Close unnecessary applications during use
- **Audio Quality**: Higher quality audio may provide better results

## 🔄 Updates

The package includes an automatic update system:

1. Click "Update" in the Pinokio interface
2. Wait for dependencies and model updates to complete
3. Restart the application to use the latest version

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

1. Fork this repository
2. Make your changes to the Pinokio scripts or Gradio interface
3. Test thoroughly on your target platform
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Mistral AI](https://mistral.ai/) for the Voxtral model
- [vLLM](https://github.com/vllm-project/vllm) for the high-performance inference backend
- [Gradio](https://gradio.app/) for the web interface framework
- [Pinokio](https://pinokio.computer/) for the package management system

## 📞 Support

For issues related to:
- **Voxtral Model**: Visit [Mistral AI documentation](https://docs.mistral.ai/)
- **Installation Problems**: Use the Reset option and try reinstalling
- **Performance Issues**: Check system requirements and GPU compatibility
- **Audio Processing**: Ensure supported audio formats and sufficient memory