import json
from django.utils import timezone
from django.conf import settings
from pywebpush import webpush, WebPushException

from .models import ListPushSubscription

def notify_subscribers_about_update(shopping_list):
    try:
        raw_timestamp = timezone.now().isoformat()
        
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
                    # Device unsubscribed or token expired, safe to delete
                    sub.delete()
                else:
                    # Log WebPush specific errors (e.g., 400 Bad Request, 401 Unauthorized)
                    print(f"WebPush error for {sub.endpoint}: {ex}")
            except Exception as e:
                # Catch any cryptography or formatting errors for a specific subscription
                print(f"Failed to send push to {sub.endpoint}: {e}")
    
    except Exception as e:
        # Catch any global errors (like missing settings) so the main Admin save doesn't crash!
        print(f"Critical error in notify_subscribers_about_update: {e}")