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
    // Install core Python requirements
    {
      method: "shell.run",
      params: {
        venv: "env",
        message: "uv pip install -r requirements.txt"
      }
    },
    // Install PyTorch with optional GPU support
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",
          xformers: true,
          triton: true,
          sageattention: true,
          force_reinstall: true
        }
      }
    },
    // Ensure a recent Transformers stack with Voxtral support
    {
      method: "shell.run",
      params: {
        venv: "env",
        message: "uv pip install --upgrade \"transformers>=4.56.0\" \"accelerate>=0.34.0\" safetensors soundfile sentencepiece librosa"
      }
    },
    // Create installation completion marker
    {
      method: "fs.write",
      params: {
        path: "INSTALLATION_COMPLETE.txt",
        text: "Voxtral installation completed successfully.\n\nNext steps:\n1. Start the app using the Start button\n2. Open the web interface at the provided URL\n3. Begin interacting with Voxtral for audio understanding\n\nFeatures:\n- Voxtral Large Audio-Language Model\n- Speech, sound, and music understanding\n- Audio transcription and translation\n- Direct audio Q&A interactions\n- Gradio web interface\n- GPU acceleration (if available)\n- Transformers backend (no vLLM required)\n\nFor support, check the README.md file.\n\nNote: The model is downloaded automatically on first use."
      }
    }
  ]
}
