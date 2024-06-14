import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm
import os

def get_embeddings_file(text_list, code_type = 'icd'):
    embeddings = []
    file_path = f'../data/embeddings_{code_type}.npy'
    if os.path.exists(file_path):
        embeddings = np.load(file_path)
    else:
        for i in tqdm(range(0, len(text_list), 10)): # stepsize
            batch = text_list[i:i+10]
            tokens = tokenizer(batch, return_tensors='pt', padding=True, truncation=True)
            with torch.no_grad():
                outputs = model(**tokens)
            batch_embeddings = outputs.last_hidden_state[:, 0, :].numpy()
            embeddings.extend(batch_embeddings)
        embeddings = np.array(embeddings)
        np.save(file_path, embeddings)
    return embeddings

def get_embeddings(text_list):
    tokens = tokenizer(text_list, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**tokens)
    embeddings = outputs.last_hidden_state[:, 0, :]
    return embeddings.numpy()

def load_icddata(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    data = []
    for line in lines:
        line_split = line.strip().split(' ')
        icd_code = line_split[0]
        description = line[len(icd_code):].strip()
        data.append((icd_code, description))

    return data

def load_ndcdata(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        lines = file.readlines()
    data = []
    for line in lines:
        line_split = line.strip().split('\t')
        ndc_code = line_split[0]
        description = line_split[1]
        data.append((ndc_code, description))

    return data

def find_nearest_icd_code(entity, threshold=0.5):
    entity_embedding = get_embeddings([entity])
    distance, index = nn_model_icd.kneighbors(entity_embedding)
    if distance[0][0] < threshold:
        nearest_icd_code = icd_codes[index[0][0]]
        description_for_icd_code = descriptions_icd[index[0][0]]
        return nearest_icd_code, description_for_icd_code
    else:
        return None, "No sufficiently similar ICD code found."

def find_nearest_ndc_code(entity, threshold=0.5):
    entity_embedding = get_embeddings([entity])
    distance, index = nn_model_ndc.kneighbors(entity_embedding)
    if distance[0][0] < threshold:
        nearest_ndc_code = ndc_codes[index[0][0]]
        description_for_ndc_code = descriptions_ndc[index[0][0]]
        return nearest_ndc_code, description_for_ndc_code
    else:
        return None, "No sufficiently similar NDC code found."

# ------- MAIN ------- #
    
tokenizer = AutoTokenizer.from_pretrained("cambridgeltl/SapBERT-from-PubMedBERT-fulltext")
model = AutoModel.from_pretrained("cambridgeltl/SapBERT-from-PubMedBERT-fulltext")

cm_data = load_icddata('../data/icd10cm_codes_2024.txt')
pcs_data = load_icddata('../data/icd10pcs_codes_2024.txt')
data_icd = cm_data + pcs_data
icd_codes, descriptions_icd = zip(*data_icd)
description_embeddings_icd = get_embeddings_file(descriptions_icd, code_type='icd')

data_ndc = load_ndcdata('../data/ndc_codes.tsv')
ndc_codes, descriptions_ndc = zip(*data_ndc)
description_embeddings_ndc = get_embeddings_file(descriptions_ndc, code_type='ndc')

nn_model_icd = NearestNeighbors(n_neighbors=1, metric='cosine').fit(description_embeddings_icd)
nn_model_ndc = NearestNeighbors(n_neighbors=1, metric='cosine').fit(description_embeddings_ndc)

def map_entities_to_ndc_icd_code(entities):
    normalized_entities = []
    for entity in entities:
        entity, ent_type, _, _ = entity
        if ent_type == 'MEDICATION':
            code, description = find_nearest_ndc_code(entity)
        else:
            code, description = find_nearest_icd_code(entity)
        if code:
            print(f"The {'NDC' if ent_type == 'MEDICATION' else 'ICD'} code for '{entity}' is {code}, for original description '{description}'")
            normalized_entities.append((entity, code, description))
        else:
            print(f"No {'NDC' if ent_type == 'MEDICATION' else 'ICD'} code found for '{entity}'")
            normalized_entities.append((entity, None, None))
    return normalized_entities

#entities = ["COPD", "interstitial lung disease", "hypertension", "bronchodilators", "steroids", "bingboingo bongboingo", "adhd", "attention deficit hyperactivity"]
#entities = ["hypertension", "metformin", "lisinopril", "diabetes"]

#entities = [('diabetes', 'MEDCOND', 29, 37), ('hypertension', 'MEDCOND', 42, 54), ('metformin', 'MEDICATION', 79, 88), ('lisinopril', 'MEDICATION', 93, 103)]
#print(map_entities_to_ndc_icd_code(entities))