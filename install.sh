#!/bin/bash

set -e

function info {
  echo -e "\033[1;34m[INFO]\033[0m $1"
}

function error {
  echo -e "\033[1;31m[ERROR]\033[0m $1"
  exit 1
}

if ! command -v ollama &> /dev/null; then
    info "Ollama is not installed, downloading Ollama..."
    
    curl -fsSL https://ollama.com/install.sh | sh || error "Error while downloading Ollama"
else
    info "Ollama already installed."
fi

if [ ! -d ".venv" ]; then
    info "Creation of a Virtual Environement..."
    python3 -m venv .venv || error "Error while creating environement"
else
    info "Virtual Environement already exist"
fi

# Activation de l'environnement virtuel
source .venv/bin/activate || error "Error while activating .venv"

# Installation des dépendances
if [ -f requirements.txt ]; then
    info "Downloading dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt || error "Error while downloading requirements"
else
    info "requirements.txt not found..."
fi

info "Installation done, make sure to install the packet dependencies for your linux distro..."