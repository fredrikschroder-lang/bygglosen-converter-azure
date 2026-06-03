// Bygglösen Konverterare - Klient-side konverteringslogik (JavaScript)

// Länskod-till-namn mappning (motsvarande kommunlankod-2026.xlsx)
const LANKOD_MAP = {
  "0001": "Stockholms län",
  "0114": "Upplands Väsby",
  "0115": "Vallentuna",
  "0117": "Österåker",
  "0120": "Värmdö",
  "0123": "Järfälla",
  "0125": "Ekerö",
  "0126": "Huddinge",
  "0127": "Botkyrka",
  "0128": "Salem",
  "0136": "Haninge",
  "0138": "Tyresö",
  "0139": "Upplands-Bro",
  "0140": "Nykvarn",
  "0160": "Täby",
  "0162": "Danderyd",
  "0163": "Sollentuna",
  "0180": "Stockholm",
  "0181": "Södertälje",
  "0182": "Nacka",
  "0183": "Sundbyberg",
  "0184": "Solna",
  "0186": "Lidingö",
  "0187": "Vaxholm",
  "0188": "Norrtälje",
  "0191": "Sigtuna",
  "0192": "Nynäshamn",
  "0003": "Uppsala län",
  "0305": "Håbo",
  "0319": "Älvkarleby",
  "0330": "Knivsta",
  "0331": "Heby",
  "0360": "Tierp",
  "0380": "Uppsala",
  "0381": "Enköping",
  "0382": "Östhammar",
  "0004": "Södermanlands län",
  "0428": "Vingåker",
  "0461": "Gnesta",
  "0480": "Nyköping",
  "0481": "Oxelösund",
  "0482": "Flen",
  "0483": "Katrineholm",
  "0484": "Eskilstuna",
  "0486": "Strängnäs",
  "0488": "Trosa",
  "0005": "Östergötlands län",
  "0509": "Ödeshög",
  "0512": "Ydre",
  "0513": "Kinda",
  "0560": "Boxholm",
  "0561": "Åtvidaberg",
  "0562": "Finspång",
  "0563": "Valdemarsvik",
  "0580": "Linköping",
  "0581": "Norrköping",
  "0582": "Söderköping",
  "0583": "Motala",
  "0584": "Vadstena",
  "0586": "Mjölby",
  "0006": "Jönköpings län",
  "0604": "Aneby",
  "0617": "Gnosjö",
  "0642": "Mullsjö",
  "0643": "Habo",
  "0662": "Gislaved",
  "0665": "Vaggeryd",
  "0680": "Jönköping",
  "0682": "Nässjö",
  "0683": "Värnamo",
  "0684": "Sävsjö",
  "0685": "Vetlanda",
  "0686": "Eksjö",
  "0687": "Tranås",
  "0007": "Kronobergs län",
  "0760": "Uppvidinge",
  "0761": "Lessebo",
  "0763": "Tingsryd",
  "0764": "Alvesta",
  "0765": "Älmhult",
  "0767": "Markaryd",
  "0780": "Växjö",
  "0781": "Ljungby",
  "0008": "Kalmar län",
  "0821": "Högsby",
  "0834": "Torsås",
  "0840": "Mörbylånga",
  "0860": "Hultsfred",
  "0861": "Mönsterås",
  "0862": "Emmaboda",
  "0880": "Kalmar",
  "0881": "Nybro",
  "0882": "Oskarshamn",
  "0883": "Västervik",
  "0884": "Vimmerby",
  "0885": "Borgholm",
  "0009": "Gotlands län",
  "0980": "Gotland",
  "0010": "Blekinge län",
  "1060": "Olofström",
  "1080": "Karlskrona",
  "1081": "Ronneby",
  "1082": "Karlshamn",
  "1083": "Sölvesborg",
  "0012": "Skåne län",
  "1214": "Svalöv",
  "1230": "Staffanstorp",
  "1231": "Burlöv",
  "1233": "Vellinge",
  "1256": "Östra Göinge",
  "1257": "Örkelljunga",
  "1260": "Bjuv",
  "1261": "Kävlinge",
  "1262": "Lomma",
  "1263": "Svedala",
  "1264": "Skurup",
  "1265": "Sjöbo",
  "1266": "Hörby",
  "1267": "Höör",
  "1270": "Tomelilla",
  "1272": "Bromölla",
  "1273": "Osby",
  "1275": "Perstorp",
  "1276": "Klippan",
  "1277": "Åstorp",
  "1278": "Båstad",
  "1280": "Malmö",
  "1281": "Lund",
  "1282": "Landskrona",
  "1283": "Helsingborg",
  "1284": "Höganäs",
  "1285": "Eslöv",
  "1286": "Ystad",
  "1287": "Trelleborg",
  "1290": "Kristianstad",
  "1291": "Simrishamn",
  "1292": "Ängelholm",
  "1293": "Hässleholm",
  "0013": "Hallands län",
  "1315": "Hylte",
  "1380": "Halmstad",
  "1381": "Laholm",
  "1382": "Falkenberg",
  "1383": "Varberg",
  "1384": "Kungsbacka",
  "0014": "Västra Götalands län",
  "1401": "Härryda",
  "1402": "Partille",
  "1407": "Öckerö",
  "1415": "Stenungsund",
  "1419": "Tjörn",
  "1421": "Orust",
  "1427": "Sotenäs",
  "1430": "Munkedal",
  "1435": "Tanum",
  "1438": "Dals-Ed",
  "1439": "Färgelanda",
  "1440": "Ale",
  "1441": "Lerum",
  "1442": "Vårgårda",
  "1443": "Bollebygd",
  "1444": "Grästorp",
  "1445": "Essunga",
  "1446": "Karlsborg",
  "1447": "Gullspång",
  "1452": "Tranemo",
  "1460": "Bengtsfors",
  "1461": "Mellerud",
  "1462": "Lilla Edet",
  "1463": "Mark",
  "1465": "Svenljunga",
  "1466": "Herrljunga",
  "1470": "Vara",
  "1471": "Götene",
  "1472": "Tibro",
  "1473": "Töreboda",
  "1480": "Göteborg",
  "1481": "Mölndal",
  "1482": "Kungälv",
  "1484": "Lysekil",
  "1485": "Uddevalla",
  "1486": "Strömstad",
  "1487": "Vänersborg",
  "1488": "Trollhättan",
  "1489": "Alingsås",
  "1490": "Borås",
  "1491": "Ulricehamn",
  "1492": "Åmål",
  "1493": "Mariestad",
  "1494": "Lidköping",
  "1495": "Skara",
  "1496": "Skövde",
  "1497": "Hjo",
  "1498": "Tidaholm",
  "1499": "Falköping",
  "0017": "Värmlands län",
  "1715": "Kil",
  "1730": "Eda",
  "1737": "Torsby",
  "1760": "Storfors",
  "1761": "Hammarö",
  "1762": "Munkfors",
  "1763": "Forshaga",
  "1764": "Grums",
  "1765": "Årjäng",
  "1766": "Sunne",
  "1780": "Karlstad",
  "1781": "Kristinehamn",
  "1782": "Filipstad",
  "1783": "Hagfors",
  "1784": "Arvika",
  "1785": "Säffle",
  "0018": "Örebro län",
  "1814": "Lekeberg",
  "1860": "Laxå",
  "1861": "Hallsberg",
  "1862": "Degerfors",
  "1863": "Hällefors",
  "1864": "Ljusnarsberg",
  "1880": "Örebro",
  "1881": "Kumla",
  "1882": "Askersund",
  "1883": "Karlskoga",
  "1884": "Nora",
  "1885": "Lindesberg",
  "0019": "Västmanlands län",
  "1904": "Skinnskatteberg",
  "1907": "Surahammar",
  "1960": "Kungsör",
  "1961": "Hallstahammar",
  "1962": "Norberg",
  "1980": "Västerås",
  "1981": "Sala",
  "1982": "Fagersta",
  "1983": "Köping",
  "1984": "Arboga",
  "0020": "Dalarnas län",
  "2021": "Vansbro",
  "2023": "Malung-Sälen",
  "2026": "Gagnef",
  "2029": "Leksand",
  "2031": "Rättvik",
  "2034": "Orsa",
  "2039": "Älvdalen",
  "2061": "Smedjebacken",
  "2062": "Mora",
  "2080": "Falun",
  "2081": "Borlänge",
  "2082": "Säter",
  "2083": "Hedemora",
  "2084": "Avesta",
  "2085": "Ludvika",
  "0021": "Gävleborgs län",
  "2101": "Ockelbo",
  "2104": "Hofors",
  "2121": "Ovanåker",
  "2132": "Nordanstig",
  "2161": "Ljusdal",
  "2180": "Gävle",
  "2181": "Sandviken",
  "2182": "Söderhamn",
  "2183": "Bollnäs",
  "2184": "Hudiksvall",
  "0022": "Västernorrlands län",
  "2260": "Ånge",
  "2262": "Timrå",
  "2280": "Härnösand",
  "2281": "Sundsvall",
  "2282": "Kramfors",
  "2283": "Sollefteå",
  "2284": "Örnsköldsvik",
  "0023": "Jämtlands län",
  "2303": "Ragunda",
  "2305": "Bräcke",
  "2309": "Krokom",
  "2313": "Strömsund",
  "2321": "Åre",
  "2326": "Berg",
  "2361": "Härjedalen",
  "2380": "Östersund",
  "0024": "Västerbottens län",
  "2401": "Nordmaling",
  "2403": "Bjurholm",
  "2404": "Vindeln",
  "2409": "Robertsfors",
  "2417": "Norsjö",
  "2418": "Malå",
  "2421": "Storuman",
  "2422": "Sorsele",
  "2425": "Dorotea",
  "2460": "Vännäs",
  "2462": "Vilhelmina",
  "2463": "Åsele",
  "2480": "Umeå",
  "2481": "Lycksele",
  "2482": "Skellefteå",
  "0025": "Norrbottens län",
  "2505": "Arvidsjaur",
  "2506": "Arjeplog",
  "2510": "Jokkmokk",
  "2513": "Överkalix",
  "2514": "Kalix",
  "2518": "Övertorneå",
  "2521": "Pajala",
  "2523": "Gällivare",
  "2560": "Älvsbyn",
  "2580": "Luleå",
  "2581": "Piteå",
  "2582": "Boden",
  "2583": "Haparanda",
  "2584": "Kiruna"
};

