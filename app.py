import os
import traceback

import gradio as gr
import torch
from transformers import AutoProcessor, VoxtralForConditionalGeneration

MODEL_ID = os.environ.get("VOXTRAL_MODEL_ID", "mistralai/Voxtral-Mini-3B-2507")
MAX_NEW_TOKENS = int(os.environ.get("VOXTRAL_MAX_NEW_TOKENS", "384"))

device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device == "cuda" else torch.float32

processor = None
model = None
load_error = None


def load_model():
    global processor, model, load_error
    if model is not None or load_error is not None:
        return

    try:
        processor = AutoProcessor.from_pretrained(MODEL_ID)
        model = VoxtralForConditionalGeneration.from_pretrained(
            MODEL_ID,
            torch_dtype=torch_dtype,
            device_map="auto" if device == "cuda" else None,
            low_cpu_mem_usage=True,
        )
        if device == "cpu":
            model.to(device)
    except Exception as exc:
        load_error = f"{exc}\n\n{traceback.format_exc()}"


def transcribe(audio_file, prompt):
    if audio_file is None:
        return "Bitte laden Sie eine Audiodatei hoch."

    if not prompt:
        prompt = "Was hoerst du in dieser Audiodatei?"

    load_model()
    if load_error:
        return (
            "Fehler beim Laden des Voxtral-Modells.\n\n"
            "Pruefen Sie Ihre GPU/RAM-Ressourcen und die installierten Abhaengigkeiten.\n\n"
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

        inputs = processor.apply_chat_template(conversation)
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
        return decoded_outputs[0] if decoded_outputs else "Keine Antwort generiert."
    except Exception as exc:
        return f"Fehler bei der Verarbeitung: {exc}"

# Gradio Interface
with gr.Blocks(title="Voxtral Audio-Text Chat", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎵 Voxtral Audio-Text Chat")
    gr.Markdown(
        "Laden Sie Audio hoch und stellen Sie eine Textfrage fuer Voxtral. "
        "Diese Version nutzt Transformers direkt (ohne vLLM)."
    )
    
    with gr.Row():
        with gr.Column():
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
            submit_btn = gr.Button("Analysieren", variant="primary")
        
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
        inputs=[audio_input, prompt_input],
        outputs=output
    )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
