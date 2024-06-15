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