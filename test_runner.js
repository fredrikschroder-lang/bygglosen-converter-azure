const { JSDOM } = require('jsdom');
const dom = new JSDOM();
global.window = dom.window;
global.document = dom.window.document;
global.DOMParser = dom.window.DOMParser;
global.XMLSerializer = dom.window.XMLSerializer;

const BygglosenConverter = require('./converter.js');

const mockXmlProjectMode = `<?xml version="1.0" encoding="ISO-8859-1"?>
<Lonerapport>
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
      <Person>
        <Personnummer>198802680374</Personnummer>
        <Namn>Erik Eriksson</Namn>
        <Yrkeskod>123</Yrkeskod>
        <Fordelningstal>100</Fordelningstal>
        <ArbetadeTimmar>40</ArbetadeTimmar>
      </Person>
      <Person>
        <Personnummer>199108125015</Personnummer>
        <Namn>Viktor Halin</Namn>
        <Yrkeskod>456</Yrkeskod>
        <Fordelningstal>0</Fordelningstal>
        <ArbetadeTimmar>80</ArbetadeTimmar>
      </Person>
    </Personer>
  </Lonegranskning>
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
      <Person>
        <Personnummer>198802680374</Personnummer>
        <Namn>Erik Eriksson</Namn>
        <Yrkeskod>123</Yrkeskod>
        <Fordelningstal>100</Fordelningstal>
        <ArbetadeTimmar>60</ArbetadeTimmar>
      </Person>
      <Person>
        <Personnummer>199202055621</Personnummer>
        <Namn>Anna Carlsson</Namn>
        <Yrkeskod>0</Yrkeskod>
        <Fordelningstal>100</Fordelningstal>
        <ArbetadeTimmar>50</ArbetadeTimmar>
      </Person>
    </Personer>
  </Lonegranskning>
</Lonerapport>`;

const mockCsvEmployeeMode = `Anst.id; Namn ; länkOD ; personnummer ; YRKESKOD ; fördelningstal ;
1;Anders Andersson;0662;900101-1234;123;100;
2;Bertil Bengtsson;1280;920202-5678;456;80;
3;Cecilia Carlsson;1293;800101-9999;833215;50;`;

const mockXmlEmployeeMode = `<?xml version="1.0" encoding="ISO-8859-1"?>
<Lonerapport>
  <Lonegranskning>
    <Organisationsnummer>556000-0000</Organisationsnummer>
    <Foretagsnamn>Testbolaget AB</Foretagsnamn>
    <LoneperiodStartdatum>20231001</LoneperiodStartdatum>
    <LoneperiodSlutdatum>20231031</LoneperiodSlutdatum>
    <Avtalsomrade>Bygg</Avtalsomrade>
    <Lonetyp>Timlon</Lonetyp>
    <Postort>Teststad</Postort>
    <Personer>
      <Person>
        <Personnummer>199001011234</Personnummer>
        <Namn>Anders Andersson</Namn>
        <Yrkeskod>123</Yrkeskod>
        <Fordelningstal>100</Fordelningstal>
        <Lon>30000</Lon>
      </Person>
      <Person>
        <Personnummer>199202025678</Personnummer>
        <Namn>Bertil Bengtsson</Namn>
        <Yrkeskod>456</Yrkeskod>
        <Fordelningstal>80</Fordelningstal>
        <Lon>32000</Lon>
      </Person>
       <Person>
        <Personnummer>198001019999</Personnummer>
        <Namn>Cecilia Carlsson</Namn>
        <Yrkeskod>0</Yrkeskod>
        <Fordelningstal>0</Fordelningstal>
        <Lon>35000</Lon>
      </Person>
    </Personer>
  </Lonegranskning>
</Lonerapport>`;

let failed = false;

function assert(condition, message) {
  if (!condition) {
    console.error(`❌ FAIL: ${message}`);
    failed = true;
  } else {
    console.log(`✅ PASS: ${message}`);
  }
}

console.log("Kör tester för converter.js...\n");

