# VIX Entropie Dashboard

Frühwarnsystem für Marktstress nach der Methode von Thorsten Wegener (The Tactical Brief, 2026). Berechnet täglich die 21-Tage-Shannon-Entropie der VIX-Veränderungen und zeigt das aktuelle Marktregime.

**Live-Demo:** https://thblees.github.io/vix-entropie/

## Was wird gemessen?

- **VIX**: implizite Volatilität S&P 500 (Tagesschluss)
- **Shannon-Entropie**: Unordnung der täglichen VIX-Veränderungen über 21 Tage, normalisiert auf 0–100 %
- **Aktive Bins**: Wie viele der 6 Klassen (von "großer Crash" bis "großer Spike") aktiv waren
- **Regime-Klassifikation**: Low / Moderate / Elevated / Danger Zone / High

## Setup auf GitHub (einmalig, ca. 15 Minuten)

### Schritt 1: Neues Repository anlegen
1. Auf [github.com/new](https://github.com/new) ein neues Repository anlegen
2. Name: `vix-entropie` (oder beliebig)
3. Auf **Public** stellen (sonst funktioniert GitHub Pages im kostenlosen Plan nicht)
4. Erstmal **kein** README, kein .gitignore, keine License

### Schritt 2: Dateien hochladen
Die folgenden Dateien aus diesem Ordner hochladen (Drag&Drop in der GitHub-Web-UI funktioniert):
- `index.html`
- `update_vix.py`
- `data.json` (wird vom Skript erzeugt – einmal mitliefern)
- `.github/workflows/daily-update.yml` (wichtig: Ordnerstruktur erhalten)
- `README.md`

### Schritt 3: GitHub Pages aktivieren
1. Im Repository auf **Settings** → **Pages**
2. Unter **Source**: `Deploy from a branch` wählen
3. Branch: `main`, Folder: `/ (root)`
4. Speichern. Nach ein paar Minuten ist die Seite unter `https://DEIN-USERNAME.github.io/vix-entropie/` erreichbar

### Schritt 4: Workflow-Berechtigungen prüfen
1. **Settings** → **Actions** → **General**
2. Unter **Workflow permissions**: `Read and write permissions` aktivieren
3. Speichern

### Schritt 5: Erste Ausführung manuell starten
1. Tab **Actions** → links auf `Daily VIX Entropy Update`
2. Rechts auf **Run workflow** → grünen Button drücken
3. Nach ~1 Minute sollte ein Commit "Auto-Update: VIX-Daten ..." erscheinen

Ab jetzt aktualisiert sich das Dashboard jeden Werktag automatisch um 23:00 UTC (kurz nach US-Börsenschluss).

## Lokales Testen (optional)

```bash
pip install yfinance pandas numpy
python update_vix.py
# öffnet data.json
# index.html im Browser öffnen (am besten via Local Server, sonst CORS-Fehler beim fetch)
python -m http.server 8000
# dann http://localhost:8000 aufrufen
```

## Methodik

Tägliche VIX-Veränderung dVIX = VIX(t) - VIX(t-1). Einsortierung in 6 Bins:

| Bin | Bereich | Bedeutung |
|-----|---------|-----------|
| 1   | < -4    | großer Vola-Crash |
| 2   | -4 bis -2 | mittlerer Crash |
| 3   | -2 bis 0  | leichte Beruhigung |
| 4   | 0 bis +2  | leichte Anspannung |
| 5   | +2 bis +4 | mittlerer Spike |
| 6   | > +4    | großer Vola-Spike |

Shannon-Entropie über 21 Tage:
H = -Σ p(x) · log₂(p(x))

Normalisierung: H / log₂(6) · 100 %

## Disclaimer

Nur zu Bildungs- und Informationszwecken. Keine Anlageberatung. Vergangene Ergebnisse garantieren keine zukünftigen Ergebnisse.
