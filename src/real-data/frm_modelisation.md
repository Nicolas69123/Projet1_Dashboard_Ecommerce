# RFM Analysis - Real Data (Online Retail)

This folder contains the RFM (Recency, Frequency, Monetary) analysis scripts and outputs for the **real Online Retail dataset**.

## Overview

The RFM analysis segments customers based on their purchasing behavior using three key metrics:
- **R (Recency)**: Days since the last purchase
- **F (Frequency)**: Number of transactions (invoices)
- **M (Monetary)**: Total amount spent

## Script: `test-modelisation.py`

### Features Implemented

#### 1. Data Loading (`load_onlineretail_data`)
- Loads `donnees_nettoyees.csv` from the `data/` folder
- Parses `InvoiceDate` as datetime
- Filters valid customers (non-null CustomerID)
- Validates required columns and numeric amounts

#### 2. RFM Calculation (`calculate_rfm_scores_onlineretail`)
- **Recency**: Days since last purchase
- **Frequency**: Unique invoices per customer
- **Monetary**: Total amount spent per customer

#### 3. Scoring and Segmentation
- `assign_rfm_scores()`: Assigns 1-5 scores for R, F, M using quantile-based binning
- `segment_customers()`: Segments customers into 7 categories:
  - **Champions**: Best customers (high R, F, M)
  - **Fidèles**: Loyal regular customers
  - **Nouveaux prometteurs**: New high-potential customers
  - **À risque**: Good customers who are drifting away
  - **Endormis**: Inactive customers
  - **Occasionnels**: Occasional buyers
  - **Moyens**: Average customers
- `get_segment_recommendations()`: Provides marketing recommendations for each segment

#### 4. Reporting
- `generate_rfm_report()`: Summary statistics by segment including:
  - Number of clients per segment
  - Average recency, frequency, monetary values
  - Percentage of total clients and revenue

#### 5. Main Execution
- Full pipeline execution with progress indicators
- Console output with detailed statistics
- Marketing recommendations by segment

### Output Files

The script generates two CSV files in `output/real-data/`:
- `output/real-data/rfm_analysis_onlineretail.csv` - Detailed RFM scores for each customer
- `output/real-data/rfm_report_onlineretail.csv` - Aggregated statistics by segment

### Usage

Run the RFM analysis script from the project root:

```bash
python src/real-data/test-modelisation.py
```

The script will:
1. Load the cleaned Online Retail data from `data/donnees_nettoyees.csv`
2. Calculate RFM metrics for all customers
3. Assign scores and segment customers
4. Generate reports and save them to `output/real-data/`
5. Display recommendations for each segment

### Integration with Dashboard

The Streamlit dashboard (`src/dashboard_streamlit.py`) loads the generated RFM files to display:
- Top customers by frequency and monetary value
- Most recent customers
- Customer distribution by segment
- Performance metrics by segment
- Interactive segment exploration with recommendations

### Real-Data Convention

Files in `src/real-data/` and `output/real-data/` work with the **latest cleaned Online Retail dataset** (`donnees_nettoyees.csv`). This convention helps separate real data analyses from synthetic/test data analyses.

