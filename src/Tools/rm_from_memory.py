from .tool import Tool
from memoriser import removeFromMemory

class RemoveFromMemory(Tool):

    name = "RemoveFromMemory"
    description = "Call this to remove an element to your long term memory."
    parameterDescription: str = "The integer key related to the element to remove."

    def activate(self, aichoice: str) -> str:
        removeFromMemory(aichoice)
        return ""
