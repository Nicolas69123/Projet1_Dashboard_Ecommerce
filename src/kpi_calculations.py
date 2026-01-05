"""
📈 Projet 1 - Calculs des KPIs E-commerce
Tous les indicateurs clés de performance
"""

import pandas as pd
import numpy as np
import duckdb
import os
from datetime import datetime, timedelta


class EcommerceKPIs:
    """Classe pour calculer tous les KPIs e-commerce."""

    def __init__(self, transactions_df: pd.DataFrame, customers_df: pd.DataFrame = None):
        self.transactions = transactions_df
        self.customers = customers_df
        self.con = duckdb.connect(':memory:')
        self.con.register('transactions', self.transactions)
        if customers_df is not None:
            self.con.register('customers', self.customers)

    # =====================
    # KPIs DE VENTES
    # =====================

    def total_revenue(self) -> float:
        """Chiffre d'affaires total."""
        return self.transactions['total_amount'].sum()

    def revenue_by_period(self, period: str = 'M') -> pd.DataFrame:
        """CA par période (D=jour, W=semaine, M=mois, Y=année)."""
        df = self.transactions.copy()
        df['period'] = df['date'].dt.to_period(period).astype(str)
        return df.groupby('period')['total_amount'].sum().reset_index()

    def revenue_growth(self, period: str = 'M') -> pd.DataFrame:
        """Croissance du CA période vs période précédente."""
        revenue = self.revenue_by_period(period)
        revenue['previous'] = revenue['total_amount'].shift(1)
        revenue['growth_pct'] = ((revenue['total_amount'] - revenue['previous']) / revenue['previous'] * 100).round(2)
        return revenue

    def top_products(self, n: int = 10) -> pd.DataFrame:
        """Top N produits par CA."""
        return self.con.execute(f"""
            SELECT
                product_name,
                category,
                SUM(quantity) as total_qty,
                SUM(total_amount) as revenue,
                COUNT(*) as nb_orders
            FROM transactions
            GROUP BY product_name, category
            ORDER BY revenue DESC
            LIMIT {n}
        """).df()

    def revenue_by_category(self) -> pd.DataFrame:
        """CA par catégorie."""
        return self.con.execute("""
            SELECT
                category,
                SUM(total_amount) as revenue,
                COUNT(*) as nb_orders,
                AVG(total_amount) as avg_order
            FROM transactions
            GROUP BY category
            ORDER BY revenue DESC
        """).df()

    # =====================
    # KPIs CLIENTS
    # =====================

    def total_customers(self) -> int:
        """Nombre total de clients uniques."""
        return self.transactions['customer_id'].nunique()

    def new_vs_returning(self) -> pd.DataFrame:
        """Nouveaux clients vs clients récurrents par mois."""
        # Premier achat par client
        first_purchase = self.transactions.groupby('customer_id')['date'].min().reset_index()
        first_purchase.columns = ['customer_id', 'first_purchase_date']
        first_purchase['first_month'] = first_purchase['first_purchase_date'].dt.to_period('M').astype(str)

        # Transactions avec info premier achat
        df = self.transactions.merge(first_purchase, on='customer_id')
        df['order_month'] = df['date'].dt.to_period('M').astype(str)
        df['is_new'] = df['order_month'] == df['first_month']

        # Agrégation
        result = df.groupby(['order_month', 'is_new']).agg({
            'customer_id': 'nunique',
            'total_amount': 'sum'
        }).reset_index()
        result['customer_type'] = result['is_new'].map({True: 'Nouveau', False: 'Récurrent'})

        return result

    def average_basket(self) -> float:
        """Panier moyen."""
        return self.transactions['total_amount'].mean()

    def average_basket_by_segment(self) -> pd.DataFrame:
        """Panier moyen par segment (si RFM disponible)."""
        return self.con.execute("""
            SELECT
                category,
                AVG(total_amount) as avg_basket,
                COUNT(*) as nb_orders
            FROM transactions
            GROUP BY category
            ORDER BY avg_basket DESC
        """).df()

    def customer_lifetime_value(self) -> pd.DataFrame:
        """LTV par client."""
        return self.con.execute("""
            SELECT
                customer_id,
                COUNT(*) as nb_orders,
                SUM(total_amount) as lifetime_value,
                MIN(date) as first_order,
                MAX(date) as last_order,
                DATEDIFF('day', MIN(date), MAX(date)) as customer_lifespan_days
            FROM transactions
            GROUP BY customer_id
            ORDER BY lifetime_value DESC
        """).df()

    # =====================
    # KPIs TEMPORELS
    # =====================

    def daily_metrics(self) -> pd.DataFrame:
        """Métriques quotidiennes."""
        return self.con.execute("""
            SELECT
                CAST(date AS DATE) as date,
                SUM(total_amount) as revenue,
                COUNT(*) as nb_orders,
                COUNT(DISTINCT customer_id) as unique_customers,
                AVG(total_amount) as avg_basket
            FROM transactions
            GROUP BY CAST(date AS DATE)
            ORDER BY date
        """).df()

    def weekday_analysis(self) -> pd.DataFrame:
        """Analyse par jour de la semaine."""
        df = self.transactions.copy()
        df['weekday'] = df['date'].dt.day_name()
        df['weekday_num'] = df['date'].dt.dayofweek

        result = df.groupby(['weekday', 'weekday_num']).agg({
            'total_amount': ['sum', 'mean', 'count']
        }).reset_index()
        result.columns = ['weekday', 'weekday_num', 'revenue', 'avg_basket', 'nb_orders']
        return result.sort_values('weekday_num')

    def hourly_analysis(self) -> pd.DataFrame:
        """Analyse par heure (si disponible)."""
        df = self.transactions.copy()
        df['hour'] = df['date'].dt.hour

        return df.groupby('hour').agg({
            'total_amount': ['sum', 'mean', 'count']
        }).reset_index()

    # =====================
    # KPIs COHORTES
    # =====================

    def cohort_retention(self) -> pd.DataFrame:
        """Analyse de rétention par cohorte."""
        df = self.transactions.copy()

        # Mois de première commande (cohorte)
        first_order = df.groupby('customer_id')['date'].min().reset_index()
        first_order.columns = ['customer_id', 'first_order_date']
        first_order['cohort'] = first_order['first_order_date'].dt.to_period('M').astype(str)

        # Merge
        df = df.merge(first_order[['customer_id', 'cohort']], on='customer_id')
        df['order_month'] = df['date'].dt.to_period('M').astype(str)

        # Calcul du mois relatif
        df['cohort_period'] = pd.to_datetime(df['cohort'])
        df['order_period'] = pd.to_datetime(df['order_month'])
        df['months_since_first'] = ((df['order_period'].dt.year - df['cohort_period'].dt.year) * 12 +
                                     (df['order_period'].dt.month - df['cohort_period'].dt.month))

        # Matrice de rétention
        cohort_data = df.groupby(['cohort', 'months_since_first'])['customer_id'].nunique().reset_index()
        cohort_data.columns = ['cohort', 'month', 'customers']

        # Pivot
        cohort_pivot = cohort_data.pivot(index='cohort', columns='month', values='customers')

        # Pourcentage de rétention
        cohort_sizes = cohort_pivot[0]
        retention = cohort_pivot.divide(cohort_sizes, axis=0) * 100

        return retention.round(1)

    # =====================
    # RAPPORT COMPLET
    # =====================

    def generate_summary(self) -> dict:
        """Génère un résumé de tous les KPIs."""
        return {
            'total_revenue': self.total_revenue(),
            'total_customers': self.total_customers(),
            'average_basket': self.average_basket(),
            'total_orders': len(self.transactions),
            'orders_per_customer': len(self.transactions) / self.total_customers(),
            'revenue_per_customer': self.total_revenue() / self.total_customers()
        }


