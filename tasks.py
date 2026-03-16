from rq.decorators import job
from redis import Redis
import os
import time
from datetime import datetime

redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))


@job('notifications', connection=redis_conn)
def send_notification(notification_id, email, message):
    print(f"[Sending] Notification {notification_id} to {email}...")

    time.sleep(3)

    sent_at = datetime.utcnow().isoformat() + "Z"
    print(f"[Sent] Notification {notification_id} at {sent_at}")

    return {
        "notification_id": notification_id,
        "email": email,
        "status": "sent",
        "sent_at": sent_at
    }
