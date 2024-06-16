import argparse
parser = argparse.ArgumentParser(description='Backend allowing for generation of EHR records via API.')

args = parser.parse_args()

print("Preparing backend...")

from extractors.extract_entities import process_text, load_models
from extractors.extract_icd_ndc import map_entities_to_ndc_icd_code
from extractors.generate_fhir import knit_fhir_resources

from gevent.pywsgi import WSGIServer # Imports the WSGIServer
#from gevent import monkey; monkey.patch_all()
from flask import Flask, request, jsonify
from flask_cors import CORS

def generate_ehr(text, nlp, loaded_models, patient_id='example/patient'):

    entities = process_text(nlp, loaded_models, text)

    normalized_entities = map_entities_to_ndc_icd_code(entities)
    
    print(normalized_entities)
    
    ehr_record = knit_fhir_resources(normalized_entities, patient_id)
    return ehr_record, entities, normalized_entities

# preparing backend

entity_model = [('MEDCOND', 'medcond'), ('MEDICATION', 'medication'), ('PROCEDURE', 'procedure'), ('SYMPTOM', 'symptom')]
nlp, loaded_models = load_models(entity_model)

app = Flask(__name__)
CORS(app)  # Initialize CORS
port = 5000

print("Serving API now...")

@app.route('/extract_entities', methods=['POST'])
def main():
    text = request.get_data(as_text=True)
    ehr, entities, normalized_entities = generate_ehr(text, nlp, loaded_models)
    return jsonify({'ehr': ehr, 'entities': entities, 'normalized_entities': normalized_entities})

if __name__ == '__main__':
    LISTEN = ('0.0.0.0',port)
    http_server = WSGIServer( LISTEN, app )
    http_server.serve_forever()
