# India Road Accident Risk & Trend Dashboard

## What this version does

This is a submission-ready, no-ML version built from the supplied datasets.

### Features
1. Historical accident-level analysis for 2018–2023.
2. Official 2023 → 2024 state-level accident trend.
3. Official 2023 → 2024 fatality trend.
4. State-level 2024 risk map.
5. Time-of-day analysis.
6. Road-type and weather analysis.
7. Accident severity and alcohol-involvement analysis.

## Important technical limitation

The detailed 2018–2023 CSV contains no latitude/longitude columns. Therefore this dashboard does **not** claim GPS-level DBSCAN hotspots. The map is a **state-level risk visualization** using approximate state centroids.

The Risk Index is a simple analytical score, not machine learning.

## Run

Install Python 3.10+.

```bash
pip install -r requirements.txt
streamlit run app.py
```

The browser should open the dashboard automatically.

## Project explanation for viva

> "Our system combines accident-level historical analysis with the latest official 2024 state-level statistics. It analyzes severity, time, road type, weather and alcohol involvement, and provides a state-level risk visualization. The recent 2024 data is used as an external trend layer."

If asked why ML is not included:

> "We prioritized a transparent and explainable analytical system for the current submission. A future version can add a properly evaluated ML model after feature validation and class-imbalance testing."

Do NOT claim that the current model predicts where future accidents will happen.
