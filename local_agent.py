import os
import json
import ollama 
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer, util
import time 
import logging

# --- CONFIGURATION ---
# We don't need OLLAMA_URL anymore, the library handles it!
MODEL_NAME = "gemma3:1b"
VAULT_FILE = "vault.txt"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
DEVICE = "cuda" #use "cuda" if torch.cuda.is_available() else "cpu"
MEASURE_TIME = True

# --- SUPPRESS WARNINGS ---
# Shut up HuggingFace and Transformers logs
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

# Initialize Models
print("Loading Embedding Model...")
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
print("Loading Whisper Model...")
whisper = WhisperModel("base.en", DEVICE, compute_type="int8")

# --- 1. RAG FUNCTIONALITY  ---
def get_vault_embeddings():
    if not os.path.exists(VAULT_FILE):
        return [], []
    with open(VAULT_FILE, 'r', encoding='utf-8') as f:
        content = f.readlines()
    sentences = [line.strip() for line in content if line.strip()]
    if not sentences:
        return [], []
    embeddings = embedder.encode(sentences, convert_to_tensor=True)
    return sentences, embeddings

def retrieve_context(query, top_k=3):
    sentences, embeddings = get_vault_embeddings()
    if len(sentences) == 0:
        return ""
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    hits = util.semantic_search(query_embedding, embeddings, top_k=top_k)
    relevant_info = [sentences[hit['corpus_id']] for hit in hits[0]]
    return "\n".join(relevant_info)

# --- 2. OLLAMA INTEGRATION ---
def chat_with_ollama(user_input, system_prompt):
    # Retrieve context from Vault
    context = retrieve_context(user_input)
    print(f"\n[RAG Context]: {context}")
    
    # Construct the prompt
    full_prompt = f"Context from my notes:\n{context}\n\nUser Question: {user_input}"
    start = time.time() # <--- Start Timer
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': full_prompt},
            ]
        )
        end = time.time()   # <--- End Timer
        if MEASURE_TIME:
            print(f"[Log] AI Thinking: {end - start:.2f}s") # <--- Print Lag
        # Access response content directly
        return response['message']['content']
        
    except Exception as e:
        return f"Error communicating with Ollama: {e}"

# --- 3. AUDIO TOOLS (Unchanged) ---
def record_audio(duration=5, fs=44100):
    print("Listening...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    print("Processing...")
    write('input.wav', fs, recording)
    return 'input.wav'

def transcribe_audio(filename):
    start = time.time()
    segments, _ = whisper.transcribe(filename)
    text = " ".join([segment.text for segment in segments])
    end = time.time()   # <--- End Timer
    if MEASURE_TIME:
        print(f"Transcription Time: {end - start:.2f} seconds")
    return text.strip()

def text_to_speech(text):
    print(f"\nAI (Voice): {text}")
    # os.system(f"say -v Samantha {text}") # Uncomment for Mac

# --- MAIN LOOP (Unchanged) ---
def main():
    system_prompt = (
        "You are Josnah, a sarcastic and slightly annoyed assistant. "
        "You always complain before helping, but you are helpful. "
        "Keep answers concise."
        "Dont use *" 
    )

    if not os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, 'w') as f:
            f.write("My name is Chris.\nI am an AI engineer.\n")

    while True:
        input("\nPress Enter to record (or Ctrl+C to exit)...")
        audio_file = record_audio(duration=5)
        user_text = transcribe_audio(audio_file)
        print(f"User: {user_text}")
        
        if not user_text:
            continue

        if "insert info" in user_text.lower():
            clean_text = user_text.lower().replace("insert info", "").strip()
            with open(VAULT_FILE, 'a') as f:
                f.write(clean_text + "\n")
            print("Info saved to vault.")
            continue

        response = chat_with_ollama(user_text, system_prompt)
        text_to_speech(response)

if __name__ == "__main__":
    main()