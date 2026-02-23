import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SUNO_API_KEY = os.getenv("SUNO_API_KEY", "")
SUNO_BASE_URL = "https://api.sunoapi.org/api/v1"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    lyrics = data.get("lyrics", "").strip()
    style = data.get("style", "Japanese hip-hop rap, J-rap")
    title = data.get("title", "日本語ラップ").strip() or "日本語ラップ"
    api_key = data.get("api_key", "").strip() or SUNO_API_KEY

    if not lyrics:
        return jsonify({"error": "歌詞を入力してください"}), 400
    if not api_key:
        return jsonify({"error": "Suno APIキーを入力してください"}), 400

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # sunoapi.org カスタムモードで歌詞とスタイルを送信
    payload = {
        "customMode": True,
        "instrumental": False,
        "model": "V4_5",
        "style": style,
        "title": title,
        "prompt": lyrics,
        "callBackUrl": "https://example.com/callback",  # ポーリング方式のため未使用
    }

    try:
        resp = requests.post(
            f"{SUNO_BASE_URL}/generate",
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.RequestException as e:
        return jsonify({"error": f"通信エラー: {str(e)}"}), 500

    if resp.status_code != 200:
        return (
            jsonify({"error": f"APIエラー ({resp.status_code}): {resp.text}"}),
            resp.status_code,
        )

    result = resp.json()
    if result.get("code") != 200:
        return jsonify({"error": result.get("msg", "生成に失敗しました")}), 500

    task_id = result["data"]["taskId"]
    return jsonify({"task_id": task_id})


@app.route("/api/status")
def get_status():
    task_id = request.args.get("task_id", "")
    api_key = request.args.get("api_key", "").strip() or SUNO_API_KEY

    if not task_id:
        return jsonify({"error": "task_idが指定されていません"}), 400
    if not api_key:
        return jsonify({"error": "Suno APIキーを入力してください"}), 400

    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        resp = requests.get(
            f"{SUNO_BASE_URL}/generate/record-info",
            params={"taskId": task_id},
            headers=headers,
            timeout=15,
        )
    except requests.RequestException as e:
        return jsonify({"error": f"通信エラー: {str(e)}"}), 500

    if resp.status_code != 200:
        return (
            jsonify({"error": f"APIエラー ({resp.status_code}): {resp.text}"}),
            resp.status_code,
        )

    result = resp.json()
    if result.get("code") != 200:
        return jsonify({"error": result.get("msg", "ステータス取得に失敗しました")}), 500

    return jsonify(result["data"])


@app.route("/api/generate-mv", methods=["POST"])
def generate_mv():
    data = request.get_json()
    music_id = data.get("music_id", "").strip()
    music_index = data.get("music_index", 0)
    api_key = data.get("api_key", "").strip() or SUNO_API_KEY

    if not music_id:
        return jsonify({"error": "music_idが指定されていません"}), 400
    if not api_key:
        return jsonify({"error": "Suno APIキーを入力してください"}), 400

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "taskId": music_id,
        "musicIndex": music_index,
        "callBackUrl": "https://example.com/callback",
    }

    try:
        resp = requests.post(
            f"{SUNO_BASE_URL}/mp4/generate",
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.RequestException as e:
        return jsonify({"error": f"通信エラー: {str(e)}"}), 500

    if resp.status_code != 200:
        return (
            jsonify({"error": f"APIエラー ({resp.status_code}): {resp.text}"}),
            resp.status_code,
        )

    result = resp.json()
    if result.get("code") != 200:
        return jsonify({"error": result.get("msg", "MV生成リクエストに失敗しました")}), 500

    task_id = result["data"]["taskId"]
    return jsonify({"task_id": task_id})


@app.route("/api/mv-status")
def get_mv_status():
    task_id = request.args.get("task_id", "")
    api_key = request.args.get("api_key", "").strip() or SUNO_API_KEY

    if not task_id:
        return jsonify({"error": "task_idが指定されていません"}), 400
    if not api_key:
        return jsonify({"error": "Suno APIキーを入力してください"}), 400

    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        resp = requests.get(
            f"{SUNO_BASE_URL}/mp4/record-info",
            params={"taskId": task_id},
            headers=headers,
            timeout=15,
        )
    except requests.RequestException as e:
        return jsonify({"error": f"通信エラー: {str(e)}"}), 500

    if resp.status_code != 200:
        return (
            jsonify({"error": f"APIエラー ({resp.status_code}): {resp.text}"}),
            resp.status_code,
        )

    result = resp.json()
    if result.get("code") != 200:
        return jsonify({"error": result.get("msg", "MVステータス取得に失敗しました")}), 500

    return jsonify(result["data"])


if __name__ == "__main__":
    app.run(debug=True, port=8080)
