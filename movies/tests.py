from datetime import date, time
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import Movie, Showtime, SeatBooking, MovieReview


class CinemaPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.movie = Movie.objects.create(
            title="Inception Matrix",
            genre="Sci-Fi",
            duration=148,
            release_date=date(2024, 5, 10),
            poster_url="https://images.unsplash.com/photo-1534447677768-be436bb09401",
            description="A mind-bending cinematic journey through shared subconscious dreams."
        )

        self.showtime = Showtime.objects.create(
            movie=self.movie,
            show_date=date.today(),
            show_time=time(19, 30),
            ticket_price=Decimal("15.00"),
            screen_number="Screen 1 - IMAX"
        )

    def test_movie_list_view(self):
        """Test home catalog loads properly with 200 status code and movie titles."""
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inception Matrix")
        self.assertContains(response, "Sci-Fi")

    def test_movie_detail_view(self):
        """Test movie detail page with showtimes and reviews."""
        response = self.client.get(reverse('movie_detail', args=[self.movie.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Screen 1 - IMAX")
        self.assertContains(response, "$15.00")

    def test_seat_booking_workflow_success(self):
        """Test valid seat booking calculates total and creates reservation."""
        url = reverse('book_seats', args=[self.showtime.id])
        # GET seat grid
        get_res = self.client.get(url)
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, "seatGridMatrix")

        # POST booking for 2 seats: A1, A2
        post_data = {
            'customer_name': 'Bruce Wayne',
            'customer_email': 'bruce@wayne.corp',
            'customer_phone': '+1 555-0100',
            'selected_seats': 'A1, A2',
        }
        post_res = self.client.post(url, post_data)
        self.assertEqual(post_res.status_code, 302)

        # Verify booking in database
        booking = SeatBooking.objects.filter(customer_email='bruce@wayne.corp').first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.seat_count, 2)
        self.assertEqual(booking.total_paid, Decimal("30.00"))  # 2 x $15.00
        self.assertTrue(booking.booking_reference.startswith("CINE-"))

        # Verify confirmation page
        conf_url = reverse('booking_confirmation', args=[booking.booking_reference])
        conf_res = self.client.get(conf_url)
        self.assertEqual(conf_res.status_code, 200)
        self.assertContains(conf_res, "Bruce Wayne")
        self.assertContains(conf_res, "A1")
        self.assertContains(conf_res, "A2")

    def test_duplicate_seat_booking_prevention(self):
        """Test that booking an already reserved seat is strictly rejected by server-side validation."""
        # First booking occupies seats B1 and B2
        SeatBooking.objects.create(
            showtime=self.showtime,
            customer_name='John Doe',
            customer_email='john@example.com',
            customer_phone='+1 555-1111',
            selected_seats='B1, B2',
            total_paid=Decimal('30.00'),
            booking_reference='CINE-TEST1'
        )

        url = reverse('book_seats', args=[self.showtime.id])

        # Attempt to book B2 (already taken) and B3 (available)
        conflicting_data = {
            'customer_name': 'Jane Doe',
            'customer_email': 'jane@example.com',
            'customer_phone': '+1 555-2222',
            'selected_seats': 'B2, B3',
        }
        res = self.client.post(url, conflicting_data)
        # Should stay on page (status 200) with validation error
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "already been reserved for this showtime")

        # Confirm Jane's booking was NOT created
        self.assertFalse(SeatBooking.objects.filter(customer_email='jane@example.com').exists())

    def test_movie_review_submission(self):
        """Test submitting 1-5 star review."""
        review_url = reverse('add_review', args=[self.movie.id])
        post_data = {
            'reviewer_name': 'Film Critic Alice',
            'rating': 5,
            'comment': 'Stunning visual direction and an unforgettable soundtrack.'
        }
        res = self.client.post(review_url, post_data)
        self.assertEqual(res.status_code, 302)

        # Check review saved
        review = MovieReview.objects.filter(reviewer_name='Film Critic Alice').first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
        self.assertEqual(self.movie.average_rating, 5.0)

    def test_booking_lookup(self):
        """Test looking up an existing ticket by reference code."""
        booking = SeatBooking.objects.create(
            showtime=self.showtime,
            customer_name='Clark Kent',
            customer_email='clark@dailyplanet.com',
            customer_phone='+1 555-9999',
            selected_seats='D4',
            total_paid=Decimal('15.00'),
            booking_reference='CINE-SUPERMAN'
        )

        lookup_url = reverse('booking_lookup') + '?ref=CINE-SUPERMAN'
        res = self.client.get(lookup_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Clark Kent")
        self.assertContains(res, "CINE-SUPERMAN")
