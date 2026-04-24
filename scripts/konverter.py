import xml.etree.ElementTree as ET
import json
import glob
import os

# Find den hentede XML-fil
xml_filer = glob.glob('./ny-fil/*.xml')
if not xml_filer:
    print("Ingen XML-fil fundet")
    exit(1)

xml_fil = xml_filer[0]
print(f"Behandler: {xml_fil}")

# Parse XML
tree = ET.parse(xml_fil)
rod = tree.getroot()

# Hent dato fra XML selv (ikke fra systemdatoen)
day = rod.find('Date/Day').text
month = rod.find('Date/Month').text
year = rod.find('Date/Year').text
dato = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

# Hent biograf-info
company = {
    "CompanyID": rod.find('Company/CompanyID').text,
    "CompanyName": rod.find('Company/CompanyName').text,
    "TicketingSystem": rod.find('Company/TicketingSystem').text
}

# Hent alle forestillinger
forestillinger = []
for show in rod.findall('Shows/Show'):
    film = show.find('Film')
    theatre = show.find('Theatre')
    showtime = show.find('ShowTime')

    kategorier = []
    for kat in show.findall('TicketCategory'):
        kategorier.append({
            "navn": kat.find('TicketCategoryName').text,
            "pris": int(kat.find('Price').text),
            "solgt": int(kat.find('Sales').text)
        })

    total_solgt = sum(k['solgt'] for k in kategorier)
    total_omsaetning = sum(k['pris'] * k['solgt'] for k in kategorier)

    forestillinger.append({
        "film": {
            "id": film.find('FilmID').text,
            "titel": film.find('FilmTitle').text,
            "land_aar": film.find('landaar').text,
            "genre": film.find('genrer').text,
            "instruktion": film.find('instruktion').text,
            "skuespil": film.find('skuespil').text,
            "udlejer": film.find('udlejer').text
        },
        "sal": {
            "id": theatre.find('TheatreID').text,
            "navn": theatre.find('TheatreName').text
        },
        "starttid": f"{showtime.find('Hour').text.zfill(2)}:{showtime.find('Min').text.zfill(2)}",
        "billetkategorier": kategorier,
        "total_solgte_billetter": total_solgt,
        "total_omsaetning_øre": total_omsaetning
    })

# Byg dagens objekt
dagens_data = {
    "dato": dato,
    "biograf": company,
    "antal_forestillinger": len(forestillinger),
    "forestillinger": forestillinger
}

# Læs eksisterende historik og undgå dubletter
data_fil = './data/data.json'
if os.path.exists(data_fil):
    with open(data_fil, 'r', encoding='utf-8') as f:
        historik = json.load(f)
    historik = [d for d in historik if d['dato'] != dato]
else:
    historik = []

historik.append(dagens_data)
historik.sort(key=lambda x: x['dato'])

os.makedirs('./data', exist_ok=True)
with open(data_fil, 'w', encoding='utf-8') as f:
    json.dump(historik, f, ensure_ascii=False, indent=2)

print(f"Gemt {len(forestillinger)} forestillinger for {dato}. Historik: {len(historik)} dage.")
