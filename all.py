import os
import re
import xml.etree.ElementTree as ET

# Define the path to the 'Forms' folder
forms_folder = "Forms"

# Initialize dictionaries to store relationships
step_to_child = set()
referenced_child = set()
lookup_relationship = set()
temp_set = set()
child_pattern = re.compile(r"STEP TO CHILD \[([^\]]+)\]")

# Iterate over each entity folder
for entity_folder in os.listdir(forms_folder):  
    entity_path = os.path.join(forms_folder, entity_folder)
    if os.path.isdir(entity_path):
        eform_file = os.path.join(entity_path, "eform.xml")
        eform_filename = eform_file.split('\\')[1]
        if os.path.exists(eform_file):
            tree = ET.parse(eform_file)
            root = tree.getroot()
            # Search for child and parent relationships in Text nodes
            for text_node in root.findall(".//{http://ebms.com.au/schema/interchange/1.1}Text"): 
                text_content = text_node.text 
                if text_content:
                    child_matches = child_pattern.findall(text_content)
                    for child_entity in child_matches:
                        if child_entity and not child_entity.startswith("$") and not child_entity.startswith("["):
                           temp_set.add(child_entity)
            if len(temp_set)>0:                           
                group_data = ", ".join(map(str, sorted(temp_set)))
                step_to_child.add(f"|{eform_filename} | {group_data} |")
                temp_set = set()        
            # Inside the loop for reference group relationships
            for group in root.findall(".//{http://ebms.com.au/schema/interchange/1.1}ReferenceGroups/{http://ebms.com.au/schema/interchange/1.1}Group"):
                linked_text = group.find("{http://ebms.com.au/schema/interchange/1.1}ReferencedEForm").text
                if linked_text:
                    temp_set.add(linked_text)
            if len(temp_set)>0:
                group_data = ", ".join(map(str, sorted(temp_set)))
                referenced_child.add(f"|{eform_filename} | {group_data} |")
                temp_set = set()     
            # Inside the loop for DB_LOOKUP relationships
            for column in root.findall(".//{http://ebms.com.au/schema/interchange/1.1}Column"):
                formula = column.get("Formula")
                default_formula = column.get("DefaultValueFormula")
                if formula and "DB_LOOKUP" in formula:
                    db_lookup_parts = formula.split("DB_LOOKUP(")
                    if len(db_lookup_parts) > 1:
                        db_lookup_text = db_lookup_parts[1].split(",")[1].strip()
                        if db_lookup_text.startswith(("\"")):
                            db_lookup_clean = db_lookup_text.split("\"")[1]
                            temp_set.add(db_lookup_clean)
                elif default_formula and "DB_LOOKUP" in default_formula:
                    db_lookup_parts = default_formula.split("DB_LOOKUP(")
                    if len(db_lookup_parts) > 1:
                        db_lookup_text = db_lookup_parts[1].split(",")[1].strip()
                        if db_lookup_text.startswith(("\"")):
                           db_lookup_clean = db_lookup_text.split("\"")[1]
                           temp_set.add(db_lookup_clean)
            if len(temp_set)>0:
                eform_filename = eform_file.split('\\')[1]
                group_data = ", ".join(map(str, sorted(temp_set)))
                lookup_relationship.add(f"| {eform_filename} | {group_data} |")
                temp_set = set()
# print the step to child relationships
print("\n--------------------\nStepTo relationship\n--------------------\n")
print("| eForm | related forms | \n |------------|----------|")
for steptoreference in sorted(step_to_child):
    print(steptoreference)
# print the referenced relationships
print("\n--------------------\nReferenced Relationships\n--------------------\n")
print("| eForm | related forms | \n |------------|----------|")
for childreference in sorted(referenced_child):
    print(childreference)
# print the look up releationships 
print("\n--------------------\nLook Up Relationships\n--------------------\n")
print("| eForm | related forms | \n |------------|----------|")
for lookreference in sorted(lookup_relationship):
    print(lookreference)