from .tool import Tool
from memoriser import addToMemory

class AddToMemory(Tool):

    name = "AddToMemory"
    description = "Call this to add a key element to your long term memory (exemple: informations on the user)"
    parameterDescription: str = "The key elements to add to memory."

    def activate(self, aichoice: str) -> str:
        addToMemory(aichoice)
        return ""
