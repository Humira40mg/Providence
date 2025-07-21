from memoriser import memory, addToMemory, removeFromMemory
from subprocess import run
from os import path

icon = path.abspath("ressources/providence.png")

balises = ["[ADD]", "[REMOVE]", "[INTERVENTION]"]

def parseResponse(response: str):
    balised = False
    for balise in balises:
        if balise in response:
            balised = True
            break
    
    if not balised : return
    
    add = response.split("[ADD]")
    remove = response.split("[REMOVE]")
    intervention = response.split("[INTERVENTION]")
    
    print(f"{add}\n{remove}\n{intervention}\n") # DEBUG
    
    if len(add) > 1 :
        addToMemory(add[1].split("[REMOVE]")[0].split("[INTERVENTION]")[0])

    if len(remove) > 1 :
        removeFromMemory(remove[1].split("[ADD]")[0].split("[INTERVENTION]")[0])

    if len(intervention) > 1 : 
        run([
            "notify-send",
            "-i", icon,
            "Providence",
            intervention[1].split("[ADD]")[0].split("[REMOVE]")[0]
        ])
    
