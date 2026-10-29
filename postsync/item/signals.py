# import requests
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Item

# # MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/o27xsc8nnggo9b6jpjph0f3rni1sl5z6"  #2005 email# replace with your Make URL
# MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/okrzo3dipv2rtcewfecgm3oi7gpynj9a" #702 email
# @receiver(post_save, sender=Item)
# def send_to_make(sender, instance, created, **kwargs):
#     if created:
#         data = {
#             "name": instance.name,
#             "description": instance.description or "",
#             "price": instance.price,
#             "image_url": instance.image.url if instance.image else "",
#         }
#         print(f"Data uploaded to Cloudinary")
#         try:
#             requests.post(MAKE_WEBHOOK_URL, json=data)
#             print(f"Sent '{instance.name}' to Make webhook")
#         except Exception as e:
#             print(f"Failed to send to Make: {e}")

# import requests
# import time
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Item

# MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/okrzo3dipv2rtcewfecgm3oi7gpynj9a" #702 email

# @receiver(post_save, sender=Item)
# def send_to_make(sender, instance, created, **kwargs):
#     if created:
#         # Wait a short moment to ensure the image is uploaded
#         time.sleep(10)  # delay in seconds; adjust if needed

#         data = {
#             "name": instance.name,
#             "description": instance.description or "",
#             "price": instance.price,
#             "image_url": instance.image.url if instance.image else "https://res.cloudinary.com/dv6pddv1p/image/upload/v1764142768/pyelqs3mmcikljlzcbjt.jpg",
#         }
#         print(f"Data ready for Make webhook")

#         try:
#             requests.post(MAKE_WEBHOOK_URL, json=data)
#             print(f"Sent '{instance.name}' to Make webhook")
#         except Exception as e:
#             print(f"Failed to send to Make: {e}")
import requests
import time
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Item

# MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/okrzo3dipv2rtcewfecgm3oi7gpynj9a"
MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/okrzo3dipv2rtcewfecgm3oi7gpynj9a"
# Fallback image URL if the item has no image
FALLBACK_IMAGE_URL = "https://res.cloudinary.com/dv6pddv1p/image/upload/v1764142768/pyelqs3mmcikljlzcbjt.jpg"

@receiver(post_save, sender=Item)
def send_to_make(sender, instance, created, **kwargs):
    if created:
        # Wait a moment to make sure the image is uploaded
        time.sleep(5)  # adjust delay as needed

        # Use the item's image URL if available, otherwise fallback
        image_url = instance.image.url if instance.image and instance.image.url else FALLBACK_IMAGE_URL

        data = {
            "name": instance.name or "Unnamed Item",
            "description": instance.description or "",
            "price": float(instance.price or 0),
            "image_url": image_url,
        }

        print(f"Sending data to Make webhook: {data}")

        try:
            response = requests.post(MAKE_WEBHOOK_URL, json=data)
            response.raise_for_status()
            print(f"Sent '{instance.name}' to Make webhook successfully")
        except Exception as e:
            print(f"Failed to send to Make: {e}")
