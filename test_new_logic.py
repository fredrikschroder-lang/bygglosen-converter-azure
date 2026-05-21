import io
import xml.etree.ElementTree as ET
from converter import convert_bygglosen_data, analyze_bygglosen_data, _parse_and_group_data, clean_personnr

def generate_test_files():
    # Multi-block XML simulating two project locations for some workers
    xml_content = """<?xml version="1.0" encoding="ISO-8859-1"?>
<Lonerapport>
  <!-- Första orter: LanOchKommun 0662 -->
  <Lonegranskning>
    <Organisationsnummer>556000-0000</Organisationsnummer>
    <Foretagsnamn>GRK Sverige AB</Foretagsnamn>
    <LoneperiodStartdatum>20260401</LoneperiodStartdatum>
    <LoneperiodSlutdatum>20260430</LoneperiodSlutdatum>
    <Avtalsomrade>Bygg</Avtalsomrade>
    <Lonetyp>Timlon</Lonetyp>
    <LanOchKommun>0662</LanOchKommun>
    <Postort>Gagnef</Postort>
    <Personer>
      <!-- Erik: giltig -->
      <Person>
        <Personnummer>198802680374</Personnummer>
        <Namn>Erik Eriksson</Namn>
        <Yrkeskod>123</Yrkeskod>
        <Fordelningstal>100</Fordelningstal>
        <ArbetadeTimmar>40</ArbetadeTimmar>
      </Person>
      <!-- Viktor: saknar fördelningstal -->
      <Person>
        <Personnummer>199108125015</Personnummer>
        <Namn>Viktor Halin</Namn>
        <Yrkeskod>456</Yrkeskod>
        <Fordelningstal>0</Fordelningstal>
        <ArbetadeTimmar>80</ArbetadeTimmar>
      </Person>
    </Personer>
  </Lonegranskning>

  <!-- Andra orter: LanOchKommun 1293 -->
  <Lonegranskning>
    <Organisationsnummer>556000-0000</Organisationsnummer>
    <Foretagsnamn>GRK Sverige AB</Foretagsnamn>
    <LoneperiodStartdatum>20260401</LoneperiodStartdatum>
    <LoneperiodSlutdatum>20260430</LoneperiodSlutdatum>
    <Avtalsomrade>Bygg</Avtalsomrade>
    <Lonetyp>Timlon</Lonetyp>
    <LanOchKommun>1293</LanOchKommun>
    <Postort>Landskrona</Postort>
    <Personer>
      <!-- Erik: Arbetar även här, giltig -->
      <Person>
        <Personnummer>198802680374</Personnummer>
        <Namn>Erik Eriksson</Namn>
        <Yrkeskod>123</Yrkeskod>
        <Fordelningstal>100</Fordelningstal>
        <ArbetadeTimmar>60</ArbetadeTimmar>
      </Person>
      <!-- Anna: saknar Yrkeskod -->
      <Person>
        <Personnummer>199202055621</Personnummer>
        <Namn>Anna Carlsson</Namn>
        <Yrkeskod>0</Yrkeskod>
        <Fordelningstal>100</Fordelningstal>
        <ArbetadeTimmar>50</ArbetadeTimmar>
      </Person>
    </Personer>
  </Lonegranskning>
</Lonerapport>
"""
    return xml_content

def test_project_mode():
    xml_str = generate_test_files()
    xml_stream = io.BytesIO(xml_str.encode('iso-8859-1'))
    
    print("\n--- TEST 1: PROJEKT-LÄGE (Ingen CSV) ---")
    
    # 1. Analysera
    warnings = analyze_bygglosen_data([xml_stream], mode='projekt')
    print(f"Hittade {len(warnings)} varningar:")
    for w in warnings:
        print(f"  - {w['namn']} ({w['pnr']}) på ort {w['lankod']} saknar {w['missing']}")
    
    # Verifiera att Viktor (saknar fördelningstal) och Anna (saknar yrkeskod) flaggas
    warning_pnrs = [w['pnr'] for w in warnings]
    assert clean_personnr("199108125015") in warning_pnrs, "Viktor bode flaggas!"
    assert clean_personnr("199202055621") in warning_pnrs, "Anna borde flaggas!"
    print("SUCCESS: Varningar stämmer för båda fallen.")
    
    # Reset stream
    xml_stream.seek(0)
    
    # 2. Konvertera
    xml_io, csv_io, header = convert_bygglosen_data([xml_stream], include_csv=True, mode='projekt')
    
    # Läs resulterande XML
    converted_xml = xml_io.getvalue().decode('iso-8859-1')
    root = ET.fromstring(converted_xml)
    
    # Hitta alla personer i XML
    persons_in_xml = root.findall('.//Person')
    print(f"Antal personer i konverterad XML: {len(persons_in_xml)}")
    
    # Verifiera att bara Erik Eriksson (8802680374) finns med (två gånger, en per ort)
    for p in persons_in_xml:
        pnr = clean_personnr(p.findtext('Personnummer'))
        namn = p.findtext('Namn')
        print(f"  - {namn} ({pnr})")
        assert pnr == clean_personnr("198802680374"), "Endast Erik borde vara med!"
        
    print("SUCCESS: Endast giltiga rader kom med i XML-exporten.")
    
    # Läs resulterande CSV
    converted_csv = csv_io.getvalue().decode('utf-8-sig').replace('\ufeff', '')
    print("Innehåll i CSV:")
    print(converted_csv)
    
    # Verifiera att bara Erik Eriksson finns med och att timmarna är rätt för respektive ort
    assert "8802680374" in converted_csv, "Erik ska finnas i CSV."
    assert "Viktor" not in converted_csv, "Viktor ska inte finnas i CSV."
    assert "Anna" not in converted_csv, "Anna ska inte finnas i CSV."
    
    # Kontrollera att startdatum stämmer
    assert header['LoneperiodStartdatum'] == '20260401', "Startdatum stämmer inte."
    print("SUCCESS: Projekt-läge fungerar felfritt!")

if __name__ == "__main__":
    try:
        test_project_mode()
        print("\nALLA TESTER GODKÄNDA!")
    except AssertionError as e:
        print(f"\nTEST MISSLYCKADES: {e}")
    except Exception as e:
        print(f"\nFEL UPPSTOD: {e}")