const fieldsToSum = [
  'ArbetadeTimmar', 'GrundlonPerTimma', 'UtbNivaPerTimma', 
  'UtbetaltOverskott', 'Lonesumma', 'OBTillagg', 
  'AvtalsenligManadslon', 'Overtidstimmar', 'Overtidstillagg', 
  'Rolltillagg', 'Aktivitetstillagg', 'Kompetenstillagg', 
  'Ansvarstillagg'
];

function cleanPersonnr(pnr) {
  if (!pnr) return "";
  const clean = String(pnr).replace(/\D/g, "");
  if (clean.length >= 10) {
    return clean.slice(-10);
  }
  return clean;
}

function padLankod(kod) {
  if (!kod) return null;
  return String(kod).trim().padStart(4, "0");
}

function isPersonValid(person) {
  const ftElem = person.querySelector('Fordelningstal');
  const ftText = ftElem ? ftElem.textContent.trim() : "0";
  
  const ykElem = person.querySelector('Yrkeskod');
  const ykText = ykElem ? ykElem.textContent.trim() : "0";
  
  const ftVal = parseFloat(ftText);
  if (isNaN(ftVal) || ftVal <= 0) {
    return false;
  }
  
  if (ykText === "0" || !ykText) {
    return false;
  }
  
  return true;
}

