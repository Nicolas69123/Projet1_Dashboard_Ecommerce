"""
📊 Test Modélisation - Analyse RFM sur données Online Retail
Analyse RFM basée sur donnees_nettoyees.csv
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime


def load_onlineretail_data(data_dir: str) -> pd.DataFrame:
    """
    Charge les données nettoyées du dataset Online Retail.
    
    Args:
        data_dir: Chemin vers le dossier data
        
    Returns:
        DataFrame avec les données chargées et préparées
    """
    print("\n📂 Chargement des données Online Retail...")
    
    filepath = os.path.join(data_dir, 'donnees_nettoyees.csv')
    
    # Charger le fichier CSV
    df = pd.read_csv(filepath, parse_dates=['InvoiceDate'])
    
    print(f"   ✓ {len(df):,} lignes chargées")
    
    # Filtrer les clients valides (non-null CustomerID)
    initial_count = len(df)
    df = df[df['CustomerID'].notna()]
    df['CustomerID'] = df['CustomerID'].astype(int)
    
    print(f"   ✓ {initial_count - len(df):,} lignes avec CustomerID manquant supprimées")
    print(f"   ✓ {len(df):,} lignes avec clients identifiés")
    
    # Vérifier les colonnes nécessaires
    required_cols = ['InvoiceNo', 'CustomerID', 'InvoiceDate', 'TotalAmount']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colonnes manquantes: {missing_cols}")
    
    # S'assurer que TotalAmount est numérique
    df['TotalAmount'] = pd.to_numeric(df['TotalAmount'], errors='coerce')
    df = df[df['TotalAmount'] > 0]  # Supprimer les montants négatifs ou nuls
    
    print(f"   ✓ {len(df):,} lignes finales après nettoyage")  
    print("Data set for RFM")  
    print(df.head())          
    print(df.info())            

    return df


def calculate_rfm_scores_onlineretail(df: pd.DataFrame, reference_date: datetime = None) -> pd.DataFrame:
    """
    Calcule les scores RFM pour chaque client du dataset Online Retail.
    
    R (Récence): Jours depuis le dernier achat
    F (Fréquence): Nombre de transactions (invoices)
    M (Montant): Total dépensé
    
    Args:
        df: DataFrame avec les transactions
        reference_date: Date de référence pour calculer la récence
        
    Returns:
        DataFrame avec les métriques RFM
    """
    print("\n🔢 Calcul des métriques RFM...")
    
    if reference_date is None:
        reference_date = df['InvoiceDate'].max()
    
    # Calcul des métriques RFM brutes par client
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': 'max',  # Dernier achat
        'InvoiceNo': 'nunique',  # Nombre d'invoices uniques (fréquence)
        'TotalAmount': 'sum'  # Total dépensé
    }).reset_index()
    
    rfm.columns = ['customer_id', 'last_purchase', 'frequency', 'monetary']
    
    # Calcul de la récence (jours depuis dernier achat)
    rfm['recency'] = (reference_date - rfm['last_purchase']).dt.days
    
    print(f"   ✓ {len(rfm):,} clients analysés")
    print(f"   ✓ Date de référence: {reference_date.strftime('%Y-%m-%d')}")
    print("Data set for RFM by customers:")  
    print(rfm.head())          
    print(rfm.info())     

    return rfm


def assign_rfm_scores(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Attribue des scores de 1 à 5 pour R, F, M.
    
    Args:
        rfm_df: DataFrame avec les métriques RFM brutes
        
    Returns:
        DataFrame avec les scores RFM ajoutés
    """
    df = rfm_df.copy()
    
    # Score Récence (inversé: moins c'est récent, meilleur c'est)
    # Récence faible = score élevé (client récent)
    df['R_score'] = pd.qcut(df['recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    
    # Score Fréquence (plus de transactions = score élevé)
    df['F_score'] = pd.qcut(df['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # Score Montant (plus dépensé = score élevé)
    df['M_score'] = pd.qcut(df['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # Convertir en int (gérer les NaN si nécessaire)
    df['R_score'] = df['R_score'].astype(float).fillna(3).astype(int)
    df['F_score'] = df['F_score'].astype(float).fillna(3).astype(int)
    df['M_score'] = df['M_score'].astype(float).fillna(3).astype(int)
    
    # Score RFM combiné
    df['RFM_score'] = df['R_score'].astype(str) + df['F_score'].astype(str) + df['M_score'].astype(str)
    df['RFM_total'] = df['R_score'] + df['F_score'] + df['M_score']
    
    print("Data set for RFM by customers with scores:")  
    print(df.head())          
    print(df.info())   

    return df


def segment_customers(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Segmente les clients selon leur profil RFM.
    
    Args:
        rfm_df: DataFrame avec les scores RFM
        
    Returns:
        DataFrame avec la colonne 'segment' ajoutée
    """
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
    
    print("Data set for RFM by customer segments:")  
    print(df.head())          
    print(df.info())  
     
    return df


def get_segment_recommendations(segment: str) -> dict:
    """
    Retourne les recommandations marketing par segment.
    
    Args:
        segment: Nom du segment
        
    Returns:
        Dictionnaire avec description, action et priorité
    """
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
    """
    Génère un rapport de synthèse par segment.
    
    Args:
        rfm_df: DataFrame avec les scores RFM et segments
        
    Returns:
        DataFrame avec le rapport agrégé par segment
    """
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
    """Exécute l'analyse RFM complète sur les données Online Retail."""
    print("=" * 50)
    print("📊 ANALYSE RFM - DONNÉES ONLINE RETAIL")
    print("=" * 50)
    
    # Chemins
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, '..', '..', 'data')
    output_dir = os.path.join(base_dir, '..', '..', 'output', 'real-data')
    
    # 1. Chargement des données
    df = load_onlineretail_data(data_dir)
    
    # 2. Calcul des métriques RFM
    rfm = calculate_rfm_scores_onlineretail(df)
    
    # 3. Attribution des scores RFM
    print("\n🎯 Attribution des scores RFM...")
    rfm = assign_rfm_scores(rfm)
    print("   ✓ Scores RFM calculés")
    
    # 4. Segmentation des clients
    print("\n👥 Segmentation des clients...")
    rfm = segment_customers(rfm)
    print(f"   ✓ {len(rfm):,} clients segmentés")
    
    # 5. Génération du rapport
    print("\n📊 Génération du rapport par segment...")
    report = generate_rfm_report(rfm)
    print(report.to_string())
    
    # 6. Sauvegarde avec des noms uniques
    os.makedirs(output_dir, exist_ok=True)
    
    analysis_file = os.path.join(output_dir, 'rfm_analysis_onlineretail.csv')
    report_file = os.path.join(output_dir, 'rfm_report_onlineretail.csv')
    
    rfm.to_csv(analysis_file, index=False)
    report.to_csv(report_file)
    
    print(f"\n💾 Résultats sauvegardés:")
    print(f"   ✓ Analyse détaillée: {analysis_file}")
    print(f"   ✓ Rapport par segment: {report_file}")
    
    # 7. Recommandations par segment
    print("\n💡 Recommandations par segment:")
    for segment in sorted(rfm['segment'].unique()):
        reco = get_segment_recommendations(segment)
        count = len(rfm[rfm['segment'] == segment])
        pct = (count / len(rfm) * 100)
        print(f"\n   🎯 {segment} ({count:,} clients, {pct:.1f}%)")
        print(f"      Description: {reco.get('description', 'N/A')}")
        print(f"      Action: {reco.get('action', 'N/A')}")
        print(f"      Priorité: {reco.get('retention_priority', 'N/A')}")
    
    # Résumé final
    print("\n" + "=" * 50)
    print("✅ ANALYSE RFM TERMINÉE")
    print("=" * 50)
    print(f"""
📊 Résumé:
   - Clients analysés: {len(rfm):,}
   - Segments identifiés: {len(rfm['segment'].unique())}
   - CA Total: {rfm['monetary'].sum():,.2f}
   - CA moyen par client: {rfm['monetary'].mean():,.2f}
   - Fréquence moyenne: {rfm['frequency'].mean():.1f} transactions
   - Récence moyenne: {rfm['recency'].mean():.0f} jours
    """)


if __name__ == "__main__":
    main()

