import gc
import os
import re
import traceback

import gradio as gr
import torch

DEFAULT_MODEL_ID = os.environ.get("VOXTRAL_MODEL_ID", "mistralai/Voxtral-Mini-3B-2507")
AVAILABLE_MODELS = [
    "mistralai/Voxtral-Mini-3B-2507",
    "mistralai/Voxtral-Small-24B-2507",
]


def _env_int(name, default):
    """Read an int from the environment, ignoring unset/blank/invalid values."""
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


MAX_NEW_TOKENS = _env_int("VOXTRAL_MAX_NEW_TOKENS", 384)

device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    # Voxtral ships bf16 weights; fp16 can overflow and produce garbage.
    torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
else:
    torch_dtype = torch.float32

processor = None
model = None
load_error = None
loaded_model_id = None
asr_pipeline = None


def _clean_generated_text(text):
    cleaned = text.replace("[TOOL_CALLS]", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _looks_garbled(text, raw_text=None):
    """
    Detect unusable generations. ``raw_text`` is the pre-cleanup output: the
    ``[TOOL_CALLS]`` marker is stripped by _clean_generated_text(), so counting
    it on the cleaned text would never match.
    """
    if raw_text is not None and raw_text.count("[TOOL_CALLS]") > 2:
        return True
    if not text:
        return True
    printable = sum(1 for ch in text if ch.isprintable())
    ratio = printable / max(1, len(text))
    return ratio < 0.85


def _whisper_transcription_fallback(audio_file):
    global asr_pipeline
    try:
        if asr_pipeline is None:
            from transformers import pipeline

            asr_pipeline = pipeline(
                task="automatic-speech-recognition",
                model="openai/whisper-small",
                device=0 if torch.cuda.is_available() else -1,
                # Whisper's window is 30 s; chunking transcribes longer clips fully.
                chunk_length_s=30,
            )
        result = asr_pipeline(audio_file)
        if isinstance(result, dict):
            return str(result.get("text", "")).strip()
        return ""
    except Exception:
        traceback.print_exc()
        return ""


def _select_chat_template(processor_obj):
    """
    Some tokenizer configs expose multiple chat templates as a list/dict.
    Normalize this into a template string for apply_chat_template().
    """
    template = getattr(processor_obj, "chat_template", None)
    if template is None and hasattr(processor_obj, "tokenizer"):
        template = getattr(processor_obj.tokenizer, "chat_template", None)

    if isinstance(template, str):
        return template

    if isinstance(template, list):
        for preferred_name in ("default", "chat", "instruct"):
            for item in template:
                if isinstance(item, dict) and item.get("name") == preferred_name and isinstance(item.get("template"), str):
                    return item["template"]
        for item in template:
            if isinstance(item, dict) and isinstance(item.get("template"), str):
                return item["template"]

    if isinstance(template, dict):
        for key in ("default", "chat", "instruct", "template"):
            value = template.get(key)
            if isinstance(value, str):
                return value

    return None


def _normalize_model_id(selected_model_id):
    """Map an arbitrary dropdown value onto a known model id."""
    if isinstance(selected_model_id, str) and selected_model_id in AVAILABLE_MODELS:
        return selected_model_id
    if DEFAULT_MODEL_ID in AVAILABLE_MODELS:
        return DEFAULT_MODEL_ID
    return AVAILABLE_MODELS[0]


def load_model(selected_model_id):
    global processor, model, load_error, loaded_model_id
    selected_model_id = _normalize_model_id(selected_model_id)

    # Only reuse when the model is already loaded successfully.
    if loaded_model_id == selected_model_id and model is not None and load_error is None:
        return

    # Selection changed (or first load): drop the previous model before loading
    # the next one, otherwise both are resident at once. gc.collect() is needed
    # for empty_cache() to actually release the old weights.
    processor = None
    model = None
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    load_error = None
    loaded_model_id = None

    try:
        # Import lazily to avoid startup crashes when a broken torchvision/torch
        # install is present; users can still open the UI and read the error.
        from transformers import AutoProcessor, VoxtralForConditionalGeneration

        processor = AutoProcessor.from_pretrained(selected_model_id)
        tokenizer = getattr(processor, "tokenizer", None)
        if tokenizer is not None and tokenizer.pad_token is None:
            # Some Voxtral tokenizer variants ship without pad_token.
            # For single-sample inference, EOS padding is a safe fallback.
            if tokenizer.eos_token is not None:
                tokenizer.pad_token = tokenizer.eos_token
            elif tokenizer.unk_token is not None:
                tokenizer.pad_token = tokenizer.unk_token

        model = VoxtralForConditionalGeneration.from_pretrained(
            selected_model_id,
            dtype=torch_dtype,
            device_map="auto" if device == "cuda" else None,
            low_cpu_mem_usage=True,
        )
        if device == "cpu":
            model.to(device)
        if tokenizer is not None and getattr(model, "config", None) is not None:
            if getattr(model.config, "pad_token_id", None) is None and tokenizer.pad_token_id is not None:
                model.config.pad_token_id = tokenizer.pad_token_id
        loaded_model_id = selected_model_id
    except Exception as exc:
        load_error = f"{exc}\n\n{traceback.format_exc()}"


def transcribe(audio_file, prompt, selected_model_id):
    if audio_file is None:
        return "Please upload an audio file."

    if not os.path.isfile(audio_file):
        return "Error: The uploaded audio file could not be found. Please upload it again."

    if not prompt:
        prompt = "What do you hear in this audio file?"

    selected_model_id = _normalize_model_id(selected_model_id)
    if device == "cpu" and "24B" in selected_model_id:
        return (
            "Voxtral-Small-24B requires significantly more memory than is practical to provide "
            "on CPU (approx. 90GB+ RAM in fp32).\n\n"
            "Please select Voxtral-Mini-3B, or use a GPU with sufficient VRAM."
        )

    load_model(selected_model_id)
    if load_error:
        return (
            "Failed to load the Voxtral model.\n\n"
            "Check your GPU/RAM resources and installed dependencies.\n\n"
            "If you see a torchvision/torch error (e.g. 'operator torchvision::nms does not exist'),\n"
            "run Reset + Install again in Pinokio so matching Torch packages get reinstalled.\n\n"
            f"Details:\n{load_error}"
        )
    try:
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "audio", "path": audio_file},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        template = _select_chat_template(processor)
        template_error = None
        try:
            if template:
                inputs = processor.apply_chat_template(
                    conversation,
                    chat_template=template,
                    add_generation_prompt=True,
                    tokenize=True,
                    return_tensors="pt",
                    return_dict=True,
                )
            else:
                inputs = processor.apply_chat_template(
                    conversation,
                    add_generation_prompt=True,
                    tokenize=True,
                    return_tensors="pt",
                    return_dict=True,
                )
        except Exception as exc:
            # Only remaining input path: Voxtral's transcription request. It
            # cannot carry the user's prompt, which the reply discloses.
            template_error = exc
            if not hasattr(processor, "apply_transcription_request"):
                return f"Processing error: Could not build inputs for Voxtral.\n\nDetails: {exc}"
            try:
                inputs = processor.apply_transcription_request(
                    audio=audio_file,
                    model_id=loaded_model_id,
                )
            except Exception as transcription_exc:
                return (
                    "Processing error: Could not build inputs for Voxtral.\n\n"
                    f"Details:\n- apply_chat_template failed: {exc}\n"
                    f"- apply_transcription_request failed: {transcription_exc}"
                )

        if device == "cuda":
            inputs = inputs.to(model.device, dtype=torch_dtype)
        else:
            inputs = inputs.to(model.device)

        tokenizer = getattr(processor, "tokenizer", None)
        eos_token_id = getattr(tokenizer, "eos_token_id", None) if tokenizer is not None else None
        pad_token_id = getattr(tokenizer, "pad_token_id", None) if tokenizer is not None else None

        # Plain greedy decoding: repetition penalties and n-gram blocking
        # corrupt transcripts, where repeated phrases are legitimate.
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                eos_token_id=eos_token_id,
                pad_token_id=pad_token_id,
            )

        input_ids = inputs.get("input_ids") if hasattr(inputs, "get") else getattr(inputs, "input_ids", None)
        if input_ids is not None:
            generated_tokens = outputs[:, input_ids.shape[1] :]
        else:
            # Without the prompt length we can only decode the full sequence.
            generated_tokens = outputs
        if generated_tokens.shape[0] == 0:
            return "No response generated."
        # Decode with special tokens kept so garbage such as repeated
        # [TOOL_CALLS] markers is detectable; the cleaned text strips them.
        raw_text = processor.batch_decode(
            generated_tokens,
            skip_special_tokens=False,
            clean_up_tokenization_spaces=True,
        )[0]
        text = processor.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )[0]
        cleaned_text = _clean_generated_text(text)
        if _looks_garbled(cleaned_text, raw_text):
            whisper_text = _whisper_transcription_fallback(audio_file)
            if whisper_text:
                return (
                    f"[Model: openai/whisper-small]\n"
                    f"[Warning: {loaded_model_id} produced unusable output, so your question was NOT answered. "
                    "Below is a plain Whisper transcript of the audio instead.]\n\n"
                    f"{whisper_text}"
                )
            return (
                "Processing error: The model produced invalid output.\n\n"
                "Please try:\n"
                "- a shorter/cleaner audio clip,\n"
                "- the other model in the dropdown,\n"
                "- or updating Transformers and restarting.\n\n"
                f"Raw output (truncated): {raw_text[:400]}"
            )
        prefix = f"[Model: {loaded_model_id}]"
        if template_error is not None:
            prefix += (
                "\n[Note: The chat template failed, so the audio was transcribed instead; "
                "your question was ignored.]"
            )
        if generated_tokens.shape[1] >= MAX_NEW_TOKENS:
            prefix += (
                f"\n[Note: Output reached the {MAX_NEW_TOKENS}-token limit and may be cut off. "
                "Raise VOXTRAL_MAX_NEW_TOKENS for longer output.]"
            )
        return f"{prefix}\n\n{cleaned_text}"
    except Exception as exc:
        return f"Processing error: {exc}"

