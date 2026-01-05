"""
🔄 Projet 1 - Pipeline ETL E-commerce
Nettoyage et transformation des données
"""

import pandas as pd
import numpy as np
import duckdb
import os
from datetime import datetime


def load_data(data_dir: str) -> dict:
    """Charge les données CSV."""
    print("📂 Chargement des données...")

    data = {
        'transactions': pd.read_csv(os.path.join(data_dir, 'transactions.csv'), parse_dates=['date']),
        'customers': pd.read_csv(os.path.join(data_dir, 'customers.csv'), parse_dates=['signup_date']),
        'products': pd.read_csv(os.path.join(data_dir, 'products.csv'))
    }

    for name, df in data.items():
        print(f"   ✓ {name}: {len(df):,} lignes")

    return data


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les transactions."""
    print("\n🧹 Nettoyage des transactions...")

    initial_count = len(df)

    # Supprimer les doublons
    df = df.drop_duplicates(subset=['transaction_id'])

    # Supprimer les valeurs négatives ou nulles
    df = df[df['quantity'] > 0]
    df = df[df['unit_price'] > 0]
    df = df[df['total_amount'] > 0]

    # Supprimer les valeurs manquantes
    df = df.dropna(subset=['customer_id', 'product_id', 'date'])

    final_count = len(df)
    print(f"   ✓ {initial_count - final_count} lignes supprimées ({final_count:,} restantes)")

    return df


def enrich_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Enrichit les transactions avec des colonnes calculées."""
    print("\n✨ Enrichissement des données...")

    # Colonnes temporelles
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.month_name()
    df['week'] = df['date'].dt.isocalendar().week
    df['day_of_week'] = df['date'].dt.day_name()
    df['is_weekend'] = df['date'].dt.dayofweek >= 5

    # Colonnes pour analyse cohorte
    df['year_month'] = df['date'].dt.to_period('M').astype(str)

    print("   ✓ Colonnes temporelles ajoutées")

    return df


def calculate_customer_metrics(transactions_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """Calcule les métriques par client."""
    print("\n📊 Calcul des métriques clients...")

    customer_metrics = transactions_df.groupby('customer_id').agg({
        'transaction_id': 'count',
        'total_amount': 'sum',
        'date': ['min', 'max']
    }).reset_index()

    customer_metrics.columns = ['customer_id', 'nb_transactions', 'total_spent', 'first_purchase', 'last_purchase']

    # Calculer le panier moyen
    customer_metrics['avg_basket'] = customer_metrics['total_spent'] / customer_metrics['nb_transactions']

    # Jours depuis dernier achat
    today = transactions_df['date'].max()
    customer_metrics['days_since_last_purchase'] = (today - customer_metrics['last_purchase']).dt.days

    # Merge avec infos clients
    customer_metrics = customer_metrics.merge(customers_df[['customer_id', 'acquisition_channel', 'signup_date']], on='customer_id', how='left')

    print(f"   ✓ Métriques calculées pour {len(customer_metrics):,} clients")

    return customer_metrics


def run_duckdb_analytics(transactions_df: pd.DataFrame) -> dict:
    """Exécute des requêtes analytiques avec DuckDB."""
    print("\n🦆 Analyse DuckDB...")

    con = duckdb.connect(':memory:')
    con.register('transactions', transactions_df)

    results = {}

    # CA par mois
    results['monthly_revenue'] = con.execute("""
        SELECT
            year_month,
            SUM(total_amount) as revenue,
            COUNT(DISTINCT customer_id) as unique_customers,
            COUNT(*) as nb_transactions,
            AVG(total_amount) as avg_basket
        FROM transactions
        GROUP BY year_month
        ORDER BY year_month
    """).df()

    # Top 10 produits
    results['top_products'] = con.execute("""
        SELECT
            product_name,
            category,
            SUM(quantity) as total_quantity,
            SUM(total_amount) as total_revenue
        FROM transactions
        GROUP BY product_name, category
        ORDER BY total_revenue DESC
        LIMIT 10
    """).df()

    # CA par catégorie
    results['revenue_by_category'] = con.execute("""
        SELECT
            category,
            SUM(total_amount) as revenue,
            COUNT(*) as nb_transactions
        FROM transactions
        GROUP BY category
        ORDER BY revenue DESC
    """).df()

    # CA par jour de la semaine
    results['revenue_by_weekday'] = con.execute("""
        SELECT
            day_of_week,
            SUM(total_amount) as revenue,
            COUNT(*) as nb_transactions
        FROM transactions
        GROUP BY day_of_week
    """).df()

    print("   ✓ Analyses DuckDB terminées")

    return results


def save_processed_data(data: dict, output_dir: str):
    """Sauvegarde les données transformées."""
    print("\n💾 Sauvegarde des données...")

    os.makedirs(output_dir, exist_ok=True)

    for name, df in data.items():
        filepath = os.path.join(output_dir, f'{name}.csv')
        df.to_csv(filepath, index=False)
        print(f"   ✓ {name} → {filepath}")


def main():
    """Exécute le pipeline ETL complet."""
    print("=" * 50)
    print("🔄 PIPELINE ETL E-COMMERCE")
    print("=" * 50)

    # Chemins
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, '..', 'data')
    output_dir = os.path.join(base_dir, '..', 'output')

    # 1. Chargement
    data = load_data(data_dir)

    # 2. Nettoyage
    transactions_clean = clean_transactions(data['transactions'])

    # 3. Enrichissement
    transactions_enriched = enrich_transactions(transactions_clean)

    # 4. Métriques clients
    customer_metrics = calculate_customer_metrics(transactions_enriched, data['customers'])

    # 5. Analytics DuckDB
    analytics = run_duckdb_analytics(transactions_enriched)

    # 6. Sauvegarde
    output_data = {
        'transactions_clean': transactions_enriched,
        'customer_metrics': customer_metrics,
        'monthly_revenue': analytics['monthly_revenue'],
        'top_products': analytics['top_products'],
        'revenue_by_category': analytics['revenue_by_category']
    }
    save_processed_data(output_data, output_dir)

    # Résumé
    print("\n" + "=" * 50)
    print("✅ PIPELINE TERMINÉ")
    print("=" * 50)
    print(f"""
📊 Résumé:
   - Transactions traitées: {len(transactions_enriched):,}
   - Clients analysés: {len(customer_metrics):,}
   - CA Total: {transactions_enriched['total_amount'].sum():,.2f} €
   - Panier moyen: {transactions_enriched['total_amount'].mean():,.2f} €
    """)


if __name__ == "__main__":
    main()
