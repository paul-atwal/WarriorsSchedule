import schedule
import time
from send_message import send_sms

def job():
    print("📅 Running weekly schedule job...")
    send_sms()

# Schedule to run every Monday at 9:00 AM PST
schedule.every().monday.at("09:00").do(job)

print("Scheduler started. The message will be sent every Monday at 9:00 AM PST.")

while True:
    schedule.run_pending()
    time.sleep(60)  