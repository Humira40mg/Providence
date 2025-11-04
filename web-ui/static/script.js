const messagesDiv = document.getElementById("messages");
const userInput = document.getElementById("userInput");

function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = "message " + sender;

    // 🔹 Utilise marked pour parser le markdown
    msg.innerHTML = marked.parse(text);

    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  addMessage(text, "user");
  userInput.value = "";

  const aiMsg = document.createElement("div");
  aiMsg.className = "message assistant";
  const toolstips = document.createElement("span");

  messagesDiv.appendChild(aiMsg);
  aiMsg.appendChild(toolstips)

  try {
    const response = await fetch("/chat", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let currentMsg = ""
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value, { stream: true });
      if (!text.trim()) continue; // ignore les vides

      let chunk;
      try {
        chunk = JSON.parse(text);
      } catch (e) {
        console.warn("Chunk invalide (pas du JSON) :", text);
        continue;
      }

      if (chunk?.message?.content) {
        toolstips.innerHTML = ""
        currentMsg += chunk.message.content;
        aiMsg.innerHTML = marked.parse(currentMsg);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
      } else {
        console.warn("Chunk sans content :", chunk);
      }
      if (chunk?.message?.tool_calls) {
        toolstips.innerHTML = "Utilisation de "
        chunk?.message?.tool_calls.forEach((tool) => {
          toolstips.innerHTML += tool.function.name + ", ";
        })
        toolstips.innerHTML += "..."
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
      }
    }

  } catch (err) {
    console.error(err);
    aiMsg.innerHTML = "Erreur de connexion au serveur.";
  }
}

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    if (e.shiftKey) {
      // Shift+Enter → insère un saut de ligne
      return; 
    } else {
      // Enter seul → envoie le message
      e.preventDefault(); // évite le retour à la ligne
      sendMessage();
    }
  }
});

// Parcourt tous les messages et remplace le contenu par le HTML Markdown
document.querySelectorAll('.message').forEach(el => {
  el.innerHTML = marked.parse(el.innerHTML); // parse Markdown en HTML
});

const toggle = document.getElementById("yappingToggle");
let yapping = toggle.checked;

toggle.addEventListener("change", () => {
  yapping = toggle.checked;
  console.log("Yapping mode:", yapping);
  fetch("/toggleyapping", {method:"POST"});
});
