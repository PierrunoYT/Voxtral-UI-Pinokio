import gradio as gr
from mistral_common.protocol.instruct.messages import AudioChunk, UserMessage
from mistral_common.audio import Audio
from openai import OpenAI

BASE_URL = "http://127.0.0.1:8000/v1"
client = OpenAI(api_key="EMPTY", base_url=BASE_URL)

def get_model_id():
    try:
        models = client.models.list()
        if models.data:
            return models.data[0].id
        else:
            return "mistralai/Voxtral-Mini-3B-2507"  # fallback
    except:
        return "mistralai/Voxtral-Mini-3B-2507"  # fallback

def transcribe(audio_file, prompt):
    if audio_file is None:
        return "Bitte laden Sie eine Audiodatei hoch."
    
    if not prompt:
        prompt = "Was hörst du in dieser Audiodatei?"
    
    try:
        model_id = get_model_id()
        audio_chunk = AudioChunk.from_audio(Audio.from_file(audio_file, strict=False))
        user_msg = UserMessage(content=[audio_chunk, {"text": prompt}]).to_openai()
        
        response = client.chat.completions.create(
            model=model_id,
            messages=[user_msg],
            temperature=0.2,
            top_p=0.95
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fehler bei der Verarbeitung: {str(e)}\n\nStellen Sie sicher, dass der vLLM-Server läuft."

# Gradio Interface
with gr.Blocks(title="Voxtral Audio-Text Chat", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎵 Voxtral Audio-Text Chat")
    gr.Markdown("Laden Sie Audio hoch und stellen Sie eine Textfrage für Voxtral.")
    
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
