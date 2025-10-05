from os import path, makedirs, environ
import torch
import sys
from langdetect import detect
from logger import logger

sys.path.insert(0, path.expanduser("~/OpenVoice"))
environ["TOKENIZERS_PARALLELISM"] = "false"

from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS


#Initialisation
ckpt_converter = path.expanduser('~/OpenVoice/checkpoints_v2/converter')
device = "cuda:0" if torch.cuda.is_available() else "cpu"
output_dir = 'audio_outputs'

tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

makedirs(output_dir, exist_ok=True)


#Obtain Tone Color Embedding
reference_speaker = "ressources/voice-reference.wav" # This is the voice you want to clone
target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, vad=True)


#Use MeloTTS as Base Speakers
src_path = f'{output_dir}/tmp.wav'

# Speed is adjustable
speed = 1.2

# --- yapping ---
yapping = True

def is_yapping():
    return yapping

def toggle_yapping():
    global yapping
    yapping = not yapping




def yap(text:str):
    """
    Uses OpenVoice V2 to speak
    """
    try :
        language = detect(text).upper()
        if language == "JA":
            language = "JP"

        model = TTS(language=language, device=device)
        speaker_ids = model.hps.data.spk2id
        
        for speaker_key in speaker_ids.keys():
            speaker_id = speaker_ids[speaker_key]
            speaker_key = speaker_key.lower().replace('_', '-')
            
            source_se = torch.load(path.expanduser(f'~/OpenVoice/checkpoints_v2/base_speakers/ses/{speaker_key}.pth'), map_location=device)
            if torch.backends.mps.is_available() and device == 'cpu':
                torch.backends.mps.is_available = lambda: False
            model.tts_to_file(text, speaker_id, src_path, speed=speed)
            save_path = f'{output_dir}/output_v2_{speaker_key}.wav'

            # Run the tone color converter
            encode_message = "@MyShell"
            tone_color_converter.convert(
                audio_src_path=src_path, 
                src_se=source_se, 
                tgt_se=target_se,
                tau=0.2,
                output_path=save_path,
                message=encode_message)
            return save_path
    except Exception as e:
        logger.error(e)