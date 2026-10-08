from django.contrib import admin
from .models import Movie, Showtime, SeatBooking, MovieReview


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration', 'release_date', 'get_avg_rating', 'get_review_count')
    list_filter = ('genre', 'release_date')
    search_fields = ('title', 'genre', 'description')

    def get_avg_rating(self, obj):
        return f"{obj.average_rating} / 5"
    get_avg_rating.short_description = "Avg Rating"

    def get_review_count(self, obj):
        return obj.review_count
    get_review_count.short_description = "Reviews"


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'show_date', 'show_time', 'screen_number', 'ticket_price', 'available_seats_count')
    list_filter = ('show_date', 'screen_number', 'movie')
    search_fields = ('movie__title', 'screen_number')


@admin.register(SeatBooking)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'customer_name', 'showtime', 'selected_seats', 'total_paid', 'created_at')
    list_filter = ('showtime__show_date', 'showtime__screen_number', 'created_at')
    search_fields = ('booking_reference', 'customer_name', 'customer_email', 'selected_seats')
    readonly_fields = ('booking_reference', 'created_at')


@admin.register(MovieReview)
class MovieReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'reviewer_name', 'rating', 'created_date')
    list_filter = ('rating', 'created_date', 'movie')
    search_fields = ('movie__title', 'reviewer_name', 'comment')
