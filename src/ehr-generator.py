from extractors.extract_entities import process_text, load_models
from extractors.extract_icd_ndc import map_entities_to_ndc_icd_code
from extractors.generate_fhir import knit_fhir_resources

def generate_ehr(text, entity_model, patient_id='example/patient'):
    
    nlp, loaded_models = load_models(entity_model)

    entities = process_text(nlp, loaded_models, text)

    normalized_entities = map_entities_to_ndc_icd_code(entities)
    
    print(normalized_entities)
    
    ehr_record = knit_fhir_resources(normalized_entities, patient_id)
    return ehr_record

text = """This is a 44 year old female with PMH of PCOS, Obesity, HTN who presented with symptoms of cholecystitis and was found incidentally to have a large pericardial effusion. A pericardiocentesis was performed and the fluid analysis was consistent with Burkitt's lymphoma. Pericardial fluid was kappa light chain restricted CD10 positive monotypic B cells expressing FMC-7, CD19, CD20, and myc rearrangement consistent with Burkitt's Lymphoma. A subsequent lumbar puncture and bone marrow biopsy were negative for any involvement which made this a primary cardiac lymphoma. A cardiac MRI showed a mass that was 3cm x 1cm on the lateral wall of the right atrium adjacent to the AV junction. Past Medical History: 1. Rare migraines 2. HTN 3. Obesity 4. PCOS/infertility 5. Viral encephalitis/meningitis-->ICH-->seizure/stroke ([**2137**]) =- from severe sinus infxn, caused mild non-focal residual deficits 6. CSF leak w/ meningitis s/p lumbar drain placement 7. R LE DVT s/p IVC filter placement 8. Knee surgery"""
entity_model = [('MEDCOND', 'alvaroalon2/biobert_diseases_ner'), ('MEDICATION', 'alvaroalon2/biobert_chemical_ner')]
print(generate_ehr(text, entity_model))