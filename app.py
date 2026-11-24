"""
app.py - Flask web server for the Fake Profile Detector.

Run:   python app.py
Open:  http://127.0.0.1:5000
"""
import os
from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for

import database
import detector
from tips import FLAG_TIPS, GENERAL_TIPS, UNIVERSAL_TIPS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLATFORMS = ["Instagram", "Facebook", "X (Twitter)", "LinkedIn", "Snapchat", "WhatsApp", "Telegram", "Other"]

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-real-use")

database.init_db()


# ---------------------------------------------------------------- helpers
def to_int(value, label, errors, minimum=0, maximum=1_000_000_000, required=True):
    value = (value or "").strip()
    if value == "":
        if required:
            errors.append(f"{label} is required.")
        return None if not required else 0
    try:
        number = int(value)
    except ValueError:
        errors.append(f"{label} must be a whole number.")
        return 0
    if number < minimum or number > maximum:
        errors.append(f"{label} must be between {minimum} and {maximum}.")
        return 0
    return number


def parse_form(form):
    """Validate the form. Returns (clean_data, errors)."""
    errors = []
    platform = form.get("platform", "Other")
    if platform not in PLATFORMS:
        platform = "Other"

    username = form.get("username", "").strip().lstrip("@")
    if not username:
        errors.append("Username is required.")
    elif len(username) > 60:
        errors.append("Username is too long.")

    data = {
        "platform": platform,
        "username": username,
        "display_name": form.get("display_name", "").strip()[:80],
        "bio": form.get("bio", "").strip()[:500],
        "followers": to_int(form.get("followers"), "Followers", errors),
        "following": to_int(form.get("following"), "Following", errors),
        "posts": to_int(form.get("posts"), "Posts", errors),
        "age_months": to_int(form.get("age_months"), "Account age", errors, maximum=600),
        "mutual": to_int(form.get("mutual"), "Mutual connections", errors, required=False) or 0,
        "avg_likes": to_int(form.get("avg_likes"), "Average likes", errors, required=False),
    }
    for flag in ("has_photo", "verified", "private", "has_link",
                 "asked_money", "urgent", "sent_link", "claims_famous"):
        data[flag] = form.get(flag) == "on"
    return data, errors


def build_tips(result):
    tips, seen = [], set()
    for f in result["findings"]:
        key = f.get("tip_key")
        if f["kind"] != "good" and key and key not in seen and key in FLAG_TIPS:
            seen.add(key)
            tips.append(FLAG_TIPS[key])
    return tips + UNIVERSAL_TIPS


def run_check(data):
    """Score the profile and attach the safety tips."""
    result = detector.analyze_profile(data)
    result["tips"] = build_tips(result)
    return result


# ---------------------------------------------------------------- pages
@app.route("/")
def index():
    return render_template("index.html", form={}, platforms=PLATFORMS)


@app.route("/analyze", methods=["POST"])
def analyze():
    data, errors = parse_form(request.form)
    if errors:
        for e in errors:
            flash(e)
        return render_template("index.html", form=request.form, platforms=PLATFORMS), 400
    result = run_check(data)
    check_id = database.save_check(data, result)
    return redirect(url_for("result", check_id=check_id))


@app.route("/result/<int:check_id>")
def result(check_id):
    check = database.get_check(check_id)
    if check is None:
        abort(404)
    return render_template("result.html", check=check, r=check["result"])


@app.route("/history")
def history():
    return render_template("history.html", checks=database.list_checks(), stats=database.stats())


@app.route("/history/<int:check_id>/delete", methods=["POST"])
def delete(check_id):
    database.delete_check(check_id)
    flash("Check deleted.")
    return redirect(url_for("history"))


@app.route("/tips")
def tips():
    return render_template("tips.html", groups=GENERAL_TIPS)


@app.route("/about")
def about():
    return render_template("about.html", real_max=detector.LIKELY_REAL_MAX, susp_max=detector.SUSPICIOUS_MAX)


# ---------------------------------------------------------------- JSON API
@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """Same checker, JSON in / JSON out. Handy for testing with Postman."""
    payload = request.get_json(silent=True) or {}
    data, errors = parse_form({k: ("on" if v is True else str(v)) for k, v in payload.items() if v is not None})
    if errors:
        return jsonify({"errors": errors}), 400
    return jsonify(run_check(data))


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
