from apscheduler.schedulers.background import BackgroundScheduler
from telegram_bot import check_expiring_members

def start_scheduler(app):
    """Start background scheduler for daily telegram alerts"""
    scheduler = BackgroundScheduler()
    
    # Check setiap hari jam 09:00 pagi
    scheduler.add_job(
        func=lambda: check_expiring_members(app),
        trigger="cron",
        hour=9,
        minute=0,
        id='daily_expiry_check'
    )
    
    # Check setiap hari jam 17:00 sore
    scheduler.add_job(
        func=lambda: check_expiring_members(app),
        trigger="cron",
        hour=17,
        minute=0,
        id='evening_expiry_check'
    )
    
    scheduler.start()
    print("✅ Scheduler started - Daily check at 09:00 & 17:00")
