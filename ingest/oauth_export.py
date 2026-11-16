import os
import json
import time
import secrets
import hashlib
from urllib.parse import urlencode
import requests
from flask import Flask, redirect, request, session, jsonify
from dotenv import load_dotenv; load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Replace these with your actual TikTok Developer Portal keys
CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "YOUR_TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "YOUR_TIKTOK_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:3000/callback"

# Split URLs so nothing strips paths on copy-paste
TIKTOK_WEB = "www" + "." + "tiktok" + "." + "com"
API_HOST = "open" + "." + "tiktokapis" + "." + "com"

AUTH_BASE_URL = "https://" + TIKTOK_WEB + "/v2" + "/auth" + "/authorize/"
TOKEN_API_URL = "https://" + API_HOST + "/v2" + "/oauth" + "/token/"
USER_INFO_URL = "https://" + API_HOST + "/v2" + "/user" + "/info/"
VIDEO_LIST_URL = "https://" + API_HOST + "/v2" + "/video" + "/list/"


def generate_pkce_pair():
    verifier = secrets.token_urlsafe(48)[:64]
    challenge = hashlib.sha256(verifier.encode("utf-8")).hexdigest()
    return verifier, challenge


def fetch_videos(access_token, limit=2000):
    all_videos = []
    cursor = None
    has_more = True

    fields = (
        "id,create_time,cover_image_url,share_url,video_description,"
        "duration,height,width,title,embed_html,embed_link,"
        "like_count,comment_count,share_count,view_count"
    )

    while has_more and len(all_videos) < limit:
        payload = {"max_count": 20}
        if cursor is not None:
            payload["cursor"] = cursor

        res = requests.post(
            VIDEO_LIST_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            params={"fields": fields},
            json=payload,
            timeout=15,
        )

        if res.status_code == 429:
            print(">>> Rate limited (429). Sleeping 5 seconds...")
            time.sleep(5)
            continue

        body = res.json()
        error = body.get("error", {})
        if error.get("code") != "ok":
            print(">>> API Error:", body)
            break

        data = body.get("data", {})
        videos = data.get("videos", [])
        all_videos.extend(videos)

        cursor = data.get("cursor")
        has_more = data.get("has_more", False)

        print(f">>> Fetched {len(all_videos)} / {limit} videos (has_more={has_more})...")
        time.sleep(0.15)

    return all_videos[:limit]


@app.route("/")
def home():
    return '<a href="/login">Log in with TikTok & Export 2,000 Videos</a>'


@app.route("/login")
def login():
    state = secrets.token_urlsafe(16)
    code_verifier, code_challenge = generate_pkce_pair()

    session["oauth_state"] = state
    session["code_verifier"] = code_verifier

    params = {
        "client_key": CLIENT_KEY,
        "scope": "user.info.basic,video.list",
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = f"{AUTH_BASE_URL}?{urlencode(params)}"
    return redirect(auth_url)


@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return jsonify({
            "step": "tiktok_authorize_error",
            "error": error,
            "description": request.args.get("error_description"),
        }), 400

    returned_state = request.args.get("state")
    if not returned_state or returned_state != session.get("oauth_state"):
        return jsonify({"step": "state_mismatch"}), 400

    code = request.args.get("code")
    code_verifier = session.pop("code_verifier", None)
    if not code or not code_verifier:
        return jsonify({"step": "missing_code_or_verifier"}), 400

    # 1. Exchange code for tokens
    token_res = requests.post(
        TOKEN_API_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
        },
        timeout=15,
    )
    token_data = token_res.json()

    if "access_token" not in token_data:
        return jsonify({"step": "token_exchange_failed", "details": token_data}), 400

    # Save tokens to disk so you can reuse them without logging in again
    with open("tokens.json", "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)

    access_token = token_data["access_token"]

    # 2. Fetch up to 2,000 videos and export to videos.json
    videos = fetch_videos(access_token, limit=2000)
    with open("videos.json", "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

    return jsonify({
        "status": "success",
        "total_videos_exported": len(videos),
        "videos_file": os.path.abspath("videos.json"),
        "tokens_file": os.path.abspath("tokens.json"),
        "sample_first_video": videos[0] if videos else None,
    })


if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=True)
