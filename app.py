from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

# --- MongoDB Connection ---
MONGO_URL = "mongodb+srv://Mohd_Akbar_Ali:akbarali@cluster0.vs7wwt0.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client["ac_controller"]
collection = db["ac_status"]

# Initialize DB if empty
if collection.count_documents({}) == 0:
    collection.insert_one({"status": "off", "temperature": 24})

# --- FRONTEND HTML (unchanged) ---
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AC Controller</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f4f7fa;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
    }
    .container {
      background: #fff;
      padding: 30px 40px;
      border-radius: 8px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.12);
      text-align: center;
    }
    .btn {
      font-size: 1.1em;
      padding: 10px 30px;
      margin: 10px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }
    .btn-on {
      background: #28a745;
      color: #fff;
    }
    .btn-off {
      background: #dc3545;
      color: #fff;
    }
    .temp-control {
      margin: 15px 0;
    }
    input[type="range"] {
      width: 200px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>AC Controller</h2>
    <div>
      <button class="btn btn-on" onclick="setAC('on')">ON</button>
      <button class="btn btn-off" onclick="setAC('off')">OFF</button>
    </div>
    <div class="temp-control">
      <label for="tempRange">Temperature: <span id="tempDisplay">24</span>°C</label><br>
      <input type="range" id="tempRange" min="16" max="30" value="24" oninput="updateTempDisplay(this.value)" onchange="setTemperature(this.value)">
    </div>
  </div>
  <script>
    function setAC(state) {
      // Replace URL with your backend endpoint
      fetch('/ac/state', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({state: state})
      })
      .then(response => response.json())
      .then(data => alert(`AC turned ${state.toUpperCase()}`))
      .catch(error => alert('Error setting AC state'));
    }
    function setTemperature(temp) {
      // Replace URL with your backend endpoint
      fetch('/ac/temperature', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({temperature: temp})
      })
      .then(response => response.json())
      .then(data => alert(`Temperature set to ${temp}°C`))
      .catch(error => alert('Error setting temperature'));
    }
    function updateTempDisplay(value) {
      document.getElementById('tempDisplay').innerText = value;
    }
  </script>
</body>
</html>"""

# --- ROUTES ---

@app.route('/')
def home():
    return render_template_string(HTML)


@app.route('/ac/state', methods=['POST'])
def ac_state():
    data = request.get_json()
    state = data.get("state", "").lower()
    if state not in ["on", "off"]:
        return jsonify({"error": "Invalid state"}), 400
    collection.update_one({}, {"$set": {"status": state}})
    return jsonify({"ok": True, "state": state})


@app.route('/ac/temperature', methods=['POST'])
def ac_temperature():
    data = request.get_json()
    try:
        temp = int(data.get("temperature", 24))
    except ValueError:
        return jsonify({"error": "Invalid temperature"}), 400
    if not 16 <= temp <= 30:
        return jsonify({"error": "Temperature out of range"}), 400
    collection.update_one({}, {"$set": {"temperature": temp}})
    return jsonify({"ok": True, "temperature": temp})


@app.route('/fetch', methods=['GET'])
def fetch_data():
    d = collection.find_one()
    return jsonify({"status": d["status"], "temperature": d["temperature"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
