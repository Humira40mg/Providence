import pvporcupine
import pyaudio
import struct
import os
import webrtcvad
import collections
import numpy as np
from faster_whisper import WhisperModel
from dotenv import load_dotenv
from logger import logger
import sounddevice as sd
from llmaccess import OllamaAccess
from parser import notify

load_dotenv()

# ---------- CONFIG ----------
access_key = os.getenv("PICOVOICE_KEY")
sd.default.device = (0, None)  # (input, output)
providence = OllamaAccess.getInstance()
KEYWORD_PATH = os.path.abspath("ressources/Providence_fr_linux_v3_0_0.ppn")
MODEL_PATH = os.path.abspath("ressources/porcupine_params_fr.pv")
SILENCE_LIMIT = 0.6  # secondes avant d'arrêter l'écoute
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 20
SAMPLES_PER_FRAME = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)  # 320
BYTES_PER_FRAME = SAMPLES_PER_FRAME * 2  # 640
# ----------------------------

# --- Wakeword ---
porcupine = pvporcupine.create(
    access_key=access_key,
    keyword_paths=[KEYWORD_PATH],
    model_path=MODEL_PATH
)

pa = pyaudio.PyAudio()
stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

# --- VAD ---
vad = webrtcvad.Vad()
vad.set_mode(1)  # 0 = tolérant, 3 = strict

# --- Faster-Whisper ---
model = WhisperModel("small", device="cpu", compute_type="int8")  # modèle rapide

def get_next_frame():
    pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
    return struct.unpack_from("h" * porcupine.frame_length, pcm)

def listen_until_silence():
    frames_per_second = 1000 // FRAME_DURATION_MS
    ring_buffer = collections.deque(maxlen=int(SILENCE_LIMIT * frames_per_second))

    audio_data = []

    while True:
        pcm = stream.read(SAMPLES_PER_FRAME, exception_on_overflow=False)
        is_speech = vad.is_speech(pcm, SAMPLE_RATE)

        if is_speech:
            audio_data.append(pcm)
            ring_buffer.clear()
        else:
            ring_buffer.append(pcm)
            if len(ring_buffer) == ring_buffer.maxlen:
                break

    return b"".join(audio_data)

def wakeOnWord(event):
    while not event.is_set():
        pcm = get_next_frame()
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            logger.info("Wakeword detected → listening...")
            notify("J'écoute...")
            
            audio_chunk = listen_until_silence()

            logger.info(" → end of listening...")
            
            # Conversion vers float32 pour Faster-Whisper
            audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0

            segments, _ = model.transcribe(audio_np, language="fr")
            transcription = " ".join([seg.text for seg in segments])
            logger.info(f"USER SAID: {transcription}")
            providence.chat(f"{transcription} Utilise le tool Intervention pour répondre, ou indiquer quels autres tools tu utilise.", selfprompt = True)
    
    porcupine.delete()
    stream.close()
    pa.terminate()

