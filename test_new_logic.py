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
        print(f"  - {w['namn']} ({w['pnr']}) saknar {w['missing']}")

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

def test_project_mode_keeps_person_separate_per_lankod():
    """
    I projekt-läge utan CSV ska samma personnummer på olika län/kommun
    aldrig slås ihop — varje (pnr, länkod)-kombination är en egen post
    med egna arbetade timmar.
    """
    print("\n--- TEST 2: PROJEKT-LÄGE bevarar separation per länkod ---")

    # En och samma person (Erik) i två olika Lonegranskning-block:
    # länkod 0114 med 10h, länkod 1480 med 25h. Får INTE bli en post med 35h.
    xml_str = """<?xml version="1.0" encoding="ISO-8859-1"?>
<Lista_lonegranskning>
  <Lonegranskning>
    <Organisationsnummer>556000-0000</Organisationsnummer>
    <Foretagsnamn>Testbolag AB</Foretagsnamn>
    <LoneperiodStartdatum>20260401</LoneperiodStartdatum>
    <LoneperiodSlutdatum>20260430</LoneperiodSlutdatum>
    <Avtalsomrade>Bygg</Avtalsomrade>
    <Lonetyp>Timlon</Lonetyp>
    <LanOchKommun>0114</LanOchKommun>
    <Personer>
      <Person>
        <Personnummer>198802680374</Personnummer>
        <Namn>Erik Eriksson</Namn>
        <Yrkeskod>123</Yrkeskod>
        <Fordelningstal>100</Fordelningstal>
        <ArbetadeTimmar>10</ArbetadeTimmar>
      </Person>
    </Personer>
  </Lonegranskning>
  <Lonegranskning>
    <Organisationsnummer>556000-0000</Organisationsnummer>
    <Foretagsnamn>Testbolag AB</Foretagsnamn>
    <LoneperiodStartdatum>20260401</LoneperiodStartdatum>
    <LoneperiodSlutdatum>20260430</LoneperiodSlutdatum>
    <Avtalsomrade>Bygg</Avtalsomrade>
    <Lonetyp>Timlon</Lonetyp>
    <LanOchKommun>1480</LanOchKommun>
    <Personer>
      <Person>
        <Personnummer>198802680374</Personnummer>
        <Namn>Erik Eriksson</Namn>
        <Yrkeskod>123</Yrkeskod>
        <Fordelningstal>100</Fordelningstal>
        <ArbetadeTimmar>25</ArbetadeTimmar>
      </Person>
    </Personer>
  </Lonegranskning>
</Lista_lonegranskning>
"""
    xml_stream = io.BytesIO(xml_str.encode('iso-8859-1'))
    xml_io, _csv_io, _header = convert_bygglosen_data(
        [xml_stream], include_csv=True, mode='projekt'
    )
    root = ET.fromstring(xml_io.getvalue().decode('iso-8859-1'))

    # Förväntat: två Lonegranskning-block, ett per länkod, var och en
    # innehåller Erik med originaltimmarna.
    blocks = root.findall('Lonegranskning')
    assert len(blocks) == 2, f"Förväntade 2 länkod-block, fick {len(blocks)}"

    timmar_per_lankod = {}
    for block in blocks:
        lankod = block.findtext('LanOchKommun')
        persons = block.findall('.//Person')
        assert len(persons) == 1, (
            f"Länkod {lankod} ska ha exakt en Erik-post, fick {len(persons)}"
        )
        timmar_per_lankod[lankod] = persons[0].findtext('ArbetadeTimmar')

    assert timmar_per_lankod.get('0114') == '10', (
        f"Länkod 0114 ska ha 10h, fick {timmar_per_lankod.get('0114')!r} "
        f"(är personerna felaktigt sammanslagna?)"
    )
    assert timmar_per_lankod.get('1480') == '25', (
        f"Länkod 1480 ska ha 25h, fick {timmar_per_lankod.get('1480')!r} "
        f"(är personerna felaktigt sammanslagna?)"
    )
    print("SUCCESS: Erik förekommer separat på båda länkoderna med rätt timmar.")

    # Regressionsskydd: i anställd-läge (utan CSV) ska samma person istället
    # slås ihop till EN post med summerade timmar (35h). Om detta beteende
    # ändras vill vi att projekt-test ovan fortfarande fångar regression.
    xml_stream2 = io.BytesIO(xml_str.encode('iso-8859-1'))
    xml_io2, _ = convert_bygglosen_data(
        [xml_stream2], include_csv=False, mode='anstalld'
    )
    root2 = ET.fromstring(xml_io2.getvalue().decode('iso-8859-1'))
    all_persons = root2.findall('.//Person')
    assert len(all_persons) == 1, (
        f"Anställd-läge ska slå ihop Erik till EN post, fick {len(all_persons)}"
    )
    assert float(all_persons[0].findtext('ArbetadeTimmar')) == 35.0, (
        "Anställd-läge ska summera timmar till 35h"
    )
    print("SUCCESS: Anställd-läge slår fortfarande ihop personen (sanity-check).")


