# Providence – Assistant IA Contextuel (Projet perso, Linux uniquement)

**Providence** est un assistant IA local qui me suit discrètement pendant que je bosse.
Toutes les **1 minute 30**, il récupère ce que je vois à l'écran et ce que j'ai d'ouvert, pour me suggérer des **conseils ou remarques contextuelles**.

> Il parle (via [OpenVoice](https://github.com/myshell-ai/OpenVoice)), il réfléchit (avec un LLM local via [Ollama](https://ollama.com/)), et il reste 100% **local**.
> Pas de cloud, pas d’écoute indiscrète.

---

## À quoi ça sert ?

C’est un assistant qui :

* Observe l’écran à intervalles réguliers
* Lit le texte à l’écran via **OCR** (et vision si le modèle le permet)
* Identifie les fenêtres ouvertes
* Génère une réaction avec un modèle LLM local (ex : Mistral, Gemma…)
* Parle avec une voix custom (en français, japonais, anglais…)
* Ne dit rien si y’a rien d’utile à dire

---

## Installation

1. Créer un environnement conda :

```bash
conda create -n providence python=3.9
conda activate providence
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Installer les dépendances système :

### Arch Linux

```bash
sudo pacman -S tesseract libnotify wmctrl
```

### Ubuntu/Debian

```bash
sudo apt install tesseract-ocr libnotify-bin wmctrl
```
4. Installer correctement [**OpenVoice**](https://github.com/myshell-ai/OpenVoice) dans *"~/OpenVoice/"*.
Utiliser l'environement conda 'providence' créé plus tôt à la place de crée un nouvel environnement 'openvoice'.
(installer les checkpoints v1 et v2).

Aussi installer ollama (sinon on ne va pas aller très loin.)

5. Lancer avec :

```bash
./run.sh
```

---

## Synthèse vocale

Utilise [**OpenVoice**](https://github.com/myshell-ai/OpenVoice) pour lire les réponses à haute voix (optionnel mais fun).
Tu peux configurer une voix spécifique dans les ressources.

---

## Appels API

Providence expose quelques routes Flask :

| Méthode | URL              | Action                              |
| ------- | ---------------- | ----------------------------------- |
| POST    | `/eyelaunch`     | Démarre l'observation               |
| POST    | `/eyestop`       | Stoppe l'observation                |
| POST    | `/toggleyapping` | Active/désactive la synthèse vocale |
| POST    | `/shutdown`      | Ferme proprement le serveur Flask   |

---

## Vie privée

Tout est **local** :

* Pas d’appel vers le cloud
* Pas de stockage externe
* Les screenshots temporaires sont automatiquement supprimés

---

## À venir

* Détection vocale ou hotword
* Interface de chat
* Meilleure personnalisation des réactions

---

## Licence

MIT — Utilisation libre. Forks bienvenus.