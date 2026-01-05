"""
📊 Projet 1 - Analyse RFM (Récence, Fréquence, Montant)
Segmentation clients pour le marketing
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime


def calculate_rfm_scores(transactions_df: pd.DataFrame, reference_date: datetime = None) -> pd.DataFrame:
    """
    Calcule les scores RFM pour chaque client.

    R (Récence): Jours depuis le dernier achat
    F (Fréquence): Nombre de transactions
    M (Montant): Total dépensé
    """
    if reference_date is None:
        reference_date = transactions_df['date'].max()

    # Calcul des métriques RFM brutes
    rfm = transactions_df.groupby('customer_id').agg({
        'date': 'max',  # Dernier achat
        'transaction_id': 'count',  # Nombre de transactions
        'total_amount': 'sum'  # Total dépensé
    }).reset_index()

    rfm.columns = ['customer_id', 'last_purchase', 'frequency', 'monetary']

    # Calcul de la récence (jours depuis dernier achat)
    rfm['recency'] = (reference_date - rfm['last_purchase']).dt.days

    return rfm


def assign_rfm_scores(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """Attribue des scores de 1 à 5 pour R, F, M."""
    df = rfm_df.copy()

    # Score Récence (inversé: moins c'est récent, meilleur c'est)
    df['R_score'] = pd.qcut(df['recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')

    # Score Fréquence
    df['F_score'] = pd.qcut(df['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

    # Score Montant
    df['M_score'] = pd.qcut(df['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

    # Convertir en int
    df['R_score'] = df['R_score'].astype(int)
    df['F_score'] = df['F_score'].astype(int)
    df['M_score'] = df['M_score'].astype(int)

    # Score RFM combiné
    df['RFM_score'] = df['R_score'].astype(str) + df['F_score'].astype(str) + df['M_score'].astype(str)
    df['RFM_total'] = df['R_score'] + df['F_score'] + df['M_score']

    return df


def segment_customers(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """Segmente les clients selon leur profil RFM."""
    df = rfm_df.copy()

    def get_segment(row):
        r, f, m = row['R_score'], row['F_score'], row['M_score']

        # Champions: Achètent récemment, souvent, et beaucoup
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'

        # Clients fidèles: Achètent régulièrement
        elif f >= 4:
            return 'Fidèles'

        # Clients potentiels: Récents mais pas encore fidélisés
        elif r >= 4 and f <= 2:
            return 'Nouveaux prometteurs'

        # À risque: Étaient bons clients mais s'éloignent
        elif r <= 2 and f >= 3 and m >= 3:
            return 'À risque'

        # Endormis: N'ont pas acheté depuis longtemps
        elif r <= 2 and f <= 2:
            return 'Endormis'

        # Clients occasionnels
        elif f <= 2:
            return 'Occasionnels'

        # Autres
        else:
            return 'Moyens'

    df['segment'] = df.apply(get_segment, axis=1)

    return df


def get_segment_recommendations(segment: str) -> dict:
    """Retourne les recommandations marketing par segment."""
    recommendations = {
        'Champions': {
            'description': 'Vos meilleurs clients',
            'action': 'Récompenser avec un programme VIP, early access aux nouveautés',
            'retention_priority': 'Haute'
        },
        'Fidèles': {
            'description': 'Clients réguliers et engagés',
            'action': 'Upselling, programme de fidélité, parrainage',
            'retention_priority': 'Haute'
        },
        'Nouveaux prometteurs': {
            'description': 'Nouveaux clients à fort potentiel',
            'action': 'Onboarding personnalisé, offres de bienvenue',
            'retention_priority': 'Moyenne'
        },
        'À risque': {
            'description': 'Bons clients qui s\'éloignent',
            'action': 'Campagne de réactivation urgente, offres spéciales',
            'retention_priority': 'Critique'
        },
        'Endormis': {
            'description': 'Clients inactifs depuis longtemps',
            'action': 'Campagne win-back, enquête satisfaction',
            'retention_priority': 'Basse'
        },
        'Occasionnels': {
            'description': 'Clients ponctuels',
            'action': 'Incentives pour augmenter la fréquence',
            'retention_priority': 'Moyenne'
        },
        'Moyens': {
            'description': 'Clients standards',
            'action': 'Personnalisation pour améliorer l\'engagement',
            'retention_priority': 'Moyenne'
        }
    }
    return recommendations.get(segment, {})


def generate_rfm_report(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """Génère un rapport de synthèse par segment."""
    report = rfm_df.groupby('segment').agg({
        'customer_id': 'count',
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': ['mean', 'sum']
    }).round(2)

    report.columns = ['nb_clients', 'recency_moy', 'frequency_moy', 'monetary_moy', 'monetary_total']
    report['pct_clients'] = (report['nb_clients'] / report['nb_clients'].sum() * 100).round(1)
    report['pct_revenue'] = (report['monetary_total'] / report['monetary_total'].sum() * 100).round(1)

    return report.sort_values('monetary_total', ascending=False)


def main():
    """Exécute l'analyse RFM complète."""
    print("=" * 50)
    print("📊 ANALYSE RFM - SEGMENTATION CLIENTS")
    print("=" * 50)

    # Chemins
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, '..', 'data')
    output_dir = os.path.join(base_dir, '..', 'output')

    # Chargement des transactions
    print("\n📂 Chargement des données...")
    transactions_df = pd.read_csv(
        os.path.join(data_dir, 'transactions.csv'),
        parse_dates=['date']
    )
    print(f"   ✓ {len(transactions_df):,} transactions chargées")

    # Calcul RFM
    print("\n🔢 Calcul des scores RFM...")
    rfm = calculate_rfm_scores(transactions_df)
    rfm = assign_rfm_scores(rfm)
    rfm = segment_customers(rfm)
    print(f"   ✓ {len(rfm):,} clients analysés")

    # Rapport
    print("\n📊 Rapport par segment:")
    report = generate_rfm_report(rfm)
    print(report.to_string())

    # Sauvegarde
    os.makedirs(output_dir, exist_ok=True)
    rfm.to_csv(os.path.join(output_dir, 'rfm_analysis.csv'), index=False)
    report.to_csv(os.path.join(output_dir, 'rfm_report.csv'))

    print(f"\n✅ Analyse sauvegardée dans {output_dir}")

    # Recommandations
    print("\n💡 Recommandations par segment:")
    for segment in rfm['segment'].unique():
        reco = get_segment_recommendations(segment)
        count = len(rfm[rfm['segment'] == segment])
        print(f"\n   🎯 {segment} ({count} clients)")
        print(f"      Action: {reco.get('action', 'N/A')}")


if __name__ == "__main__":
    main()
