import spacy
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

def extract_entities_sentences(nlp, ner_model, text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    sentence_offsets = [sent.start_char for sent in doc.sents]

    sentence_entities_batch = ner_model(sentences, batch_size=len(sentences)) #adjust batch size

    entities = []
    for sent_idx, sentence_entities in enumerate(sentence_entities_batch):
        start_offset = sentence_offsets[sent_idx]
        
        for entity in sentence_entities:
            entity_text = entity['word']
            entity_type = entity['entity_group']
            start = entity['start'] + start_offset
            end = entity['end'] + start_offset
            
            entities.append((entity_text, entity_type, start, end))

    return entities

def extract_entities_from_text(nlp, models, text):
    # reconstruct entities?
    entities = []
    for model in models:
        entity_name, ner_model = model
        model_specific_entities = extract_entities_sentences(nlp, ner_model, text)
        print(f"Extracted {len(model_specific_entities)} entities for {entity_name}")
        entities.extend(model_specific_entities)
    return entities

def process_text(entity_model, text):
    nlp = spacy.load("en_core_web_sm")
    loaded_models = [] # list of tuples (entity_name, ner_model)

    for entity_name, model_path in entity_model:
        #TODO change to new type of model saving
        #model = AutoModelForTokenClassification.from_pretrained(f"model_{model_path}")
        #tokenizer = AutoTokenizer.from_pretrained(f"tok_{model_path}")
        
        model = AutoModelForTokenClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
    
        label_to_ids = {
            f'B-{entity_name}': 0,
            f'I-{entity_name}': 1,
            'O': 2
        }
        ids_to_label = {
            0:f'B-{entity_name}',
            1:f'I-{entity_name}',
            2:'O'
        }
    
        model.config.id2label = ids_to_label
        model.config.label2id = label_to_ids
    
        ner_model = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    
        loaded_models.append((entity_name, ner_model))
    
    entities = extract_entities_from_text(nlp, loaded_models, text.strip())
    
    # entity reconstruction
    reconstructed_entities = []
    for entity in entities:
        entity_text = entity[0]
        entity_type = entity[1]
        start = entity[2]
        end = entity[3]

        if entity_text.startswith('##'):
            entity_text = entity_text[2:]
            if reconstructed_entities:
                prev_entity = reconstructed_entities[-1]
                prev_entity_text = prev_entity[0]
                prev_entity_type = prev_entity[1]
                prev_start = prev_entity[2]
                prev_end = prev_entity[3]
                                
                if prev_end == start:
                    reconstructed_text = prev_entity_text + entity_text
                    reconstructed_entities[-1] = (reconstructed_text, prev_entity_type, prev_start, end)
                    continue
        
        reconstructed_entities.append((entity_text, entity_type, start, end))
        
    entities = reconstructed_entities
    
    print(f"Extracted {len(entities)} entities in total (after reconstruction)")
    
    return entities

# input of script
#entity_model = [('MEDCOND', 'medcond'), ('SYMPTOM', 'symptom'), ('MEDICATION', 'medication'), ('PROCEDURE', 'procedure')]
#entity_model = [('MEDCOND', 'alvaroalon2/biobert_diseases_ner'), ('MEDICATION', 'alvaroalon2/biobert_chemical_ner')]
#text = "The patient has a history of diabetes and hypertension. He is currently taking metformin and lisinopril. The patient is scheduled for a coronary artery bypass grafting procedure."

#print(process_text(entity_model, text))
