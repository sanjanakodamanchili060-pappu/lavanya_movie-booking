from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Movie, Showtime, SeatBooking, MovieReview
from .forms import SeatBookingForm, MovieReviewForm


def movie_list(request):
    """Movie catalog view with search, genre filters, and average ratings."""
    query = request.GET.get('q', '').strip()
    selected_genre = request.GET.get('genre', '').strip()
    sort_by = request.GET.get('sort', 'latest')

    movies = Movie.objects.all()

    if query:
        movies = movies.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(genre__icontains=query)
        )

    if selected_genre:
        movies = movies.filter(genre__iexact=selected_genre)

    if sort_by == 'title':
        movies = movies.order_by('title')
    elif sort_by == 'oldest':
        movies = movies.order_by('release_date')
    else:  # default 'latest'
        movies = movies.order_by('-release_date')

    # Get distinct genres for filter pills
    all_genres = Movie.objects.values_list('genre', flat=True).distinct()
    genres_list = sorted(list(set(g.strip() for g in all_genres if g)))

    # Fetch featured spotlight movie (first or highest rated)
    spotlight_movie = movies.first() if movies.exists() else None

    context = {
        'movies': movies,
        'genres': genres_list,
        'selected_genre': selected_genre,
        'query': query,
        'sort_by': sort_by,
        'spotlight_movie': spotlight_movie,
    }
    return render(request, 'movies/movie_list.html', context)


def movie_detail(request, movie_id):
    """Movie detail view showing trailer/poster, showtimes by date, and community reviews."""
    movie = get_object_or_404(Movie, id=movie_id)
    showtimes = movie.showtimes.all().order_by('show_date', 'show_time')

    # Group showtimes by date for clean Bootstrap date pills/tabs
    showtimes_by_date = {}
    for st in showtimes:
        date_key = st.show_date
        if date_key not in showtimes_by_date:
            showtimes_by_date[date_key] = []
        showtimes_by_date[date_key].append(st)

    reviews = movie.reviews.all().order_by('-created_date')
    review_form = MovieReviewForm()

    context = {
        'movie': movie,
        'showtimes_by_date': showtimes_by_date,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'movies/movie_detail.html', context)


def add_review(request, movie_id):
    """Process 1-5 star review submission for a movie."""
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.save()
            messages.success(request, f"Thank you, {review.reviewer_name}! Your {review.rating}-star review was posted successfully.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")

    return redirect('movie_detail', movie_id=movie.id)


def book_seats(request, showtime_id):
    """
    Seat selection & booking workflow.
    Renders 5x8 seating matrix, manages live calculations, and validates server-side.
    """
    showtime = get_object_or_404(Showtime, id=showtime_id)
    movie = showtime.movie
    booked_seats = showtime.get_booked_seats_list()

    # 5 rows (A through E) and 8 columns (1 through 8)
    rows = ['A', 'B', 'C', 'D', 'E']
    cols = list(range(1, 9))

    if request.method == 'POST':
        form = SeatBookingForm(request.POST, showtime=showtime)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.showtime = showtime

            # Compute total ticket cost server-side
            seats_list = booking.get_seats_list()
            booking.total_paid = Decimal(len(seats_list)) * showtime.ticket_price
            booking.save()

            messages.success(request, f"Booking successful! Your tickets for {movie.title} are confirmed.")
            return redirect('booking_confirmation', booking_reference=booking.booking_reference)
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errors in form.errors.items():
                if field != '__all__':
                    for error in errors:
                        messages.error(request, f"{error}")
    else:
        form = SeatBookingForm(showtime=showtime)

    context = {
        'showtime': showtime,
        'movie': movie,
        'booked_seats': booked_seats,
        'rows': rows,
        'cols': cols,
        'form': form,
    }
    return render(request, 'movies/book_seats.html', context)


def booking_confirmation(request, booking_reference):
    """Render cinema digital ticket with QR code badge, seats, and movie details."""
    booking = get_object_or_404(SeatBooking, booking_reference=booking_reference)
    context = {
        'booking': booking,
        'showtime': booking.showtime,
        'movie': booking.showtime.movie,
        'seats': booking.get_seats_list(),
    }
    return render(request, 'movies/booking_confirmation.html', context)


def booking_lookup(request):
    """Allows customers to search and view their booking via reference code or email."""
    query = request.GET.get('ref', '').strip()
    booking = None
    searched = False

    if query:
        searched = True
        booking = SeatBooking.objects.filter(
            Q(booking_reference__iexact=query) | Q(customer_email__iexact=query)
        ).first()
        if not booking:
            messages.warning(request, f"No booking found for '{query}'. Please check your booking reference code or email.")

    context = {
        'booking': booking,
        'query': query,
        'searched': searched,
    }
    return render(request, 'movies/booking_lookup.html', context)


def api_booked_seats(request, showtime_id):
    """JSON endpoint for retrieving occupied seats for a given showtime."""
    showtime = get_object_or_404(Showtime, id=showtime_id)
    return JsonResponse({
        'showtime_id': showtime.id,
        'booked_seats': showtime.get_booked_seats_list(),
        'available_count': showtime.available_seats_count,
        'ticket_price': float(showtime.ticket_price),
    })
