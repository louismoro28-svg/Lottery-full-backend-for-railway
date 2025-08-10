
# Lottery Full Backend for Railway

This backend supports both the **new clean endpoints** and **legacy alias endpoints** so your existing Glide rows keep working.

## Endpoints
- `/health`
- `/predictions?key=...`
- `/predictions.csv?key=...`
- `/glide_weekly_report?key=...`
- `/predictions/data/glide_weekly_report.json?key=...` (alias)
- `/glide_view_predictions?date=YYYY-MM-DD&key=...`
- `/glide_backtest?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&key=...`
- `/weekly_report_for_week?start_date=YYYY-MM-DD&key=...`
- `/glide_weekly_report_for_week?start_date=YYYY-MM-DD&key=...` (alias)

## Deploy to Railway
1. Create new project
2. Upload this zip OR push to GitHub and connect
3. Set **Start Command** to:
```
python app.py
```
4. Add env var:
```
API_KEY=mysecretkey123
```
