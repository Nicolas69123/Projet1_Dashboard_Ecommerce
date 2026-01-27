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


def show_main_dashboard(df: pd.DataFrame):
    """Page principale : dashboard e-commerce."""
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


def show_rfm_page(df: pd.DataFrame):
    """Page secondaire : placeholder pour l'analyse RFM."""
    st.header("Analyse RFM")

     # Charger donnees_nettoyees.csv (indépendant de df)
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "..", "data")
    output_dir = os.path.join(base_dir, "..", "output", "real-data")

    cleaned_path = os.path.join(data_dir, "donnees_nettoyees.csv")
     # Data set of donnees nettoyees
    try:
        df_clean = pd.read_csv(cleaned_path, parse_dates=["InvoiceDate"])
    except FileNotFoundError:
        st.error("Fichier donnees_nettoyees.csv introuvable. Vérifiez le dossier data/.")
        return

        # 2) Résultats RFM agrégés
    analysis_path = os.path.join(output_dir, "rfm_analysis_onlineretail.csv")
    report_path = os.path.join(output_dir, "rfm_report_onlineretail.csv")
    try:
        rfm = pd.read_csv(analysis_path)
        report = pd.read_csv(report_path)
    except FileNotFoundError:
        st.error(
            "Fichiers RFM introuvables. Exécutez d'abord :\n"
            "`python src/real-data/test-modelisation.py` pour générer les fichiers RFM."
        )
        return

    st.markdown(
        """ Cette page affiche l'analyse RFM basée sur vos transactions.

        - R (Récence): Jours depuis le dernier achat  
        - F (Fréquence): Nombre de transactions (invoices)  
        - M (Montant): Total dépensé
        """
    )

