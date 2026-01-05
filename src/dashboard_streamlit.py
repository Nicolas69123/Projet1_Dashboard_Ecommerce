"""
Projet 1 - Dashboard Streamlit E-commerce
Interface interactive pour visualiser les KPIs
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Dashboard E-commerce",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalise - contraste optimal
st.markdown("""
<style>
    /* Theme global */
    .main {
        background-color: #ffffff;
    }

    /* Metrics cards */
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }

    .stMetric label {
        color: #495057 !important;
        font-weight: 600;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: #212529 !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: #212529 !important;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    /* Tables */
    .dataframe {
        color: #212529;
    }

    /* Links */
    a {
        color: #0066cc !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Charge les donnees avec cache Streamlit."""
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, '..', 'data')

    transactions = pd.read_csv(
        os.path.join(data_dir, 'transactions.csv'),
        parse_dates=['date']
    )

    # Enrichissement
    transactions['year_month'] = transactions['date'].dt.to_period('M').astype(str)
    transactions['weekday'] = transactions['date'].dt.day_name()

    return transactions


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calcule les KPIs principaux."""
    return {
        'revenue': df['total_amount'].sum(),
        'orders': len(df),
        'customers': df['customer_id'].nunique(),
        'avg_basket': df['total_amount'].mean(),
        'avg_items': df['quantity'].mean()
    }


def main():
    # Header
    st.title("Dashboard E-commerce")
    st.markdown("---")

    # Chargement des donnees
    try:
        df = load_data()
    except FileNotFoundError:
        st.error("Donnees non trouvees. Executez d'abord: python src/generate_data.py")
        st.stop()

    # Sidebar - Filtres
    st.sidebar.header("Filtres")

    # Filtre dates
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()

    date_range = st.sidebar.date_input(
        "Periode",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filtre categories
    categories = ['Toutes'] + sorted(df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("Categorie", categories)

    # Application des filtres
    mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
    if selected_category != 'Toutes':
        mask &= df['category'] == selected_category

    filtered_df = df[mask]

    # KPIs
    kpis = calculate_kpis(filtered_df)

    # Ligne 1: Metriques principales
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Chiffre d'Affaires", f"{kpis['revenue']:,.0f} EUR")
    with col2:
        st.metric("Commandes", f"{kpis['orders']:,}")
    with col3:
        st.metric("Clients", f"{kpis['customers']:,}")
    with col4:
        st.metric("Panier Moyen", f"{kpis['avg_basket']:.2f} EUR")
    with col5:
        st.metric("Articles/Commande", f"{kpis['avg_items']:.1f}")

    st.markdown("---")

    # Ligne 2: Graphiques principaux
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Evolution du CA")
        monthly_revenue = filtered_df.groupby('year_month')['total_amount'].sum().reset_index()
        fig = px.line(
            monthly_revenue,
            x='year_month',
            y='total_amount',
            markers=True,
            labels={'year_month': 'Mois', 'total_amount': 'CA (EUR)'}
        )
        fig.update_traces(line_color='#0066cc', line_width=2)
        fig.update_layout(
            height=350,
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font_color='#212529',
            xaxis=dict(gridcolor='#e9ecef'),
            yaxis=dict(gridcolor='#e9ecef')
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("CA par Categorie")
        category_revenue = filtered_df.groupby('category')['total_amount'].sum().reset_index()
        # Palette de couleurs avec bon contraste
        colors = ['#0066cc', '#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6c757d']
        fig = px.pie(
            category_revenue,
            values='total_amount',
            names='category',
            hole=0.4,
            color_discrete_sequence=colors
        )
        fig.update_layout(
            height=350,
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font_color='#212529'
        )
        fig.update_traces(textfont_color='#ffffff', textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)

    # Ligne 3: Analyses detaillees
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Produits")
        top_products = filtered_df.groupby('product_name')['total_amount'].sum().nlargest(10).reset_index()
        fig = px.bar(
            top_products,
            x='total_amount',
            y='product_name',
            orientation='h',
            labels={'total_amount': 'CA (EUR)', 'product_name': 'Produit'}
        )
        fig.update_traces(marker_color='#0066cc')
        fig.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font_color='#212529',
            xaxis=dict(gridcolor='#e9ecef'),
            yaxis=dict(gridcolor='#e9ecef')
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("CA par Jour de la Semaine")
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_labels = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        weekday_revenue = filtered_df.groupby('weekday')['total_amount'].sum().reindex(weekday_order).reset_index()
        weekday_revenue['weekday_fr'] = weekday_labels
        fig = px.bar(
            weekday_revenue,
            x='weekday_fr',
            y='total_amount',
            labels={'weekday_fr': 'Jour', 'total_amount': 'CA (EUR)'}
        )
        fig.update_traces(marker_color='#28a745')
        fig.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font_color='#212529',
            xaxis=dict(gridcolor='#e9ecef'),
            yaxis=dict(gridcolor='#e9ecef')
        )
        st.plotly_chart(fig, use_container_width=True)

    # Ligne 4: Tableau detaille
    st.subheader("Transactions Recentes")
    recent = filtered_df.nlargest(20, 'date')[['date', 'transaction_id', 'customer_id', 'product_name', 'quantity', 'total_amount']]
    recent['date'] = recent['date'].dt.strftime('%Y-%m-%d %H:%M')
    recent.columns = ['Date', 'Transaction', 'Client', 'Produit', 'Quantite', 'Montant (EUR)']
    st.dataframe(recent, use_container_width=True, hide_index=True)

    # Footer
    st.markdown("---")
    st.caption(
        f"Dashboard genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')} | "
        f"Donnees: {len(filtered_df):,} transactions"
    )


if __name__ == "__main__":
    main()
