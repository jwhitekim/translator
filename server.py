"""
Translation Studio — minimal proxy server.

DeepL API는 브라우저 직접 호출 시 CORS 차단됨.
이 서버가 DeepL 요청을 대신 중계하고, index.html을 서빙함.

실행:
    pip install -r requirements.txt
    python server.py

브라우저에서 http://localhost:8080 접속
"""

import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DEEPL_API_KEY = os.environ["DEEPL_API_KEY"]
DEEPL_URL = "https://api-free.deepl.com/v2/translate"


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json()
    resp = requests.post(
        DEEPL_URL,
        headers={"Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"},
        json={"text": data.get("text", []), "target_lang": data.get("target_lang", "KO")},
        timeout=15,
    )
    return (resp.content, resp.status_code, {"Content-Type": "application/json"})


if __name__ == "__main__":
    print("서버 시작: http://localhost:8080")
    app.run(port=8080, debug=False)
