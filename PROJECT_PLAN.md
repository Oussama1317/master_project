# AI Insurance Adjuster — Project Plan

## Overview
Système intelligent d'estimation des sinistres et de détection des fraudes pour compagnies d'assurance, combinant vision par ordinateur et analyse de données.

---

## 1. Architecture Globale

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend / API                        │
│         (Upload d'images, formulaire sinistre)           │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
               ▼                          ▼
┌─────────────────────────┐  ┌─────────────────────────────┐
│  Engine A                │  │  Engine B                    │
│  Cost Estimation         │  │  Fraud Detection             │
│                          │  │                              │
│  • Semantic Segmentation │  │  • Pattern Analysis          │
│  • Damage Measurement    │  │  • Inconsistency Detection   │
│  • Pricing DB Lookup     │  │  • Red Flag System           │
└───────────┬─────────────┘  └──────────────┬──────────────┘
            │                               │
            ▼                               ▼
┌──────────────────────────────────────────────────────────┐
│                    AI/ML Pipeline                        │
│  • YOLO + Mask R-CNN                                     │
│  • U-Net (Segmentation)                                  │
│  • Anomaly Detection Models                              │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Phases du Projet

### Phase 1 — Fondations (Semaine 1-2)
- [ ] Initialisation du projet (Python, env, structure)
- [ ] Setup dataset : COCO, Kaggle Car Damage, Fire Detection
- [ ] Installation de YOLOv8 / Detectron2 / U-Net
- [ ] Pipeline de prétraitement d'images (augmentation, normalisation)

### Phase 2 — Moteur A : Cost Estimation (Semaine 3-5)
- [ ] Entraînement du modèle de segmentation sémantique (U-Net / Mask R-CNN)
- [ ] Module de mesure des zones endommagées (pixel → m²)
- [ ] Base de données de prix (SQLite / CSV des matériaux)
- [ ] API de génération de facture estimative
- [ ] Tests et validation

### Phase 3 — Moteur B : Fraud Detection (Semaine 6-8)
- [ ] Analyse des motifs de brûlure (Pool Pattern, V-Pattern, etc.)
- [ ] Comparaison texte vs image (NLP + CV)
- [ ] Système de scoring / Red Flags
- [ ] Générateur de données synthétiques (Unreal Engine / Blender)
- [ ] Entraînement sur données réelles + synthétiques

### Phase 4 — Intégration & Déploiement (Semaine 9-10)
- [ ] API REST complète (FastAPI)
- [ ] Interface de démonstration (Streamlit / Gradio)
- [ ] Tests d'intégration
- [ ] Documentation

---

## 3. Stack Technique

| Composant              | Technologie                        |
|-----------------------|------------------------------------|
| Langage               | Python 3.11+                       |
| Deep Learning         | PyTorch, TensorFlow                |
| Segmentation          | U-Net, Mask R-CNN, YOLOv8-seg      |
| Object Detection      | YOLOv8, Detectron2                 |
| NLP                   | BERT / Sentence Transformers       |
| Web Framework         | FastAPI                            |
| UI Demo               | Streamlit / Gradio                 |
| Data Processing       | OpenCV, NumPy, Pandas              |
| Data Augmentation     | Albumentations, Imgaug             |
| Synthetic Data        | Unreal Engine / Blender + Python   |
| Database              | SQLite / PostgreSQL                |

---

## 4. Jeux de Données

| Dataset           | Source        | Usage                              |
|-------------------|--------------|------------------------------------|
| COCO              | cocodataset.org | Objets courants (meubles, etc.)   |
| Car Damage        | Kaggle       | Dégâts matériels                   |
| Fire & Smoke      | Kaggle/Roboflow | Détection incendie                |
| xView             | DIUx         | Catastrophes structurelles         |
| Synthétiques      | Unreal Engine | Incendies criminels générés        |

---

## 5. Modèles de Détection de Fraude (Patterns)

| Pattern           | Description                                      | Red Flag |
|-------------------|--------------------------------------------------|----------|
| Pool Pattern      | Tache circulaire → liquide inflammable versé      | 🔴 Haut  |
| V-Pattern         | Traces en V → point d'origine suspect             | 🟡 Moyen |
| Multiple Origins  | Plusieurs foyers d'incendie                       | 🔴 Haut  |
| Missing Items     | Objets valorisants absents avant sinistre         | 🔴 Haut  |
| Incohérence texte | Description ne correspond pas aux dégâts visibles | 🟡 Moyen |

---

## 6. Métriques de Succès

- **Précision segmentation** : IoU ≥ 0.75
- **Précision détection fraude** : F1-score ≥ 0.85
- **Taux de faux positifs** : ≤ 5%
- **Temps de traitement** : ≤ 5 secondes par image

---

## 7. Structure des Dossiers Proposée

```
master_project/
├── data/
│   ├── raw/              # Datasets bruts
│   ├── processed/        # Données prétraitées
│   └── synthetic/        # Données générées
├── models/
│   ├── segmentation/     # U-Net / Mask R-CNN
│   ├── detection/        # YOLO
│   └── fraud/            # Patterns & NLP
├── src/
│   ├── engine_a/         # Cost Estimation
│   │   ├── segmentation.py
│   │   ├── measurement.py
│   │   └── pricing.py
│   ├── engine_b/         # Fraud Detection
│   │   ├── pattern_analysis.py
│   │   ├── inconsistency.py
│   │   └── red_flag.py
│   ├── api/              # FastAPI
│   ├── preprocessing/    # Image processing
│   └── utils/            # Helpers
├── notebooks/            # Jupyter experiments
├── synthetic/            # Unreal Engine scripts
├── requirements.txt
├── PROJECT_PLAN.md
└── README.md
```

---

## 8. Prochaines Étapes Immédiates

1. **Valider ce plan** avec l'équipe
2. **Configurer l'environnement** Python + dépendances
3. **Télécharger les datasets** open-source
4. **Créer le premier notebook** d'exploration
5. **Démarrer Phase 1** — Fondations
