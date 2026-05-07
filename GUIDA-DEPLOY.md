# 🌊 OndaMia — Guida Completa Deploy & Play Store
## Da file HTML → App Android pubblicata

---

## 📋 PANORAMICA DEL PROCESSO

```
[File HTML locale]
      ↓
[GitHub Pages — hosting gratuito]
      ↓
[Bubblewrap — converte PWA in APK]
      ↓
[Android Studio — test su emulatore]
      ↓
[Google Play Console — pubblicazione]
```

---

## STEP 1 — Struttura file del progetto

Assicurati di avere questa struttura nella cartella `ondamia-pwa/`:

```
ondamia-pwa/
│
├── index.html          ← App principale
├── manifest.json       ← Configurazione PWA
├── sw.js               ← Service Worker (cache offline)
├── offline.html        ← Pagina offline
├── generate_icons.py   ← Generatore icone
│
└── icons/
    ├── icon-72.png
    ├── icon-96.png
    ├── icon-128.png
    ├── icon-144.png
    ├── icon-152.png
    ├── icon-192.png    ← maskable (richiesta da Android)
    ├── icon-384.png
    └── icon-512.png    ← maskable (richiesta dal Play Store)
```

---

## STEP 2 — Genera le icone

```bash
# Installa Pillow se non ce l'hai
pip install Pillow

# Genera icone di default (logo OndaMia)
python3 generate_icons.py

# OPPURE usa il tuo logo
python3 generate_icons.py --source logo.png
```

> ⚠️ Le icone maskable (192 e 512) sono **obbligatorie** per il Play Store.

---

## STEP 3 — Deploy su GitHub Pages (hosting gratuito)

### 3a. Crea un account GitHub (se non ce l'hai)
→ https://github.com/signup

### 3b. Crea repository
1. Vai su https://github.com/new
2. Nome repo: `ondamia`
3. Spunta **Public**
4. Clicca **Create repository**

### 3c. Carica i file
```bash
# Da terminale nella cartella ondamia-pwa/
git init
git add .
git commit -m "OndaMia v1.0 — primo deploy"
git branch -M main
git remote add origin https://github.com/TUO-USERNAME/ondamia.git
git push -u origin main
```

### 3d. Attiva GitHub Pages
1. Vai su Settings del repo → Pages
2. Source: **Deploy from branch**
3. Branch: `main` / `/ (root)`
4. Salva

Dopo 1-2 minuti la tua PWA sarà live su:
```
https://TUO-USERNAME.github.io/ondamia/
```

### 3e. Verifica che la PWA funzioni
Apri l'URL nel browser → F12 → Application → Manifest
Deve mostrare tutti i campi di `manifest.json`.

---

## STEP 4 — Configura Digital Asset Links

> Questo è il passaggio che "lega" la PWA all'app Android (richiesto da Google).

### 4a. Genera la firma dell'app
Dopo aver creato il progetto con Bubblewrap (Step 5), esegui:
```bash
keytool -list -v -keystore ondamia.keystore
```
Copia il valore **SHA-256 fingerprint**.

### 4b. Crea il file assetlinks.json
Crea la cartella `.well-known/` nel tuo repo e il file:

**`.well-known/assetlinks.json`**
```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "it.ondamia.app",
    "sha256_cert_fingerprints": [
      "AA:BB:CC:...:TUO-SHA256-QUI"
    ]
  }
}]
```

Poi committa e pusha. Sarà accessibile su:
```
https://TUO-USERNAME.github.io/ondamia/.well-known/assetlinks.json
```

---

## STEP 5 — Bubblewrap: converti PWA in APK

### 5a. Installa i requisiti
```bash
# Installa Node.js (se non ce l'hai)
# → https://nodejs.org

# Installa Bubblewrap globalmente
npm install -g @bubblewrap/cli
```

### 5b. Inizializza il progetto TWA
```bash
mkdir ondamia-twa
cd ondamia-twa

bubblewrap init --manifest https://TUO-USERNAME.github.io/ondamia/manifest.json
```

Bubblewrap ti farà alcune domande. Rispondi così:

| Domanda | Risposta consigliata |
|--------|---------------------|
| Application name | OndaMia |
| Package ID | it.ondamia.app |
| Version code | 1 |
| Version name | 1.0.0 |
| Signing key path | ondamia.keystore |
| Signing key alias | ondamia |
| Min SDK version | 23 (Android 6.0) |
| Target SDK version | 34 |
| Enable notifications | Y (per future push) |

### 5c. Genera l'APK
```bash
bubblewrap build
```

Troverai il file `app-release-signed.apk` nella cartella di output.

---

## STEP 6 — Test in Android Studio

### 6a. Apri il progetto
1. Avvia Android Studio
2. **Open** → seleziona la cartella `ondamia-twa/`
3. Aspetta il sync Gradle (può volerci qualche minuto)

### 6b. Crea un emulatore
1. **Tools → Device Manager → Create Device**
2. Scegli: **Pixel 7** (o simile)
3. System image: **API 34 (Android 14)**
4. Finish

