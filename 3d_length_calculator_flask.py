from flask import Flask, request, render_template_string
import math

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>3D Filament Length Calculator</title>
    <style>
        :root {
            --bg1: #0f172a;
            --bg2: #1e293b;
            --card: #ffffff;
            --text: #0f172a;
            --muted: #64748b;
            --accent: #2563eb;
            --accent-hover: #1d4ed8;
            --ok-bg: #eff6ff;
            --ok-border: #60a5fa;
            --err-bg: #fef2f2;
            --err-border: #f87171;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, var(--bg1), var(--bg2));
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }

        .card {
            width: 100%;
            max-width: 720px;
            background: var(--card);
            border-radius: 18px;
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.25);
            overflow: hidden;
        }

        .header {
            padding: 28px 30px 18px 30px;
            background: linear-gradient(135deg, #2563eb, #1e40af);
            color: white;
        }

        .header h1 {
            margin: 0 0 8px 0;
            font-size: 30px;
        }

        .header p {
            margin: 0;
            font-size: 15px;
            opacity: 0.95;
        }

        .content {
            padding: 28px 30px 30px 30px;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
        }

        .field {
            display: flex;
            flex-direction: column;
        }

        label {
            font-size: 14px;
            font-weight: bold;
            color: var(--text);
            margin-bottom: 8px;
        }

        input {
            width: 100%;
            padding: 13px 14px;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            font-size: 16px;
            background: #f8fafc;
            outline: none;
        }

        input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
            background: #fff;
        }

        .hint {
            margin-top: 4px;
            font-size: 13px;
            color: var(--muted);
        }

        button {
            margin-top: 24px;
            width: 100%;
            border: none;
            border-radius: 12px;
            padding: 14px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            color: white;
            background: var(--accent);
        }

        button:hover {
            background: var(--accent-hover);
        }

        .result {
            margin-top: 24px;
            padding: 18px;
            border-radius: 12px;
            background: var(--ok-bg);
            border-left: 6px solid var(--ok-border);
        }

        .result h2 {
            margin: 0 0 10px 0;
        }

        .result-row {
            margin: 6px 0;
            font-size: 17px;
        }

        .error {
            margin-top: 24px;
            padding: 16px;
            border-radius: 12px;
            background: var(--err-bg);
            border-left: 6px solid var(--err-border);
            color: #991b1b;
        }

        @media (max-width: 640px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h1>3D Filament Length Calculator</h1>
            <p>Calculate how many meters of filament remain on your spool.</p>
        </div>

        <div class="content">
            <form method="post">
                <div class="grid">
                    <div class="field">
                        <label>Total weight (g)</label>
                        <input type="number" step="any" name="total_weight" value="{{ total_weight or '' }}" required>
                        <div class="hint">Weight of spool + filament</div>
                    </div>

                    <div class="field">
                        <label>Spool weight (g)</label>
                        <input type="number" step="any" name="spool_weight" value="{{ spool_weight or '' }}" required>
                        <div class="hint">Empty spool weight</div>
                    </div>

                    <div class="field">
                        <label>Density (g/cm³)</label>
                        <input type="number" step="any" name="density" value="{{ density or '' }}" required>
                        <div class="hint">PLA 1.24, PETG 1.27, ABS 1.04</div>
                    </div>

                    <div class="field">
                        <label>Diameter (mm)</label>
                        <input type="number" step="any" name="diameter" value="{{ diameter or '1.75' }}" required>
                    </div>
                </div>

                <button type="submit">Calculate</button>
            </form>

            {% if result %}
                <div class="result">
                    <h2>Result</h2>
                    <div class="result-row">Filament weight: <strong>{{ filament_weight }} g</strong></div>
                    <div class="result-row">Length: <strong>{{ result }} meters</strong></div>
                </div>
            {% endif %}

            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


def filament_length(weight, density, diameter):
    weight_kg = weight / 1000
    density_kg_m3 = density * 1000
    diameter_m = diameter / 1000

    area = math.pi * (diameter_m / 2) ** 2
    return weight_kg / (density_kg_m3 * area)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    filament_weight = None
    error = None

    total_weight = None
    spool_weight = None
    density = None
    diameter = 1.75

    if request.method == "POST":
        try:
            total_weight = float(request.form["total_weight"])
            spool_weight = float(request.form["spool_weight"])
            density = float(request.form["density"])
            diameter = float(request.form["diameter"])

            filament = total_weight - spool_weight

            if filament <= 0:
                raise ValueError("Spool weight must be less than total weight")

            length = filament_length(filament, density, diameter)

            filament_weight = f"{filament:.0f}"
            result = f"{length:.2f}"

        except Exception as e:
            error = str(e)

    return render_template_string(
        HTML,
        result=result,
        filament_weight=filament_weight,
        error=error,
        total_weight=total_weight,
        spool_weight=spool_weight,
        density=density,
        diameter=diameter
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055)
