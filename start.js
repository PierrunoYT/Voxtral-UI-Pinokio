module.exports = {
  daemon: true,
  run: [
    // Start Gradio app. No GRADIO_SERVER_PORT is set on purpose: Gradio scans
    // for a free port itself, and the URL it prints is captured below. Setting
    // it to an unresolved template variable would export an empty string.
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        env: {
          GRADIO_SERVER_NAME: "127.0.0.1"
        },
        message: "python app.py",
        on: [{
          // Capture the local URL Gradio prints, e.g. "Running on local URL:  http://127.0.0.1:7860"
          event: "/(http:\/\/[0-9.:]+)/",
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
