
from flask import Flask, render_template_string, request
import json, os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Connector Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{font-family:Arial;background:#f3f6fa;margin:0;padding:25px;color:#1f2937}
.container{max-width:1100px;margin:auto}
h1{text-align:center;margin-bottom:5px}
.subtitle{text-align:center;color:#666;margin-bottom:25px}
.cards{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:25px}
.card{flex:1;min-width:180px;background:white;padding:20px;border-radius:14px;text-align:center;box-shadow:0 3px 12px #ddd}
.number{font-size:30px;font-weight:bold;color:#2563eb}
.status{color:green;font-weight:bold}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.chartbox{background:white;padding:20px;border-radius:14px;box-shadow:0 3px 12px #ddd}
.query{background:white;padding:20px;border-radius:14px;margin-top:20px;box-shadow:0 3px 12px #ddd}
input{width:70%;padding:12px;border:1px solid #ccc;border-radius:8px}
button{padding:12px 20px;border:0;border-radius:8px;background:#2563eb;color:white}
pre{white-space:pre-wrap;background:#f8fafc;padding:15px;border-radius:8px}
@media(max-width:750px){.charts{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="container">
<h1>🔗 Unified Connector Dashboard</h1>
<p class="subtitle">Gmail + Google Drive + WhatsApp</p>

<div class="cards">
<div class="card"><h2>📧 Gmail</h2><div class="number">{{gmail_count}}</div><p>Emails</p><p class="status">● Connected</p></div>
<div class="card"><h2>📁 Google Drive</h2><div class="number">{{drive_count}}</div><p>Files</p><p class="status">● Connected</p></div>
<div class="card"><h2>💬 WhatsApp</h2><div class="number">{{whatsapp_count}}</div><p>Messages</p><p class="status">● Connector Ready</p></div>
</div>

<div class="charts">
<div class="chartbox"><h2>Gmail Overview</h2><canvas id="gmailChart"></canvas></div>
<div class="chartbox"><h2>Google Drive Overview</h2><canvas id="driveChart"></canvas></div>
</div>

<div class="query">
<h2>🔍 Ask a Question</h2>
<form method="POST">
<input name="query" placeholder="Example: show Gmail data" required>
<button>Search</button>
</form>
{% if result %}<h3>Result</h3><pre>{{result}}</pre>{% endif %}
</div>
</div>

<script>
new Chart(document.getElementById('gmailChart'), {
 type:'doughnut',
 data:{labels:['Sales','Marketing','Other'],
 datasets:[{data:[{{gmail_sales}},{{gmail_marketing}},{{gmail_other}}]}]},
 options:{responsive:true}
});
new Chart(document.getElementById('driveChart'), {
 type:'bar',
 data:{labels:['Sales','Marketing','Verification','Office','Accounts'],
 datasets:[{label:'Files',data:[{{drive_sales}},{{drive_marketing}},{{drive_verification}},{{drive_office}},{{drive_accounts}}]}]},
 options:{responsive:true,scales:{y:{beginAtZero:true}}}
});
</script>
</body>
</html>
"""

def load_json(filename):
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def records(data, keys):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in keys:
            if isinstance(data.get(k), list):
                return data[k]
    return []

def classify_gmail(data):
    rows = records(data, ["emails","messages","data","results"])
    counts = {"sales":0,"marketing":0,"other":0}
    for r in rows:
        if isinstance(r, dict):
            text = str(r.get("classification", r.get("category", r.get("label","other")))).lower()
            if "sales" in text: counts["sales"] += 1
            elif "marketing" in text: counts["marketing"] += 1
            else: counts["other"] += 1
    return counts

def classify_drive(data):
    rows = records(data, ["files","documents","data","results"])
    counts = {"sales":0,"marketing":0,"verification":0,"office":0,"accounts":0}
    for r in rows:
        if isinstance(r, dict):
            text = str(r.get("category", r.get("classification", r.get("label","office")))).lower()
            found = False
            for k in counts:
                if k in text:
                    counts[k] += 1
                    found = True
                    break
            if not found:
                counts["office"] += 1
    return counts

def get_count(data):
    if isinstance(data, list): return len(data)
    if isinstance(data, dict):
        if isinstance(data.get("files"), list): return len(data["files"])
        if isinstance(data.get("messages"), list): return len(data["messages"])
        return len(data)
    return 0

@app.route("/", methods=["GET","POST"])
def dashboard():
    gmail = load_json("gmail_output.json")
    drive = load_json("drive_output.json")
    whatsapp = load_json("whatsapp_output.json")
    gc, dc = classify_gmail(gmail), classify_drive(drive)
    result = ""
    if request.method == "POST":
        q = request.form.get("query","").lower()
        if "gmail" in q or "email" in q:
            result = json.dumps(gmail, indent=2, ensure_ascii=False) if gmail else "Gmail data not available."
        elif "drive" in q or "file" in q:
            result = json.dumps(drive, indent=2, ensure_ascii=False) if drive else "Google Drive data not available."
        elif "whatsapp" in q or "message" in q:
            result = json.dumps(whatsapp, indent=2, ensure_ascii=False) if whatsapp else "WhatsApp data not available yet."
        else:
            result = "No matching connector found."
    return render_template_string(HTML,
        gmail_count=get_count(gmail), drive_count=get_count(drive), whatsapp_count=get_count(whatsapp),
        gmail_sales=gc["sales"], gmail_marketing=gc["marketing"], gmail_other=gc["other"],
        drive_sales=dc["sales"], drive_marketing=dc["marketing"], drive_verification=dc["verification"],
        drive_office=dc["office"], drive_accounts=dc["accounts"], result=result)

if __name__ == "__main__":
    app.run(debug=True)
