module.exports = {
  run: [
    // Install UV package manager for faster installations
    {
      method: "shell.run",
      params: {
        venv: "env",
        message: "pip install uv"
      }
    },
    // Install basic requirements first (gradio, openai, etc.)
    {
      method: "shell.run",
      params: {
        venv: "env",
        message: "uv pip install -r requirements.txt"
      }
    },
    // Install mistral-common with audio support
    {
      method: "shell.run",
      params: {
        venv: "env",
        message: "pip install --upgrade \"mistral-common[audio]\""
      }
    },
    // Install PyTorch with GPU support before vLLM to ensure compatibility
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",
          xformers: true,
          triton: true,
          sageattention: true,
          force_reinstall: false
        }
      }
    },
    // Install vLLM from PyPI (stable version) for Windows compatibility
    {
      method: "shell.run",
      params: {
        venv: "env",
        message: "pip install vllm"
      }
    },
    // Create installation completion marker
    {
      method: "fs.write",
      params: {
        path: "INSTALLATION_COMPLETE.txt",
        text: "Voxtral installation completed successfully.\n\nNext steps:\n1. Start the vLLM server using the Start button\n2. Open the web interface at the provided URL\n3. Begin interacting with Voxtral for audio understanding\n\nFeatures:\n- Voxtral Large Audio-Language Model\n- Speech, sound, and music understanding\n- Audio transcription and translation\n- Direct audio Q&A interactions\n- Gradio web interface\n- GPU acceleration (if available)\n- PyTorch with CUDA support (if NVIDIA GPU detected)\n\nFor support, check the README.md file.\n\nNote: The vLLM server will download the Voxtral model on first use.\n\nIMPORTANT: vLLM may have limited Windows support. For best results, use Linux or WSL."
      }
    }
  ]
}
