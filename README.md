# ADAM AI — Conversational LLM with Live Captioning

A lightweight conversational LLM assistant with live audio captioning and a simple GUI. This project listens to microphone input, transcribes live captions, and provides conversational responses from an LLM. Uses automatic silence and speech detection to keep the conversation going.

**Highlights**
- Real-time live captioning from microphone audio.
- Conversational LLM integration for contextual responses.
- Simple local GUI for captions and interaction.
- Modular Python codebase for easy extension.

**Quick Start**
- Install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

- Configure environment variables (if using remote LLM APIs):

```bash
set OPENAI_API_KEY=your_api_key_here
# or export OPENAI_API_KEY=your_api_key_here (on Unix)
```

- Run the agent (example):

```bash
python local_agent.py
```

- Run the voice listener (captures microphone and publishes captions):

```bash
python VoiceListener.py
```

- GUI display (in `modules/gui_display.py`) can be launched or integrated by the main script.

**Files & Structure**
- `local_agent.py`: Main agent orchestration; ties together the LLM, caption stream, and UI.
- `VoiceListener.py`: Captures microphone audio and produces live captions/transcripts.
- `mictest.py`: Microphone test utility.
- `modules/gui_display.py`: Simple GUI window to display live captions and interaction.
- `requirements.txt`: Python dependencies pinned by `pip freeze`.
- `vault.txt`: (Sensitive storage — treat carefully; do not commit secrets.)

**Configuration**
- LLM selection: configure which model or API the agent uses in `local_agent.py` or via environment variables.
- Microphone device: if needed, edit `VoiceListener.py` to select specific input device indices.

**Usage Tips**
- Ensure microphone permissions are granted to Python on your OS.
- If using a cloud LLM, verify network connectivity and API key validity.
- For lower-latency captioning, prefer lightweight STT models or streaming APIs.

**Development**
- Run the microphone test: `python mictest.py`.
- Add or swap LLM backends by implementing a small adapter that exposes `send_prompt()` and `stream_responses()` style methods.
- Keep changes small and run local tests before committing.

**Contributing**
- Open an issue describing the feature or bug.
- Fork, add tests, and submit a PR with a clear description.

**License**
- MIT 

**Acknowledgements**
- Built as a modular prototype for local conversational assistants with live captioning.


---
