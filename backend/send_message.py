import os
from twilio.rest import Client
from dotenv import load_dotenv
from process_schedule import format_schedule_message, filter_upcoming_games
from fetch_schedule import fetch_warriors_schedule

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_MESSAGING_SERVICE_SID = os.getenv("TWILIO_MESSAGING_SERVICE_SID")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")

def send_sms():
    """Fetches the Warriors schedule and sends it as an SMS using Twilio."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        raw_games = fetch_warriors_schedule()
        upcoming_games = filter_upcoming_games(raw_games)
        message_body = format_schedule_message(upcoming_games)

        if not upcoming_games:
            print("No upcoming games in the next 7 days.")
            return

        message = client.messages.create(
            messaging_service_sid=TWILIO_MESSAGING_SERVICE_SID,
            body=message_body,
            to=RECIPIENT_PHONE_NUMBER
        )

        print(f"Message sent successfully! SID: {message.sid}")

    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    send_sms()