# Gradio Interface
with gr.Blocks(title="Voxtral Audio-Text Chat") as app:
    gr.Markdown("# 🎵 Voxtral Audio-Text Chat")
    gr.Markdown(
        "Upload audio and ask a text question for Voxtral. "
        "This version uses Transformers directly (no vLLM)."
    )
    gr.Markdown(
        "Models are only loaded/downloaded when you click **Generate** "
        "(not at app startup)."
    )

    with gr.Row():
        with gr.Column():
            model_select = gr.Dropdown(
                label="Voxtral Model",
                choices=AVAILABLE_MODELS,
                value=DEFAULT_MODEL_ID if DEFAULT_MODEL_ID in AVAILABLE_MODELS else AVAILABLE_MODELS[0],
                interactive=True,
            )
            audio_input = gr.Audio(
                label="Upload Audio",
                type="filepath",
                sources=["upload", "microphone"]
            )
            prompt_input = gr.Textbox(
                label="Your Question About the Audio",
                placeholder="What do you hear in this audio file?",
                lines=3
            )
            submit_btn = gr.Button("Generate", variant="primary")

        with gr.Column():
            output = gr.Textbox(
                label="Voxtral Response",
                lines=10,
                interactive=False
            )

    # Examples
    gr.Markdown("### Example Prompts:")
    gr.Markdown("""
    - "Transcribe this audio."
    - "What kind of music is this?"
    - "What emotions do you hear?"
    - "Describe the sounds in detail."
    - "Translate the speech into English."
    """)

    submit_btn.click(
        fn=transcribe,
        inputs=[audio_input, prompt_input, model_select],
        outputs=output,
        show_progress="full",
        concurrency_limit=1,
    )

if __name__ == "__main__":
    # Respect Pinokio-injected GRADIO_SERVER_NAME / GRADIO_SERVER_PORT env vars
    # so the launcher can pick a free port and bind to 127.0.0.1. Parsing the
    # port here (rather than leaving it to Gradio) keeps a blank/invalid value
    # from crashing startup; None lets Gradio scan for a free port.
    # concurrency_limit=1 on the click handler above serializes requests since
    # model/processor are shared global state that isn't safe for concurrent access.
    app.queue().launch(
        server_name=os.environ.get("GRADIO_SERVER_NAME") or "127.0.0.1",
        server_port=_env_int("GRADIO_SERVER_PORT", None),
        share=False,
        show_error=True,
        theme=gr.themes.Soft(),
    )
