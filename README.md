
# Lottery Full Backend for Railway

This backend supports both the **new clean endpoints** and **legacy alias endpoints** so your existing Glide rows keep working.

## Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/louismoro28-svg/Lottery-full-backend-for-railway.git
cd Lottery-full-backend-for-railway

# Install dependencies
pip install -r requirements.txt

# Set API key
export API_KEY=mysecretkey123

# Run the application
python app.py
```

The server will start at `http://localhost:8080`

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

## Contributing

Want to contribute? Check out our [Contributing Guide](CONTRIBUTING.md) for instructions on:
- Setting up the development environment
- Creating your own version of this backend
- Making and submitting changes
- Testing guidelines
