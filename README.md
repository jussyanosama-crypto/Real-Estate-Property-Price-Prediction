# Real Estate Property Price Prediction

This project estimates recorded NYC property sale prices from property characteristics, location, building classification, and sale timing.

## Business problem

The model supports first-pass price review, comparable-property screening, inventory checks, and investigation of unusual transactions. It is decision support, not a replacement for professional appraisal, inspection, or human review.

## Dataset

The project uses the official [NYC Citywide Rolling Calendar Sales dataset](https://data.cityofnewyork.us/dataset/NYC-Citywide-Rolling-Calendar-Sales/usep-8jbt), accessed through the Socrata API. The included snapshot has 82,345 records and 21 columns covering 2025-09-01 through 2026-08-31 when this project was run.

I also considered King County housing and California Housing. NYC was selected for first-party provenance, geographic detail, building attributes, and direct relevance to the business question. No datasets were merged.

## Cleaning and features

The notebook:

- removes exact duplicates and invalid dates;
- excludes non-positive sale prices, missing/zero gross square footage, and impossible construction years;
- converts numeric fields that contain commas;
- imputes remaining missing feature values inside the model pipelines;
- engineers sale year/month, borough name, and property age;
- excludes address, block, lot, and apartment number because they are identifiers or too granular for a transferable model;
- keeps `price_per_sqft` and `log_price` for analysis only; neither is a model feature.

After the documented filters, the modeling table contains 22,272 rows. The notebook explicitly checks that target-derived columns do not appear in the feature list.

## Modeling method

1. Sort cleaned records by sale date.
2. Use the earliest 80% for training and the latest 20% as the untouched final test period.
3. Compare a median-price baseline, Ridge regression, and Gradient Boosting.
4. Fit preprocessing inside scikit-learn pipelines: training-only imputation, encoding, and scaling.
5. Use `TimeSeriesSplit` inside the training period for model selection and hyperparameter tuning.
6. Evaluate the tuned model once on the later test period.

The target is modeled as `log1p(sale_price)` and transformed back to dollars for evaluation. This reduces the influence of the strongly right-skewed price distribution while keeping the business metrics in currency units.

## Results from the verified run

Final model: tuned `GradientBoostingRegressor` with a log-transformed target.

| Metric | Final test result |
|---|---:|
| MAE | **$1,200,493** |
| RMSE | **$6,696,346** |
| R² | **0.407** |
| Time-series CV MAE | **$1,667,380** |

MAE is the average absolute prediction error. RMSE is more sensitive to very large misses. R² compares the model with a mean-price baseline. The final test period contains 4,455 later-dated sales and was not used for model selection or tuning.

The largest errors are concentrated in the highest price band. Very high-value luxury, portfolio, and commercial transactions are not fully described by the available fields, so the model should be used cautiously for those cases.

## Interpretation and limitations

Permutation importance measures how much test MAE changes when an original feature is shuffled. In the completed run, `total_units` produced the largest positive change; most other feature changes were small or negative on the sampled test set. This is predictive importance, not causality.

The data is NYC-specific, time-limited, and based on recorded sale prices rather than asking prices or verified transaction economics. Public records contain missing fields, heterogeneous property types, nominal/non-market transfers, and possible recording errors. Renovation quality, floor, view, condition, financing, and detailed unit-level attributes are missing or incomplete. Performance should be revalidated before applying the model to a new market or future market regime.

## Project structure

```text
.
├── nyc_citywide_rolling_sales.csv
├── real_estate_property_price_prediction.ipynb
├── README.md
├── requirements.txt
├── download_data.py
└── .gitignore
```

## Reproduce

Run from the repository root:

```powershell
python -m pip install -r requirements.txt
python download_data.py
```

Then open `real_estate_property_price_prediction.ipynb` and run all cells. The notebook is self-contained: it loads `nyc_citywide_rolling_sales.csv` directly and contains its own fallback download logic if the file is missing. The rolling source may change after a future download, so the notebook prints the actual snapshot date range and row count.

## Files

- `real_estate_property_price_prediction.ipynb` — complete analysis and modeling workflow.
- `nyc_citywide_rolling_sales.csv` — source snapshot used for the verified run.
- `download_data.py` — simple relative-path download script.
- `requirements.txt` — packages used by the notebook and download script.
