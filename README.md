
# EHR-Generator

A pipeline that extracts multiple medical entities from patient admission notes, maps them to their respective ICD/NDC code and outputs a standardized FHIR structure.

## Datasets

The ICD Codes were taken directly from the website for [Centers for Medicare & Medicaid Services](https://www.cms.gov/medicare/coding-billing/icd-10-codes/). 

The NDC Codes were taken from [openFDA](https://open.fda.gov/data/ndc/), but had to be thoroughly preprocessed for use. Each **proprietary name** and **non-proprietary name** was taken from each row, and used for two rows with the same NDC code in the resulting tsv file. Beware that non-unique entries were removed arbitrarily.

## Entity Matching

Currently, four different types of entities will be matched from the incoming admission notes:

- **Medical Conditions:** Long(er)-term diseases, such as *diabetes mellitus*, *ADHD* or *COVID-19*.
- **Symptoms:** Short-term conditions, which may indicate a medical condition. E.g. a *fever* may indicate *COVID-19*.
- **Medication/Treatment:** This includes both pharmaceuticals and physical treatments, such as *metformin* or *rehab*.
- **Surgical Procedures:** E.g. *coronary artery bypass grafting*.

The code and datasets for training for these NER models is done can be found in my [previous repository](https://github.com/Padraig20/Disease-Detection-NLP).

## ICD/NDC Code Matching

