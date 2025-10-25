from flask import Flask, request, jsonify, render_template, send_from_directory
import joblib, json
import pandas as pd
import os

# === Load model, scaler, meta ===
try:
    model = joblib.load("nn_model.pkl")
    scaler = joblib.load("minmax_scaler.pkl")
    with open("model_meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
except Exception as e:
    raise RuntimeError(f"Error loading model or metadata: {e}")

feature_order = meta.get("feature_order", [])
sex_mapping = meta.get("sex_mapping", {})
threshold = float(f"{meta.get('threshold', 0.5):.20f}")

app = Flask(__name__)

# --- Serve files from Pictures folder ---
@app.route('/Pictures/<path:filename>')
def serve_picture(filename):
    return send_from_directory('Pictures', filename)

# --- Trang giao diện chính ---
@app.route("/")
def home():
    return render_template("index.html")
# --- Trang Predict ---
@app.route("/index")
def index():
    return render_template("index.html")
# --- Trang Overview ---
@app.route("/overview")
def overview():
    return render_template("Overview.html")
# --- Trang How It Works ---        
@app.route("/howitworks")
def howitworks():
    return render_template("Howitworks.html")   
# --- Trang Contact ---        
@app.route("/contact")
def contact():
    return render_template("Contact.html")
# --- Trang About Us ---        
@app.route("/aboutus")
def aboutus():
    return render_template("Aboutus.html")
# --- API dự đoán ---
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)

        # Kiểm tra đầu vào
        required_fields = ["sex", "age", "ct_echdc3", "ct_sort1", "ct_ref"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        sex = data["sex"]
        age = float(data["age"])
        ct_echdc3 = float(data["ct_echdc3"])
        ct_sort1 = float(data["ct_sort1"])
        ct_ref = float(data["ct_ref"])

        if sex not in sex_mapping:
            return jsonify({"error": f"Invalid sex value: {sex}"}), 400

        # Tính ΔCT
        dct_echdc3 = ct_echdc3 - ct_ref
        dct_sort1 = ct_sort1 - ct_ref

        # Tạo input cho mô hình
        X_input = pd.DataFrame([[
            sex_mapping[sex],
            age,
            dct_echdc3,
            dct_sort1
        ]], columns=feature_order)

        X_scaled = scaler.transform(X_input)
        prob = float(model.predict_proba(X_scaled)[0][1])
        pred = int(prob < threshold)

        return jsonify({
            "ΔCT_ECHDC3": round(dct_echdc3, 4),
            "ΔCT_SORT1": round(dct_sort1, 4),
            "Probability": round(prob, 20),
            "Threshold": f"{threshold:.20f}",
            "Prediction": "Cancer" if pred == 1 else "Normal"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Chạy ứng dụng ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=True)