function parseCsv(csvText) {
  const rows = csvText.split(/\r?\n/);
  if (rows.length === 0) return {};
  
  const parsedRows = [];
  rows.forEach(line => {
    if (!line.trim()) return;
    const cols = [];
    let cell = '';
    let insideQuote = false;
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        insideQuote = !insideQuote;
      } else if (char === ';' && !insideQuote) {
        cols.push(cell.trim());
        cell = '';
      } else {
        cell += char;
      }
    }
    cols.push(cell.trim());
    parsedRows.push(cols);
  });
  
  if (parsedRows.length === 0) return {};
  
  const headers = parsedRows[0];
  const dataRows = parsedRows.slice(1);
  
  const headerIndices = {};
  headers.forEach((h, idx) => {
    headerIndices[h.trim().toLowerCase()] = idx;
  });
  
  function getVal(row, aliases) {
    for (const alias of aliases) {
      const norm = alias.toLowerCase();
      if (headerIndices[norm] !== undefined) {
        return row[headerIndices[norm]] || '';
      }
    }
    return '';
  }
  
  const pnrToCsvData = {};
  dataRows.forEach(row => {
    const pnrRaw = getVal(row, ['Personnr', 'Personnummer', 'Pnr', 'Person nr', 'Social Security']);
    const lankodRaw = getVal(row, ['Län och kommun', 'Länkod', 'Lankod', 'Kommun', 'Län']);
    const yrkeskodRaw = getVal(row, ['Yrkeskod', 'Yrke', 'Yrkes-kod', 'Profession', 'Job description', 'B_YRKESKOD']);
    const fordelningstalRaw = getVal(row, ['Fördelningstal', 'Fordelningstal', 'F-tal', 'Fördelning', 'B_FORDELNINGSTAL']);
    
    const pnr = cleanPersonnr(pnrRaw);
    const lankod = padLankod(lankodRaw);
    
    if (pnr) {
      pnrToCsvData[pnr] = {
        lankod: lankod,
        yrkeskod: yrkeskodRaw ? yrkeskodRaw.trim() : null,
        fordelningstal: fordelningstalRaw ? fordelningstalRaw.trim() : null
      };
    }
  });
  
  return pnrToCsvData;
}

