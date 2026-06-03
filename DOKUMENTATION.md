# Bygglösen Konverterare — Teknisk dokumentation (Statisk)

Senast uppdaterad: 2026-06-03

En helt klientside-baserad webbapplikation som konverterar Bygglösenfiler från Kontek-format till Byggnads-format. Applikationen körs helt lokalt i användarens webbläsare utan någon server-backend.

För användarvänlig information om appens funktioner se [README.md](README.md).

---

## Innehåll

1. [Översikt](#översikt)
2. [Tekniska komponenter](#tekniska-komponenter)
3. [Applikationslogik i JavaScript](#applikationslogik)
4. [Projektstruktur](#projektstruktur)
5. [Lokal utveckling och tester](#lokal-utveckling)
6. [Driftsättning (Azure Static Web Apps)](#driftsättning-azure)
7. [Kostnadsjämförelse](#kostnader)
8. [Säkerhet och Integritet](#säkerhet)
9. [Felsökning](#felsökning)

---

<a id="översikt"></a>
## 1. Översikt

### Vad appen gör

Användaren laddar upp en eller flera XML-filer från Kontek-systemet ("Bygglösenfiler") och får tillbaka en konverterad fil i Byggnads format. Appen kan köras i två olika lägen och stöder två exportformat (XML och CSV).

### Driftmiljö

Appen körs som en **statisk webbsida** och kan hostas gratis på **Azure Static Web Apps (Free SKU)** eller köras lokalt genom att öppna `index.html` direkt. Den tidigare Container App- och Flask-lösningen är avvecklad till förmån för denna billigare, snabbare och säkrare arkitektur.

---

<a id="tekniska-komponenter"></a>
## 2. Tekniska komponenter

| Lager | Teknologi | Kommentar |
|-------|-----------|-----------|
| UI / Gränssnitt | Vanilla HTML5 / Jinja-oberoende | Placerad i [index.html](index.html) |
| Layout / Styling | Vanilla CSS3 (Outfit font) | Inline i HTML för enkel distribution |
| Logik | JavaScript (ES6) | Placerad i [converter.js](converter.js) |
| PDF-rendering | jsPDF + AutoTable (CDN) | Körs på klientsidan för fellistan |
| XML-parsning | `DOMParser` (inbyggd i webbläsaren) | Läser och manipulerar XML-trädet direkt i minnet |
| XML-serialisering | `XMLSerializer` (inbyggd) | Genererar XML-strängar från DOM-objekt |
| CSV-decoding | `TextDecoder` (inbyggd) | Automatisk detektering av UTF-8 och CP1252-kodningar |
| Teckenkodning | `encodeISO88591` (egen JS-funktion) | Skriver ut XML-filen i rätt ISO-8859-1 (Latin1) teckenkodning |
| Hosting | Azure Static Web Apps | Free SKU, global distribution via CDN |

---

<a id="applikationslogik"></a>
## 3. Applikationslogik

### 3.1 Två lägen

Appen stöder två rapporteringssätt:

* **Projekt-läge (GRK):**
  - Län & Kommun hämtas från `<LanOchKommun>` på varje `<Lonegranskning>`-block i XML.
  - Ingen CSV behövs.
  - Samma personnummer kan förekomma på flera Län/Kommun-poster — varje kombination av (pnr, länkod) hålls separat (egentidsredovisning, arbetade timmar etc.).
  
* **Anställd-läge / Hängavtal:**
  - Län & Kommun styrs av en CSV-fil med personkort.
  - Samma personnummer slås ihop till en post även om de förekommer flera gånger i XML — fält som timmar summeras.
  - CSV-filen kan även fylla i Yrkeskod och Fördelningstal när XML saknar dem.

### 3.2 Sammanslagningsnyckel (`converter.js:338`)

```javascript
const mergeKey = mode === 'projekt' ? `${cleanPnr}_${lankod}` : cleanPnr;
```

Personer med samma `mergeKey` slås ihop. Numeriska fält (`ArbetadeTimmar`, `Lonesumma`, `Overtidstimmar`, etc.) summeras. För `Yrkeskod` och `Fordelningstal` används det första icke-noll-värdet som hittas.

### 3.3 Filtrering (`converter.js:146`)

`isPersonValid` avgör om en person tas med i exporten:
- `Fordelningstal` måste vara numeriskt och > 0.
- `Yrkeskod` måste vara icke-tom och inte "0".

Personer med ofullständig data exkluderas och visas i granskningssteget i rött samt i den nedladdningsbara PDF-fellistan.

Fellistan kan laddas ner som en PDF-fil (med namnet `Byggnads_fellista_YYYY-MM-DD.pdf`) med hjälp av knappen **📄 Ladda ner Fellista (PDF)** i granskningsläget. PDF-filen genereras helt på klientsidan via jsPDF och AutoTable.

### 3.4 Länkod-till-namn-mappning

Mappningen från länkod (t.ex. `0662` -> "Gislaved") är inbakad direkt som ett JSON-objekt i [converter.js](converter.js) under variabeln `LANKOD_MAP`. Den är extraherad från `kommunlankod-2026.xlsx` för att slippa Excel-beroenden i runtime.

### 3.5 Teckenkodning och filnedladdning

- **XML-export:** XML-deklarationen anger `ISO-8859-1`. Eftersom webbläsare normalt sparar textsträngar som UTF-8, konverterar JS-funktionen `encodeISO88591` teckenkoderna i strängen (efter NFC-normalisering) till en `Uint8Array` av Latin-1 bytes innan den skapar en Blob för nedladdning. Det säkerställer att svenska tecken (ÅÄÖåäöé) tolkas korrekt av Byggnads mottagarsystem.
- **CSV-export:** Skrivs i UTF-8 med BOM (`\ufeff`) för att Excel automatiskt ska öppna filen med rätt teckenkodning och kolumnindelning.

### 3.6 Gränssnitt och Exportcenter

Gränssnittet innehåller följande designuppdateringar:
- **Exsitec Logotyp:** Logotypen (`img/exsitec_logo_grey.svg`) visas högst upp till vänster och anpassas automatiskt för mobila enheter via responsiv CSS.
- **Exportcenter:** I granskningsläget (steg 2) finns en tydlig panel med rubriken **Exportera resultat**. Den innehåller en informationsruta som förklarar att personer med ofullständig data (från fellistan) automatiskt utesluts ur exportfilerna. Den har två separata, tydliga kort för de olika exportformaten:
  - **Bygglösen-fil (XML):** Med en grön knapp **Ladda ner XML-fil** som exporterar den formaterade XML-filen i rätt ISO-8859-1-kodning.
  - **Kontrollrapport (CSV):** Med en blå knapp **Ladda ner CSV-rapport** som exporterar en kalkylbladsrapport i UTF-8 BOM för enkel granskning i Excel.

---

<a id="projektstruktur"></a>
## 4. Projektstruktur

```
.
├── index.html            # Huvudgränssnitt (statiskt HTML)
├── converter.js          # All databehandling, parsning och databastabell
├── lankod_map.json       # Referensfil med JSON-länskodsmappning
├── img/                  # Logotyp-resurser
│   └── exsitec_logo_grey.svg # Exsitec-logotyp för gränssnittet
├── test_runner.html      # Testkörare för webbläsare
├── test_runner.js        # Testkörare för Node.js
├── package.json          # npm-testinställningar
├── package-lock.json     # npm locks
└── DOKUMENTATION.md      # Detta dokument
```

Alla gamla Python-filer (`app.py`, `converter.py`, `test_logic.py`, `requirements.txt`), virtuella miljöer (`.venv`) samt Docker-filer (`Dockerfile`, `.dockerignore`) har raderats då de inte längre behövs.

---

<a id="lokal-utveckling"></a>
## 5. Lokal utveckling och tester

### Körning lokalt
Dubbelklicka på [index.html](index.html) eller starta en lokal HTTP-server:
```bash
npx http-server .
```

### Tester
Testerna kontrollerar sammanslagning, datumkontroller, CSV-fallback och teckenkodning.
- **I webbläsaren:** Öppna [test_runner.html](test_runner.html) i valfri webbläsare.
- **I terminalen:**
  ```bash
  npm install
  node test_runner.js
  ```

---

<a id="driftsättning-azure"></a>
## 6. Driftsättning (Azure Static Web Apps)

### 6.1 Avveckling av gamla Azure-resurser
Då appen blivit helt statisk kan följande resurser raderas i Azure-portalen eller via CLI för att spara pengar:
1. **Azure Container App:** `bygglosen-converter` i resource group `HRM_apps`
2. **Azure Container Registry (ACR):** `acrbygglosen1658`
3. **Container Apps Environment:** `cae-bygglosen`
4. **Log Analytics Workspace:** Tillhörande cae-bygglosen workspace

### 6.2 Skapa Azure Static Web App
Skapa en Static Web App via Azure Portal eller CLI under **Free SKU**. Peka ut mappen med `index.html` som root. Azure Static Web Apps har ett inbyggt gratis globalt CDN och kostar ingenting.

---

<a id="kostnader"></a>
## 7. Kostnadsjämförelse

| Resurs | Tidigare (Container App) | Ny (Static Web App) |
|--------|--------------------------|---------------------|
| Azure Container Apps | ~$0-3 / månad | **0 kr (Free SKU)** |
| Azure Container Registry | ~$5 / månad (Fast avgift) | **Ingen (Behövs ej)** |
| Log Analytics Workspace | ~$0-2 / månad | **Ingen (Behövs ej)** |
| **Totalt / månad** | **~$5-10 (~50-100 SEK)** | **0 SEK** |

---

<a id="säkerhet"></a>
## 8. Säkerhet och Integritet

- **100% GDPR-säker:** Ingen data skickas över internet för bearbetning. Detta eliminerar behovet av SSL/TLS-tunnlar för API-anrop, nätverkskontroller eller kryptering under transport av lönefiler.
- **Inga sårbarheter i backend:** Eftersom det saknas ett operativsystem (ingen container) och ett backend-språk (inget Python/Flask), finns det inga servrar eller beroenden som kan drabbas av säkerhetshål.
- **Inga Secrets att rotera:** Inga API-nycklar, Clerk-certifikat eller krypteringsnycklar lagras i applikationen.

---

<a id="felsökning"></a>
## 9. Felsökning

### Svenska tecken blir konstiga i den konverterade XML-filen
Om mottagarsystemet klagar på teckenkodning, se till att filen laddas ner via knappen "Ladda ner XML-fil" (vilket använder `encodeISO88591`-funktionen). Om filen manuellt sparas eller kopieras via urklipp i webbläsaren kan den sparas som UTF-8 av misstag.

### CSV-filen kan inte läsas i Anställd-läge
Om sidan ger ett felmeddelande när en CSV laddas upp, kontrollera att filen är semikolonseparerad (`;`) samt sparad i antingen UTF-8 eller Windows-1252 (Standard Excel CSV-format).
