from booking.bot_runner import run_bot
from datetime import datetime

if __name__ == "__main__":
    email = "mohamedmordi69@gmail.com"
    password = "ZZZzzzCCCccc123456!@#"
    passport_number = "A12345678"
    nationality = "Egyptian"
    birth_date = "15/05/1990"  
    phone_number = "01234567890"
    passport_image_path = "E:\\image (2).png"  

    success = run_bot(
        email=email,
        password=password,
        passport_number=passport_number,
        nationality=nationality,
        birth_date=birth_date,
        phone_number=phone_number,
        passport_image_path=passport_image_path
    )
    print("Success:", success)
