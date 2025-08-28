from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing, Booking, Review
from faker import Faker
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample listings, bookings, and reviews'

    def handle(self, *args, **options):
        fake = Faker()
        
        self.stdout.write("Creating sample users...")
        host, _ = User.objects.get_or_create(
            username='host_user',
            defaults={
                'email': 'host@example.com',
                'password': 'testpass123',
                'first_name': 'Host',
                'last_name': 'User'
            }
        )
        
        guest, _ = User.objects.get_or_create(
            username='guest_user',
            defaults={
                'email': 'guest@example.com',
                'password': 'testpass123',
                'first_name': 'Guest',
                'last_name': 'User'
            }
        )
        
        self.stdout.write("Creating sample listings...")
        property_types = [choice[0] for choice in Listing.PROPERTY_TYPES]
        amenities = ['Wifi', 'Kitchen', 'Pool', 'Parking', 'AC', 'TV']
        
        listings = [
            Listing.objects.create(
                host=host,
                title=fake.sentence(nb_words=4),
                description=fake.paragraph(nb_sentences=5),
                address=fake.address(),
                property_type=random.choice(property_types),
                price_per_night=random.randint(50, 500),
                bedrooms=random.randint(1, 5),
                bathrooms=random.randint(1, 3),
                max_guests=random.randint(2, 10),
                amenities=random.sample(amenities, k=random.randint(2, 5))
            ) for _ in range(10)
        ]
        
        self.stdout.write("Creating sample bookings...")
        status_choices = [choice[0] for choice in Booking.STATUS_CHOICES]
        
        for _ in range(15):
            listing = random.choice(listings)
            start_date = fake.date_this_year(after_today=True)
            end_date = start_date + timedelta(days=random.randint(1, 14))
            
            booking = Booking.objects.create(
                guest=guest,
                listing=listing,
                start_date=start_date,
                end_date=end_date,
                total_price=(end_date - start_date).days * listing.price_per_night,
                status=random.choice(status_choices),
                special_requests=fake.sentence() if random.random() > 0.5 else ''
            )
            
            if booking.status == 'completed' and random.random() > 0.3:
                Review.objects.create(
                    booking=booking,
                    rating=random.randint(1, 5),
                    comment=fake.paragraph()
                )
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))