
# 📝 EHR-Generator

A pipeline that extracts multiple medical entities from patient admission notes, maps them to their respective ICD/NDC code and outputs a standardized FHIR structure.

## 📊 Datasets

The ICD Codes were taken directly from the website for [Centers for Medicare & Medicaid Services](https://www.cms.gov/medicare/coding-billing/icd-10-codes/). 

The NDC Codes were taken from [openFDA](https://open.fda.gov/data/ndc/), but had to be thoroughly preprocessed for use. Each **proprietary name** and **non-proprietary name** was taken from each row, and used for two rows with the same NDC code in the resulting tsv file. Beware that non-unique entries were removed arbitrarily.

## 💊 Entity Matching

Currently, four different types of entities will be matched from the incoming admission notes:

- **Medical Conditions:** Long(er)-term diseases, such as *diabetes mellitus*, *ADHD* or *COVID-19*.
- **Symptoms:** Short-term conditions, which may indicate a medical condition. E.g. a *fever* may indicate *COVID-19*.
- **Medication/Treatment:** This includes both pharmaceuticals and physical treatments, such as *metformin* or *rehab*.
- **Surgical Procedures:** E.g. *coronary artery bypass grafting*.

The code and datasets for training for these NER models is done can be found in my [previous repository](https://github.com/Padraig20/Disease-Detection-NLP).

## 🔍 ICD/NDC Code Matching

For medical entity normalization, we leverage **SapBERT** to create embeddings for ICD (International Classification of Diseases) and NDC (National Drug Code). The core functionalities include generating embeddings for these codes, performing nearest neighbor searches, and determining the cosine similarity between embeddings to find the closest matches based on a defined threshold.

#### SapBERT

[SapBERT](https://github.com/cambridgeltl/SapBERT) is a BERT-based model pretrained on PubMed articles, specifically designed for creating biomedical embeddings. In this project, SapBERT is used to generate dense vector representations (embeddings) for both ICD and NDC codes, which are then utilized for similarity searches.

#### Embedding Generation

The code provides functions to generate embeddings for lists of text descriptions associated with ICD and NDC codes. Embeddings are saved to files to avoid recomputation and can be downloaded from the first release of this repository:

-   **`get_embeddings_file(text_list, code_type)`**: Generates or loads embeddings from a file for a given list of text descriptions.
-   **`get_embeddings(text_list)`**: Directly generates embeddings for a provided list of text descriptions without saving them.

#### Nearest Neighbor Search

To find the most similar code based on text descriptions, the code uses a nearest neighbor search with *k=1*:

-   **`find_nearest_icd_code(entity, threshold)`**: Finds the nearest ICD code for a given entity based on a cosine similarity threshold. Returns the code and its description if a similar code is found.
-   **`find_nearest_ndc_code(entity, threshold)`**: Finds the nearest NDC code for a given entity based on a cosine similarity threshold. Returns the code and its description if a similar code is found.

#### Cosine Similarity with Threshold

Cosine similarity is used to measure the similarity between the embeddings of the input text and the embeddings of the medical codes. The nearest neighbor search is constrained by a similarity threshold to ensure only sufficiently similar codes are considered valid matches. This threshold is adjustable:

-   For ICD codes, the default threshold is set to **0.4**.
-   For NDC codes, the default threshold is set to **0.3**.

## 🔥 FHIR Bunde Structuring

The resulting (normalized) entities can be structured into FHIR (Fast Healthcare Interoperability Resources) resources from HL7 (Health Level 7). FHIR is a standard for exchanging healthcare information electronically. Each entity is grouped into the fitting resource, as can be seen in the [FHIR Resourceguide](https://www.hl7.org/fhir/resourceguide.html).

The patient ID is necessary and can be added into the system manually (is not automatically extracted from text due to ambiguous format).

- **<code\>** will be replaced with the ICD/NDC code.
- **<description\>** will be replaced with the normalized expression (i.e. the expression linked to the ICD/NDC code).
- **<extracted_text\>** will be replaced with the text that has been extracted via the respective NER model.
-  **<patient-id\>** will be replaced with the patient ID that has been input by the user.

Beware that in the resource type for *Condition*, the clinical status is required by design, but set to *Unknown* by default. It is not extracted by the system and would need to be added manually by the user.

#### Symptom

```json
{
  "resource": {
    "resourceType": "Condition",
    "clinicalStatus": {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
          "code": "unknown"
        }
      ]
    },
    "code": {
      "coding": [
        {
          "system": "http://hl7.org/fhir/sid/icd-10",
          "code": "<code>",
          "display": "<description>"
        }
      ],
      "text": "<extracted_text>"
    },
    "subject": {
      "reference": "<patient-id>"
    },
    "note": [
      {
        "text": "symptom"
      }
    ]
  }
}
```

#### Medical Condition

````json
{
  "resource": {
    "resourceType": "Condition",
    "clinicalStatus": {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
          "code": "unknown"
        }
      ]
    },
    "code": {
      "coding": [
        {
          "system": "http://hl7.org/fhir/sid/icd-10",
          "code": "<code>",
          "display": "<description>"
        }
      ],
      "text": "<extracted_text>"
    },
    "subject": {
      "reference": "<patient-id>"
    },
    "note": [
      {
        "text": "medical condition"
      }
    ]
  }
}
````

#### Medication/Treatment

````json
{
  "resource": {
    "resourceType": "Medication",
    "code": {
      "coding": [
        {
          "system": "http://hl7.org/fhir/sid/ndc",
          "code": "<code>",
          "display": "<description>"
        }
      ],
      "text": "<extracted_text>"
    }
  }
}
````

#### Surgical Procedure

````json
{
  "resource": {
    "resourceType": "Procedure",
    "code": {
      "coding": [
        {
          "system": "http://hl7.org/fhir/sid/icd-10",
          "code": "<code>",
          "display": "<description>"
        }
      ],
      "text": "<extracted_text>"
    },
    "subject": {
      "reference": "<patient-id>"
    }
  }
}
````

#### Example of FHIR Bundle Output

````json
{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [
    {
      "resource": {
        "resourceType": "Condition",
        "clinicalStatus": {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
              "code": "unknown"
            }
          ]
        },
        "code": {
          "coding": [
            {
              "system": "http://hl7.org/fhir/sid/icd-10",
              "code": "R7303",
              "display": "Prediabetes"
            }
          ],
          "text": "diabetes"
        },
        "subject": {
          "reference": "example/patient"
        },
        "note": [
          {
            "text": "medical condition"
          }
        ]
      }
    },
    {
      "resource": {
        "resourceType": "Condition",
        "clinicalStatus": {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
              "code": "unknown"
            }
          ]
        },
        "code": {
          "coding": [
            {
              "system": "http://hl7.org/fhir/sid/icd-10",
              "code": "I10",
              "display": "Essential (primary) hypertension"
            }
          ],
          "text": "hypertension"
        },
        "subject": {
          "reference": "example/patient"
        },
        "note": [
          {
            "text": "medical condition"
          }
        ]
      }
    },
    {
      "resource": {
        "resourceType": "Medication",
        "code": {
          "coding": [
            {
              "system": "http://hl7.org/fhir/sid/ndc",
              "code": "0378-6001",
              "display": "metformin"
            }
          ],
          "text": "metformin"
        }
      }
    },
    {
      "resource": {
        "resourceType": "Medication",
        "code": {
          "coding": [
            {
              "system": "http://hl7.org/fhir/sid/ndc",
              "code": "0591-0405",
              "display": "Lisinopril"
            }
          ],
          "text": "lisinopril"
        }
      }
    },
    {
      "resource": {
        "resourceType": "Condition",
        "clinicalStatus": {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
              "code": "unknown"
            }
          ]
        },
        "code": {
          "coding": [
            {
              "system": "http://hl7.org/fhir/sid/icd-10",
              "code": "R519",
              "display": "Headache, unspecified"
            }
          ],
          "text": "headache"
        },
        "subject": {
          "reference": "example/patient"
        },
        "note": [
          {
            "text": "symptom"
          }
        ]
      }
    },
    {
      "resource": {
        "resourceType": "Procedure",
        "code": {
          "coding": [
            {
              "system": "http://hl7.org/fhir/sid/icd-10",
              "code": "I25709",
              "display": "Atherosclerosis of coronary artery bypass graft(s), unspecified, with unspecified angina pectoris"
            }
          ],
          "text": "coronary artery bypass grafting"
        },
        "subject": {
          "reference": "example/patient"
        }
      }
    }
  ]
}
````
