module.exports = {
  daemon: true,
  run: [
    // Start Gradio app (let Gradio pick the port; capture printed URL).
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        env: {
          GRADIO_SERVER_NAME: "127.0.0.1",
          GRADIO_SERVER_PORT: "{{port}}"
        },
        message: "python app.py",
        on: [{
          // Capture the local URL Gradio prints, e.g. "Running on local URL:  http://127.0.0.1:7860"
          event: "/(http:\\/\\/[0-9.:]+)/",
          done: true
        }]
      }
    },
    // Expose the captured URL to pinokio.js so the "Open Web UI" tab shows up.
    {
      method: "local.set",
      params: {
        url: "{{input.event[1]}}"
      }
    }
  ]
}
