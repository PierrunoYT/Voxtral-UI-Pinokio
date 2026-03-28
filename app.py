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
MAX_NEW_TOKENS = int(os.environ.get("VOXTRAL_MAX_NEW_TOKENS", "384"))

device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device == "cuda" else torch.float32

processor = None
model = None
load_error = None
loaded_model_id = None
asr_pipeline = None


def _clean_generated_text(text):
    cleaned = text.replace("[TOOL_CALLS]", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _looks_garbled(text):
    if not text:
        return True
    if text.count("[TOOL_CALLS]") > 2:
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
            )
        result = asr_pipeline(audio_file)
        if isinstance(result, dict):
            text = str(result.get("text", "")).strip()
            if text:
                return text
        return ""
    except Exception:
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


def load_model(selected_model_id):
    global processor, model, load_error, loaded_model_id
    if selected_model_id not in AVAILABLE_MODELS:
        selected_model_id = DEFAULT_MODEL_ID

    # Only reuse when the model is already loaded successfully.
    if loaded_model_id == selected_model_id and model is not None and load_error is None:
        return

    # Selection changed (or first load): clear previous state.
    if model is not None:
        del model
    if processor is not None:
        del processor
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    processor = None
    model = None
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
            torch_dtype=torch_dtype,
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
        return "Bitte laden Sie eine Audiodatei hoch."

    if not prompt:
        prompt = "Was hoerst du in dieser Audiodatei?"

    load_model(selected_model_id)
    if load_error:
        return (
            "Fehler beim Laden des Voxtral-Modells.\n\n"
            "Pruefen Sie Ihre GPU/RAM-Ressourcen und die installierten Abhaengigkeiten.\n\n"
            "Falls Sie einen torchvision/torch Fehler sehen (z.B. 'operator torchvision::nms does not exist'),\n"
            "fuehren Sie in Pinokio bitte Reset + Install erneut aus, damit passende Torch-Pakete neu installiert werden.\n\n"
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
        input_build_errors = []
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
            template_error = exc
            input_build_errors.append(f"apply_chat_template failed: {exc}")
            inputs = None

            # Fallback 1: transcription request helper (if available).
            if hasattr(processor, "apply_transcription_request"):
                try:
                    inputs = processor.apply_transcription_request(
                        audio=audio_file,
                        model_id=loaded_model_id,
                    )
                except Exception as transcription_exc:
                    input_build_errors.append(
                        f"apply_transcription_request failed: {transcription_exc}"
                    )

            # Fallback 2: direct processor call with loaded waveform.
            if inputs is None:
                try:
                    import librosa  # type: ignore[reportMissingImports]

                    sampling_rate = getattr(
                        getattr(processor, "feature_extractor", None),
                        "sampling_rate",
                        16000,
                    )
                    waveform, _ = librosa.load(audio_file, sr=sampling_rate, mono=True)
                    text_prompt = prompt

                    for call_kwargs in (
                        {"text": [text_prompt], "audio": [waveform]},
                        {"text": [text_prompt], "audios": [waveform]},
                    ):
                        try:
                            inputs = processor(
                                **call_kwargs,
                                return_tensors="pt",
                                padding=False,
                            )
                            break
                        except Exception as direct_exc:
                            input_build_errors.append(
                                f"processor direct call failed ({list(call_kwargs.keys())}): {direct_exc}"
                            )
                except Exception as librosa_exc:
                    input_build_errors.append(f"librosa/direct audio fallback failed: {librosa_exc}")

            if inputs is None:
                return (
                    "Fehler bei der Verarbeitung: Eingaben konnten fuer Voxtral nicht erstellt werden.\n\n"
                    "Details:\n- " + "\n- ".join(input_build_errors)
                )

        if device == "cuda":
            inputs = inputs.to(model.device, dtype=torch_dtype)
        else:
            inputs = inputs.to(model.device)

        tokenizer = getattr(processor, "tokenizer", None)
        eos_token_id = getattr(tokenizer, "eos_token_id", None) if tokenizer is not None else None
        pad_token_id = getattr(tokenizer, "pad_token_id", None) if tokenizer is not None else None

        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                temperature=0.0,
                repetition_penalty=1.1,
                no_repeat_ngram_size=3,
                eos_token_id=eos_token_id,
                pad_token_id=pad_token_id,
            )

        generated_tokens = outputs[:, inputs.input_ids.shape[1] :]
        decoded_outputs = processor.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )
        if decoded_outputs:
            cleaned_text = _clean_generated_text(decoded_outputs[0])
            if _looks_garbled(cleaned_text):
                whisper_text = _whisper_transcription_fallback(audio_file)
                if whisper_text:
                    return (
                        f"[Modell: {loaded_model_id}]\n"
                        "[Hinweis: Voxtral-Fallback-Ausgabe war ungueltig, Whisper-Transkription wurde verwendet.]\n\n"
                        f"{whisper_text}"
                    )
                return (
                    "Fehler bei der Verarbeitung: Das Modell hat im Fallback-Modus ungueltige Ausgabe erzeugt.\n\n"
                    "Bitte versuchen Sie:\n"
                    "- ein kuerzeres/sauberes Audio,\n"
                    "- das andere Modell im Dropdown,\n"
                    "- oder Transformers erneut updaten und neu starten.\n\n"
                    f"Rohausgabe (gekuerzt): {decoded_outputs[0][:400]}"
                )
            prefix = f"[Modell: {loaded_model_id}]"
            if template_error is not None:
                prefix += "\n[Hinweis: Chat-Template fehlgeschlagen, Transkriptions-Fallback wurde verwendet.]"
            return f"{prefix}\n\n{cleaned_text}"
        return "Keine Antwort generiert."
    except Exception as exc:
        if "Can't compile non template nodes" in str(exc):
            return (
                "Fehler bei der Template-Verarbeitung des Modells.\n\n"
                "Der Fehler tritt in der Tokenizer-Template-Verarbeitung auf.\n"
                "Die App versucht jetzt automatisch einen Fallback-Modus.\n\n"
                f"Details: {exc}"
            )
        return f"Fehler bei der Verarbeitung: {exc}"

