import xml.etree.ElementTree as ET
import csv
import io
from collections import defaultdict
import openpyxl
import os

def clean_personnr(pnr):
    """Tar bort ALLT utom siffror och returnerar de sista 10 siffrorna för robust matchning."""
    if not pnr:
        return ""
    p = "".join(c for c in str(pnr) if c.isdigit())
    if len(p) >= 10:
        return p[-10:]
    return p

def pad_lankod(kod):
    """Ser till att länskoden alltid är 4 siffror (t.ex. 662 -> 0662)."""
    if not kod:
        return None
    return str(kod).strip().zfill(4)

def load_lankod_map(excel_path='kommunlankod-2026.xlsx'):
    """Laddar en map från Kod -> Namn från Excel-filen."""
    lankod_map = {}
    if not os.path.exists(excel_path):
        return lankod_map
        
    try:
        wb = openpyxl.load_workbook(excel_path, read_only=True)
        sheet = wb.active
        for row in sheet.iter_rows(values_only=True):
            if not row or len(row) < 2:
                continue
            
            kod, namn = row[0], row[1]
            if kod:
                kod_str = str(kod).strip().zfill(4)
                namn_str = str(namn).strip()
                if kod_str.isdigit():
                   lankod_map[kod_str] = namn_str
    except Exception as e:
        print(f"Varning: Kunde inte läsa excel-filen: {e}")
        
    return lankod_map

def generate_csv_data(header_data, lankod_namn_map, grouped_persons):
    """Genererar CSV-data baserat på den konverterade XML-strukturen."""
    output = io.StringIO()
    output.write('\ufeff')
    
    excluded_fields = {'Arbetsplatsnr', 'UtlanadTillOrgnr', '_original_lankod', '_target_lankod'}
    static_headers = ['Postort', 'LanOchKommun', 'LoneperiodStartdatum', 'LoneperiodSlutdatum']
    
    person_fields = []
    seen_person_fields = set()
    
    for lankod, person_list in grouped_persons.items():
        for p in person_list:
            for child in p:
                if child.tag not in seen_person_fields and child.tag not in excluded_fields:
                    seen_person_fields.add(child.tag)
                    person_fields.append(child.tag)
    
    if 'Personnummer' in person_fields:
        person_fields.remove('Personnummer')
        person_fields.insert(0, 'Personnummer')
    
    headers = static_headers + person_fields
    
    writer = csv.DictWriter(output, fieldnames=headers, delimiter=';', extrasaction='ignore')
    writer.writeheader()
    
    for lankod, person_list in grouped_persons.items():
        row_base = {
            'Postort': lankod_namn_map.get(lankod, header_data.get('Postort', '')),
            'LanOchKommun': lankod,
            'LoneperiodStartdatum': header_data.get('LoneperiodStartdatum', ''),
            'LoneperiodSlutdatum': header_data.get('LoneperiodSlutdatum', '')
        }
        
        for p in person_list:
            row = row_base.copy()
            for child in p:
                if child.tag not in excluded_fields:
                    row[child.tag] = child.text
            writer.writerow(row)
            
    return output.getvalue().encode('utf-8-sig')

def _is_person_valid(person):
    ft_elem = person.find('Fordelningstal')
    ft_text = ft_elem.text.strip() if ft_elem is not None and ft_elem.text else "0"
    
    yk_elem = person.find('Yrkeskod')
    yk_text = yk_elem.text.strip() if yk_elem is not None and yk_elem.text else "0"
    
    try:
        if float(ft_text) <= 0:
            return False
    except (ValueError, TypeError):
        return False
        
    if yk_text == "0" or not yk_text:
        return False
        
    return True

