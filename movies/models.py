import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, help_text="e.g. Action, Sci-Fi, Drama")
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    release_date = models.DateField()
    poster_url = models.URLField(max_length=500)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-release_date', 'title']

    def __str__(self):
        return self.title

    @property
    def formatted_duration(self):
        hours = self.duration // 60
        mins = self.duration % 60
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        if avg is not None:
            return round(avg, 1)
        return 0.0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def full_stars_count(self):
        return int(round(self.average_rating))


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    show_date = models.DateField()
    show_time = models.TimeField()
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2, default=12.50)
    screen_number = models.CharField(max_length=50, help_text="e.g. Screen 1 - IMAX")

    class Meta:
        ordering = ['show_date', 'show_time']

    def __str__(self):
        return f"{self.movie.title} - {self.show_date} {self.show_time.strftime('%H:%M')} ({self.screen_number})"

    def get_booked_seats_list(self):
        """Returns a list of all seat identifiers currently booked for this showtime."""
        booked = []
        for booking in self.bookings.all():
            for seat in booking.get_seats_list():
                if seat:
                    booked.append(seat.strip().upper())
        return list(set(booked))

    @property
    def total_seats(self):
        return 40  # 5 rows x 8 columns = 40 seats matrix

    @property
    def booked_seats_count(self):
        return len(self.get_booked_seats_list())

    @property
    def available_seats_count(self):
        return max(0, self.total_seats - self.booked_seats_count)


class SeatBooking(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    selected_seats = models.CharField(max_length=255, help_text="Comma-separated seat codes, e.g. A1, A2, B5")
    total_paid = models.DecimalField(max_digits=8, decimal_places=2)
    booking_reference = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.customer_name} ({self.showtime.movie.title})"

    def get_seats_list(self):
        if not self.selected_seats:
            return []
        return [s.strip().upper() for s in self.selected_seats.split(',') if s.strip()]

    @property
    def seat_count(self):
        return len(self.get_seats_list())

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate clean cinema-style booking reference like CINE-8F3B2
            unique_part = uuid.uuid4().hex[:6].upper()
            self.booking_reference = f"CINE-{unique_part}"
        super().save(*args, **kwargs)


class MovieReview(models.Model):
    RATING_CHOICES = [
        (5, '5 - Masterpiece'),
        (4, '4 - Very Good'),
        (3, '3 - Average'),
        (2, '2 - Poor'),
        (1, '1 - Terrible'),
    ]

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=RATING_CHOICES,
        default=5
    )
    comment = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.reviewer_name} ({self.rating}/5) for {self.movie.title}"
