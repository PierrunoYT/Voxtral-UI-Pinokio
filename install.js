module.exports = {
  requires: {
    bundle: "ai"
  },
  run: [
    // Install PyTorch first via shared torch.js. If requirements.txt ran first,
    // accelerate would pull CPU-only torch from PyPI (Windows), and uv would
    // then treat the unpinned CUDA install as already satisfied and skip it.
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",
          path: "app"
        }
      }
    },
    // Install core Python requirements on top of the GPU-specific torch.
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: "uv pip install -r requirements.txt"
      }
    },
    // Create installation completion marker
    {
      method: "fs.write",
      params: {
        path: "INSTALLATION_COMPLETE.txt",
        text: "Voxtral installation completed successfully.\n\nNext steps:\n1. Start the app using the Start button\n2. Open the web interface at the provided URL\n3. Begin interacting with Voxtral for audio understanding\n\nFeatures:\n- Voxtral Mini 3B / Small 24B audio-language models\n- Speech, sound, and music understanding\n- Audio transcription and translation\n- Direct audio Q&A interactions\n- Gradio web interface\n- GPU acceleration (if available)\n- Transformers backend (no vLLM required)\n\nFor support, check the README.md file.\n\nNote: The model is downloaded automatically on first use."
      }
    }
  ]
}
