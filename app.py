from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

# --- MongoDB Connection ---
MONGO_URL = "mongodb+srv://Mohd_Akbar_Ali:akbarali@cluster0.4qyhb4n.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client["ac_controller"]
collection = db["ac_status"]

# --- Initialize default AC status if empty ---
if collection.count_documents({}) == 0:
    collection.insert_one({"status": "OFF", "temperature": 24})

# --- Frontend HTML (unchanged from your provided code) ---
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AC Controller Web App</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      background: #111;
      color: #fff;
      font-family: Arial, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      flex-direction: column;
    }
    .ac-status {
      margin-bottom: 20px;
      font-size: 1.3em;
    }
    .controls {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
    }
    .temp-section {
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .temp-controls {
      display: flex;
      gap: 10px;
      margin: 15px 0;
    }
    button {
      background: #222;
      color: #fff;
      border: none;
      outline: none;
      padding: 15px 25px;
      margin: 0 5px;
      border-radius: 7px;
      font-size: 1.2em;
      cursor: pointer;
      transition: background 0.25s;
    }
    button:active, button:focus {
      background: #444;
    }
    .set-temp-btn {
      background: #2979FF;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <div class="ac-status" id="status">AC is OFF</div>
  <div class="controls">
    <button onclick="toggleAC(true)">Turn ON</button>
    <button onclick="toggleAC(false)">Turn OFF</button>
  </div>
  <div class="temp-section">
    <div>Temperature: <span id="temp">24</span>°C</div>
    <div class="temp-controls">
      <button onclick="changeTemp(-1)">-</button>
      <button onclick="changeTemp(1)">+</button>
    </div>
    <button class="set-temp-btn" onclick="setTemp()">Set Temperature</button>
  </div>
  <script>
    let acOn = false;
    let temperature = 24;
    const statusDiv = document.getElementById('status');
    const tempSpan = document.getElementById('temp');

    // Load initial state from backend
    async function loadStatus() {
      const res = await fetch('/fetch');
      const data = await res.json();
      acOn = data.status === "ON";
      temperature = data.temperature;
      statusDiv.textContent = acOn ? "AC is ON" : "AC is OFF";
      tempSpan.textContent = temperature;
    }

    async function toggleAC(state) {
      acOn = state;
      statusDiv.textContent = acOn ? "AC is ON" : "AC is OFF";
      await fetch('/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({status: acOn ? "ON" : "OFF", temperature})
      });
    }

    function changeTemp(delta) {
      temperature += delta;
      tempSpan.textContent = temperature;
    }

    async function setTemp() {
      if (!acOn) {
        alert("Please turn on the AC first.");
        return;
      }
      await fetch('/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({status: acOn ? "ON" : "OFF", temperature})
      });
      alert("Set temperature to " + temperature + "°C");
    }

    loadStatus();
    setInterval(loadStatus, 2000);
  </script>
</body>
</html>
"""

# --- Flask Routes ---
@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/fetch')
def fetch():
    data = collection.find_one()
    return jsonify({"status": data["status"], "temperature": data["temperature"]})

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    collection.update_one({}, {"$set": {
        "status": data["status"],
        "temperature": int(data["temperature"])
    }})
    return jsonify({"ok": True})

# --- Run Flask App ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
