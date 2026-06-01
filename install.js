module.exports = {
  requires: {
    bundle: "ai"
  },
  run: [
    // Install core Python requirements
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: "uv pip install -r requirements.txt"
      }
    },
    // Install PyTorch (+ optional GPU stack) via shared torch.js
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",
          path: "app",
          xformers: true,
          triton: true,
          sageattention: true
        }
      }
    },
    // Ensure a recent Transformers stack with Voxtral support
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
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
