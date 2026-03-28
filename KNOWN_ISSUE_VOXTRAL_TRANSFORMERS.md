# Known Issue: Voxtral + Transformers Compatibility

## Suggested Issue Title

`Voxtral Transformers path: chat template fails ("Can't compile non template nodes") and fallback output is garbled`

## Typical Symptoms

- `Can't compile non template nodes`
- `name 'TranscriptionRequest' is not defined`
- Garbled output containing repeated `[TOOL_CALLS]` tokens

## Where To Report

- This project (Pinokio integration/package issue):  
  [Open an issue in this repository](https://github.com/PierrunoYT/Voxtral-UI-Pinokio/issues/new)
- Transformers implementation issue:  
  [Open an issue in huggingface/transformers](https://github.com/huggingface/transformers/issues/new/choose)
- Model-level discussion for Voxtral Mini:  
  [Voxtral-Mini discussions](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507/discussions)

## Include These Details In Your Report

- OS, GPU, and Python version
- Installed package versions:
  - `transformers`
  - `torch`
  - `torchvision`
  - `torchaudio`
  - `mistral-common`
- Full traceback/error log
- Short audio sample details and the exact prompt used

