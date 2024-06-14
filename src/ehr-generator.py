from extractors.extract_entities import process_text
from extractors.extract_icd_ndc import map_entities_to_ndc_icd_code

text = 'The patient was prescribed 100mg of aspirin for 5 days. Patient has a history of diabetes and hypertension. He is currently taking metformin and lisinopril. The patient is scheduled for a coronary artery bypass grafting procedure.'

entity_model = [('MEDCOND', 'alvaroalon2/biobert_diseases_ner'), ('MEDICATION', 'alvaroalon2/biobert_chemical_ner')]

entities = process_text(entity_model, text)

normalized_entities = map_entities_to_ndc_icd_code(entities)

print(normalized_entities)