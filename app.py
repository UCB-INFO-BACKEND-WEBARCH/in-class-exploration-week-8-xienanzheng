"""
Notification Service API - Starter (Synchronous)

This version sends notifications SYNCHRONOUSLY.
Each request blocks for 3 seconds while "sending" the notification.

YOUR TASK: Convert this to use rq for background processing!
"""

from flask import Flask, jsonify, request
import os
import time
import uuid
from datetime import datetime
from redis import Redis
from rq.job import Job
from tasks import send_notification

app = Flask(__name__)

# In-memory store for notifications
notifications = {}
redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))


def send_notification_sync(notification_id, email, message):
    """
    Send a notification (SLOW - blocks for 3 seconds!)

    In production, this would call an email service like Mailgun.
    We simulate the slow API with time.sleep().
    """
    print(f"[Sending] Notification {notification_id} to {email}...")

    # This is the problem - blocking for 3 seconds!
    time.sleep(3)

    sent_at = datetime.utcnow().isoformat() + "Z"
    print(f"[Sent] Notification {notification_id} at {sent_at}")

    return {
        "notification_id": notification_id,
        "email": email,
        "status": "sent",
        "sent_at": sent_at
    }


@app.route('/')
def index():
    return jsonify({
        "service": "Notification Service (Synchronous - SLOW!)",
        "endpoints": {
            "POST /notifications": "Send a notification (takes 3 seconds!)",
            "GET /notifications": "List all notifications",
            "GET /notifications/<id>": "Get a notification",
            "GET /jobs/<job_id>": "Get job status"
        }
    })


@app.route('/notifications', methods=['POST'])
def create_notification():
    """
    Send a notification.

    WARNING: This blocks for 3 seconds!
    The user has to wait while we "send" the notification.

    TODO: Convert this to use rq for background processing!
    """
    data = request.get_json()

    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400

    # Create notification record
    notification_id = str(uuid.uuid4())
    email = data['email']
    message = data.get('message', 'You have a new notification!')

    # THIS IS THE PROBLEM: We block here for 3 seconds!
    # The user can't do anything while we wait.
    # NOTE: This now queues a background job instead of blocking.
    job = send_notification.delay(notification_id, email, message)

    notification = {
        "id": notification_id,
        "email": email,
        "message": message,
        "status": "queued",
        "sent_at": None
    }
    notifications[notification_id] = notification

    return jsonify({"job_id": job.id}), 202


@app.route('/notifications', methods=['GET'])
def list_notifications():
    """List all notifications."""
    return jsonify({
        "notifications": list(notifications.values())
    })


@app.route('/notifications/<notification_id>', methods=['GET'])
def get_notification(notification_id):
    """Get a single notification."""
    notification = notifications.get(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    return jsonify(notification)

@app.route('/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status and result."""
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        return jsonify({"error": "Job not found"}), 404

    response = {
        "job_id": job.id,
        "status": job.get_status(),
        "result": job.result
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
