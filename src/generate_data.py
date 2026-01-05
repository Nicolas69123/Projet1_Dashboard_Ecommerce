"""
📊 Projet 1 - Génération de données E-commerce
Génère des transactions réalistes pour le dashboard
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# Configuration
fake = Faker('fr_FR')
np.random.seed(42)

# Paramètres
NUM_TRANSACTIONS = 50000
NUM_CUSTOMERS = 5000
NUM_PRODUCTS = 200
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)


def generate_products(n_products: int) -> pd.DataFrame:
    """Génère un catalogue de produits."""
    categories = ['Électronique', 'Mode', 'Maison', 'Sport', 'Beauté', 'Alimentation']

    products = []
    for i in range(n_products):
        category = random.choice(categories)
        products.append({
            'product_id': f'PROD_{i+1:04d}',
            'product_name': fake.word().capitalize() + ' ' + fake.word().capitalize(),
            'category': category,
            'unit_price': round(random.uniform(5, 500), 2),
            'cost_price': round(random.uniform(2, 250), 2)
        })

    df = pd.DataFrame(products)
    df['cost_price'] = df['unit_price'] * random.uniform(0.4, 0.7)
    return df


def generate_customers(n_customers: int) -> pd.DataFrame:
    """Génère une base de clients."""
    customers = []

    acquisition_channels = ['Google Ads', 'Facebook', 'Organic', 'Email', 'Referral']

    for i in range(n_customers):
        signup_date = fake.date_between(start_date=START_DATE - timedelta(days=365), end_date=END_DATE)
        customers.append({
            'customer_id': f'CUST_{i+1:05d}',
            'customer_name': fake.name(),
            'email': fake.email(),
            'city': fake.city(),
            'country': 'France',
            'signup_date': signup_date,
            'acquisition_channel': random.choice(acquisition_channels)
        })

    return pd.DataFrame(customers)


def generate_transactions(n_transactions: int, products_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """Génère des transactions de vente."""
    transactions = []

    # Distribution temporelle avec saisonnalité
    date_range = pd.date_range(start=START_DATE, end=END_DATE, freq='D')

    for i in range(n_transactions):
        # Date avec saisonnalité (plus de ventes en fin d'année)
        date = random.choice(date_range)
        month = date.month

        # Plus de probabilité en novembre-décembre (Black Friday, Noël)
        if month in [11, 12]:
            if random.random() < 0.3:  # 30% de chance de garder
                date = random.choice(date_range)

        # Sélection client et produit
        customer = customers_df.sample(1).iloc[0]
        product = products_df.sample(1).iloc[0]

        # Quantité (distribution exponentielle)
        quantity = max(1, int(np.random.exponential(2)))

        transactions.append({
            'transaction_id': f'TXN_{i+1:06d}',
            'date': date,
            'customer_id': customer['customer_id'],
            'product_id': product['product_id'],
            'product_name': product['product_name'],
            'category': product['category'],
            'quantity': quantity,
            'unit_price': product['unit_price'],
            'total_amount': round(quantity * product['unit_price'], 2)
        })

    return pd.DataFrame(transactions)


def main():
    """Génère toutes les données et les sauvegarde."""
    print("🚀 Génération des données E-commerce...")

    # Créer le dossier data s'il n'existe pas
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Génération
    print("📦 Génération des produits...")
    products_df = generate_products(NUM_PRODUCTS)

    print("👥 Génération des clients...")
    customers_df = generate_customers(NUM_CUSTOMERS)

    print("💳 Génération des transactions...")
    transactions_df = generate_transactions(NUM_TRANSACTIONS, products_df, customers_df)

    # Sauvegarde
    products_df.to_csv(os.path.join(data_dir, 'products.csv'), index=False)
    customers_df.to_csv(os.path.join(data_dir, 'customers.csv'), index=False)
    transactions_df.to_csv(os.path.join(data_dir, 'transactions.csv'), index=False)

    print(f"""
✅ Données générées avec succès !
   - {len(products_df)} produits → data/products.csv
   - {len(customers_df)} clients → data/customers.csv
   - {len(transactions_df)} transactions → data/transactions.csv
    """)

    # Aperçu
    print("\n📊 Aperçu des transactions:")
    print(transactions_df.head(10))

    print(f"\n💰 CA Total: {transactions_df['total_amount'].sum():,.2f} €")
    print(f"🛒 Panier moyen: {transactions_df['total_amount'].mean():,.2f} €")


if __name__ == "__main__":
    main()
