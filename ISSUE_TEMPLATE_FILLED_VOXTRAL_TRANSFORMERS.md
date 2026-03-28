# Issue Template (Filled): Voxtral + Transformers

## Title
Voxtral Transformers path: chat template fails ("Can't compile non template nodes") and fallback output is garbled

## Summary
Running Voxtral locally with the Transformers backend on Windows fails in multiple ways:
1) `apply_chat_template` fails with `Can't compile non template nodes`
2) fallback path can fail with `name 'TranscriptionRequest' is not defined`
3) direct processor fallback can fail due to missing pad token
4) when fallback does run, output can be garbled with repeated `[TOOL_CALLS]` and unreadable token soup

## Environment
- OS: Windows 10 (`10.0.26200.8037`)
- Shell: PowerShell / CMD via Pinokio
- Python: 3.10.15 (Conda base + app venv)
- App: `PierrunoYT/Voxtral-UI-Pinokio`
- Backend: Transformers (no vLLM server)
- Launch path: `D:\pinokio\api\Voxtral-UI-Pinokio.git`

## Model + Runtime
- Default model: `mistralai/Voxtral-Mini-3B-2507`
- Alternative model available: `mistralai/Voxtral-Small-24B-2507`
- UI loads/downloads model on Generate click (not app startup)

## Relevant Package/Version Notes Observed
- `transformers >= 4.56.0` used
- `accelerate >= 0.34.0` used
- Torch stack had mismatch incidents (`torchvision::nms does not exist`)
- At one point `uv` upgraded torch to `2.11.0` automatically
- `librosa` was required for fallback audio loading (`load_audio_as requires the librosa library`)

## Reproduction Steps
1. Start app (`python app.py`) from Pinokio env.
2. Open Gradio UI.
3. Select model (`mistralai/Voxtral-Mini-3B-2507`).
4. Upload audio and enter prompt.
5. Click Generate.

## Expected Behavior
Readable transcription/answer for the uploaded audio and prompt.

## Actual Behavior
Frequently fails with one of the following:

### Error 1
```text
Can't compile non template nodes
```

### Error 2
```text
name 'TranscriptionRequest' is not defined
```

### Error 3
```text
Asking to pad but the tokenizer does not have a padding token.
Please select a token to use as `pad_token` ...
```

### Error 4 (garbled output)
Output includes repeated `[TOOL_CALLS]` and unreadable token fragments (example):
```text
[Modell: mistralai/Voxtral-Mini-3B-2507]
[Hinweis: Chat-Template fehlgeschlagen, Transkriptions-Fallback wurde verwendet.]

[TOOL_CALLS] [TOOL_CALLS] [TOOL_CALLS] ... Ã©e ren ache tern ption ...
```

## Additional Related Error Encountered Earlier
Before stabilizing env, importing transformers could fail due to torch/torchvision mismatch:
```text
RuntimeError: operator torchvision::nms does not exist
ModuleNotFoundError: Could not import module 'AutoProcessor'
```

## What Was Already Tried
- Removed vLLM and moved to Transformers-only backend.
- Lazy model import to avoid startup crash.
- Multiple fallback input-building paths.
- Added `librosa`.
- Set tokenizer/model `pad_token` fallback.
- Deterministic generation + output cleaning.
- Reset/reinstall env and torch stack cleanup/reinstall attempts.

## Request
Please advise the correct and stable inference path for Voxtral on Transformers in this setup (Windows), specifically for:
- chat template compilation failure (`Can't compile non template nodes`)
- transcription request API consistency (`TranscriptionRequest` path)
- avoiding garbled `[TOOL_CALLS]` generation in fallback mode.

