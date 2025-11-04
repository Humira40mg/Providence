from .tool import Tool
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from config_read import GOOGLE_API_KEY, GOOGLE_CX


class WebSearch(Tool):

    name = "WebSearch"
    description = "Call this to make a web search. Use this to answer properly to a question."
    parameterDescription: str = "What you need to search"
    hidden = "Eyes"

    def activate(self, aichoice: str) -> dict: 
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CX,
            "q": aichoice,
            "num": 3 
        }

        response = requests.get(url, params=params)
        if not response.ok:
            return f"Erreur API Google : {response.text}"

        data = response.json()
        items = data.get("items", [])

        if not items:
            return "Aucune réponse trouvée."

        results = []

        for item in items:
            title = item.get("title", "Sans titre")
            snippet = item.get("snippet", "")
            link = item.get("link", "")

            # On tente de récupérer le contenu de la page
            try:
                page_resp = requests.get(link, timeout=5)
                soup = BeautifulSoup(page_resp.text, "html.parser")
                # on récupère le texte brut
                text = soup.get_text(separator="\n", strip=True)
                # tronquer si trop long
                text_preview = text[:500] + "..." if len(text) > 500 else text
            except Exception as e:
                text_preview = f"Impossible de scraper la page: {e}"

            results.append(f"{title}\n{snippet}\n{link}\nContenu:\n{text_preview}\n{'-'*50}")

        return {"role":"tool", "content":"\n".join(results), "tool_name":"WebSearch"}