def test_analyze_deduplicates_warnings_by_pnr():
    """
    En person som saknar Fördelningstal/Yrkeskod och förekommer på flera
    Län/Kommun i projekt-läge ska bara dyka upp EN gång i granskningen
    (datan ligger på personnivå i Kontek).
    """
    print("\n--- TEST 3: Granskning deduperar varningar per personnummer ---")

    # Samma person, samma saknade fält, på två länkoder.
    xml_str = """<?xml version="1.0" encoding="ISO-8859-1"?>
<Lista_lonegranskning>
  <Lonegranskning>
    <Organisationsnummer>556000-0000</Organisationsnummer>
    <Foretagsnamn>Testbolag AB</Foretagsnamn>
    <LoneperiodStartdatum>20260401</LoneperiodStartdatum>
    <LoneperiodSlutdatum>20260430</LoneperiodSlutdatum>
    <Avtalsomrade>Bygg</Avtalsomrade>
    <Lonetyp>Timlon</Lonetyp>
    <LanOchKommun>0114</LanOchKommun>
    <Personer>
      <Person>
        <Personnummer>199108125015</Personnummer>
        <Namn>Viktor Halin</Namn>
        <Yrkeskod>456</Yrkeskod>
        <Fordelningstal>0</Fordelningstal>
        <ArbetadeTimmar>10</ArbetadeTimmar>
      </Person>
    </Personer>
  </Lonegranskning>
  <Lonegranskning>
    <Organisationsnummer>556000-0000</Organisationsnummer>
    <Foretagsnamn>Testbolag AB</Foretagsnamn>
    <LoneperiodStartdatum>20260401</LoneperiodStartdatum>
    <LoneperiodSlutdatum>20260430</LoneperiodSlutdatum>
    <Avtalsomrade>Bygg</Avtalsomrade>
    <Lonetyp>Timlon</Lonetyp>
    <LanOchKommun>1480</LanOchKommun>
    <Personer>
      <Person>
        <Personnummer>199108125015</Personnummer>
        <Namn>Viktor Halin</Namn>
        <Yrkeskod>456</Yrkeskod>
        <Fordelningstal>0</Fordelningstal>
        <ArbetadeTimmar>25</ArbetadeTimmar>
      </Person>
    </Personer>
  </Lonegranskning>
</Lista_lonegranskning>
"""
    xml_stream = io.BytesIO(xml_str.encode('iso-8859-1'))
    warnings = analyze_bygglosen_data([xml_stream], mode='projekt')

    viktor_warnings = [w for w in warnings if w['pnr'] == clean_personnr("199108125015")]
    assert len(viktor_warnings) == 1, (
        f"Viktor ska visas exakt EN gång i granskningen, fick {len(viktor_warnings)}"
    )
    assert 'lankod' not in viktor_warnings[0], (
        "Varningar ska inte längre exponera 'lankod' (datan är personnivå)"
    )
    assert 'Fördelningstal' in viktor_warnings[0]['missing']
    print("SUCCESS: Viktor visas en gång, utan länkod-fält.")


if __name__ == "__main__":
    try:
        test_project_mode()
        test_project_mode_keeps_person_separate_per_lankod()
        test_analyze_deduplicates_warnings_by_pnr()
        print("\nALLA TESTER GODKÄNDA!")
    except AssertionError as e:
        print(f"\nTEST MISSLYCKADES: {e}")
    except Exception as e:
        print(f"\nFEL UPPSTOD: {e}")
