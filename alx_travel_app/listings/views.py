from rest_framework import viewsets, permissions, status
from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Booking, Payment
from .serializers import BookingSerializer
from .payment_utils import initiate_chapa_payment, CHAPA_VERIFY_URL
from .tasks import send_booking_confirmation, send_booking_confirmation_email
from alx_travel_app import settings
import requests
import os

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        
        # Trigger email task asynchronously
        send_booking_confirmation_email.delay(
            booking_id=booking.id,
            user_email=booking.user.email,
            user_name=f"{booking.user.first_name} {booking.user.last_name}",
            listing_title=booking.listing.title,
            check_in=booking.check_in.strftime('%Y-%m-%d'),
            check_out=booking.check_out.strftime('%Y-%m-%d'),
            total_price=str(booking.total_price)
        )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]




class InitiatePaymentView(APIView):
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
            
            # Check if payment already exists
            if hasattr(booking, 'payment'):
                return Response(
                    {"error": "Payment already initiated for this booking"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initiate payment with Chapa
            payment_response = initiate_chapa_payment(booking, request)
            
            if not payment_response or 'status' not in payment_response or payment_response['status'] != 'success':
                return Response(
                    {"error": "Failed to initiate payment"},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.total_price,
                transaction_id=payment_response['data']['tx_ref'],
                chapa_response=payment_response
            )
            
            return Response({
                "status": "success",
                "checkout_url": payment_response['data']['checkout_url'],
                "transaction_id": payment.transaction_id
            })
            
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class VerifyPaymentView(APIView):
    def get(self, request):
        transaction_id = request.query_params.get('tx_ref')
        
        if not transaction_id:
            return Response(
                {"error": "Transaction reference required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            
            # Verify with Chapa API
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
            }
            
            verify_url = f"{CHAPA_VERIFY_URL}{transaction_id}"
            response = requests.get(verify_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    payment.status = 'completed'
                    payment.chapa_response = data
                    payment.save()
                    
                    # Trigger confirmation email (Celery task)
                    send_booking_confirmation.delay(payment.booking.id)
                    
                    return Response({"status": "completed"})
                else:
                    payment.status = 'failed'
                    payment.save()
                    return Response({"status": "failed"})
            
            return Response(
                {"error": "Payment verification failed"},
                status=status.HTTP_502_BAD_GATEWAY
            )
            
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )