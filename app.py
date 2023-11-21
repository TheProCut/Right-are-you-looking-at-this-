import os
import requests
import base64
import time
from flask import Flask, redirect, render_template_string, request, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
REDIRECT_URI = os.environ['REDIRECT_URI']
DISCORD_API_URL = "https://discord.com/api"

authurl1 = os.environ['REDIRECT_AUTH_URL_1']
authurl2 = os.environ['REDIRECT_AUTH_URL_2']
authurl3 = os.environ['REDIRECT_AUTH_URL_3']
authurl4 = os.environ['REDIRECT_AUTH_URL_4']
authurl5 = os.environ['REDIRECT_AUTH_URL_5']


@app.route("/")
def home():
    if "discord_token" in session:
        discord_user = get_discord_user()
        playerid = str(discord_user["id"])
        playerid_bytes = playerid.encode("ascii")

        base64_bytes = base64.b64encode(playerid_bytes)
        base64_string = base64_bytes.decode("ascii")

        return redirect(
            f"{authurl1}{base64_string}{authurl2}{base64_bytes}{authurl3}{playerid}{authurl4}{discord_user['username']}{authurl5}{discord_user['global_name']}"
        )
    else:
        return redirect(
            f"{DISCORD_API_URL}/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
        )

@app.route("/logout")
def logout():
    session.pop("discord_token", None)
    return redirect("https://bloxco.org/")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(f"{DISCORD_API_URL}/oauth2/token",
                             data=data,
                             headers=headers)
    token_data = response.json()
    session["discord_token"] = token_data["access_token"]
    return redirect("/")

def get_discord_user():
    headers = {"Authorization": f"Bearer {session['discord_token']}"}
    response = requests.get(f"{DISCORD_API_URL}/users/@me", headers=headers)
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
