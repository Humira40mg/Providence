from abc import ABC, abstractmethod

class Tool(ABC):
    name: str = ""
    description: str = ""
    parameterDescription: str = ""
    hidden: str = "N/A"

    @abstractmethod
    def activate(self, iachoice: str) -> str:
        pass

    def ollamaFormat(self):
        return {
            "type": "function", 
            "function": {
                "name":self.name,
                "description": self.description, 
                "parameters": {
                    "type": "object",
                    "properties": {
                        "aichoice": {
                            "type": "string", 
                            "description": self.parameterDescription
                            }
                        }, 
                    "required": ["aichoice"]
                    }
                }
            }

