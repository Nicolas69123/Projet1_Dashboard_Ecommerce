# RFM analyses

### Script src/test-modelisation.py

#### Features implemented
- Data loading (load_onlineretail_data) 
Loads donnees_nettoyees.csv

- Parses InvoiceDate as datetime, 
 Filters valid customers (non-null CustomerID), 
 Validates required columns and numeric amounts

- RFM calculation (calculate_rfm_scores_onlineretail)
##### Recency: days since last purchase
##### Frequency: unique invoices per customer
##### Monetary: total amount spent per customer

- Scoring and segmentation
assign_rfm_scores(): assigns 1-5 scores for R, F, M
segment_customers(): segments into 7 categories
get_segment_recommendations(): marketing recommendations

- Reporting
generate_rfm_report(): summary statistics by segment
- Main execution
- Full pipeline execution
Console output with progress indicators
Unique output filenames:
output/rfm_analysis_onlineretail.csv
output/rfm_report_onlineretail.csv

```bash

py src/test-modelisation.py

```