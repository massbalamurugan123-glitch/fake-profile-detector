"""tips.py - all the safety advice shown in the app."""

# Tips that are chosen automatically depending on which warning signs were found
FLAG_TIPS = {
    "username": "Search the username on other platforms. Real people usually use a similar name in several places.",
    "impersonation": "Compare this profile with the real one: ask a friend, check the official website, and look for the verified badge inside the app.",
    "photo": "Be careful with profiles that hide behind no photo. Ask for a normal video call or meet through a mutual friend before trusting them.",
    "scam": "Ignore offers of easy money, giveaways, crypto, trading or loans. If it sounds too good to be true, it is.",
    "new": "Be extra careful with brand-new accounts. Wait, watch how the account behaves, and do not share personal details.",
    "empty": "An account with no posts has no track record. Do not trust it with private information.",
    "bought": "Fake followers are easy to buy. Look at who comments and whether the comments sound real, not just the numbers.",
    "bot": "Accounts that follow thousands of people are usually bots. Do not follow back or click their links.",
    "mutual": "Check whether friends you trust actually know this person before accepting the request.",
    "money": "Never send money, gift cards, OTPs, passwords or bank details to someone you only know online. Stop talking and report the account.",
    "urgent": "Scammers create panic. Real people will wait while you verify. Take a break and talk to a family member or teacher.",
    "link": "Do not open unknown links or files. They can steal your passwords. Hover or long-press to see where a link really goes.",
}

# Tips shown to everybody, grouped for the Safety tips page
GENERAL_TIPS = [
    {
        "title": "Before you accept a request",
        "items": [
            "Ask yourself: do I know this person in real life? If not, think twice.",
            "Open the profile. Check the photo, the posts, the date it was created and who follows it.",
            "Look for mutual friends. A profile with no common connections is a warning sign.",
            "Search the person's name and photo on Google to see if they appear somewhere else.",
            "Be careful if a stranger sends a request and immediately starts a private chat.",
        ],
    },
    {
        "title": "Protect your own account",
        "items": [
            "Use a strong, unique password for each app (12+ characters, mix of words, numbers and symbols).",
            "Turn on two-factor authentication (2FA) everywhere it is offered.",
            "Make your account private and review who can see your posts, stories and friend list.",
            "Never share your OTP, password or backup codes with anyone, even if they say they are support staff.",
            "Do not post your phone number, home address, school timetable or live location.",
        ],
    },
    {
        "title": "Spot the common scams",
        "items": [
            "Fake celebrity or brand accounts offering giveaways, prizes or verification badges.",
            "Romance or friendship scams where a stranger builds trust and then asks for money.",
            "Fake job or internship offers that ask you to pay a fee first.",
            "Messages with links saying 'Is this you in this video?' or 'You won, click here'.",
            "Cloned accounts: a copy of your real friend's profile asking you for urgent money.",
        ],
    },
    {
        "title": "Protect your photos",
        "items": [
            "Photos you post can be copied to make fake profiles. Keep your account private if you can.",
            "Avoid sharing photos with your school uniform, ID cards, tickets or house number visible.",
            "Never send private pictures to someone you have not met. They can be used to blackmail you.",
            "If your photo is being misused, take screenshots and report it to the platform.",
        ],
    },
    {
        "title": "If something goes wrong",
        "items": [
            "Stop replying, then block and report the account inside the app.",
            "Save screenshots of the chat, profile and any payment details as proof.",
            "Change your passwords right away if you clicked a strange link.",
            "Tell a trusted adult, teacher or friend. You are not in trouble for being targeted.",
            "In India, report cyber fraud at cybercrime.gov.in or call the helpline 1930. Elsewhere, use your national cybercrime portal.",
        ],
    },
]

# Always appended to the results page
UNIVERSAL_TIPS = [
    "Verify through a second channel (a phone call or a mutual friend) before trusting an online profile.",
    "Report fake accounts to the platform - it protects other people too.",
]
