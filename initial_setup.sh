#!/bin/bash

echo -e "\e[94mCreating a new virtual environment...\e[0m"
python3 -m venv .venv

echo -e "\e[94mActivating the virtual environment...\e[0m"
source .venv/bin/activate

echo -e "\e[94mInstalling dependencies from requirements.txt...\e[0m"
pip install -r requirements.txt

echo -e "\e[94mDownloading spacy language model...\e[0m"
python -m spacy download en_core_web_sm

echo -e "\e[94mMoving into the 'data' directory...\e[0m"
cd data || { echo "Directory 'data' does not exist. Exiting."; exit 1; }

echo -e "\e[94mDownloading embeddings_icd.npy...\e[0m"
wget https://github.com/Padraig20/EHR-Generator/releases/download/Embeddings/embeddings_icd.npy

echo -e "\e[94mDownloading embeddings_ndc.npy...\e[0m"
wget https://github.com/Padraig20/EHR-Generator/releases/download/Embeddings/embeddings_ndc.npy

echo -e "\e[95m\nSetup complete.\e[0m"
echo -e "\e[95mMove to the 'src' folder and invoke 'python api.py' to start the backend server.\n\e[0m"
echo -e "\e[91mMake sure to activate the virtual environment before running the server using 'source .venv/bin/activate'.\e[0m"