function indentXmlNode(node, indentLevel = 0) {
  const indent = "  ".repeat(indentLevel);
  const childNodes = Array.from(node.childNodes);
  const hasElementChildren = childNodes.some(n => n.nodeType === 1);
  
  if (hasElementChildren) {
    childNodes.forEach(child => {
      if (child.nodeType === 1) {
        const textNode = node.ownerDocument.createTextNode("\n" + indent + "  ");
        node.insertBefore(textNode, child);
        indentXmlNode(child, indentLevel + 1);
      }
    });
    const textNode = node.ownerDocument.createTextNode("\n" + indent);
    node.appendChild(textNode);
  }
}

function cleanWhitespaceNodes(node) {
  const childNodes = Array.from(node.childNodes);
  childNodes.forEach(child => {
    if (child.nodeType === 3 && !child.textContent.trim()) {
      node.removeChild(child);
    } else if (child.nodeType === 1) {
      cleanWhitespaceNodes(child);
    }
  });
}

function generateCsvData(headerData, groupedPersons) {
  const excludedFields = new Set(['Arbetsplatsnr', 'UtlanadTillOrgnr', '_original_lankod', '_target_lankod']);
  const staticHeaders = ['Postort', 'LanOchKommun', 'LoneperiodStartdatum', 'LoneperiodSlutdatum'];
  
  const personFields = [];
  const seenPersonFields = new Set();
  
  Object.keys(groupedPersons).forEach(lankod => {
    const personList = groupedPersons[lankod];
    personList.forEach(p => {
      Array.from(p.children).forEach(child => {
        const tagName = child.tagName;
        if (!seenPersonFields.has(tagName) && !excludedFields.has(tagName)) {
          seenPersonFields.add(tagName);
          personFields.push(tagName);
        }
      });
    });
  });
  
  const pnrIdx = personFields.indexOf('Personnummer');
  if (pnrIdx !== -1) {
    personFields.splice(pnrIdx, 1);
    personFields.unshift('Personnummer');
  }
  
  const headers = [...staticHeaders, ...personFields];
  
  let csvRows = [];
  csvRows.push(headers.join(';'));
  
  Object.keys(groupedPersons).forEach(lankod => {
    const personList = groupedPersons[lankod];
    const rowBase = {
      'Postort': LANKOD_MAP[lankod] || headerData['Postort'] || '',
      'LanOchKommun': lankod,
      'LoneperiodStartdatum': headerData['LoneperiodStartdatum'] || '',
      'LoneperiodSlutdatum': headerData['LoneperiodSlutdatum'] || ''
    };
    
    personList.forEach(p => {
      const row = { ...rowBase };
      Array.from(p.children).forEach(child => {
        const tagName = child.tagName;
        if (!excludedFields.has(tagName)) {
          row[tagName] = child.textContent;
        }
      });
      
      const line = headers.map(h => row[h] || '').join(';');
      csvRows.push(line);
    });
  });
  
  return csvRows.join('\r\n');
}

