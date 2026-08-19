# Pai's Bakery — Territory Realignment Dashboard (Streamlit)

Interactive version of the Power BI concept, built in Python/Streamlit.
Data source: Ivey Publishing Case W25442.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Opens at http://localhost:8501

## Deploy for free (to share a link / embed in your PPT presentation)
1. Push this folder to a GitHub repo.
2. Go to https://share.streamlit.io, sign in with GitHub.
3. Point it at the repo, main file `app.py`. It deploys in ~2 minutes with a public URL.

## Files
- `app.py` — the dashboard
- `requirements.txt` — dependencies
- `data/*.csv` — exported from Pais_Bakery_Territory_Dashboard_Data.xlsx (same tables as the Power BI workbook: Territories_Master, Sales_Reps, map_data (Current + Proposed scenarios stacked), outlet_flow, sales_flow, rep_impact)

## What it shows
- Sidebar toggle: Current (As-Is) vs Proposed (Realignment)
- Map: territory centroids, sized by outlets served, colored by rep, overlap highlighted
- KPI cards: assignments, overlap count, territories covered, fleet fuel cost/day (with delta)
- Fuel cost bar chart per rep, current vs proposed
- Sankey + list of retail outlet reallocation flow between reps (Exhibit 12)