# ========= 1) Top 10 clients par fréquence + panier moyen =========
    st.subheader("Clients les plus fréquents (Top 10)")

    top_freq = (
        rfm
        .copy()
        .assign(avg_basket=lambda d: d["monetary"] / d["frequency"])
        .sort_values("frequency", ascending=False)
        .head(10)
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 10 par fréquence d'achat**")
        st.dataframe(
            top_freq[["customer_id", "frequency", "monetary", "avg_basket"]],
            use_container_width=True,
            hide_index=True,
        )

    with col2:
        st.markdown("**Fréquence vs panier moyen (Top 10)**")
        fig_freq = px.bar(
            top_freq,
            x="customer_id",
            y="frequency",
            hover_data=["avg_basket", "monetary"],
            labels={"customer_id": "Client", "frequency": "Nombre de transactions"},
        )
        fig_freq.update_layout(height=350)
        st.plotly_chart(fig_freq, use_container_width=True)

    st.markdown("---")

     # ========= 2) Top 10 clients par montant total =========
    st.subheader("Top 10 clients par montant total dépensé")

    top_monetary = (
        rfm
        .sort_values("monetary", ascending=False)
        .head(10)
    )

    col3, col4 = st.columns(2)
    with col3:
        st.dataframe(
            top_monetary[["customer_id", "monetary", "frequency", "recency"]],
            use_container_width=True,
            hide_index=True,
        )

    with col4:
        fig_m = px.bar(
            top_monetary,
            x="customer_id",
            y="monetary",
            labels={"customer_id": "Client", "monetary": "Montant total"},
        )
        fig_m.update_layout(height=350)
        st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("---")

     # ========= 3) Clients avec la récence la plus courte =========
    st.subheader("Clients les plus récents (récence la plus courte)")

    most_recent = (
        rfm
        .sort_values("recency", ascending=True)  # plus petit = plus récent
        .head(10)
    )
    most_recent = most_recent[["customer_id", "recency", "monetary", "frequency", "segment"]]

    st.dataframe(
        most_recent,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        "_Ces clients ont acheté très récemment. La colonne `monetary` montre leur investissement total._"
    )

    st.markdown("---")

    # ========= 4) Stats SHare per segment  =========
    st.subheader("Répartition des clients par segment (en nombre de clients)")

    fig_seg_pie = px.pie(
        report,
        values="nb_clients",
        names="segment",
        hole=0.4,  # donut style; remove if you prefer full pie
        labels={"segment": "Segment", "nb_clients": "Nombre de clients"},
    )

    fig_seg_pie.update_traces(textinfo="percent+label")
    fig_seg_pie.update_layout(
        height=400,
        showlegend=True,
        legend_title_text="Segment",
    )

    st.plotly_chart(fig_seg_pie, use_container_width=True)
    # ========= 4) Stats par segment + recommandations interactives =========
    st.subheader("Performance par segment RFM")

    # Graphique barres : CA total par segment
    col5, col6 = st.columns(2)
    with col5:
        fig_seg_rev = px.bar(
            report,
            x="segment",
            y="monetary_total",
            hover_data=["nb_clients", "pct_clients", "pct_revenue"],
            labels={
                "segment": "Segment",
                "monetary_total": "CA total",
            },
        )
        fig_seg_rev.update_layout(height=350)
        st.plotly_chart(fig_seg_rev, use_container_width=True)

    with col6:
        fig_seg_share = px.bar(
            report,
            x="segment",
            y="pct_revenue",
            hover_data=["pct_clients"],
            labels={
                "segment": "Segment",
                "pct_revenue": "% du CA total",
            },
        )
        fig_seg_share.update_layout(height=350)
        st.plotly_chart(fig_seg_share, use_container_width=True)

    st.markdown("---")

      # Recommandations interactives par segment
    st.subheader("Détails et recommandations par segment")

    # On peut réutiliser la même logique que dans src/real-data/test-modelisation.py
    def get_segment_recommendations(segment: str) -> dict:
        recommendations = {
            "Champions": {
                "description": "Vos meilleurs clients",
                "action": "Récompenser avec un programme VIP, early access aux nouveautés",
                "retention_priority": "Haute",
            },
            "Fidèles": {
                "description": "Clients réguliers et engagés",
                "action": "Upselling, programme de fidélité, parrainage",
                "retention_priority": "Haute",
            },
            "Nouveaux prometteurs": {
                "description": "Nouveaux clients à fort potentiel",
                "action": "Onboarding personnalisé, offres de bienvenue",
                "retention_priority": "Moyenne",
            },
            "À risque": {
                "description": "Bons clients qui s'éloignent",
                "action": "Campagne de réactivation urgente, offres spéciales",
                "retention_priority": "Critique",
            },
            "Endormis": {
                "description": "Clients inactifs depuis longtemps",
                "action": "Campagne win-back, enquête satisfaction",
                "retention_priority": "Basse",
            },
            "Occasionnels": {
                "description": "Clients ponctuels",
                "action": "Incentives pour augmenter la fréquence",
                "retention_priority": "Moyenne",
            },
            "Moyens": {
                "description": "Clients standards",
                "action": "Personnalisation pour améliorer l'engagement",
                "retention_priority": "Moyenne",
            },
        }
        return recommendations.get(segment, {})

    segments = sorted(rfm["segment"].unique())
    selected_segment = st.selectbox("Choisir un segment", segments)

    seg_df = rfm[rfm["segment"] == selected_segment]
    reco = get_segment_recommendations(selected_segment)

    col7, col8 = st.columns(2)
    with col7:
        st.markdown(f"### Segment : **{selected_segment}**")
        st.metric("Nombre de clients", f"{len(seg_df):,}")
        st.metric("CA total", f"{seg_df['monetary'].sum():,.0f}")
        st.metric("CA moyen / client", f"{seg_df['monetary'].mean():,.0f}")
    with col8:
        st.markdown("**Description**")
        st.write(reco.get("description", "N/A"))
        st.markdown("**Action recommandée**")
        st.write(reco.get("action", "N/A"))
        st.markdown("**Priorité de rétention**")
        st.write(reco.get("retention_priority", "N/A"))

    st.markdown("##### Clients du segment sélectionné (échantillon)")
    st.dataframe(
        seg_df[["customer_id", "recency", "frequency", "monetary"]].head(20),
        use_container_width=True,
        hide_index=True,
    )

   # Lignes de test des données nettoyées
    # st.subheader("Aperçu des données nettoyées")
    # st.dataframe(df_clean.head(), use_container_width=True, hide_index=True)

    # st.write(f"Nombre de lignes : {len(df_clean):,}")
    # st.write("Colonnes disponibles :", ", ".join(df_clean.columns))




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

    # Navigation multi-page
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Page",
        ["Dashboard principal", "Analyse RFM"]
    )

    if page == "Dashboard principal":
        show_main_dashboard(df)
    elif page == "Analyse RFM":
        show_rfm_page(df)


if __name__ == "__main__":
    main()
