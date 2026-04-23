"""
Translation Studio — proxy server.

실행:
    pip install -r requirements.txt
    python server.py

브라우저에서 http://localhost:8080 접속
"""

import os
import time
import requests
from flask import Flask, request, Response, send_from_directory, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DEEPL_API_KEY = os.environ["DEEPL_API_KEY"]
DEEPL_URL     = "https://api-free.deepl.com/v2/translate"

NAVER_DICT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer":    "https://en.dict.naver.com/",
    "Accept":     "application/json",
}

# ── Routes ───────────────────────────────────────────────────────


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
    return Response(resp.content, status=resp.status_code, content_type="application/json")


@app.route("/api/naver-dict")
def naver_dict_proxy():
    query = request.args.get("query", "").strip()
    if not query:
        return ("", 400)

    params = {
        "query":              query,
        "m":                  "pc",
        "shouldSearchVlive":  "true",
        "lang":               "ko",
        "hid":                str(int(time.time() * 1000)),
    }
    resp = requests.get(
        "https://en.dict.naver.com/api3/enko/search",
        params=params,
        headers=NAVER_DICT_HEADERS,
        timeout=5,
    )
    data = resp.json()

    word_section = (
        data.get("searchResultMap", {})
            .get("searchResultListMap", {})
            .get("WORD", {})
            .get("items", [])
    )

    def strip_tags(s):
        return s.replace("<strong>", "").replace("</strong>", "")

    results = []
    for item in word_section[:3]:
        entry    = strip_tags(item.get("expEntry", ""))
        pron_list = item.get("searchPhoneticSymbolList", [])
        phonetic  = pron_list[0].get("symbolValue", "") if pron_list else ""

        senses = []
        for collector in item.get("meansCollector", []):
            pos = collector.get("partOfSpeech", "")
            for mean in collector.get("means", []):
                senses.append({
                    "pos":          pos,
                    "value":        mean.get("value", ""),
                    "exampleOri":   strip_tags(mean.get("exampleOri", "")),
                    "exampleTrans": mean.get("exampleTrans", ""),
                })

        results.append({"entry": entry, "phonetic": phonetic, "senses": senses})

    return jsonify({"query": query, "results": results})


if __name__ == "__main__":
    print("서버 시작: http://localhost:8080")
    app.run(port=8080, debug=False)
