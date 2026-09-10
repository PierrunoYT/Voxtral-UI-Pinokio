# Voxtral UI (Pinokio)

Run Mistral AI's [Voxtral](https://mistral.ai/) audio-language model locally through a Gradio web
interface, packaged as a one-click [Pinokio](https://pinokio.computer/) app. Uses the Hugging Face
Transformers backend directly — no vLLM or external inference server required.

## Features

- Local, offline inference with Mistral's Voxtral models
- Audio Q&A, transcription, and translation from a simple web UI
- Automatic GPU detection (CUDA) with CPU fallback
- Automatic Whisper fallback if Voxtral's chat-template path produces garbled output
- Cross-platform Pinokio scripts (Windows, Linux, macOS) with GPU-specific PyTorch installs

## Requirements

- **RAM**: 16GB+ (32GB+ recommended)
- **GPU**: Recommended, 9GB+ VRAM for Voxtral-Mini-3B. Voxtral-Small-24B requires a GPU — it
  is not practical to run on CPU.
- **Storage**: ~10GB for Voxtral-Mini-3B, ~55GB for Voxtral-Small-24B (downloaded
  automatically on first use, into the Hugging Face cache)
- **OS**: Windows 10/11, macOS, or Linux

## Installation

1. Install [Pinokio](https://pinokio.computer/)
2. In Pinokio, open **Discover** and add this repository, or paste the repo URL directly
3. Click **Install** and wait for setup to finish
4. Click **Start**, then **Open Web UI**

## Usage

1. Upload an audio file (or record from a microphone)
2. Pick a model (Voxtral-Mini-3B by default; Voxtral-Small-24B for higher quality, GPU only)
3. Enter a question or instruction about the audio
4. Click **Generate** to run inference

Models are downloaded and loaded lazily on first use, not at app startup.

## Project Structure

```
Voxtral-UI-Pinokio/
├── pinokio.js       # Menu/UI state machine
├── pinokio.json     # Package metadata
├── install.js       # Installs Python deps + PyTorch
├── start.js         # Launches the Gradio app (daemon)
├── update.js        # git pull + dependency refresh
├── reset.js         # Removes the venv + install marker
├── link.js          # Deduplicates shared venv files
├── torch.js         # Platform/GPU-specific PyTorch install logic
├── icon.png
└── app/
    ├── app.py           # Gradio + Transformers Voxtral inference
    └── requirements.txt
```

## Configuration

The app reads these optional environment variables at startup:

| Variable | Default | Purpose |
| --- | --- | --- |
| `VOXTRAL_MODEL_ID` | `mistralai/Voxtral-Mini-3B-2507` | Model preselected in the dropdown |
| `VOXTRAL_MAX_NEW_TOKENS` | `384` | Generation length cap |
| `GRADIO_SERVER_NAME` | `127.0.0.1` | Bind address |
| `GRADIO_SERVER_PORT` | auto | Fixed port; unset lets Gradio pick a free one |

## Troubleshooting

**Chat template errors / garbled output** — Some Voxtral + Transformers version combinations hit
`Can't compile non template nodes` or produce repeated `[TOOL_CALLS]` tokens. The app already
falls back automatically (transcription-request API, then a direct processor call, then a Whisper
ASR fallback) — if all of those fail, try updating dependencies via Pinokio's **Update** button.

**Out of memory** — Use a shorter audio clip, switch to Voxtral-Mini-3B, or free up VRAM/RAM by
closing other applications.

**`operator torchvision::nms does not exist` or similar torch/torchvision errors** — Run **Reset**
then **Install** again in Pinokio to reinstall a matching PyTorch stack.

**Slow responses on CPU** — Expected; audio models are compute-intensive. Prefer a GPU with 9GB+
VRAM.

## Acknowledgments

- [Mistral AI](https://mistral.ai/) for Voxtral
- [Hugging Face Transformers](https://github.com/huggingface/transformers)
- [Gradio](https://gradio.app/)
- [Pinokio](https://pinokio.computer/)
