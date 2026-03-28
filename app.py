import os
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
        model = VoxtralForConditionalGeneration.from_pretrained(
            selected_model_id,
            torch_dtype=torch_dtype,
            device_map="auto" if device == "cuda" else None,
            low_cpu_mem_usage=True,
        )
        if device == "cpu":
            model.to(device)
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
            # Some tokenizer/template combinations on Windows fail in the
            # tokenizer chat-template compiler. Fallback to transcription path.
            inputs = processor.apply_transcription_request(
                audio=audio_file,
                model_id=loaded_model_id,
            )

        if device == "cuda":
            inputs = inputs.to(model.device, dtype=torch_dtype)
        else:
            inputs = inputs.to(model.device)

        with torch.inference_mode():
            outputs = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS)

        generated_tokens = outputs[:, inputs.input_ids.shape[1] :]
        decoded_outputs = processor.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
        )
        if decoded_outputs:
            prefix = f"[Modell: {loaded_model_id}]"
            if template_error is not None:
                prefix += "\n[Hinweis: Chat-Template fehlgeschlagen, Transkriptions-Fallback wurde verwendet.]"
            return f"{prefix}\n\n{decoded_outputs[0]}"
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
