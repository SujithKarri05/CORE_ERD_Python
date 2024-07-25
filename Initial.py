import os
import re
import xml.etree.ElementTree as ET

# Define the path to the 'Forms' folder
forms_folder = "Forms"

# Initialize dictionaries to store relationships
linked_relationships = {}
child_relationships = set()
parent_relationships = set()
child_pattern = re.compile(r"STEP TO CHILD \[([^\]]+)\]")

# Iterate over each entity folder
for entity_folder in os.listdir(forms_folder): #looping 
    entity_path = os.path.join(forms_folder, entity_folder) #path
    if os.path.isdir(entity_path): #if directory
        eform_file = os.path.join(entity_path, "eform.xml") #find file
        if os.path.exists(eform_file): #if exists
            tree = ET.parse(eform_file) #parse file
            root = tree.getroot() #assignmentt ?

            # Search for child and parent relationships in Text nodes
            for text_node in root.findall(".//{http://ebms.com.au/schema/interchange/1.1}Text"): #search for this link
                text_content = text_node.text #?
                if text_content: #if the content
                    child_matches = child_pattern.findall(text_content) #Checking for step to
                    for child_entity in child_matches: #each match
                        if child_entity and not child_entity.startswith("$") and not child_entity.startswith("["): #filter
                            child_relationships.add(child_entity) #list them
                        
            # Inside the loop for reference group relationships
            for group in root.findall(".//{http://ebms.com.au/schema/interchange/1.1}ReferenceGroups/{http://ebms.com.au/schema/interchange/1.1}Group"):
                linked_text = group.find("{http://ebms.com.au/schema/interchange/1.1}ReferencedEForm").text
                if linked_text:
                    linked_relationships.setdefault(entity_folder, []).append(linked_text)

            # Inside the loop for DB_LOOKUP relationships
            for column in root.findall(".//{http://ebms.com.au/schema/interchange/1.1}Column"):
                formula = column.get("Formula")
                default_formula = column.get("DefaultValueFormula")
                if formula and "DB_LOOKUP" in formula:
                    db_lookup_parts = formula.split("DB_LOOKUP(")
                    if len(db_lookup_parts) > 1:
                        db_lookup_text = db_lookup_parts[1].split(",")[1].strip()
                        if not db_lookup_text.startswith(("[", "$", "<", ">", "ARRAY_", "\"")):
                            linked_relationships.setdefault(entity_folder, []).append(db_lookup_text)
                elif default_formula and "DB_LOOKUP" in default_formula:
                    db_lookup_parts = default_formula.split("DB_LOOKUP(")
                    if len(db_lookup_parts) > 1:
                        db_lookup_text = db_lookup_parts[1].split(",")[1].strip()
                        if not db_lookup_text.startswith(("[", "$", "<", ">", "ARRAY_", "\"")):
                            linked_relationships.setdefault(entity_folder, []).append(db_lookup_text)

# Print sorted relationships
print("\n--------------------\nLinked relationships:\n--------------------\n")
for entity_folder, linked_texts in sorted(linked_relationships.items()):
    for linked_text in sorted(set(linked_texts)):
        print(linked_text)

# Print child relationships
print("\n--------------------\nParent -> Child relationships:\n--------------------\n")
for child_entity in sorted(set(child_relationships)):
    print(f"Action -> {child_entity}")