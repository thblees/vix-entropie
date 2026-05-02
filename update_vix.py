"""
VIX Entropie Dashboard - Daily Update Script
Holt VIX-Tagesschlusskurse, berechnet 21-Tage-Shannon-Entropie nach Wegener,
schreibt das Ergebnis als JSON für das HTML-Dashboard.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
from datetime import datetime, timezone

# ---------------------------------------------------------------
# 1. VIX-Daten holen (letzte 2 Jahre, damit Backtest moeglich ist)
# ---------------------------------------------------------------
print("Hole VIX-Daten von Yahoo Finance...")
vix = yf.download("^VIX", period="2y", interval="1d", auto_adjust=False, progress=False)

# yfinance kann MultiIndex-Spalten zurückgeben - flach machen
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.get_level_values(0)

vix = vix[["Close"]].copy()
vix.columns = ["VIX"]
vix = vix.dropna()
print(f"  {len(vix)} Tage VIX-Daten geladen, letzter Tag: {vix.index[-1].date()}")

# ---------------------------------------------------------------
# 2. Tägliche VIX-Veränderung
# ---------------------------------------------------------------
vix["dVIX"] = vix["VIX"].diff()

# ---------------------------------------------------------------
# 3. In 6 Bins einsortieren (nach Wegener)
#    Bin 1: < -4   (großer Vola-Crash)
#    Bin 2: -4 bis -2
#    Bin 3: -2 bis 0
#    Bin 4: 0 bis +2
#    Bin 5: +2 bis +4
#    Bin 6: > +4   (großer Vola-Spike)
# ---------------------------------------------------------------
bins = [-np.inf, -4, -2, 0, 2, 4, np.inf]
bin_labels = ["<-4", "-4..-2", "-2..0", "0..+2", "+2..+4", ">+4"]
vix["bin"] = pd.cut(vix["dVIX"], bins=bins, labels=bin_labels)

# ---------------------------------------------------------------
# 4. Rolling 21-Day Shannon-Entropie
# ---------------------------------------------------------------
WINDOW = 21
MAX_ENTROPY = np.log2(6)  # ca. 2.585 Bits = 100%

def shannon_entropy_normalized(window_bins):
    """Berechnet normalisierte Shannon-Entropie für ein Fenster von Bin-Labels."""
    counts = window_bins.value_counts()
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    h = -np.sum(probs * np.log2(probs))
    return (h / MAX_ENTROPY) * 100

def active_bins(window_bins):
    """Zählt, wie viele der 6 Bins im Fenster aktiv waren."""
    return window_bins.value_counts().gt(0).sum()

entropies = []
active = []
dates = []

for i in range(len(vix)):
    if i < WINDOW:
        entropies.append(None)
        active.append(None)
    else:
        window = vix["bin"].iloc[i-WINDOW+1:i+1].dropna()
        if len(window) < WINDOW * 0.8:  # Wenn zu wenig Daten, skip
            entropies.append(None)
            active.append(None)
        else:
            entropies.append(round(shannon_entropy_normalized(window), 2))
            active.append(int(active_bins(window)))

vix["entropy"] = entropies
vix["active_bins"] = active

# ---------------------------------------------------------------
# 5. Regime-Klassifikation
# ---------------------------------------------------------------
def classify(vix_val, entropy_val, bins_active):
    if entropy_val is None:
        return "n/a"
    # Danger Zone: niedriger VIX + hohe Entropie
    if vix_val < 22 and entropy_val >= 65 and bins_active >= 5:
        return "danger_zone"
    if entropy_val >= 80:
        return "high"
    if entropy_val >= 65:
        return "elevated"
    if entropy_val >= 40:
        return "moderate"
    return "low"

vix["regime"] = vix.apply(
    lambda r: classify(r["VIX"], r["entropy"], r["active_bins"]), axis=1
)

# ---------------------------------------------------------------
# 6. JSON-Output für das Dashboard
# ---------------------------------------------------------------
# Letzte 252 Handelstage (ca. 1 Jahr) für den Chart
recent = vix.tail(252).copy()
recent.index = recent.index.strftime("%Y-%m-%d")

data_points = []
for date, row in recent.iterrows():
    data_points.append({
        "date": date,
        "vix": round(row["VIX"], 2),
        "dvix": round(row["dVIX"], 2) if pd.notna(row["dVIX"]) else None,
        "entropy": row["entropy"],
        "active_bins": row["active_bins"],
        "regime": row["regime"]
    })

# Aktueller Stand
latest = vix.iloc[-1]
latest_date = vix.index[-1].strftime("%Y-%m-%d")

# Bin-Verteilung des aktuellen 21-Tage-Fensters
current_window = vix["bin"].tail(WINDOW).dropna()
bin_distribution = {label: int(current_window.value_counts().get(label, 0)) for label in bin_labels}

output = {
    "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "latest": {
        "date": latest_date,
        "vix": round(latest["VIX"], 2),
        "entropy": latest["entropy"],
        "active_bins": int(latest["active_bins"]) if latest["active_bins"] else 0,
        "regime": latest["regime"]
    },
    "current_bin_distribution": bin_distribution,
    "history": data_points
}

with open("data.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"OK - data.json geschrieben")
print(f"  Letzter Tag: {latest_date}")
print(f"  VIX: {round(latest['VIX'], 2)}")
print(f"  Entropie: {latest['entropy']}%")
print(f"  Aktive Bins: {int(latest['active_bins']) if latest['active_bins'] else 0}/6")
print(f"  Regime: {latest['regime']}")
