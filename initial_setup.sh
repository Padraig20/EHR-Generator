#!/bin/bash

echo "Creating a new virtual environment..."
python3 -m venv .venv

echo "Activating the virtual environment..."
source .venv/bin/activate

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Downloading spacy language model..."
python -m spacy download en_core_web_sm

echo "Moving into the 'data' directory..."
cd data || { echo "Directory 'data' does not exist. Exiting."; exit 1; }

echo "Downloading embeddings_icd.npy..."
wget https://github.com/Padraig20/EHR-Generator/releases/download/Embeddings/embeddings_icd.npy

echo "Downloading embeddings_ndc.npy..."
wget https://github.com/Padraig20/EHR-Generator/releases/download/Embeddings/embeddings_ndc.npy

echo "Setup complete. Move to the 'src' folder and invoke 'python api.py' to start the backend server."