# Gradio Interface
with gr.Blocks(title="Voxtral Audio-Text Chat", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎵 Voxtral Audio-Text Chat")
    gr.Markdown(
        "Laden Sie Audio hoch und stellen Sie eine Textfrage fuer Voxtral. "
        "Diese Version nutzt Transformers direkt (ohne vLLM)."
    )
    gr.Markdown(
        "Modelle werden erst beim Klick auf **Generieren** geladen bzw. heruntergeladen "
        "(nicht beim App-Start)."
    )
    
    with gr.Row():
        with gr.Column():
            model_select = gr.Dropdown(
                label="Voxtral Modell",
                choices=AVAILABLE_MODELS,
                value=DEFAULT_MODEL_ID if DEFAULT_MODEL_ID in AVAILABLE_MODELS else AVAILABLE_MODELS[0],
                interactive=True,
            )
            audio_input = gr.Audio(
                label="Audio hochladen", 
                type="filepath",
                sources=["upload", "microphone"]
            )
            prompt_input = gr.Textbox(
                label="Ihre Frage zum Audio",
                placeholder="Was hörst du in dieser Audiodatei?",
                lines=3
            )
            submit_btn = gr.Button("Generieren", variant="primary")
        
        with gr.Column():
            output = gr.Textbox(
                label="Voxtral Antwort",
                lines=10,
                interactive=False
            )
    
    # Examples
    gr.Markdown("### Beispiel-Prompts:")
    gr.Markdown("""
    - "Transkribiere dieses Audio."
    - "Was für Musik ist das?"
    - "Welche Emotionen hörst du?"
    - "Beschreibe die Geräusche im Detail."
    - "Übersetze das gesprochene ins Deutsche."
    """)
    
    submit_btn.click(
        fn=transcribe,
        inputs=[audio_input, prompt_input, model_select],
        outputs=output,
        show_progress="full",
    )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
