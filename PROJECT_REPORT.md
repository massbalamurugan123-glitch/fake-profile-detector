# Fake Profile Detector and Safety Tips
First Year Project - B.Sc Artificial Intelligence & Machine Learning

## 1. Abstract
Fake social media profiles are used for scams, impersonation and harassment. This project is a web application
that collects the details of a profile (username, name, bio, followers, following, posts, account age, mutual
connections, engagement and suspicious behaviour), analyses them with explainable rules, and shows a risk score
from 0 to 100 with a verdict (Likely real, Suspicious, Likely fake). It lists the reasons behind the score and gives
personalised safety tips. All checks are saved in a database so they can be reviewed later.

## 2. Objectives
1. Collect profile information through a simple, validated web form.
2. Identify whether a profile is real or fake using measurable warning signs.
3. Explain the result so the user learns what to look for.
4. Educate users with clear safety tips related to what was found.

## 3. Technologies
| Part | Tool | Why |
|---|---|---|
| Backend | Python, Flask | Simple web framework, easy to explain |
| Database | SQLite | No installation needed, stores history |
| Frontend | HTML, CSS, JavaScript | Responsive pages and form helpers |

## 4. System design
```
User -> Web form (HTML/JS) -> Flask (app.py) -> validate input
                                   |-> detector.analyze_profile()  (rules -> score, verdict, reasons)
                                   |-> tips (matched to warnings)
                                   |-> database.save_check()       (SQLite)
                                   -> Result page: score, reasons, tips
```

## 5. Modules
- **Input module** - form on the home page with browser and server-side validation.
- **Scoring module** - rule table; each rule adds or removes points; total limited to 0-100.
- **Tips module** - tips chosen from the warnings found, plus a general Safety tips page.
- **History module** - list, open and delete earlier checks.
- **API module** - JSON endpoint `/api/analyze` for testing.

## 6. Algorithm
1. Read and clean the form data.
2. Start with score = 0. For every rule that matches, add (warning) or subtract (good sign) its points.
3. Limit the score to 0-100. If the profile asked for money, OTP or bank details the score is at least 40
   (the account may be hacked or cloned).
4. Verdict: 0-25 Likely real, 26-54 Suspicious, 55-100 Likely fake.
5. Build the list of reasons and tips, save everything, show the result.

### Main rules
| Rule | Points |
|---|---|
| Asked for money / OTP / bank details | +30 |
| Scam words in bio, strange link, pressure to act fast, follows thousands but few follow back, huge followers in a new account | +15 each |
| No profile photo, account under 1 month old | +15 each |
| Auto-generated username, zero posts, very low engagement | +12 each |
| Account 2+ years old | -10 |
| Verified badge | -15 |
| Active posting (30+ posts), healthy engagement, 5+ mutual connections | -8 each |

## 7. Test cases
| # | Input | Expected result |
|---|---|---|
| 1 | Old account, 55 posts, mutual friends, normal numbers | Likely real, score 0 |
| 2 | New account, no photo, 0 posts, crypto giveaway bio, asked for money | Likely fake |
| 3 | Good account that asks for money | At least Suspicious (score 40+) |
| 4 | 50,000 followers but average likes 3 | "Very low engagement" shown |
| 5 | Empty username or text in a number box | Error message, no result |
| 6 | Open a result that does not exist | 404 page |

Automated tests are in `tests/test_project.py`.

## 8. Limitations
- Rule-based: a real person can look suspicious and a careful fake can look real.
- Details are entered manually; the system does not read social media sites.
- The profile photo itself is not analysed.

## 9. Future scope
Train a machine learning classifier on a public fake-profile dataset, add reverse image search,
user accounts, and a browser extension.

## 10. Conclusion
A rule-based scoring system inside a full stack web application can help people judge online profiles
and learn safe habits.