def _parse_and_group_data(xml_file_streams, csv_file_stream=None, default_lankod="1293", override_start=None, override_end=None, mode="anstalld"):
    lankod_namn_map = load_lankod_map()
    pnr_to_csv_data = {}
    
    if mode == "anstalld" and csv_file_stream is not None:
        encodings_to_try = ['utf-8-sig', 'iso-8859-1', 'cp1252']
        csv_rows = []
        start_pos = csv_file_stream.tell()
        
        success = False
        for encoding in encodings_to_try:
            try:
                csv_file_stream.seek(start_pos)
                wrapper = io.TextIOWrapper(csv_file_stream, encoding=encoding, newline='')
                data = wrapper.read()
                wrapper.detach()
                reader = csv.DictReader(io.StringIO(data), delimiter=';')
                csv_rows = list(reader)
                success = True
                break
            except UnicodeDecodeError:
                if 'wrapper' in locals():
                    try:
                        wrapper.detach()
                    except Exception:
                        pass
                continue
                
        if not success:
             raise ValueError("Kunde inte läsa CSV-filen. Kontrollera att den är sparad som UTF-8 eller ISO-8859-1.")

        sample_row = csv_rows[0] if csv_rows else {}
        headers_normalized = {k.strip().lower(): k for k in sample_row.keys()}
        
        def get_csv_val(row, *aliases):
            for alias in aliases:
                norm_alias = alias.lower()
                if norm_alias in headers_normalized:
                    return row.get(headers_normalized[norm_alias], '')
            return ''

        for row in csv_rows:
            pnr_raw = get_csv_val(row, 'Personnr', 'Personnummer', 'Pnr', 'Person nr', 'Social Security')
            lankod_raw = get_csv_val(row, 'Län och kommun', 'Länkod', 'Lankod', 'Kommun', 'Län')
            yrkeskod_raw = get_csv_val(row, 'Yrkeskod', 'Yrke', 'Yrkes-kod', 'Profession', 'Job description', 'B_YRKESKOD')
            fordelningstal_raw = get_csv_val(row, 'Fördelningstal', 'Fordelningstal', 'F-tal', 'Fördelning', 'B_FORDELNINGSTAL')
            
            pnr = clean_personnr(pnr_raw)
            lankod = pad_lankod(lankod_raw)
            
            if pnr:
                pnr_to_csv_data[pnr] = {
                    'lankod': lankod,
                    'yrkeskod': yrkeskod_raw.strip() if yrkeskod_raw else None,
                    'fordelningstal': fordelningstal_raw.strip() if fordelningstal_raw else None
                }

    all_persons_collected = []
    header_data = None
    
    if not isinstance(xml_file_streams, list):
        xml_file_streams = [xml_file_streams]

    for stream in xml_file_streams:
        try:
            tree = ET.parse(stream)
            root = tree.getroot()
            
            original_groups = root.findall('Lonegranskning')
            if not original_groups:
                if root.tag == 'Lonegranskning':
                    original_groups = [root]
                else:
                    continue

            for original_group in original_groups:
                if header_data is None:
                    header_data = {
                        'Organisationsnummer': original_group.findtext('Organisationsnummer'),
                        'Foretagsnamn': original_group.findtext('Foretagsnamn'),
                        'LoneperiodStartdatum': original_group.findtext('LoneperiodStartdatum'),
                        'LoneperiodSlutdatum': original_group.findtext('LoneperiodSlutdatum'),
                        'Avtalsomrade': original_group.findtext('Avtalsomrade'),
                        'Lonetyp': original_group.findtext('Lonetyp'),
                        'Postort': original_group.findtext('Postort') or ""
                    }
                    
                    if override_start:
                        header_data['LoneperiodStartdatum'] = override_start.replace('-', '')
                    if override_end:
                        header_data['LoneperiodSlutdatum'] = override_end.replace('-', '')
                
                file_lankod = original_group.findtext('LanOchKommun')
                
                all_persons_container = original_group.find('Personer')
                if all_persons_container is not None:
                    persons = all_persons_container.findall('Person')
                    for p in persons:
                        p.set('_original_lankod', file_lankod or '')
                    all_persons_collected.extend(persons)
                
        except Exception as e:
            raise ValueError(f"Kunde inte parsa en av XML-filerna: {e}")

    if not header_data:
        raise ValueError("Fel: Kunde inte hitta 'Lonegranskning' data i någon av XML-filerna.")

    fields_to_sum = [
        'ArbetadeTimmar', 'GrundlonPerTimma', 'UtbNivaPerTimma', 
        'UtbetaltOverskott', 'Lonesumma', 'OBTillagg', 
        'AvtalsenligManadslon', 'Overtidstimmar', 'Overtidstillagg', 
        'Rolltillagg', 'Aktivitetstillagg', 'Kompetenstillagg', 
        'Ansvarstillagg'
    ]
    
    merged_persons_map = {}
    
    for person in all_persons_collected:
        pnr = person.findtext('Personnummer')
        if not pnr:
            continue
            
        clean_pnr = clean_personnr(pnr)
        raw_lankod = person.get('_original_lankod') or person.findtext('LanOchKommun') or default_lankod
        lankod = pad_lankod(raw_lankod)
        
        if mode == 'projekt':
            merge_key = f"{clean_pnr}_{lankod}"
        else:
            merge_key = clean_pnr
            
        if merge_key in merged_persons_map:
            existing_person = merged_persons_map[merge_key]
            
            for field in fields_to_sum:
                elem_exist = existing_person.find(field)
                elem_new = person.find(field)
                
                if elem_new is not None:
                    if elem_exist is not None:
                        try:
                            val1 = float(elem_exist.text or 0)
                            val2 = float(elem_new.text or 0)
                            elem_exist.text = "{:.2f}".format(val1 + val2)
                        except ValueError:
                            pass
                    else:
                        new_elem = ET.SubElement(existing_person, field)
                        new_elem.text = elem_new.text

            for field in ['Yrkeskod', 'Fordelningstal']:
                base_elem = existing_person.find(field)
                new_elem = person.find(field)
                base_val = base_elem.text.strip() if base_elem is not None and base_elem.text else ""
                
                if (not base_val or base_val == "0") and new_elem is not None and new_elem.text:
                    new_val = new_elem.text.strip()
                    if new_val and new_val != "0":
                        if base_elem is None:
                            base_elem = ET.SubElement(existing_person, field)
                        base_elem.text = new_val
        else:
            import copy
            person_copy = copy.deepcopy(person)
            person_copy.set('_target_lankod', lankod)
            merged_persons_map[merge_key] = person_copy
            
            ft_elem = person_copy.find('Fordelningstal')
            if ft_elem is not None and ft_elem.text:
                try:
                    ft_elem.text = str(int(float(ft_elem.text)))
                except ValueError:
                    pass
            
    unique_persons = list(merged_persons_map.values())

    if mode == 'anstalld':
        for person in unique_persons:
            pnr_xml = person.findtext('Personnummer')
            clean_pnr = clean_personnr(pnr_xml)
            
            if clean_pnr in pnr_to_csv_data:
                csv_data = pnr_to_csv_data[clean_pnr]
                
                yrkeskod_elem = person.find('Yrkeskod')
                current_yrkeskod = yrkeskod_elem.text.strip() if yrkeskod_elem is not None and yrkeskod_elem.text else ""
                if (not current_yrkeskod or current_yrkeskod == "0") and csv_data['yrkeskod']:
                    if yrkeskod_elem is None:
                        yrkeskod_elem = ET.SubElement(person, 'Yrkeskod')
                    yrkeskod_elem.text = str(csv_data['yrkeskod']).strip()
                
                ford_elem = person.find('Fordelningstal')
                current_ford = ford_elem.text.strip() if ford_elem is not None and ford_elem.text else "0"
                is_empty_or_zero = current_ford == "0" or not current_ford
                
                if is_empty_or_zero and csv_data['fordelningstal']:
                    if ford_elem is None:
                        ford_elem = ET.SubElement(person, 'Fordelningstal')
                    try:
                        val = int(float(str(csv_data['fordelningstal']).strip()))
                        ford_elem.text = str(val)
                    except ValueError:
                        ford_elem.text = str(csv_data['fordelningstal']).strip()

    grouped_persons = defaultdict(list)
    
    for person in unique_persons:
        if mode == 'projekt':
            target_kod = person.get('_target_lankod') or default_lankod
        else:
            pnr_xml = person.findtext('Personnummer')
            clean_pnr = clean_personnr(pnr_xml)
            
            if clean_pnr in pnr_to_csv_data and pnr_to_csv_data[clean_pnr]['lankod']:
                target_kod = pnr_to_csv_data[clean_pnr]['lankod']
            else:
                existing_lankod = person.findtext('LanOchKommun') or person.get('_original_lankod')
                if existing_lankod:
                    target_kod = pad_lankod(existing_lankod)
                else:
                    target_kod = default_lankod
        
        grouped_persons[target_kod].append(person)

    return header_data, lankod_namn_map, grouped_persons

