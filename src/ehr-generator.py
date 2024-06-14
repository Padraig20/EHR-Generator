from extractors.extract_entities import process_text
from extractors.extract_icd_ndc import map_entities_to_ndc_icd_code
import json

def get_medication_fhir_resource(extracted_text, code, description):
    with open('../fhir-resources/medication.json', 'r') as f:
        medication = f.read()
        medication = medication.replace('<code>', code)
        medication = medication.replace('<description>', description)
        medication = medication.replace('<extracted_text>', extracted_text)
        return medication

def get_condition_fhir_resource(extracted_text, code, description, patient_id):
    with open('../fhir-resources/medcond.json', 'r') as f:
        condition = f.read()
        condition = condition.replace('<code>', code)
        condition = condition.replace('<description>', description)
        condition = condition.replace('<extracted_text>', extracted_text)
        condition = condition.replace('<patient-id>', patient_id)
        return condition

def get_procedure_fhir_resource(extracted_text, code, description, patient_id):
    with open('../fhir-resources/procedure.json', 'r') as f:
        procedure = f.read()
        procedure = procedure.replace('<code>', code)
        procedure = procedure.replace('<description>', description)
        procedure = procedure.replace('<extracted_text>', extracted_text)
        procedure = procedure.replace('<patient-id>', patient_id)
        return procedure

def get_symptom_fhir_resource(extracted_text, code, description, patient_id):
    with open('../fhir-resources/symptom.json', 'r') as f:
        symptom = f.read()
        symptom = symptom.replace('<code>', code)
        symptom = symptom.replace('<description>', description)
        symptom = symptom.replace('<extracted_text>', extracted_text)
        symptom = symptom.replace('<patient-id>', patient_id)
        return symptom

def knit_fhir_resources(normalized_entities, patient_id):
    fhir_resources = ""
    for entity in normalized_entities:
        entity, code, description, ent_type = entity
        if ent_type == 'MEDICATION':
            fhir_resources = fhir_resources + get_medication_fhir_resource(entity, code, description) + ","
        elif ent_type == 'MEDCOND':
            fhir_resources = fhir_resources + get_condition_fhir_resource(entity, code, description, patient_id) + ","
        elif ent_type == 'PROCEDURE':
            fhir_resources = fhir_resources + get_procedure_fhir_resource(entity, code, description, patient_id) + ","
        elif ent_type == 'SYMPTOM':
            fhir_resources = fhir_resources + get_symptom_fhir_resource(entity, code, description, patient_id) + ","
    
    if len(fhir_resources) > 0:
        fhir_resources = fhir_resources[:-1]
    
    with open('../fhir-resources/general.json', 'r') as f:
        general = f.read()
        
    ehr_record = json.loads(general.replace('"<input>"', fhir_resources))
    
    return ehr_record

def generate_ehr(text, entity_model, patient_id='example/patient'):

    entities = process_text(entity_model, text)

    normalized_entities = map_entities_to_ndc_icd_code(entities)
    
    ehr_record = knit_fhir_resources(normalized_entities, patient_id)
    return ehr_record

text = 'The patient was prescribed 100mg of aspirin for 5 days. Patient has a history of diabetes and hypertension. He is currently taking metformin and lisinopril. The patient is scheduled for a coronary artery bypass grafting procedure.'
entity_model = [('MEDCOND', 'alvaroalon2/biobert_diseases_ner'), ('MEDICATION', 'alvaroalon2/biobert_chemical_ner')]
print(generate_ehr(text, entity_model))