function parseAndGroupData(xmlTexts, csvText = null, defaultLankod = "1293", overrideStart = null, overrideEnd = null, mode = "anstalld") {
  let pnrToCsvData = {};
  if (mode === "anstalld" && csvText) {
    pnrToCsvData = parseCsv(csvText);
  }
  
  const allPersonsCollected = [];
  let headerData = null;
  
  xmlTexts.forEach(xmlText => {
    // Clean up XML string from BOM or bad declarations if needed, and parse it
    const cleanXmlText = xmlText.trim().replace(/^\ufeff/, "");
    const doc = new DOMParser().parseFromString(cleanXmlText, "application/xml");
    
    const parserError = doc.querySelector("parsererror");
    if (parserError) {
      throw new Error("Kunde inte parsa en av XML-filerna. Kontrollera att det är en giltig XML-fil.");
    }
    
    let originalGroups = Array.from(doc.querySelectorAll('Lonegranskning'));
    if (originalGroups.length === 0) {
      if (doc.documentElement.tagName === 'Lonegranskning') {
        originalGroups = [doc.documentElement];
      } else {
        return;
      }
    }
    
    originalGroups.forEach(originalGroup => {
      if (!headerData) {
        headerData = {
          'Organisationsnummer': originalGroup.querySelector('Organisationsnummer') ? originalGroup.querySelector('Organisationsnummer').textContent : '',
          'Foretagsnamn': originalGroup.querySelector('Foretagsnamn') ? originalGroup.querySelector('Foretagsnamn').textContent : '',
          'LoneperiodStartdatum': originalGroup.querySelector('LoneperiodStartdatum') ? originalGroup.querySelector('LoneperiodStartdatum').textContent : '',
          'LoneperiodSlutdatum': originalGroup.querySelector('LoneperiodSlutdatum') ? originalGroup.querySelector('LoneperiodSlutdatum').textContent : '',
          'Avtalsomrade': originalGroup.querySelector('Avtalsomrade') ? originalGroup.querySelector('Avtalsomrade').textContent : '',
          'Lonetyp': originalGroup.querySelector('Lonetyp') ? originalGroup.querySelector('Lonetyp').textContent : '',
          'Postort': (originalGroup.querySelector('Postort') ? originalGroup.querySelector('Postort').textContent : '') || ''
        };
        
        if (overrideStart) {
          headerData['LoneperiodStartdatum'] = overrideStart.replace(/-/g, '');
        }
        if (overrideEnd) {
          headerData['LoneperiodSlutdatum'] = overrideEnd.replace(/-/g, '');
        }
      }
      
      const fileLankod = originalGroup.querySelector('LanOchKommun') ? originalGroup.querySelector('LanOchKommun').textContent : '';
      const allPersonsContainer = originalGroup.querySelector('Personer');
      if (allPersonsContainer) {
        const persons = Array.from(allPersonsContainer.querySelectorAll('Person'));
        persons.forEach(p => {
          p.setAttribute('_original_lankod', fileLankod || '');
          allPersonsCollected.push(p);
        });
      }
    });
  });
  
  if (!headerData) {
    throw new Error("Fel: Kunde inte hitta 'Lonegranskning' data i någon av XML-filerna.");
  }
  
  const mergedPersonsMap = {};
  allPersonsCollected.forEach(person => {
    const pnr = person.querySelector('Personnummer') ? person.querySelector('Personnummer').textContent.trim() : "";
    if (!pnr) return;
    
    const cleanPnr = cleanPersonnr(pnr);
    const rawLankod = person.getAttribute('_original_lankod') || (person.querySelector('LanOchKommun') ? person.querySelector('LanOchKommun').textContent.trim() : "") || defaultLankod;
    const lankod = padLankod(rawLankod);
    
    const mergeKey = mode === 'projekt' ? `${cleanPnr}_${lankod}` : cleanPnr;
    
    if (mergedPersonsMap[mergeKey]) {
      const existingPerson = mergedPersonsMap[mergeKey];
      
      fieldsToSum.forEach(field => {
        let elemExist = existingPerson.querySelector(field);
        const elemNew = person.querySelector(field);
        
        if (elemNew) {
          if (elemExist) {
            const val1 = parseFloat(elemExist.textContent) || 0;
            const val2 = parseFloat(elemNew.textContent) || 0;
            elemExist.textContent = (val1 + val2).toFixed(2);
          } else {
            elemExist = existingPerson.ownerDocument.createElement(field);
            elemExist.textContent = elemNew.textContent;
            existingPerson.appendChild(elemExist);
          }
        }
      });
      
      ['Yrkeskod', 'Fordelningstal'].forEach(field => {
        let baseElem = existingPerson.querySelector(field);
        const newElem = person.querySelector(field);
        const baseVal = baseElem ? baseElem.textContent.trim() : "";
        
        if ((!baseVal || baseVal === "0") && newElem && newElem.textContent) {
          const newVal = newElem.textContent.trim();
          if (newVal && newVal !== "0") {
            if (!baseElem) {
              baseElem = existingPerson.ownerDocument.createElement(field);
              existingPerson.appendChild(baseElem);
            }
            baseElem.textContent = newVal;
          }
        }
      });
    } else {
      const personCopy = person.cloneNode(true);
      personCopy.setAttribute('_target_lankod', lankod);
      mergedPersonsMap[mergeKey] = personCopy;
      
      const ftElem = personCopy.querySelector('Fordelningstal');
      if (ftElem && ftElem.textContent) {
        const val = parseFloat(ftElem.textContent);
        if (!isNaN(val)) {
          ftElem.textContent = Math.floor(val).toString();
        }
      }
    }
  });
  
  const uniquePersons = Object.values(mergedPersonsMap);
  
  if (mode === 'anstalld') {
    uniquePersons.forEach(person => {
      const pnrXml = person.querySelector('Personnummer') ? person.querySelector('Personnummer').textContent : '';
      const cleanPnr = cleanPersonnr(pnrXml);
      
      if (pnrToCsvData[cleanPnr]) {
        const csvData = pnrToCsvData[cleanPnr];
        
        let yrkeskodElem = person.querySelector('Yrkeskod');
        const currentYrkeskod = yrkeskodElem ? yrkeskodElem.textContent.trim() : '';
        if ((!currentYrkeskod || currentYrkeskod === '0') && csvData.yrkeskod) {
          if (!yrkeskodElem) {
            yrkeskodElem = person.ownerDocument.createElement('Yrkeskod');
            person.appendChild(yrkeskodElem);
          }
          yrkeskodElem.textContent = csvData.yrkeskod;
        }
        
        let fordElem = person.querySelector('Fordelningstal');
        const currentFord = fordElem ? fordElem.textContent.trim() : '0';
        const isEmptyOrZero = currentFord === '0' || !currentFord;
        
        if (isEmptyOrZero && csvData.fordelningstal) {
          if (!fordElem) {
            fordElem = person.ownerDocument.createElement('Fordelningstal');
            person.appendChild(fordElem);
          }
          const val = parseFloat(csvData.fordelningstal);
          if (!isNaN(val)) {
            fordElem.textContent = Math.floor(val).toString();
          } else {
            fordElem.textContent = csvData.fordelningstal;
          }
        }
      }
    });
  }
  
  const groupedPersons = {};
  uniquePersons.forEach(person => {
    let targetKod = defaultLankod;
    if (mode === 'projekt') {
      targetKod = person.getAttribute('_target_lankod') || defaultLankod;
    } else {
      const pnrXml = person.querySelector('Personnummer') ? person.querySelector('Personnummer').textContent : '';
      const cleanPnr = cleanPersonnr(pnrXml);
      
      if (pnrToCsvData[cleanPnr] && pnrToCsvData[cleanPnr].lankod) {
        targetKod = pnrToCsvData[cleanPnr].lankod;
      } else {
        const existingLankod = (person.querySelector('LanOchKommun') ? person.querySelector('LanOchKommun').textContent : '') || person.getAttribute('_original_lankod');
        if (existingLankod) {
          targetKod = padLankod(existingLankod);
        }
      }
    }
    
    if (!groupedPersons[targetKod]) {
      groupedPersons[targetKod] = [];
    }
    groupedPersons[targetKod].push(person);
  });
  
  return { headerData, groupedPersons };
}

