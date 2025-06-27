from booking.bot_runner import run_bot

if __name__ == "__main__":
    email = "your_email@example.com"
    password = "your_password"
    success = run_bot(email, password)
    print("Success:", success)