// Test 1: Projekt-läge varningar
try {
  const warnings = BygglosenConverter.analyzeBygglosenData([mockXmlProjectMode], null, "1293", "projekt");
  assert(warnings.length === 2, "Hittade 2 varningar");
  
  const hasViktor = warnings.some(w => w.pnr === "9108125015" && w.missing.includes("Fördelningstal"));
  assert(hasViktor, "Varning för Viktor saknar Fördelningstal");

  const hasAnna = warnings.some(w => w.pnr === "9202055621" && w.missing.includes("Yrkeskod"));
  assert(hasAnna, "Varning för Anna saknar Yrkeskod");
} catch (e) {
  console.error("Test 1 kraschade:", e);
  failed = true;
}

// Test 2: Projekt-läge konvertering
try {
  const { xmlContent, csvContent } = BygglosenConverter.convertBygglosenData(
    [mockXmlProjectMode], null, "1293", null, null, "projekt", true
  );

  const docParsed = new DOMParser().parseFromString(xmlContent, "application/xml");
  const persons = docParsed.querySelectorAll('Person');
  assert(persons.length === 2, "Endast 2 personer (Erik x 2) i XML-export");

  let allErik = true;
  persons.forEach(p => {
    const pnr = BygglosenConverter.cleanPersonnr(p.querySelector('Personnummer').textContent);
    if (pnr !== "8802680374") allErik = false;
  });
  assert(allErik, "Alla exporterade personer är Erik Eriksson");

  const hasLankod0662 = xmlContent.includes('<LanOchKommun>0662</LanOchKommun>');
  assert(hasLankod0662, "XML innehåller länkod 0662");

  const hasLankod1293 = xmlContent.includes('<LanOchKommun>1293</LanOchKommun>');
  assert(hasLankod1293, "XML innehåller länkod 1293");

  assert(csvContent.includes('8802680374'), "CSV innehåller Erik Erikssons personnummer");
  assert(!csvContent.includes('Viktor'), "CSV innehåller inte Viktor");
} catch (e) {
  console.error("Test 2 kraschade:", e);
  failed = true;
}

// Test 3: Anställd-läge konvertering med CSV-fallback
try {
  const { xmlContent, csvContent } = BygglosenConverter.convertBygglosenData(
    [mockXmlEmployeeMode], mockCsvEmployeeMode, "1293", null, null, "anstalld", true
  );

  assert(xmlContent.includes('<Yrkeskod>833215</Yrkeskod>'), "Cecilia fick yrkeskod från CSV");
  assert(xmlContent.includes('<Fordelningstal>50</Fordelningstal>'), "Cecilia fick fördelningstal från CSV");
  assert(csvContent.includes('833215') && csvContent.includes('50'), "Cecilia har fallback-värden i CSV");

  assert(xmlContent.includes('Anders Andersson'), "Anders Andersson är med");
  assert(xmlContent.includes('Bertil Bengtsson'), "Bertil Bengtsson är med");
  assert(xmlContent.includes('Cecilia Carlsson'), "Cecilia Carlsson är med");
} catch (e) {
  console.error("Test 3 kraschade:", e);
  failed = true;
}

// Test 4: Windows-1252 teckenkodning
try {
  const testStr = "ÅÄÖåäöé";
  const bytes = BygglosenConverter.encodeISO88591(testStr);
  const expected = [197, 196, 214, 229, 228, 246, 233];
  
  let match = true;
  for (let i = 0; i < expected.length; i++) {
    if (bytes[i] !== expected[i]) match = false;
  }
  assert(match, "Windows-1252 byte-representation stämmer för svenska tecken");
} catch (e) {
  console.error("Test 4 kraschade:", e);
  failed = true;
}

console.log("");
if (failed) {
  console.error("❌ ETT ELLER FLERA TESTER MISSLYCKADES!");
  process.exit(1);
} else {
  console.log("🎉 ALLA TESTER GODKÄNDA!");
  process.exit(0);
}
