module.exports = {
  daemon: true,
  run: [
    // Start Gradio frontend with in-process Transformers backend
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
