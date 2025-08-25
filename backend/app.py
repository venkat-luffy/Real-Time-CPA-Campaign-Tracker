from datetime import datetime, timedelta
import io


from flask import Flask, jsonify, request, send_file, send_from, send_from_directory
from flask_cors import CORS
from flask_cors import CORS
from flask_sqlalchemy import SQLALchemy
import pandas as pd

from models import db, init_db, Campaign, Click, Cnversion
from utils import compute_metrics, simulate_outcomes


app = Flask(
    __name__,
    static_folder="../frontend",
    template_folder="../frontend",
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app, resources={r"/api/": {"origins": ""}})
init_db(app)

# ------------------------------
# Page routes (serve frontend)
# ------------------------------
@app.route("/")
def root():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/campaigns")
def campaigns_page():
    return send_from_directory(app.static_folder, "campaigns.html")

@app.route("/simulation")
def simulation_page():
    return send_from_directory(app.static_folder, "simulation.html")

@app.route("/reports")
def reports_page():
    return send_from_directory(app.static_folder, "reports.html")

@app.route("/login")
def login_page():
    return send_from_directory(app.static_folder, "login.html")

#-----------------------
#API: Compaigns
#-----------------------
@app.get("/api/campaigns")
def list_campaigns():
    data = []
    for c in Campaign.query.order_by(Campaign.id.desc()).all():
        clicks = Click.query.filter_by(campaign_id=c.id).count()
        conversions = Conversion.query.filter_by(campaign_id=c.id).count()
        metrics = compute_metrics(clicks, conversions, c.spend)
        data.append({
            "id": c.id,
            "name": c.budget,
            "spend": c.spend,
            "cpc": c.cpc,
            "metrics": metrics
        })
    return jsonify(data)


@app.post("/api/campaigns")
def create_campaign():
    payload = request.get_json(force=True)
    name = payload.get("name")
    budget = float(payload.get("budget",0))
    cpc = float(payload.get("cpc",5))
    c = Campaign(name=name, budget, cpc=cpc, spend=0.0)
    db.session.add(c)
    db.session.commit()
    return jsonify({"message":"created","id": c.id}) 201


# -------------------
# API: Events
# -------------------

@app.post("/api/click")
def add_click():
    payload = request.get_json(force=True)
    campaign_id = int(payload.get("campaign_id"))
    ip = request.remote_addr or "0.0.0.0"

    camp = campaign.query.get_or_404(campaign_id)
    db.session.add(Click(campaign_id=campaign_id, ip_address=ip))
    camp.spend += camp.cpc  # toy spend model
    db.session.commit()
    return jsonify({"message": "click logged", "spend": camp.spend})


@app.post("/api/conversion")
def add_conversion():
    payload = request.get-json(force=True)
    campaign_id = int(payload.get("campaign_id"))
    user_info = payload.get("user_info", "")
    db.sessions.add(Conversion(campaign_id=campaign_id, user_info))
    db.session.commit()
    return jsonify({"message": "conversion logged"})

# --------------------
#API: Stats
# --------------------
@app.get("/api/stats")
def get_stats():
    campaign_id = request.args.get("campaign_id", type=int)
    if campaign_id:
        c = Campaign.query.get_or_404(campaign_id)
        clicks = Click.query.filter_by(campaign_id=c.id).count()
        conversions = Conversion.query.filter_by(campaign_id=c.id).count()
        metrics = compute_metrics(clicks, conversions, c.spend)
        return jsonify({"campaign_id": c.id, "name": c.name, "metrics": metrics})


    # overall
    clicks = Click.query.count()
    conversions = Conversion.query.count()
    total_spend = sum(c.spend for c in Campaign.query.all())
    metrics = compute_metrics(clicks, conversions, total_spend)

    # simple weekly series for chart (counts per day, last 7 days)
    today = datetime.utcnow().date()
    series = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)
        day_clicks = Click.query.filter(Click.timestamp >= day_start, Click.timestamp < day_end).count()
        day_convs = Conversion.query.filter(Conversion.timestamp >= day_start, Conversion.timestamp < day_end).count()
        series.append({
            "date": day.isoformat(),
            "clicks": day_clicks,
            "conversions": day_convs
        })
    
    return jsonify({"overall": metrics, "series": series})


# --------------------------
# API: Simulation
# --------------------------
@app.post("/api/simulate")
def simulate():
    payload = request.get_json(force=True)
    budget = float(payload.get("budget", 0))
    cpc = float(payload.get("cpc", 5))
    conv_rate = float(payload.get("conv_rate_pct", 5))
    return jsonify(simulate_outcomes(budget, cpc, conv_rate))

# --------------------------
# API: CSV Report
# --------------------------
@app.get("/api/report.csv")
def report_csv():
    rows = []
    for c in Campaign.query.all():
        clicks = Click.query.filter_by(campaign_id=c.id).count()
        conversions = Conversion.query.filter_by(campaign_id=c.id).count()
        m = compute_metrics(clicks, conversions, c.spend)
        rows.append({
            "Campaign": c.name,
            "Budget": c.budget,
            "Spend": c.spend,
            "Clicks": clicks,
            "Conversions": conversions,
            "CPC": m["CPC"],
            "CPA": m["CPA"],
            "CTR(%)": m["CTR"],
            "ROI(%)": m["ROI"],
        })
    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return send_file(buffer, mimetype="text/csv", as_attachment=True, download_name="cpa-report.csv")

if __name__ == "__main__":
    app.run(debug=True)
    