### 6c. Esegui l'app
- Premi ▶ (Run) con l'emulatore selezionato
- L'app si aprirà nell'emulatore come vera app Android

### 6d. Cosa verificare sull'emulatore
- [ ] App si apre senza barra URL (standalone mode) ✓
- [ ] Navigazione tra le sezioni funziona ✓
- [ ] localStorage salva i dati ✓
- [ ] Pagina offline quando si disattiva la rete ✓
- [ ] Icona app nella home screen ✓
- [ ] Splash screen con colori corretti ✓

---

## STEP 7 — Google Play Console

### 7a. Account sviluppatore
→ https://play.google.com/console
Costo una tantum: **25 USD**

### 7b. Crea l'app
1. **Crea app** → Applicazione
2. Nome: OndaMia — Diario Emozionale
3. Lingua predefinita: Italiano
4. App o Gioco: **App**
5. Gratuita o a pagamento: **Gratuita**

### 7c. Carica l'APK / AAB
Per il Play Store è preferibile l'**AAB** (Android App Bundle):
```bash
bubblewrap build --skipPwaValidation
# Il file .aab è preferito al .apk per il Play Store
```

1. **Release → Production → Create new release**
2. Carica il file `.aab`
3. Aggiungi note di release in italiano

### 7d. Scheda del Play Store (da compilare)
```
Titolo:       OndaMia — Diario Emozionale
Sottotitolo:  Esplora le tue emozioni, respira, scrivi

Descrizione breve (80 car.):
Diario emotivo interattivo per adolescenti. Mappa corporea, respirazione guidata e journaling creativo.

Descrizione completa:
OndaMia è uno spazio sicuro per esplorare le proprie emozioni.
Con la mappa corporea interattiva puoi indicare dove senti tensione o
calore e scoprire l'emozione collegata. Tecniche di respirazione guidata
(Box Breathing, 4-7-8, Coerenza Cardiaca) ti aiutano nei momenti difficili.
Il journaling creativo trasforma il blocco emotivo in espressione artistica.
La Scatola delle Emozioni ti permette di depositare pensieri e emoji come
gesto concreto di consapevolezza.

Categoria: Salute e fitness / Benessere mentale
Tag: emozioni, adolescenti, mindfulness, diario, alessitimia
```

### 7e. Screenshot richiesti
Dimensioni Play Store (obbligatorie):
- Telefono: 1080×1920 px (almeno 2, max 8)
- Tablet 7": 1200×1920 px
- Feature graphic: 1024×500 px

Per catturarli usa l'emulatore Android Studio:
**Camera icon → Screenshot** nella barra laterale dell'emulatore.

### 7f. Classificazione contenuti
1. Vai su **Classificazione contenuti**
2. Compila il questionario onestamente
3. Sezione salute mentale: seleziona le opzioni appropriate
4. La classificazione sarà circa **PEGI 3** o **PEGI 7**

### 7g. Privacy Policy (OBBLIGATORIA)
Devi pubblicare una Privacy Policy. Dato che l'app salva dati solo in locale:

Esempio minimo:
```
OndaMia non raccoglie, trasmette né condivide dati personali.
Tutti i dati (voci del diario, emozioni, sessioni di respiro) sono
salvati esclusivamente sul dispositivo dell'utente tramite localStorage.
Nessun dato viene inviato a server esterni.
L'app non utilizza analytics, cookie di terze parti o pubblicità.
```

Pubblica questa policy su GitHub Pages:
`https://TUO-USERNAME.github.io/ondamia/privacy.html`

---

## 🗓️ TIMELINE REALISTICA

| Fase | Tempo stimato |
|------|--------------|
| Genera icone + deploy GitHub Pages | 30 min |
| Setup Bubblewrap + genera APK | 1-2 ore |
| Test in Android Studio | 2-4 ore |
| Compilazione scheda Play Store | 2-3 ore |
| **Review Google** | **3-7 giorni** |
| **App live nel Play Store** | ✅ |

---

## 🔮 STEP 2 (FUTURO) — Backend + Community

Quando sarai pronto per la versione con backend:

```
PWA attuale (offline)
      +
Supabase (database gratuito) / Firebase
      ↓
- Account utenti (anonimo o con email)
- Sync diario su cloud
- Community: thread anonimi per emozione
- Link psicologi / associazioni
- Notifiche push giornaliere
```

Tecnologie consigliate:
- **Supabase** (PostgreSQL + Auth + Realtime) — gratuito fino a 50k utenti
- **Cloudflare Workers** — per le API (gratuito)

---

## 📞 RISORSE UTILI

- Bubblewrap docs: https://github.com/GoogleChromeLabs/bubblewrap
- PWA Checker: https://www.pwabuilder.com
- Play Console: https://play.google.com/console
- Digital Asset Links tester: https://developers.google.com/digital-asset-links/tools/generator
- Lighthouse audit PWA: DevTools → Lighthouse → Progressive Web App

---

*Documento generato per il progetto OndaMia — Diario Emozionale Interattivo*
*Versione 1.0 — Step 1: PWA offline*
