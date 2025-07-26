from memoriser import memory, addToMemory, removeFromMemory
from subprocess import run
from os import path

icon = path.abspath("ressources/providence.png")

balises = ["[ADD]", "[REMOVE]", "[INTERVENTION]"]

def notify(msg):
    run([
            "notify-send",
            "-i", icon,
            "Providence",
            msg
        ])

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
    
    if len(add) > 1 :
        for i in range(len(add[1:-1])):
            addToMemory(add[i].split("[REMOVE]")[0].split("[INTERVENTION]")[0].replace("```", " "))

    if len(remove) > 1 :
        for i in range(len(remove[1:-1])):
            removeFromMemory(remove[i].split("[ADD]")[0].split("[INTERVENTION]")[0].replace("```", " "))

    if len(intervention) > 1 : 
        return intervention[1].split("[ADD]")[0].split("[REMOVE]")[0].replace("```", " ")
    
