from .tool import Tool
from yapper import yap, yapping
from pygame import mixer
from parser import notify
from os import remove
from config_read import texthistory

last_intervention = ""

class Intervention(Tool):

    name = "Intervention"
    description = "Call this to notify the user with a usefull information, advice or fun fact."
    parameterDescription: str = "The sentence to tell to the user."
    hidden = "Chat"

    def activate(self, aichoice: str) -> dict:
        global last_intervention
        
        if aichoice == last_intervention : return None
        last_intervention = aichoice

        texthistory.append({"role":"assistant", "content":aichoice})
        aichoice = aichoice.replace("*", "")
        
        if yapping :
            audio = yap(aichoice)
            if audio:
                mixer.music.load(audio)
                notify(aichoice)
                mixer.music.play()
                while mixer.music.get_busy():
                    continue
                remove(audio)
                remove("audio_outputs/tmp.wav")
                return
        notify(aichoice)
        
        return None