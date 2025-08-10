
from flask import Flask, jsonify, request, send_file
import os

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "mysecretkey123")

# Health endpoint
@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Glide Lottery API (Full Backend)"})

# Predictions
@app.route("/predictions")
def predictions():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"predictions": [{"game": "Pick 3", "date": "2024-08-01", "hot_number": 7}]})
    
@app.route("/predictions.csv")
def predictions_csv():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    csv_content = "game,date,hot_number\nPick 3,2024-08-01,7\n"
    return csv_content, 200, {"Content-Type": "text/csv"}

# Weekly report (clean)
@app.route("/glide_weekly_report")
def glide_weekly_report():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"report_data": [{"game": "Pick 3", "predictions_count": 12, "hit_count": 3}]})
    
# Weekly report alias for old path
@app.route("/predictions/data/glide_weekly_report.json")
def glide_weekly_report_alias():
    return glide_weekly_report()

# View predictions
@app.route("/glide_view_predictions")
def glide_view_predictions():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"predictions": [{"date": "2024-08-01", "first_combo": "123"}]})

# Backtest
@app.route("/glide_backtest")
def glide_backtest():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"backtest": {"hit_rate": 75}})

# Historical weekly
@app.route("/weekly_report_for_week")
def weekly_report_for_week():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"historical": [{"week": "2024-07-01", "hit_rate": 50}]})
    
# Alias for historical weekly
@app.route("/glide_weekly_report_for_week")
def glide_weekly_report_for_week_alias():
    return weekly_report_for_week()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
