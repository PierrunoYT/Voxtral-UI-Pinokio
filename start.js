module.exports = {
  daemon: true,
  run: [
    // Start vLLM server with Voxtral model
    {
      method: "shell.run",
      params: {
        venv: "env",
        env: {
          CUDA_VISIBLE_DEVICES: "0"
        },
        message: "vllm serve mistralai/Voxtral-Mini-3B-2507 --tokenizer_mode mistral --config_format mistral --load_format mistral --host 127.0.0.1 --port 8000",
        on: [{
          // Wait for vLLM server to start
          event: "/INFO.*Application startup complete/",
          done: true
        }, {
          // Alternative startup pattern
          event: "/INFO.*Uvicorn running on/",
          done: true
        }, {
          // Fallback pattern
          event: "/Running on.*http:\/\/127\.0\.0\.1:8000/",
          done: true
        }]
      }
    },
    // Wait a moment for server to be fully ready
    {
      method: "shell.run",
      params: {
        message: "timeout 5 2>nul || sleep 5"
      }
    },
    // Start Gradio frontend
    {
      method: "shell.run",
      params: {
        venv: "env",
        env: {
          GRADIO_SERVER_PORT: "7860",
          GRADIO_SERVER_NAME: "0.0.0.0"
        },
        message: "python app.py",
        on: [{
          // Wait for Gradio server to start
          event: "/Running on local URL:.*http:\/\/[0-9.:]+:7860/",
          done: true
        }, {
          // Alternative Gradio startup pattern
          event: "/Running on public URL:.*https:\/\/[a-zA-Z0-9.-]+\.gradio\.live/",
          done: true
        }, {
          // Fallback pattern for localhost
          event: "/http:\/\/localhost:7860/",
          done: true
        }, {
          // Generic Gradio pattern
          event: "/Gradio app running/",
          done: true
        }]
      }
    },
    // Set the local variable 'url' for the web interface
    {
      method: "local.set",
      params: {
        url: "http://localhost:7860"
      }
    }
  ]
}