function analyzeBygglosenData(xmlTexts, csvText = null, defaultLankod = "1293", mode = "anstalld") {
  const { headerData, groupedPersons } = parseAndGroupData(xmlTexts, csvText, defaultLankod, null, null, mode);
  
  const warnings = [];
  Object.keys(groupedPersons).forEach(lankod => {
    const personList = groupedPersons[lankod];
    personList.forEach(person => {
      const missing = [];
      
      const ftElem = person.querySelector('Fordelningstal');
      const ftText = ftElem ? ftElem.textContent.trim() : '0';
      const ftVal = parseFloat(ftText);
      if (isNaN(ftVal) || ftVal <= 0) {
        missing.push("Fördelningstal");
      }
      
      const ykElem = person.querySelector('Yrkeskod');
      const ykText = ykElem ? ykElem.textContent.trim() : '0';
      if (ykText === '0' || !ykText) {
        missing.push("Yrkeskod");
      }
      
      if (missing.length > 0) {
        const pnr = person.querySelector('Personnummer') ? person.querySelector('Personnummer').textContent : 'Okänt';
        let namn = person.querySelector('Namn') ? person.querySelector('Namn').textContent : '';
        if (!namn) {
          const fornamn = person.querySelector('Fornamn') ? person.querySelector('Fornamn').textContent : '';
          const efternamn = person.querySelector('Efternamn') ? person.querySelector('Efternamn').textContent : '';
          namn = `${fornamn} ${efternamn}`.trim();
        }
        if (!namn) {
          namn = "Okänt namn";
        }
        
        warnings.push({
          pnr: cleanPersonnr(pnr),
          namn: namn,
          missing: missing,
          lankod: lankod
        });
      }
    });
  });
  
  // Deduplicate warnings by personnummer (similar to converter.py granskningsflöde)
  const seenPnr = new Set();
  const dedupedWarnings = [];
  warnings.forEach(w => {
    if (!seenPnr.has(w.pnr)) {
      seenPnr.add(w.pnr);
      dedupedWarnings.push(w);
    }
  });
  
  return dedupedWarnings;
}

