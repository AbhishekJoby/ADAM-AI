import sounddevice as sd
import numpy as np

def print_volume(indata, frames, time, status):
    if status:
        print(f"Status: {status}")
    
    # Calculate volume (RMS) exactly like the main agent
    volume = np.sqrt(np.mean(indata**2))
    
    # Create a visual bar
    bar_length = int(volume * 500)  # Scale up for visibility
    bar = "█" * bar_length
    
    # Print the raw number (Use THIS for your threshold)
    print(f"Volume: {volume:.5f} | {bar}")

print("------------------------------------------------")
print("  MIC TEST TOOL - Press Ctrl+C to stop")
print("------------------------------------------------")
print("1. Sit completely silent to find your 'NOISE FLOOR'.")
print("2. Speak normally to find your 'SPEECH LEVEL'.")
print("------------------------------------------------")

try:
    # Check 50 times per second (similar to main loop)
    with sd.InputStream(callback=print_volume, blocksize=int(44100 * 0.05)):
        while True:
            pass
except KeyboardInterrupt:
    print("\nStopped.")