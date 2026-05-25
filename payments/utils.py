import requests
from django.conf import settings


class KhaltiPayment:

    @staticmethod
    def initiate_payment(**data):
        payload = {
            "return_url": "http://127.0.0.1:8000/api/payments/callback/",
            "website_url": "http://localhost:3000/",
            "amount": int(float(data.get("amount"))) * 100,
            "purchase_order_id": str(data.get("donation_id")),
            "purchase_order_name": "Donation Payment",
            "customer_info": {
                "name": data.get("name"),
                "email": data.get("email"),
                "phone": data.get("phone"),
            }
        }

        headers = {
            "Authorization": f"key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            settings.KHALTI_INIT_URL,
            json=payload,
            headers=headers,
            timeout=30  
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def verify_payment(pidx):
        headers = {
            "Authorization": f"key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            settings.KHALTI_VERIFY_URL,
            json={"pidx": pidx},
            headers=headers,
            timeout=30  # ✅ add this
        )
        response.raise_for_status()
        return response.json()