from concurrent.futures import ThreadPoolExecutor
from booking.bot_runner import run_bot

accounts = [
    ("email1@example.com", "password1"),
    ("email2@example.com", "password2"),
    ("email3@example.com", "password3"),
    # ...
    ("email40@example.com", "password40"),
]

def run_for_account(account):
    email, password = account
    print(f"🚀 Starting login for: {email}")
    result = run_bot(email, password)
    print(f"✅ Done with {email} → Success: {result}")

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=40) as executor:
        executor.map(run_for_account, accounts)