def analyze_bygglosen_data(xml_file_streams, csv_file_stream=None, default_lankod="1293", mode="anstalld"):
    header_data, _, grouped_persons = _parse_and_group_data(
        xml_file_streams, csv_file_stream, default_lankod, mode=mode
    )
    
    warnings = []
    
    for lankod, person_list in grouped_persons.items():
        for person in person_list:
            missing = []
            
            ft_elem = person.find('Fordelningstal')
            ft_text = ft_elem.text.strip() if ft_elem is not None and ft_elem.text else "0"
            try:
                if float(ft_text) <= 0:
                    missing.append("Fördelningstal")
            except (ValueError, TypeError):
                missing.append("Fördelningstal")
                
            yk_elem = person.find('Yrkeskod')
            yk_text = yk_elem.text.strip() if yk_elem is not None and yk_elem.text else "0"
            if yk_text == "0" or not yk_text:
                missing.append("Yrkeskod")
                
            if missing:
                pnr = person.findtext('Personnummer') or 'Okänt'
                namn = person.findtext('Namn')
                if not namn:
                    fornamn = person.findtext('Fornamn') or ''
                    efternamn = person.findtext('Efternamn') or ''
                    namn = f"{fornamn} {efternamn}".strip()
                if not namn:
                    namn = "Okänt namn"
                    
                warnings.append({
                    "pnr": clean_personnr(pnr),
                    "namn": namn,
                    "missing": missing,
                    "lankod": lankod
                })
                
    return warnings

