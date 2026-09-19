import sys
import argparse
from booking.bot_runner import run_bot

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test booking runner')
    parser.add_argument('--booking-id', type=int, help='Booking ID from database')
    parser.add_argument('--email', type=str, default='test@example.com')
    parser.add_argument('--password', type=str, default='TestPassword123!')
    parser.add_argument('--passport', type=str, default='A12345678')
    parser.add_argument('--nationality', type=str, default='Egyptian')
    parser.add_argument('--dob', type=str, default='15/05/1990')
    parser.add_argument('--phone', type=str, default='01234567890')
    parser.add_argument('--image', type=str, default=None)
    parser.add_argument('--simulate', action='store_true', help='Run in simulation mode')

    args = parser.parse_args()

    success = run_bot(
        booking_id=args.booking_id,
        email=args.email,
        password=args.password,
        passport_number=args.passport,
        nationality=args.nationality,
        birth_date=args.dob,
        phone_number=args.phone,
        passport_image_path=args.image,
        simulate=args.simulate
    )
    print(f'Finished: Success = {success}')
