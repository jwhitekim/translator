"""
Translation Studio — proxy server.

실행:
    pip install -r requirements.txt
    python server.py

브라우저에서 http://localhost:8080 접속
"""

import os
import urllib.parse
import requests
from flask import Flask, request, Response, send_from_directory, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DEEPL_API_KEY = os.environ["DEEPL_API_KEY"]
DEEPL_URL     = "https://api-free.deepl.com/v2/translate"

naver_session = requests.Session()
naver_session.headers.update({
    "User-Agent":      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
    "Referer":         "https://endic.naver.com/",
})


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


FREE_DICT_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"


@app.route("/api/dict")
def dict_lookup():
    """DeepL(한국어) + Free Dictionary API(발음/품사/영어 정의) 병렬 조합."""
    query = request.args.get("query", "").strip().lower()
    if not query:
        return jsonify({"error": "no query"}), 400

    import concurrent.futures

    def get_korean():
        r = requests.post(
            DEEPL_URL,
            headers={"Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"},
            json={"text": [query], "target_lang": "KO", "source_lang": "EN"},
            timeout=6,
        )
        return r.json()["translations"][0]["text"] if r.ok else None

    def get_free_dict():
        r = requests.get(FREE_DICT_URL.format(urllib.parse.quote(query)), timeout=6)
        return r.json() if r.ok else None

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        ko_future = ex.submit(get_korean)
        fd_future = ex.submit(get_free_dict)
        ko_word = ko_future.result()
        fd_data = fd_future.result()

    if not ko_word and not fd_data:
        return jsonify({"error": "not found", "query": query}), 404

    entries = []
    phonetic = ""

    if fd_data and isinstance(fd_data, list):
        entry    = fd_data[0]
        phonetic = entry.get("phonetic") or next(
            (p.get("text", "") for p in entry.get("phonetics", []) if p.get("text")), ""
        )
        for meaning in entry.get("meanings", [])[:3]:
            means = []
            if ko_word:
                means.append(f"[KO] {ko_word}")
                ko_word = None  # 첫 번째 품사에만 표시
            for d in meaning.get("definitions", [])[:3]:
                if d.get("definition"):
                    means.append(d["definition"])
            if means:
                entries.append({
                    "word": query,
                    "pron": phonetic,
                    "pos":  meaning.get("partOfSpeech", ""),
                    "means": means,
                })

    # Free Dict 결과 없어도 한국어 번역은 표시
    if not entries and ko_word:
        entries.append({"word": query, "pron": "", "pos": "", "means": [f"[KO] {ko_word}"]})

    if not entries:
        return jsonify({"error": "not found", "query": query}), 404

    return jsonify({"query": query, "entries": entries})


if __name__ == "__main__":
    print("서버 시작: http://localhost:8080")
    app.run(port=8080, debug=False)
