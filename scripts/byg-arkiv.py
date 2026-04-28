import xml.etree.ElementTree as ET
import json
import os
import subprocess
from datetime import date, timedelta

def parse_xml_fil(xml_fil):
    try:
        tree = ET.parse(xml_fil)
        rod = tree.getroot()

        day = rod.find('Date/Day').text
        month = rod.find('Date/Month').text
        year = rod.find('Date/Year').text
        dato = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        company = {
            "CompanyID": rod.find('Company/CompanyID').text,
            "CompanyName": rod.find('Company/CompanyName').text,
            "TicketingSystem": rod.find('Company/TicketingSystem').text
        }

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

        return {
            "dato": dato,
            "aar": year,
            "maaned": month.zfill(2),
            "biograf": company,
            "antal_forestillinger": len(forestillinger),
            "forestillinger": forestillinger
        }
    except Exception as e:
        print(f"  Fejl ved parsing af {xml_fil}: {e}")
        return None

# Loop fra 2013 til i dag
start = date(2013, 1, 1)
slut = date.today()
aktuel = start

# { "2026-04": [...], "2026-05": [...], ... }
maanedsdata = {}

ftp_host = os.environ['FTP_HOST']
ftp_user = os.environ['FTP_USER']
ftp_pass = os.environ['FTP_PASS']

print(f"Henter data fra {start} til {slut}...")

while aktuel <= slut:
    dato_str = aktuel.strftime('%Y%m%d')
    aar = str(aktuel.year)
    maaned = aktuel.strftime('%m')
    maaned_nøgle = f"{aar}-{maaned}"
    filnavn = f"{dato_str}_179_roedovre.xml"

    os.makedirs('./tmp-arkiv', exist_ok=True)
    lokal_fil = f"./tmp-arkiv/{filnavn}"

    subprocess.run([
        'lftp', '-u', f"{ftp_user},{ftp_pass}", ftp_host,
        '-e', f'set ssl:verify-certificate no; get -O ./tmp-arkiv/ {filnavn}; bye'
    ], capture_output=True, text=True)

    if os.path.exists(lokal_fil):
        data = parse_xml_fil(lokal_fil)
        if data:
            if maaned_nøgle not in maanedsdata:
                maanedsdata[maaned_nøgle] = []
            maanedsdata[maaned_nøgle].append(data)
            print(f"  ✓ {dato_str} – {data['antal_forestillinger']} forestillinger")
        os.remove(lokal_fil)
    else:
        print(f"  – {dato_str} ikke fundet")

    aktuel += timedelta(days=1)

# Gem én fil per måned
os.makedirs('./data', exist_ok=True)
for maaned_nøgle, dage in maanedsdata.items():
    dage.sort(key=lambda x: x['dato'])
    fil = f"./data/{maaned_nøgle}.json"
    with open(fil, 'w', encoding='utf-8') as f:
        json.dump(dage, f, ensure_ascii=False, indent=2)
    print(f"Gemt {fil} med {len(dage)} dage")

print("Arkiv færdigt!")
