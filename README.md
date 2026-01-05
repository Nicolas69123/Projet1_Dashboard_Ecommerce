# 📊 Projet 1 : Dashboard KPIs E-commerce

## 🎯 Contexte & Problématique

**Situation initiale :** Une startup e-commerce manque de visibilité sur ses performances. Excel devient inadéquat face à 500k+ transactions annuelles.

**Besoin métier :** Créer un dashboard professionnel avec KPIs temps réel pour le CEO et l'équipe marketing.

## 📋 Objectifs

- ✅ Implémenter un tableau de bord Power BI professionnel
- ✅ Fournir une visibilité temps réel sur les KPIs
- ✅ Remplacer Excel par une solution scalable

## 📊 Données Disponibles

| Élément | Détail |
|---------|--------|
| **Source** | Online Retail Dataset (UCI) + données générées |
| **Volume** | 541,909 transactions sur 12 mois |
| **Enrichissement** | Données récentes générées via Faker Python |

**Champs clés :** ID transaction, date, client, produit, quantité, prix unitaire, montant total

## 🔢 KPIs à Calculer

### 💰 Ventes
- Chiffre d'affaires (jour, mois, année)
- Évolution CA vs N-1
- Top 10 produits

### 👥 Clients
- Nouveaux clients vs récurrents
- Panier moyen
- Taux de conversion
- **Analyse RFM** (Récence, Fréquence, Montant)

### 📈 Cohortes
- Rétention par mois de première commande
- LTV (Lifetime Value) par cohorte

## 🛠️ Stack Technique

| Outil | Usage |
|-------|-------|
| Python | ETL, génération données |
| Pandas/NumPy | Manipulation données |
| DuckDB | Requêtes analytiques |
| Power BI / Streamlit | Dashboard |
| PostgreSQL | Base de données (optionnel) |

## 📁 Structure du Projet

```
Projet1_Dashboard_Ecommerce/
├── README.md
├── data/
│   └── transactions.csv          # Données générées
├── src/
│   ├── generate_data.py          # Génération des données
│   ├── etl_pipeline.py           # Pipeline ETL
│   ├── kpi_calculations.py       # Calculs KPIs
│   ├── rfm_analysis.py           # Analyse RFM
│   └── dashboard_streamlit.py    # Dashboard interactif
└── output/
    └── kpis_report.html          # Rapport généré
```

## 🚀 Quick Start

```bash
# 1. Installer les dépendances
pip install pandas numpy duckdb faker streamlit plotly

# 2. Générer les données
python src/generate_data.py

# 3. Exécuter l'ETL
python src/etl_pipeline.py

# 4. Lancer le dashboard
streamlit run src/dashboard_streamlit.py
```

## ✅ Critères de Réussite

- [ ] Chargement du dashboard < 3 secondes
- [ ] Actualisation quotidienne automatique
- [ ] KPIs e-commerce complets et standards
- [ ] Design professionnel

## ⏱️ Durée & Difficulté

- **Difficulté :** ⭐⭐⭐ Intermédiaire
- **Durée estimée :** 60 minutes
