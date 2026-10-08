from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movies/<int:movie_id>/review/', views.add_review, name='add_review'),
    path('showtimes/<int:showtime_id>/book/', views.book_seats, name='book_seats'),
    path('bookings/confirmation/<str:booking_reference>/', views.booking_confirmation, name='booking_confirmation'),
    path('bookings/lookup/', views.booking_lookup, name='booking_lookup'),
    path('api/showtimes/<int:showtime_id>/booked-seats/', views.api_booked_seats, name='api_booked_seats'),
]
