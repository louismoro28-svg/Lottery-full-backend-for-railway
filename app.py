import os, json, glob, io, csv
from datetime import datetime
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from io import StringIO

# -------------------------
# App + CORS
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# Config
# -------------------------
API_KEY = os.environ.get("API_KEY", "mysecretkey123")  # set in Railway Variables
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# -------------------------
# Helpers
# -------------------------
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
    resp = jsonify(payload)
    resp.headers["Cache-Control"] = "no-store"
    return resp

def _to_csv_response(rows, filename="data.csv"):
    out = StringIO()
    cols = sorted({k for r in rows for k in r.keys()}) if rows else ["message"]
    writer = csv.DictWriter(out, fieldnames=cols)
    writer.writeheader()
    if not rows:
        writer.writerow({"message": "no data"})
    else:
        for r in rows:
            writer.writerow({k: r.get(k) for k in cols})
    resp = make_response(out.getvalue())
    resp.headers["Content-Type"] = "text/csv"
    resp.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    resp.headers["Cache-Control"] = "no-store"
    return resp

def _flatten_predictions(items):
    """
    Flatten list of game objects that look like:
      { "game": "...", "date": "YYYY-MM-DD", "hot_number": .., "mirror_number": ..,
        "model_accuracy": .., "predictions": [ {"combo": "1234", "final_score": 0.87}, ... ] }
    into rows with columns: date, game, hot, mirror, model_accuracy, combo, final_score
    """
    flat = []
    for g in items or []:
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

def _filter_by_game(rows, game):
    if not game:
        return rows
    g = game.strip().lower()
    return [r for r in rows if str(r.get("game", "")).lower() == g]

# -------------------------
# Basic routes
# -------------------------
@app.route("/")
def home():
    return _json_ok({"status": "ok", "message": "Lottery backend is running (Flask) on Railway"})

@app.route("/health")
def health():
    return _json_ok({"status": "ok"})

@app.route("/routes")
def routes():
    return _json_ok(sorted([r.rule for r in app.url_map.iter_rules()]))

# -------------------------
# JSON API (Glide-friendly)
# -------------------------
# /predictions -> list[ {...} ], optional ?game=&date=YYYY-MM-DD
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

# /glide_weekly_report -> {"report_data":[...]}
@app.route("/glide_weekly_report")
def glide_weekly_report():
    auth = _require_key()
    if auth: return auth
    src = os.path.join(DATA_DIR, "weekly_report", "weekly_report.json")
    report = _load_json(src) or {"report_data": []}
    if isinstance(report, list):
        report = {"report_data": report}
    if "report_data" not in report:
        report = {"report_data": []}
    return _json_ok(report)

# /historical_week -> {"report_data":[...]}, optional ?date=YYYY-MM-DD (matches filename)
@app.route("/historical_week")
def historical_week():
    auth = _require_key()
    if auth: return auth
    hw_dir = os.path.join(DATA_DIR, "historical_week")
    qdate = request.args.get("date")
    path = None
    if qdate:
        matches = glob.glob(os.path.join(hw_dir, f"*{qdate}*.json"))
        if matches: path = sorted(matches)[-1]
    else:
        matches = glob.glob(os.path.join(hw_dir, "*.json"))
        if matches: path = sorted(matches)[-1]
    js = _load_json(path) if path else None
    return _json_ok(js or {"report_data": []})

# /backtest -> {"results":[...]} or {"hit_data":[...]} (we'll pass through)
@app.route("/backtest")
def backtest():
    auth = _require_key()
    if auth: return auth
    src = os.path.join(DATA_DIR, "backtest", "backtest.json")
    data = _load_json(src) or {}
    return _json_ok(data)

# /archives -> list archive files, or ?date=YYYY-MM-DD returns that file’s data
@app.route("/archives")
def archives():
    auth = _require_key()
    if auth: return auth
    arc_dir = os.path.join(DATA_DIR, "archives")
    qdate = request.args.get("date")
    if qdate:
        matches = glob.glob(os.path.join(arc_dir, f"*{qdate}*.json"))
        if matches:
            js = _load_json(sorted(matches)[-1])
            return _json_ok(js or {})
        return _json_ok({"error": "not found", "date": qdate})
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(arc_dir, "*.json")))
    return _json_ok({"files": files})

# Legacy alias: {"predictions":[...]} wrapper around /predictions
@app.route("/glide_view_predictions")
def glide_view_predictions():
    auth = _require_key()
    if auth: return auth
    # emulate calling /predictions in the same request context
    items = []
    src = os.path.join(DATA_DIR, "predictions", "predictions.json")
    data = _load_json(src) or {"predictions": []}
    items = data.get("predictions", [])
    return _json_ok({"predictions": items})

