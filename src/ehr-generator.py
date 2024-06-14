from extractors.extract_entities import process_text
from extractors.extract_icd_ndc import map_entities_to_ndc_icd_code
import json

def get_medication_fhir_resource(extracted_text, code, description):
    with open('../fhir-resources/medication.json', 'r') as f:
        medication = f.read()
        
        if not code:
            medication = json.loads(medication)
            del medication['resource']['code']['coding']
            medication = json.dumps(medication)
        else:
            medication = medication.replace('<code>', code)
            medication = medication.replace('<description>', description)
        medication = medication.replace('<extracted_text>', extracted_text)
        return medication

def get_condition_fhir_resource(extracted_text, code, description, patient_id):
    with open('../fhir-resources/medcond.json', 'r') as f:
        condition = f.read()

        if not code:
            condition = json.loads(condition)
            del condition['resource']['code']['coding']
            condition = json.dumps(condition)
        else:
            condition = condition.replace('<code>', code)
            condition = condition.replace('<description>', description)
        condition = condition.replace('<extracted_text>', extracted_text)
        condition = condition.replace('<patient-id>', patient_id)
        return condition

def get_procedure_fhir_resource(extracted_text, code, description, patient_id):
    with open('../fhir-resources/procedure.json', 'r') as f:
        procedure = f.read()

        if not code:
            procedure = json.loads(procedure)
            del procedure['resource']['code']['coding']
            procedure = json.dumps(procedure)
        else:
            procedure = procedure.replace('<code>', code)
            procedure = procedure.replace('<description>', description)
        procedure = procedure.replace('<extracted_text>', extracted_text)
        procedure = procedure.replace('<patient-id>', patient_id)
        return procedure

def get_symptom_fhir_resource(extracted_text, code, description, patient_id):
    with open('../fhir-resources/symptom.json', 'r') as f:
        symptom = f.read()

        if not code:
            symptom = json.loads(symptom)
            del symptom['resource']['code']['coding']
            symptom = json.dumps(symptom)
        else:
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
    
    print(normalized_entities)
    
    ehr_record = knit_fhir_resources(normalized_entities, patient_id)
    return ehr_record

text = """This is a 44 year old female with PMH of PCOS, Obesity, HTN who presented with symptoms of cholecystitis and was found incidentally to have a large pericardial effusion. A pericardiocentesis was performed and the fluid analysis was consistent with Burkitt's lymphoma. Pericardial fluid was kappa light chain restricted CD10 positive monotypic B cells expressing FMC-7, CD19, CD20, and myc rearrangement consistent with Burkitt's Lymphoma. A subsequent lumbar puncture and bone marrow biopsy were negative for any involvement which made this a primary cardiac lymphoma. A cardiac MRI showed a mass that was 3cm x 1cm on the lateral wall of the right atrium adjacent to the AV junction. Past Medical History: 1. Rare migraines 2. HTN 3. Obesity 4. PCOS/infertility 5. Viral encephalitis/meningitis-->ICH-->seizure/stroke ([**2137**]) =- from severe sinus infxn, caused mild non-focal residual deficits 6. CSF leak w/ meningitis s/p lumbar drain placement 7. R LE DVT s/p IVC filter placement 8. Knee surgery"""
entity_model = [('MEDCOND', 'alvaroalon2/biobert_diseases_ner'), ('MEDICATION', 'alvaroalon2/biobert_chemical_ner')]
print(generate_ehr(text, entity_model))