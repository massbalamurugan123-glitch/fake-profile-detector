"""
detector.py
-----------
The "brain" of the project.

analyze_profile() turns the profile details the user typed into a risk score
(0-100), a verdict (Likely real / Suspicious / Likely fake) and a list of reasons.
Every rule is simple and explainable: warning signs add points, good signs remove points.

IMPORTANT: this is a rule-based screening tool. It gives a risk estimate,
not a proof. A real person can look "suspicious" and a clever fake can look "real".
"""

import difflib
import re
from dataclasses import dataclass, asdict
from typing import Optional


# --------------------------------------------------------------------------
# Settings you can tune
# --------------------------------------------------------------------------
LIKELY_REAL_MAX = 25      # score 0-25   -> Likely real
SUSPICIOUS_MAX = 54       # score 26-54  -> Suspicious, 55+ -> Likely fake
ASKED_MONEY_FLOOR = 40    # minimum score when the profile asked for money / OTP / bank details

SPAM_WORDS = [
    "giveaway", "dm for", "dm me", "crypto", "bitcoin", "forex", "trading signals",
    "earn money", "make money", "earn $", "investment", "100% profit", "guaranteed",
    "double your", "click link", "whatsapp me", "telegram", "cash app", "sugar",
    "onlyfans", "loan", "lottery", "winner", "free followers", "work from home",
]


# --------------------------------------------------------------------------
# Profile scoring
# --------------------------------------------------------------------------
@dataclass
class Finding:
    kind: str       # "risk", "good" or "info"
    points: int     # risk points added (+) or removed (-)
    title: str
    detail: str
    tip_key: Optional[str] = None


def _letters_only(text: str) -> str:
    return re.sub(r"[^a-z]", "", text.lower())


def analyze_profile(data: dict) -> dict:
    """
    data keys (all already cleaned by app.py):
      username, display_name, bio, followers, following, posts, age_months,
      mutual, avg_likes (None if unknown), has_photo, verified, private, has_link,
      asked_money, urgent, sent_link, claims_famous
    """
    findings = []

    def add(kind, points, title, detail, tip=None):
        findings.append(Finding(kind, points, title, detail, tip))

    username = data["username"]
    display = data.get("display_name", "")
    bio = data.get("bio", "")
    followers, following, posts = data["followers"], data["following"], data["posts"]
    age = data["age_months"]

    # ---- Username & name ----------------------------------------------------
    digits = sum(c.isdigit() for c in username)
    trailing = re.search(r"\d+$", username)
    if len(username) > 0 and (digits / len(username) > 0.4 or (trailing and len(trailing.group()) >= 5)):
        add("risk", 12, "Username looks auto-generated",
            "It has a lot of random numbers. Bots and mass-made accounts often look like this.", "username")

    name_a, name_b = _letters_only(display), _letters_only(username)
    if name_a and name_b:
        similarity = difflib.SequenceMatcher(None, name_a, name_b).ratio()
        contained = name_b in name_a or name_a in name_b
        first = name_a[:4] in name_b if len(name_a) >= 4 else False
        if similarity < 0.3 and not contained and not first:
            add("risk", 5, "Name and username do not match",
                "The display name and the username have nothing in common. This is common for fakes that copy a name.", "impersonation")

    # ---- Profile completeness ----------------------------------------------
    if not data["has_photo"]:
        add("risk", 15, "No profile photo", "Fake and throw-away accounts often skip the photo.", "photo")
    if not bio.strip():
        add("risk", 6, "Empty bio", "Real people usually write at least a few words about themselves.")

    lowered = bio.lower()
    spam_hits = [w for w in SPAM_WORDS if w in lowered]
    if spam_hits:
        add("risk", 15, "Spam or scam words in the bio",
            "Found: " + ", ".join(spam_hits[:4]) + ". These are typical of money or promotion scams.", "scam")

    # ---- Age, activity, followers -------------------------------------------
    if age < 1:
        add("risk", 15, "Account is less than 1 month old", "Brand-new accounts are the most common type of fake.", "new")
    elif age < 3:
        add("risk", 10, "Very new account (under 3 months)", "New accounts deserve extra care.", "new")
    elif age >= 24:
        add("good", -10, "Account is 2+ years old", "Long-lived accounts are less likely to be throw-away fakes.")

    if posts == 0:
        add("risk", 12, "No posts at all", "An account with zero posts has no history to trust.", "empty")
    elif followers >= 5000 and posts < 5:
        add("risk", 10, "Many followers but almost no posts",
            "Big following with so little content can mean bought followers.", "bought")
    elif posts >= 30:
        add("good", -8, "Active posting history", f"{posts} posts shows real, ongoing activity.")

    if following >= 1500 and followers < following * 0.1:
        add("risk", 15, "Follows thousands but few follow back",
            f"Following {following} while only {followers} follow back is typical of follow-spam bots.", "bot")

    if age < 3 and followers > 10000:
        add("risk", 15, "Huge follower count in a very short time",
            "Gaining over 10,000 followers in under 3 months is rarely natural.", "bought")

    avg_likes = data.get("avg_likes")
    if avg_likes is not None and followers >= 1000:
        rate = avg_likes / followers
        if rate < 0.002:
            add("risk", 12, "Very low engagement",
                f"About {rate * 100:.2f}% of followers react to posts. Real accounts are usually much higher.", "bought")
        elif rate >= 0.01:
            add("good", -8, "Healthy engagement", f"About {rate * 100:.1f}% of followers react to posts.")

    # ---- Trust signals --------------------------------------------------------
    if data["verified"]:
        add("good", -15, "Verified badge ticked",
            "Always confirm the badge yourself inside the app - fakes can copy a badge in the photo or name.")
    if data["mutual"] == 0:
        add("risk", 5, "No mutual connections", "You share no friends or followers with this profile.", "mutual")
    elif data["mutual"] >= 5:
        add("good", -8, "Several mutual connections", f"You share {data['mutual']} connections.")

    # ---- Behaviour red flags --------------------------------------------------
    if data["asked_money"]:
        add("risk", 30, "Asked for money, gift cards, OTP or bank details",
            "This is the number one sign of a scam. Never send money or codes to someone you only know online.", "money")
    if data["urgent"]:
        add("risk", 15, "Pressure or urgency", "Scammers rush you so you do not have time to think.", "urgent")
    if data["sent_link"]:
        add("risk", 15, "Sent a strange link or file", "Unknown links can steal passwords or install malware.", "link")
    if data["claims_famous"] and not data["verified"]:
        add("risk", 10, "Claims to be a celebrity or brand but is not verified",
            "Fans and customers are often targeted by fake celebrity or brand accounts.", "impersonation")
    if data["has_link"] and age < 3:
        add("risk", 6, "External link on a very new account", "New accounts pushing outside links are often promoting scams.", "link")

    # ---- Final score --------------------------------------------------------------
    score = max(0, min(100, sum(f.points for f in findings)))
    # Safety floor: asking for money is dangerous even on an old, active account
    # (it may be a hacked or cloned account), so it can never look "real".
    if data["asked_money"]:
        score = max(score, ASKED_MONEY_FLOOR)
    if score <= LIKELY_REAL_MAX:
        level, verdict = "real", "Likely real"
        summary = "Few warning signs were found. Stay careful anyway - no tool can be 100% sure."
    elif score <= SUSPICIOUS_MAX:
        level, verdict = "suspicious", "Suspicious"
        summary = "Several warning signs were found. Do not share personal details until you can verify this person another way."
    else:
        level, verdict = "fake", "Likely fake"
        summary = "Many strong warning signs were found. Avoid this profile, do not send money or information, and consider reporting it."

    # Findings that add risk first (largest first), then good signs
    ordered = sorted(findings, key=lambda f: (f.kind == "good", -f.points))
    return {
        "score": score,
        "level": level,
        "verdict": verdict,
        "summary": summary,
        "findings": [asdict(f) for f in ordered],
    }
