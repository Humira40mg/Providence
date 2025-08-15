from .tool import Tool
from yapper import yap, yapping
from pygame import mixer
from parser import notify
from os import remove

last_intervention = ""

class Intervention(Tool):

    name = "Intervention"
    description = "Call this to notify the user with a usefull information, advice or fun fact."
    parameterDescription: str = "The sentence to tell to the user."

    def activate(self, aichoice: str) -> str:
        global last_intervention
        
        if aichoice == last_intervention : return ""
        last_intervention = aichoice
       
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
        
        return ""