def main():
    """Calcule et affiche tous les KPIs."""
    print("=" * 50)
    print("📈 CALCUL DES KPIs E-COMMERCE")
    print("=" * 50)

    # Chemins
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, '..', 'data')
    output_dir = os.path.join(base_dir, '..', 'output')

    # Chargement
    print("\n📂 Chargement des données...")
    transactions = pd.read_csv(os.path.join(data_dir, 'transactions.csv'), parse_dates=['date'])

    # Calcul KPIs
    kpis = EcommerceKPIs(transactions)

    # Résumé
    summary = kpis.generate_summary()
    print("\n📊 RÉSUMÉ DES KPIs:")
    print(f"   💰 CA Total: {summary['total_revenue']:,.2f} €")
    print(f"   👥 Clients uniques: {summary['total_customers']:,}")
    print(f"   🛒 Panier moyen: {summary['average_basket']:.2f} €")
    print(f"   📦 Commandes totales: {summary['total_orders']:,}")
    print(f"   📈 Commandes/client: {summary['orders_per_customer']:.2f}")
    print(f"   💎 CA/client: {summary['revenue_per_customer']:.2f} €")

    # Top produits
    print("\n🏆 TOP 5 PRODUITS:")
    top = kpis.top_products(5)
    print(top.to_string(index=False))

    # CA par catégorie
    print("\n📂 CA PAR CATÉGORIE:")
    cat = kpis.revenue_by_category()
    print(cat.to_string(index=False))

    # Sauvegarde
    os.makedirs(output_dir, exist_ok=True)
    pd.DataFrame([summary]).to_csv(os.path.join(output_dir, 'kpi_summary.csv'), index=False)
    kpis.top_products(10).to_csv(os.path.join(output_dir, 'top_products.csv'), index=False)
    kpis.revenue_by_category().to_csv(os.path.join(output_dir, 'revenue_by_category.csv'), index=False)
    kpis.daily_metrics().to_csv(os.path.join(output_dir, 'daily_metrics.csv'), index=False)

    print(f"\n✅ KPIs sauvegardés dans {output_dir}")


if __name__ == "__main__":
    main()
