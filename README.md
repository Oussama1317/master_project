# AI Insurance Adjuster

Système intelligent d'estimation des sinistres et de détection des fraudes pour compagnies d'assurance.

## Architecture

- **Engine A** — Cost Estimation : Segmentation sémantique des dommages + calcul de zone + tarification
- **Engine B** — Fraud Detection : Analyse des motifs criminels + détection d'incohérences

## Structure

```
src/
├── engine_a/          # Cost Estimation Engine
│   ├── segmentation.py
│   ├── measurement.py
│   └── pricing.py
├── engine_b/          # Fraud Detection Engine
│   ├── pattern_analysis.py
│   ├── inconsistency.py
│   └── red_flag.py
├── api/               # FastAPI endpoints
├── preprocessing/     # Image preprocessing pipeline
└── utils/             # Shared utilities
```

## Installation

```bash
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

## Démarrage

```bash
uvicorn src.api.main:app --reload
```

Voir `PROJECT_PLAN.md` pour le plan détaillé.