# -------------------------
# CSV API
# -------------------------
# Generic Predictions CSV + 4 shortcuts (already added earlier, keep if you’re using them)
@app.route("/predictions_csv")
def predictions_csv():
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

    rows = _flatten_predictions(items)
    fname = f'predictions_{(game or "all").replace(" ","_")}.csv'
    return _to_csv_response(rows, filename=fname)

@app.route("/predictions_csv/mega")
def predictions_csv_mega():
    request.args = request.args.copy()
    return predictions_csv()

@app.route("/predictions_csv/powerball")
def predictions_csv_powerball():
    request.args = request.args.copy()
    return predictions_csv()

@app.route("/predictions_csv/nywin3")
def predictions_csv_nywin3():
    request.args = request.args.copy()
    return predictions_csv()

@app.route("/predictions_csv/nywin4")
def predictions_csv_nywin4():
    request.args = request.args.copy()
    return predictions_csv()

# Weekly report CSV with ?game=
@app.route("/weekly_report_csv")
def weekly_report_csv():
    auth = _require_key()
    if auth: return auth
    qgame = request.args.get("game")
    src = os.path.join(DATA_DIR, "weekly_report", "weekly_report.json")
    data = _load_json(src) or {"report_data": []}
    rows = data.get("report_data", [])
    rows = _filter_by_game(rows, qgame)
    fname = "weekly_report.csv" if not qgame else f"weekly_report_{qgame}.csv"
    return _to_csv_response(rows, filename=fname)

# Backtest CSV with ?game=
@app.route("/backtest_csv")
def backtest_csv():
    auth = _require_key()
    if auth: return auth
    qgame = request.args.get("game")
    src = os.path.join(DATA_DIR, "backtest", "backtest.json")
    js = _load_json(src) or {}
    rows = js.get("results") or js.get("hit_data") or []
    rows = _filter_by_game(rows, qgame)
    fname = "backtest.csv" if not qgame else f"backtest_{qgame}.csv"
    return _to_csv_response(rows, filename=fname)

# Historical week CSV with ?date=YYYY-MM-DD and ?game=
@app.route("/historical_csv")
def historical_csv():
    auth = _require_key()
    if auth: return auth
    hw_dir = os.path.join(DATA_DIR, "historical_week")
    qdate = request.args.get("date")
    qgame = request.args.get("game")

    matches = []
    if qdate:
        matches = glob.glob(os.path.join(hw_dir, f"*{qdate}*.json"))
    if not matches:
        matches = glob.glob(os.path.join(hw_dir, "*.json"))
    if not matches:
        return _to_csv_response([], filename="historical.csv")

    path = sorted(matches)[-1]
    data = _load_json(path) or {"report_data": []}
    rows = data.get("report_data", [])
    rows = _filter_by_game(rows, qgame)

    fname = "historical.csv"
    if qdate and qgame:
        fname = f"historical_{qdate}_{qgame}.csv"
    elif qdate:
        fname = f"historical_{qdate}.csv"
    elif qgame:
        fname = f"historical_{qgame}.csv"
    return _to_csv_response(rows, filename=fname)

# Archives CSV with ?date=YYYY-MM-DD and ?game=
@app.route("/archives_csv")
def archives_csv():
    auth = _require_key()
    if auth: return auth
    arc_dir = os.path.join(DATA_DIR, "archives")
    qdate = request.args.get("date")
    qgame = request.args.get("game")

    if qdate:
        matches = glob.glob(os.path.join(arc_dir, f"*{qdate}*.json"))
        if not matches:
            return _to_csv_response([], filename=f"archives_{qdate}.csv")
        js = _load_json(sorted(matches)[-1]) or []
        rows = js if isinstance(js, list) else [js]
        rows = _filter_by_game(rows, qgame)
        fname = f"archives_{qdate}.csv" if not qgame else f"archives_{qdate}_{qgame}.csv"
        return _to_csv_response(rows, filename=fname)

    # No date: combine all archives and (optionally) filter by game
    rows = []
    for p in sorted(glob.glob(os.path.join(arc_dir, "*.json"))):
        js = _load_json(p) or []
        rows.extend(js if isinstance(js, list) else [js])
    rows = _filter_by_game(rows, qgame)
    fname = "archives.csv" if not qgame else f"archives_{qgame}.csv"
    return _to_csv_response(rows, filename=fname)

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)