import xml.etree.ElementTree as ET
import json
import glob
import os
from datetime import datetime

# Find den hentede XML-fil
xml_filer = glob.glob('./ny-fil/*.xml')
if not xml_filer:
    print("Ingen XML-fil fundet")
    exit(1)

xml_fil = xml_filer[0]
print(f"Behandler: {xml_fil}")

# Læs eksisterende data hvis den findes
data_fil = './data/data.json'
if os.path.exists(data_fil):
    with open(data_fil, 'r', encoding='utf-8') as f:
        eksisterende = json.load(f)
else:
    eksisterende = []

# Parse XML
tree = ET.parse(xml_fil)
rod = tree.getroot()

# Konverter XML-elementer til dictionary
def xml_til_dict(element):
    result = {}
    for barn in element:
        if len(barn) > 0:
            result[barn.tag] = xml_til_dict(barn)
        else:
            result[barn.tag] = barn.text
    return result

ny_data = {
    "dato": datetime.now().strftime('%Y-%m-%d'),
    "data": xml_til_dict(rod)
}

# Tilføj ny data til historik
eksisterende.append(ny_data)

# Gem samlet JSON
os.makedirs('./data', exist_ok=True)
with open(data_fil, 'w', encoding='utf-8') as f:
    json.dump(eksisterende, f, ensure_ascii=False, indent=2)

print(f"Gemt {len(eksisterende)} poster i data.json")
