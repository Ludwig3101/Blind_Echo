# Blind Echo

Ein 2D-Echolot-Horrorspiel in Pygame, inspiriert von *Dark Echo*.

Du bist in völliger Dunkelheit gefangen. Die Welt existiert für dich nur dort, wo Schallwellen von Wänden und Hindernissen abprallen. Aber Vorsicht: Geräusche wecken das, was im Schatten lauert.

## Steuerung

| Taste | Aktion |
|---|---|
| **W, A, S, D** | Bewegen (normale Schritte erzeugen leise Schallwellen) |
| **Shift** (halten) | Schleichen (lautlos, halbes Bewegungstempo) |
| **Leertaste** (tippen) | Klatschen (schneller Schallimpuls) |
| **Leertaste** (halten) | Stampfen aufladen (weites, mehrfach reflektierendes Echo) |
| **R** | Level neu starten |

## Spielelemente

- **Wände & Hindernisse:** Nur sichtbar, wenn Schallwellen darauf treffen.
- **Wasserpfützen (blau):** Verlangsamen die Bewegung und verursachen verräterisches Plätschern.
- **Monster (rot):** Schlafen zunächst in der Dunkelheit. Wenn sie Geräusche hören, wachen sie auf und jagen die Schallquelle.
- **Ausgang (gelb/weiß):** Sendet leise Pings aus – erreiche ihn, um das Level abzuschließen.

## Installation & Start

Voraussetzungen: Python 3 mit `pygame` und `numpy`.

```bash
pip install pygame numpy
python Main.py
```
