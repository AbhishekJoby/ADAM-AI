import time
import queue
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

class VoiceInputListener:
    def __init__(self, model_size="base.en", device="cuda", compute_type="float16"):
        print("[AI] Loading Whisper Model...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.audio_queue = queue.Queue()
        self.stream = None
        self.running = False
        
        # Public attributes
        self.current_text = ""
        self.final_text = ""

    def _callback(self, indata, frames, time_info, status):
        """Thread-safe callback. Puts audio into the queue."""
        if self.running: # Only record if the flag is true
            self.audio_queue.put(indata.copy())

    def listen(self, fs=16000, silence_threshold=0.075, silence_duration=1.8):
        """
        Records audio and returns text. safely handles start/stop.
        """
        print("\n[AI] I'm listening... (Say 'OVER' to stop)")
        
        # Reset State
        self.current_text = ""
        self.final_text = ""
        self.running = True
        
        # Clear old audio from queue
        with self.audio_queue.mutex:
            self.audio_queue.queue.clear()

        # Start Audio Stream
        self.stream = sd.InputStream(samplerate=fs, channels=1, callback=self._callback)
        self.stream.start()

        audio_buffer = []
        started_talking = False
        silence_start_time = None
        last_transcribe_time = time.time()

        try:
            while self.running:
                # 1. Pull Audio from Queue
                try:
                    # Wait up to 0.1s for audio data (avoids CPU spin)
                    chunk = self.audio_queue.get(timeout=0.1)
                    audio_buffer.append(chunk)
                except queue.Empty:
                    continue

                # 2. Silence Detection
                latest_chunk = audio_buffer[-1]
                volume = np.sqrt(np.mean(latest_chunk**2))

                if volume > silence_threshold:
                    if not started_talking:
                        print(" [Started Talking]...")
                        started_talking = True
                    silence_start_time = None
                elif started_talking:
                    if silence_start_time is None:
                        silence_start_time = time.time()
                    
                    if time.time() - silence_start_time > silence_duration:
                        print("\n[Stop Condition] Silence detected.")
                        break

                # 3. Real-Time Check (Every 1.0s)
                if time.time() - last_transcribe_time > 1.0 and started_talking:
                    last_transcribe_time = time.time()
                    
                    # Flatten audio
                    current_audio = np.concatenate(audio_buffer, axis=0).flatten().astype(np.float32)
                    
                    # Quick Transcribe
                    segments, _ = self.model.transcribe(current_audio, beam_size=1, language="en")
                    temp_text = " ".join([s.text for s in segments]).strip()
                    
                    self.current_text = temp_text
                    print(f"\r[Live]: {self.current_text}", end="", flush=True)

                    # Check Keyword "OVER"
                    if "over" in temp_text.lower().split():
                        print("\n[Stop Condition] Keyword 'OVER' detected.")
                        self.final_text = temp_text
                        break

        except KeyboardInterrupt:
            print("\n[User Interrupt] Stopping...")
        
        finally:
            # === CRITICAL CLEANUP SECTION ===
            self.running = False
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
        
        # Final Processing
        if not self.final_text and audio_buffer:
            print("\n[Processing] Finalizing...")
            full_audio = np.concatenate(audio_buffer, axis=0).flatten().astype(np.float32)
            segments, _ = self.model.transcribe(full_audio, beam_size=5)
            self.final_text = " ".join([s.text for s in segments]).strip()

        # Clean Text
        return self.final_text.replace("OVER", "").replace("over", "").strip()

# --- SAFE TEST RUNNER ---
if __name__ == "__main__":
    listener = VoiceInputListener()
    try:
        # while True:
        #     text = listener.listen()
        #     if text:
        #         print(f"\n[Result]: {text}")
        text = listener.listen()
        if text:
            print(f"\n[Result]: {text}")
        sd.stop()
    except KeyboardInterrupt:
        print("\nExiting gracefully...")
        # Force kill leftover threads if any exist