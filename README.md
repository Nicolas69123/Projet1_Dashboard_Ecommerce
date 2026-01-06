# Projet 1 : Dashboard KPIs E-commerce

**Demo en ligne :** https://nicolas69123.github.io/Projet1_Dashboard_Ecommerce/

---

## Contexte & Problematique

**Situation initiale :** Une startup e-commerce manque de visibilite sur ses performances. Excel devient inadequat face a 500k+ transactions annuelles.

**Besoin metier :** Creer un dashboard professionnel avec KPIs temps reel pour le CEO et l'equipe marketing.

## Objectifs

- Implementer un tableau de bord Power BI professionnel
- Fournir une visibilite temps reel sur les KPIs
- Remplacer Excel par une solution scalable

## Donnees Disponibles

| Element | Detail |
|---------|--------|
| **Source** | Online Retail Dataset (UCI) + donnees generees |
| **Volume** | 541,909 transactions sur 12 mois |
| **Enrichissement** | Donnees recentes generees via Faker Python |

**Champs cles :** ID transaction, date, client, produit, quantite, prix unitaire, montant total

## KPIs a Calculer

### Ventes
- Chiffre d'affaires (jour, mois, annee)
- Evolution CA vs N-1
- Top 10 produits

### Clients
- Nouveaux clients vs recurrents
- Panier moyen
- Taux de conversion
- Analyse RFM (Recence, Frequence, Montant)

### Cohortes
- Retention par mois de premiere commande
- LTV (Lifetime Value) par cohorte

## Stack Technique

| Outil | Usage |
|-------|-------|
| Python | ETL, generation donnees |
| Pandas/NumPy | Manipulation donnees |
| DuckDB | Requetes analytiques |
| Power BI / Streamlit | Dashboard |
| PostgreSQL | Base de donnees (optionnel) |

## Structure du Projet

```
Projet1_Dashboard_Ecommerce/
├── README.md
├── index.html                    # Redirection GitHub Pages
├── dashboard.html                # Dashboard statique
├── data/
│   └── transactions.csv          # Donnees generees
├── src/
│   ├── generate_data.py          # Generation des donnees
│   ├── etl_pipeline.py           # Pipeline ETL
│   ├── kpi_calculations.py       # Calculs KPIs
│   ├── rfm_analysis.py           # Analyse RFM
│   └── dashboard_streamlit.py    # Dashboard interactif
└── output/
    └── kpis_report.html          # Rapport genere
```

## Quick Start

```bash
# 1. Installer les dependances
pip install pandas numpy duckdb faker streamlit plotly

# 2. Generer les donnees
python src/generate_data.py

# 3. Executer l'ETL
python src/etl_pipeline.py

# 4. Lancer le dashboard
streamlit run src/dashboard_streamlit.py
```

## Criteres de Reussite

- [ ] Chargement du dashboard < 3 secondes
- [ ] Actualisation quotidienne automatique
- [ ] KPIs e-commerce complets et standards
- [ ] Design professionnel

## Duree & Difficulte

- **Difficulte :** Intermediaire
- **Duree estimee :** 60 minutes
