import re
from memoriser import memory, addToMemory, removeFromMemory
from subprocess import run

balises = ["<add>", "<remove>", "<intervention>", "</add>", "</remove>", "</intervention>"]

def parseResponse(response: str):
    balised = False
    for balise in balises:
        if balise in response:
            balised = True
            break
    
    if not balised : return
    
    add = re.findall(r'<add>(.*?)</add>', response)
    remove = re.findall(r'<remove>(.*?)</remove>', response)
    intervention = re.findall(r'<intervention>(.*?)</intervention>', response)
    
    print(f"{add}\n{remove}\n{intervention}\n") # DEBUG
    
    for info in add :
        if len(info) > 1:
            addToMemory(info)

    for info in remove :
        if len(info) > 1:
            removeFromMemory(info)

    for msg in intervention:
        if len(msg) > 1:
            run([
                "notify-send",
                "-i", "ressources/providence.png",
                "Providence",
                msg
            ])
    
