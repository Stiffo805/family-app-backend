import json
from django.utils import timezone
from django.conf import settings
from pywebpush import webpush, WebPushException

from .models import ListPushSubscription


def notify_subscribers_about_update(shopping_list):
    # Get the raw, timezone-aware current time (usually UTC internally)
    # and convert it to a standard ISO 8601 string so JavaScript easily understands it.
    raw_timestamp = timezone.now().isoformat()
    
    # We send raw data instead of a pre-formatted sentence
    payload = json.dumps({
        "title": "Aktualizacja listy zakupów",
        "list_title": shopping_list.title,
        "timestamp": raw_timestamp,
        "url": f"/family-app-frontend/shopping/lists/{shopping_list.id}"
    })
    
    subscriptions = ListPushSubscription.objects.filter(shopping_list=shopping_list)
    
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_ADMIN_EMAIL}
            )
        except WebPushException as ex:
            if ex.response and ex.response.status_code == 410:
                sub.delete()