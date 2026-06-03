# Bygglösen Konverterare (Klient-side)

En helt klientside-baserad webbapplikation för konvertering av Bygglösenfiler från Konteks XML-format till Byggnads XML- och CSV-format. 

Logiken är flyttad från en tidigare Flask/Python-backend till 100% lokal JavaScript i webbläsaren. Detta innebär att applikationen är blixtsnabb (inga kalla starter av containrar), helt gratis att drifta samt har högsta möjliga datasäkerhet (GDPR) då löneuppgifter och personnummer aldrig skickas till någon server.

---

## Innehåll

- [Vad applikationen gör](#vad-applikationen-gör)
- [Dataflöde och integritet](#dataflöde-och-integritet)
- [Projektstruktur](#projektstruktur)
- [Lokal utveckling och tester](#lokal-utveckling-och-tester)
- [Driftsättning (Azure Static Web Apps)](#driftsättning-azure-static-web-apps)

---

## Vad applikationen gör

Användaren väljer lönefiler från Kontek (XML) och kan vid behov ladda upp en CSV-fil för anställda (Anställd-läge / Hängavtal) för att styra eller komplettera uppgifter.

Applikationen:
1. Parsar XML-filerna och samlar in header-information (organisation, datumintervall).
2. Slår ihop dubbletter av anställda baserat på personnummer (och länkod i projekt-läge).
3. Summerar arbetade timmar, lön, övertid m.m.
4. Validerar att alla poster har giltiga yrkeskoder och fördelningstal.
5. Visar en lista med varningar för personer som saknar komplett data (och som därmed utesluts ur exporten). Denna lista kan laddas ner som en PDF-fellista (`Byggnads_fellista_YYYY-MM-DD.pdf`).
6. Genererar en ny, formaterad XML-fil (ISO-8859-1) sorterad och uppdelad i block per länkod, samt en matchande CSV-rapport (UTF-8 BOM för Excel-kompatibilitet) via ett dedikerat Exportcenter med separata nedladdningskort.

### De två lägena
* **Projekt-läge:** Län & Kommun hämtas direkt från respektive projekt i XML-filerna. Ingen CSV-fil behövs. Samma personnummer kan förekomma separat på olika projektorter.
* **Anställd-läge / Hängavtal:** Län & kommun styrs av personkortet i den uppladdade CSV-filen. Samma personnummer slås ihop oavsett var det förekommer i XML-filerna.

---

## Dataflöde och integritet

> [!IMPORTANT]
> **Högsta datasäkerhet och GDPR-efterlevnad.**
> Eftersom all databehandling sker direkt i användarens webbläsare, skickas aldrig dina känsliga filer eller personuppgifter över nätverket. All konvertering och filgenerering sker i webbläsarens lokala minne via standard-API:er.

---

## Projektstruktur

```
Bygglösen/
├── index.html            # Huvudanvändargränssnitt (HTML/CSS/JS)
├── converter.js          # Konverteringslogik, XML-hantering samt länkod-databas (JS)
├── lankod_map.json       # JSON-version av länskodsdatabasen (för referens)
├── img/                  # Logotyp-resurser
│   └── exsitec_logo_grey.svg # Exsitec-logotyp för gränssnittet
├── test_runner.html      # Visuell testkörare för webbläsaren
├── test_runner.js        # Headless testkörare för Node.js
├── package.json          # Dependencies för lokala JS-tester (jsdom)
├── Byggnads LänKommun_formatted (1).csv  # Exempelfil för anställd-läge
└── DOKUMENTATION.md      # Teknisk dokumentation av systemet
```

---

## Lokal utveckling och tester

Du kan köra applikationen lokalt genom att helt enkelt dubbelklicka på `index.html` eller köra en lokal webbserver.

### Köra tester

Testerna validerar XML/CSV-sammanslagning, fallback-logik, teckenkodning och filtrering. Du kan köra dem på två sätt:

#### 1. I webbläsaren (Visuellt)
Dubbelklicka på `test_runner.html`. Sidan kör alla tester och visar gröna eller röda resultat direkt på skärmen.

#### 2. Via terminalen (Node.js)
Installera testberoenden och kör skriptet:
```bash
npm install
node test_runner.js
```

---

## Driftsättning (Azure Static Web Apps)

Eftersom appen nu är 100% statisk kan den driftsättas kostnadsfritt på **Azure Static Web Apps**. 

### Fördelar med Azure Static Web Apps (Free tier)
- **0 kr/månad** i fasta avgifter (ACR och ACA kan stängas ner).
- Ingen hantering av containrar, registry-lösenord eller kalla starter.
- Blixtsnabb laddning via globalt CDN.

### Snabbdeploy via Azure CLI
1. Stå i katalogen där `index.html` ligger.
2. Skapa den statiska webbappen:
   ```bash
   az staticwebapp create \
     --name bygglosen-converter \
     --resource-group HRM_apps \
     --source . \
     --location "swedencentral" \
     --sku Free
   ```
3. Följ instruktionerna i Azure CLI för att länka ditt GitHub-repo för automatisk CI/CD vid push till branchen.
