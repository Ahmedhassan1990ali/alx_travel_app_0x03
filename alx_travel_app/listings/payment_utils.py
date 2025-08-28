import requests
import os
from django.conf import settings

CHAPA_API_URL = "https://api.chapa.co/v1/transaction/initialize"
CHAPA_VERIFY_URL = "https://api.chapa.co/v1/transaction/verify/"

def initiate_chapa_payment(booking, request):
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": str(booking.total_price),
        "currency": "ETB",
        "email": booking.user.email,
        "first_name": booking.user.first_name,
        "last_name": booking.user.last_name,
        "tx_ref": f"booking-{booking.id}-{booking.created_at.timestamp()}",
        "callback_url": f"{settings.BASE_URL}/api/payments/verify/",
        "return_url": f"{settings.FRONTEND_URL}/bookings/{booking.id}/status",
        "customization": {
            "title": "ALX Travel Booking",
            "description": f"Payment for booking #{booking.id}"
        }
    }
    
    try:
        response = requests.post(CHAPA_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Chapa API Error: {e}")
        return None