def convert_bygglosen_data(xml_file_streams, csv_file_stream=None, default_lankod="1293", include_csv=False, override_start=None, override_end=None, mode="anstalld"):
    header_data, lankod_namn_map, grouped_persons = _parse_and_group_data(
        xml_file_streams, csv_file_stream, default_lankod, override_start, override_end, mode
    )

    filtered_grouped_persons = defaultdict(list)
    for lankod, person_list in grouped_persons.items():
        xml_person_list = []
        for p in person_list:
            if _is_person_valid(p):
                xml_person_list.append(p)
        if xml_person_list:
            filtered_grouped_persons[lankod] = xml_person_list

    new_root = ET.Element('Lista_lonegranskning')
    
    for lankod, xml_person_list in filtered_grouped_persons.items():
        lg_block = ET.SubElement(new_root, 'Lonegranskning')
        
        header_keys = [
            'Organisationsnummer', 'Foretagsnamn', 'LoneperiodStartdatum', 
            'LoneperiodSlutdatum', 'Avtalsomrade', 'Lonetyp'
        ]
        
        for key in header_keys:
            val = header_data.get(key, '')
            elem = ET.SubElement(lg_block, key)
            elem.text = val
            
        lk_elem = ET.SubElement(lg_block, 'LanOchKommun')
        lk_elem.text = lankod
        
        po_elem = ET.SubElement(lg_block, 'Postort')
        po_elem.text = lankod_namn_map.get(lankod, header_data.get('Postort', ''))
            
        personer_block = ET.SubElement(lg_block, 'Personer')
        for p in xml_person_list:
            if '_original_lankod' in p.attrib:
                del p.attrib['_original_lankod']
            if '_target_lankod' in p.attrib:
                del p.attrib['_target_lankod']
            personer_block.append(p)

    try:
        ET.indent(new_root, space="  ", level=0)
    except AttributeError:
        pass
        
    new_tree = ET.ElementTree(new_root)
    xml_io = io.BytesIO()
    new_tree.write(xml_io, encoding='ISO-8859-1', xml_declaration=True)
    xml_io.seek(0)
    
    if include_csv:
        csv_data = generate_csv_data(header_data, lankod_namn_map, filtered_grouped_persons)
        csv_io = io.BytesIO(csv_data)
        return xml_io, csv_io, header_data
        
    return xml_io, header_data
