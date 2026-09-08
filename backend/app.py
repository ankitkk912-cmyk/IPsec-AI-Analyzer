from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import base64

from database import init_db, save_analysis, list_analyses, get_analysis
from analyzer import analyze_config
from report_generator import create_pdf_report
from ai_engine import get_ai_explanation


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")

app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

init_db()

ALLOWED_EXTENSIONS = {
    ".conf",
    ".txt",
    ".json",
    ".cfg",
    ".ini",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
}


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "IPsec AI Analyzer"
    })


@app.post("/api/analyze")
def analyze():

    uploaded = request.files.get("config")

    if not uploaded or not uploaded.filename:
        return jsonify({
            "error": "Please select a configuration file or image."
        }), 400

    suffix = Path(uploaded.filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        return jsonify({
            "error": "Allowed files: .conf, .cfg, .txt, .json, .ini, .png, .jpg, .jpeg, .webp"
        }), 400

    filename = secure_filename(uploaded.filename)

    # =========================================================
    # IMAGE FILES
    # =========================================================

    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:

        try:
            image_bytes = uploaded.read()

            if not image_bytes:
                return jsonify({
                    "error": "The image is empty."
                }), 400

            api_key = os.getenv("OPENAI_API_KEY")

            if not api_key:
                return jsonify({
                    "error": "OPENAI_API_KEY is not configured."
                }), 500

            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            encoded_image = base64.b64encode(
                image_bytes
            ).decode("utf-8")

            mime_type = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp"
            }[suffix]

            response = client.responses.create(

                model=os.getenv(
                    "OPENAI_MODEL",
                    "gpt-5.6-luna"
                ),

                input=[
                    {
                        "role": "user",
                        "content": [

                            {
                                "type": "input_text",
                                "text": """
You are a defensive IPsec VPN security analyzer.

Read the configuration shown in this image.

Extract the visible IPsec, IKE, VPN,
encryption, authentication, tunnel,
crypto policy and security configuration.

Return the extracted configuration as plain text.

Do NOT invent missing information.

If something is unclear or not visible,
write "unclear".
"""
                            },

                            {
                                "type": "input_image",
                                "image_url": (
                                    f"data:{mime_type};base64,"
                                    f"{encoded_image}"
                                )
                            }

                        ]
                    }
                ]
            )

            content = response.output_text.strip()

            if not content:
                return jsonify({
                    "error": "AI could not read IPsec configuration from this image."
                }), 400

        except Exception as exc:

            return jsonify({
                "error": f"Image analysis failed: {exc}"
            }), 500

    # =========================================================
    # TEXT / CONFIGURATION FILES
    # =========================================================

    else:

        try:
            content = uploaded.read().decode(
                "utf-8",
                errors="replace"
            )

        except Exception as exc:

            return jsonify({
                "error": f"Could not read configuration file: {exc}"
            }), 400

        if not content.strip():
            return jsonify({
                "error": "The configuration file is empty."
            }), 400

    # =========================================================
    # IPSEC ANALYSIS
    # =========================================================

    result = analyze_config(content)

    analysis_id = save_analysis(
        filename,
        result
    )

    # Save extracted configuration
    safe_name = f"{analysis_id}_{filename}"

    (UPLOAD_DIR / safe_name).write_text(
        content,
        encoding="utf-8"
    )

    result["id"] = analysis_id
    result["filename"] = filename

    return jsonify(result)


@app.get("/api/history")
def history():
    return jsonify(list_analyses())


@app.get("/api/analysis/<int:analysis_id>")
def analysis_detail(analysis_id):

    item = get_analysis(analysis_id)

    if not item:
        return jsonify({
            "error": "Analysis not found."
        }), 404

    return jsonify(item)


@app.get("/api/report/<int:analysis_id>")
def report(analysis_id):

    item = get_analysis(analysis_id)

    if not item:
        return jsonify({
            "error": "Analysis not found."
        }), 404

    pdf_path = create_pdf_report(item)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"ipsec_security_report_{analysis_id}.pdf"
    )


@app.post("/api/ai-explain/<int:analysis_id>")
def ai_explain(analysis_id):

    item = get_analysis(analysis_id)

    if not item:
        return jsonify({
            "error": "Analysis not found."
        }), 404

    explanation = get_ai_explanation(item)

    return jsonify({
        "explanation": explanation
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )