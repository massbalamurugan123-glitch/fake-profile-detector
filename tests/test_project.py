"""Run with:  python -m unittest discover -s tests -v   (from the project folder)"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
import detector

BASE = dict(
    username="priya_k", display_name="Priya Kumar", bio="Student. Loves travel.",
    followers=420, following=380, posts=55, age_months=40, mutual=12, avg_likes=40,
    has_photo=True, verified=False, private=False, has_link=False,
    asked_money=False, urgent=False, sent_link=False, claims_famous=False,
)


def profile(**changes):
    d = dict(BASE)
    d.update(changes)
    return d


class ScoringTests(unittest.TestCase):
    def test_normal_profile_is_real(self):
        r = detector.analyze_profile(profile())
        self.assertEqual(r["level"], "real")
        self.assertEqual(r["score"], 0)

    def test_obvious_fake_is_fake(self):
        fake = profile(
            username="jenny88231904", display_name="Official Support Team", bio="DM me for crypto giveaway! Earn money",
            followers=12000, following=4000, posts=0, age_months=0, mutual=0, avg_likes=None,
            has_photo=False, asked_money=True, sent_link=True,
        )
        r = detector.analyze_profile(fake)
        self.assertEqual(r["level"], "fake")
        self.assertGreaterEqual(r["score"], 80)

    def test_asking_for_money_alone_is_suspicious_or_worse(self):
        r = detector.analyze_profile(profile(asked_money=True))
        self.assertIn(r["level"], ("suspicious", "fake"))

    def test_score_is_clamped(self):
        r = detector.analyze_profile(profile(age_months=0, posts=0, has_photo=False, asked_money=True,
                                             urgent=True, sent_link=True, bio="crypto giveaway lottery",
                                             followers=20000, following=9000, mutual=0))
        self.assertLessEqual(r["score"], 100)
        self.assertGreaterEqual(r["score"], 0)

    def test_good_signs_never_go_below_zero(self):
        r = detector.analyze_profile(profile(verified=True))
        self.assertEqual(r["score"], 0)

    def test_low_engagement_flagged(self):
        r = detector.analyze_profile(profile(followers=50000, following=100, avg_likes=3))
        titles = [f["title"] for f in r["findings"]]
        self.assertIn("Very low engagement", titles)


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.DB_PATH = os.path.join(tempfile.mkdtemp(), "test.db")
        import app as app_module
        database.init_db()
        cls.app = app_module.app
        cls.app.testing = True

    def setUp(self):
        self.client = self.app.test_client()

    def form(self, **extra):
        data = {"platform": "Instagram", "username": "test_user", "display_name": "Test User", "bio": "hello",
                "followers": "100", "following": "100", "posts": "10", "age_months": "12"}
        data.update(extra)
        return data

    def test_pages_load(self):
        for url in ("/", "/history", "/tips", "/about"):
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_submit_and_view_result(self):
        r = self.client.post("/analyze", data=self.form(), follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"risk out of 100", r.data)
        self.assertIn(b"What you should do", r.data)

    def test_validation_errors(self):
        r = self.client.post("/analyze", data=self.form(username="", followers="abc"))
        self.assertEqual(r.status_code, 400)
        self.assertIn(b"Username is required", r.data)

    def test_api(self):
        r = self.client.post("/api/analyze", json={"username": "bot99999999", "followers": 5, "following": 3000,
                                                   "posts": 0, "age_months": 0, "asked_money": True})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["level"], "fake")

    def test_delete_check(self):
        self.client.post("/analyze", data=self.form(username="to_delete"))
        r = self.client.post("/history/1/delete", follow_redirects=True)
        self.assertEqual(r.status_code, 200)

    def test_missing_result_404(self):
        self.assertEqual(self.client.get("/result/99999").status_code, 404)


if __name__ == "__main__":
    unittest.main()
