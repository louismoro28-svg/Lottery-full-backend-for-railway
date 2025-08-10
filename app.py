import os, json, glob
from datetime import datetime
from flask import Flask, jsonify, request, send_file, abort
from flask_cors import CORS

# ---- App + CORS ----
app = Flask(__name__)
CORS(app)

# ---- Config ----
API_KEY = os.environ.get("API_KEY", "mysecretkey123")   # set in Railway Variables
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ---- Helpers ----
def _require_key():
    key = request.args.get("key")
    if not API_KEY or key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 403

def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def _json_ok(payload):
    # Add no-cache so Glide always sees fresh data when you update
    resp = jsonify(payload)
    resp.headers["Cache-Control"] = "no-store"
    return resp

# ---- Basic routes ----
@app.route("/")
def home():
    return _json_ok({"status": "ok", "message": "Lottery backend is running (Flask) on Railway"})

@app.route("/health")
def health():
    return _json_ok({"status": "ok"})

# ---- PREDICTIONS ----
# Source file: data/predictions/predictions.json
# Supports optional ?game= and ?date= (YYYY-MM-DD)
@app.route("/predictions")
def predictions():
    auth = _require_key()
    if auth: return auth

    src = os.path.join(DATA_DIR, "predictions", "predictions.json")
    data = _load_json(src) or {"predictions": []}
    items = data.get("predictions", [])

    game = request.args.get("game")
    date = request.args.get("date")
    if game:
        items = [r for r in items if str(r.get("game","")).lower() == game.lower()]
    if date:
        items = [r for r in items if str(r.get("date")) == date]

    return _json_ok(items)

# ---- WEEKLY REPORT (Glide-friendly) ----
# Source file: data/weekly_report/weekly_report.json
# Returns an object with "report_data" so Glide JSON Path works
@app.route("/glide_weekly_report")
def glide_weekly_report():
    auth = _require_key()
    if auth: return auth

    src = os.path.join(DATA_DIR, "weekly_report", "weekly_report.json")
    report = _load_json(src) or {"report_data": []}
    # Ensure shape is stable for Glide
    if isinstance(report, list):
        report = {"report_data": report}
    if "report_data" not in report:
        report = {"report_data": []}
    return _json_ok(report)

# ---- HISTORICAL WEEK (one file) ----
# Looks for latest file in data/historical_week/*.json or ?date=YYYY-MM-DD
@app.route("/historical_week")
def historical_week():
    auth = _require_key()
    if auth: return auth

    hw_dir = os.path.join(DATA_DIR, "historical_week")
    date = request.args.get("date")  # expecting YYYY-MM-DD in filename
    path = None

    if date:
        # try exact match in filename
        matches = glob.glob(os.path.join(hw_dir, f"*{date}*.json"))
        if matches:
            path = sorted(matches)[-1]
    else:
        matches = glob.glob(os.path.join(hw_dir, "*.json"))
        if matches:
            path = sorted(matches)[-1]

    js = _load_json(path) if path else None
    return _json_ok(js or {"report_data": []})

# ---- BACKTEST ----
# Source: data/backtest/backtest.json
@app.route("/backtest")
def backtest():
    auth = _require_key()
    if auth: return auth

    src = os.path.join(DATA_DIR, "backtest", "backtest.json")
    data = _load_json(src) or {"results": []}
    return _json_ok(data)

# ---- ARCHIVES ----
# List all archive files (date keyed) or return specific file with ?date=YYYY-MM-DD
@app.route("/archives")
def archives():
    auth = _require_key()
    if auth: return auth

    arc_dir = os.path.join(DATA_DIR, "archives")
    date = request.args.get("date")
    if date:
        matches = glob.glob(os.path.join(arc_dir, f"*{date}*.json"))
        if matches:
            js = _load_json(sorted(matches)[-1])
            return _json_ok(js or {})
        return _json_ok({"error": "not found", "date": date})

    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(arc_dir, "*.json")))
    return _json_ok({"files": files})

# ---- Legacy /Glide aliases kept for your app rows ----
@app.route("/glide_view_predictions")
def glide_view_predictions():
    # Same as /predictions but returns {"predictions": [...]}
    auth = _require_key()
    if auth: return auth
    with app.test_request_context():
        items = predictions().json if hasattr(predictions(), "json") else []
    return _json_ok({"predictions": items})

# ---- MAIN (Railway port) ----
import io, csv

def _flatten_predictions(items):
    """Flatten your per-game predictions into uniform rows."""
    flat = []
    for g in items:
        game = g.get("game")
        date = g.get("date")
        hot = g.get("hot_number")
        mirror = g.get("mirror_number")
        acc = g.get("model_accuracy")
        for p in g.get("predictions", []):
            flat.append({
                "date": date,
                "game": game,
                "hot": hot,
                "mirror": mirror,
                "model_accuracy": acc,
                "combo": p.get("combo"),
                "final_score": p.get("final_score"),
            })
    return flat

def _to_csv_response(rows, filename="predictions.csv"):
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["date","game","hot","mirror","model_accuracy","combo","final_score"],
        extrasaction="ignore"
    )
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    data = output.getvalue()
    from flask import Response
    resp = Response(data, mimetype="text/csv")
    resp.headers["Content-Disposition"] = f'inline; filename="{filename}"'
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route("/predictions_csv")
def predictions_csv():
    # Auth
    auth = _require_key()
    if auth: return auth

    # Load JSON like in /predictions
    src = os.path.join(DATA_DIR, "predictions", "predictions.json")
    data = _load_json(src) or {"predictions": []}
    items = data.get("predictions", [])

    # Optional filters
    game = request.args.get("game")  # exact match, case-insensitive
    date = request.args.get("date")  # YYYY-MM-DD
    if game:
        items = [r for r in items if str(r.get("game","")).lower() == game.lower()]
    if date:
        items = [r for r in items if str(r.get("date")) == date]

    # Flatten & return CSV
    rows = _flatten_predictions(items)
    fname = f'predictions_{(game or "all").replace(" ","_")}.csv'
    return _to_csv_response(rows, filename=fname)

# ---- Convenience endpoints for four games ----
@app.route("/predictions_csv/mega")
def predictions_csv_mega():
    with app.test_request_context(
        f'/predictions_csv?game=Mega%20millions&key={request.args.get("key","")}'
    ):
        return predictions_csv()

@app.route("/predictions_csv/powerball")
def predictions_csv_powerball():
    with app.test_request_context(
        f'/predictions_csv?game=Powerball&key={request.args.get("key","")}'
    ):
        return predictions_csv()

@app.route("/predictions_csv/nywin3")
def predictions_csv_nywin3():
    with app.test_request_context(
        f'/predictions_csv?game=NY%20win3&key={request.args.get("key","")}'
    ):
        return predictions_csv()

@app.route("/predictions_csv/nywin4")
def predictions_csv_nywin4():
    with app.test_request_context(
        f'/predictions_csv?game=NY%20win4&key={request.args.get("key","")}'
    ):
        return predictions_csv()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)