function convertBygglosenData(xmlTexts, csvText = null, defaultLankod = "1293", overrideStart = null, overrideEnd = null, mode = "anstalld", includeCsv = false) {
  const { headerData, groupedPersons } = parseAndGroupData(xmlTexts, csvText, defaultLankod, overrideStart, overrideEnd, mode);
  
  const filteredGroupedPersons = {};
  Object.keys(groupedPersons).forEach(lankod => {
    const personList = groupedPersons[lankod];
    const xmlPersonList = [];
    personList.forEach(p => {
      if (isPersonValid(p)) {
        xmlPersonList.push(p);
      }
    });
    if (xmlPersonList.length > 0) {
      filteredGroupedPersons[lankod] = xmlPersonList;
    }
  });
  
  const doc = document.implementation.createDocument(null, 'Lista_lonegranskning');
  const newRoot = doc.documentElement;
  
  Object.keys(filteredGroupedPersons).forEach(lankod => {
    const xmlPersonList = filteredGroupedPersons[lankod];
    const lgBlock = doc.createElement('Lonegranskning');
    newRoot.appendChild(lgBlock);
    
    const headerKeys = [
      'Organisationsnummer', 'Foretagsnamn', 'LoneperiodStartdatum', 
      'LoneperiodSlutdatum', 'Avtalsomrade', 'Lonetyp'
    ];
    
    headerKeys.forEach(key => {
      const val = headerData[key] || '';
      const elem = doc.createElement(key);
      elem.textContent = val;
      lgBlock.appendChild(elem);
    });
    
    const lkElem = doc.createElement('LanOchKommun');
    lkElem.textContent = lankod;
    lgBlock.appendChild(lkElem);
    
    const poElem = doc.createElement('Postort');
    poElem.textContent = LANKOD_MAP[lankod] || headerData['Postort'] || '';
    lgBlock.appendChild(poElem);
    
    const personerBlock = doc.createElement('Personer');
    lgBlock.appendChild(personerBlock);
    
    xmlPersonList.forEach(p => {
      const pImported = doc.importNode(p, true);
      pImported.removeAttribute('_original_lankod');
      pImported.removeAttribute('_target_lankod');
      personerBlock.appendChild(pImported);
    });
  });
  
  cleanWhitespaceNodes(newRoot);
  indentXmlNode(newRoot, 0);
  
  const xmlSerializer = new XMLSerializer();
  const xmlContent = '<?xml version="1.0" encoding="ISO-8859-1"?>\n' + xmlSerializer.serializeToString(doc) + '\n';
  
  if (includeCsv) {
    const csvContent = generateCsvData(headerData, filteredGroupedPersons);
    return { xmlContent, csvContent, headerData };
  }
  
  return { xmlContent, headerData };
}

// Windows-1252 / ISO-8859-1 encoder to download file in ISO-8859-1 encoding in browser
function encodeISO88591(str) {
  // Normalize string to NFC to merge decomposed characters (e.g. o + combining diaeresis -> ö)
  const normalizedStr = str.normalize('NFC');
  const len = normalizedStr.length;
  const buffer = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    let code = normalizedStr.charCodeAt(i);
    if (code > 255) {
      // Basic character fallback for non-ISO-8859-1 characters
      code = 63; // '?'
    }
    buffer[i] = code;
  }
  return buffer;
}

// Export for browser global context or test scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    LANKOD_MAP,
    cleanPersonnr,
    padLankod,
    isPersonValid,
    parseCsv,
    analyzeBygglosenData,
    convertBygglosenData,
    encodeISO88591,
    generateCsvData
  };
} else {
  window.BygglosenConverter = {
    analyzeBygglosenData,
    convertBygglosenData,
    encodeISO88591,
    cleanPersonnr,
    padLankod
  };
}
