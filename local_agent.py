import os
import time
import logging
import ollama
from sentence_transformers import SentenceTransformer, util

from VoiceListener import VoiceInputListener
from modules.gui_display import CaptionWindow  #GUI Module

#to supress GUI error
from tkinter import TclError

# --- CONFIGURATION ---
MODEL_NAME = "gemma3:1b"
VAULT_FILE = "vault.txt"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
MEASURE_TIME = True

# --- SUPPRESS WARNINGS ---
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

# --- INITIALIZE MODELS ---
print("Loading Embedding Model...")
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)


# --- 1. RAG FUNCTIONALITY ---
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
    
    start = time.time()
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': full_prompt},
            ]
        )
        end = time.time()
        if MEASURE_TIME:
            print(f"[Log] AI Thinking: {end - start:.2f}s")
        return response['message']['content']
        
    except Exception as e:
        return f"Error communicating with Ollama: {e}"

# --- 3. OUTPUT ---
def text_to_speech(text):
    print(f"\nAI (Voice): {text}")
    # os.system(f"say -v Samantha {text}") # Uncomment for Mac

# --- MAIN LOOP ---
def main():
    system_prompt = (
        "You are Adam, a sarcastic and slightly annoyed assistant. "
        "You always complain before helping, but you are helpful. "
        "Keep answers concise. "
        "Don't use markdown formatting like * or #."
    )

    # Ensure vault exists
    if not os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, 'w') as f:
            f.write("My name is Jobz.\nI am an tinkerer.\n")

    gui = CaptionWindow()
    print("Initializing Hearing System...(whisper model)")
    # Check if you have a GPU, otherwise change device to "cpu"
    listener = VoiceInputListener(model_size="base.en", device="cuda")

    while True:
        try:
            user_text = listener.listen(on_update=gui.update_live) #just remove the callback to disable GUI updates
            # If user_text is empty (e.g. just noise), skip loop
            if not user_text:
                print("No speech detected, please try again.")
                gui.update_live("No speech detected.")
                continue

            print(f"\n[User Said]: {user_text}")
            gui.update_context(user_text)

            # --- COMMANDS ---
            if "insert info" in user_text.lower():
                clean_text = user_text.lower().replace("insert info", "").strip()
                with open(VAULT_FILE, 'a') as f:
                    f.write(clean_text + "\n")
                print("Info saved to vault.")
                gui.update_context(f"Saved to Vault: {clean_text}")
                continue

            # --- GENERATE RESPONSE ---
            response = chat_with_ollama(user_text, system_prompt)
            text_to_speech(response)
        except TclError:
            print("GUI closed. Exiting...")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")