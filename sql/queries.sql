/*1. CHIFFRE D’AFFAIRES TOTAL (CA)
   Question business :
    Combien d'argent l’entreprise a généré au total ?
 */

SELECT 
    SUM(total_amount) AS ca_total
FROM fact_sales;



/*  2. CHIFFRE D’AFFAIRES PAR MOIS
   Question business :
    Comment évoluent les ventes dans le temps ?
 */

SELECT
    d.year,
    d.month,
    d.month_name,
    SUM(f.total_amount) AS ca_mensuel
FROM fact_sales f


JOIN dim_date d
-- On joint la dimension temps
ON DATE(f.invoice_date) = d.date
-- On relie la date de la vente à la date du calendrier

GROUP BY d.year, d.month, d.month_name

ORDER BY d.year, d.month;
-- Affichage chronologique (très important pour Power BI)


/* 3. ÉVOLUTION DU CA (MOIS PAR MOIS)
   Question business :
    Est-ce que le chiffre d’affaires augmente ou baisse ?
 */

SELECT
    d.year,
    d.month,
    SUM(f.total_amount) AS ca_mensuel,
    
    -- LAG permet de récupérer la valeur du mois précédent
    LAG(SUM(f.total_amount)) OVER (
        ORDER BY d.year, d.month
    ) AS ca_mois_precedent,

    -- Calcul du pourcentage d’évolution
    ROUND(
        (
            SUM(f.total_amount)
            - LAG(SUM(f.total_amount)) OVER (ORDER BY d.year, d.month)
        )
        / LAG(SUM(f.total_amount)) OVER (ORDER BY d.year, d.month) * 100,
        2
    ) AS evolution_pourcentage

FROM fact_sales f
JOIN dim_date d ON DATE(f.invoice_date) = d.date

GROUP BY d.year, d.month
ORDER BY d.year, d.month;


/*4. TOP 10 DES PRODUITS LES PLUS RENTABLES
   Question business :
    Quels produits génèrent le plus de chiffre d’affaires ?
 */

SELECT
    p.description AS produit,
    SUM(f.total_amount) AS ca_produit
FROM fact_sales f

JOIN dim_products p
-- Jointure avec la dimension produits
ON f.stock_code = p.stock_code

GROUP BY p.description
-- Un résultat par produit

ORDER BY ca_produit DESC
-- Classement du plus rentable au moins rentable

LIMIT 10;
-- On garde seulement les 10 premiers


/* 5. PANIER MOYEN
   Question business :
    Combien un client dépense en moyenne par commande ?
*/

SELECT
    ROUND(
        SUM(total_amount) / COUNT(DISTINCT invoice_no),
        2
    ) AS panier_moyen
FROM fact_sales;


/* 6. NOUVEAUX CLIENTS VS CLIENTS RÉCURRENTS
   Question business :
    Est-ce qu’on attire de nouveaux clients ?
    Est-ce qu’ils reviennent acheter ?
 */

WITH first_purchase AS (
    -- On calcule la première date d’achat de chaque client
    SELECT
        customer_id,
        MIN(invoice_date) AS first_purchase_date
    FROM fact_sales
    GROUP BY customer_id
)

SELECT
    d.year,
    d.month,

    COUNT(DISTINCT CASE
        WHEN DATE(f.invoice_date) = DATE(fp.first_purchase_date)
        THEN f.customer_id
    END) AS nouveaux_clients,

    COUNT(DISTINCT CASE
        WHEN DATE(f.invoice_date) > DATE(fp.first_purchase_date)
        THEN f.customer_id
    END) AS clients_recurrents

FROM fact_sales f
JOIN first_purchase fp ON f.customer_id = fp.customer_id
JOIN dim_date d ON DATE(f.invoice_date) = d.date

GROUP BY d.year, d.month
ORDER BY d.year, d.month;


/* 7. ANALYSE RFM
   Question business :
    Qui sont les meilleurs clients ?
 */

SELECT
    customer_id,

    -- RECENCY : nombre de jours depuis le dernier achat
    DATE_PART(
        'day',
        CURRENT_DATE - MAX(invoice_date)
    ) AS recency,

    -- FREQUENCY : nombre de commandes
    COUNT(DISTINCT invoice_no) AS frequency,

    -- MONETARY : montant total dépensé
    SUM(total_amount) AS monetary

FROM fact_sales
GROUP BY customer_id;


/* 8. ANALYSE PAR COHORTES (RÉTENTION CLIENT)
   Question business :
    Les clients reviennent-ils après leur premier achat ?
*/

WITH cohort AS (
    -- Mois du premier achat par client
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(invoice_date)) AS cohort_month
    FROM fact_sales
    GROUP BY customer_id
),

activity AS (
    -- Activité mensuelle des clients
    SELECT
        f.customer_id,
        c.cohort_month,
        DATE_TRUNC('month', f.invoice_date) AS activity_month
    FROM fact_sales f
    JOIN cohort c ON f.customer_id = c.customer_id
)

SELECT
    cohort_month,
    activity_month,
    COUNT(DISTINCT customer_id) AS clients_actifs
FROM activity
GROUP BY cohort_month, activity_month
ORDER BY cohort_month, activity_month;


/*9. LIFETIME VALUE (LTV) PAR COHORTE
   Question business :
    Combien rapporte un client sur toute sa durée de vie ?
 */

SELECT
    DATE_TRUNC('month', MIN(invoice_date)) AS cohort_month,
    ROUND(
        SUM(total_amount) / COUNT(DISTINCT customer_id),
        2
    ) AS ltv
FROM fact_sales
GROUP BY cohort_month
ORDER BY cohort_month;
