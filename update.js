module.exports = {
  run: [
    // Pull the latest launcher + app code.
    {
      method: "shell.run",
      params: {
        message: "git pull"
      }
    },
    // Reinstall Python requirements so dependency changes from the pull land
    // in the existing venv instead of only taking effect after a full Reset.
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: "uv pip install -r requirements.txt"
      }
    }
  ]
}
