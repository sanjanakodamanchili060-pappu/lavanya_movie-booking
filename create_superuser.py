"""
Automated superuser & sample data initialization script for Render and local environments.
Safe to run multiple times (idempotent).
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jishitha.settings")
django.setup()

from django.contrib.auth import get_user_model
from movies.models import Movie, Showtime, SeatBooking, MovieReview
from datetime import date, time, timedelta
from decimal import Decimal

User = get_user_model()

def init_superuser():
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@cineverse.local")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "AdminPass123!")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' successfully created.")
    else:
        print(f"Superuser '{username}' already exists.")


def init_sample_data():
    if Movie.objects.count() > 0:
        print(f"Database already contains {Movie.objects.count()} movies. Skipping initial seed.")
        return

    print("Seeding initial movie catalog, showtimes, and reviews...")

    # Real working poster images (high quality cinema posters via Unsplash & TMDB CDN)
    sample_movies = [
        {
            "title": "Interstellar Odyssey",
            "genre": "Sci-Fi",
            "duration": 169,
            "release_date": date(2024, 7, 19),
            "poster_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=800&q=80",
            "description": "When Earth faces catastrophic resource depletion, a courageous team of astronauts embarks on humanity's most ambitious voyage across a wormhole in search of a habitable new world."
        },
        {
            "title": "Shadows of Gotham",
            "genre": "Action",
            "duration": 152,
            "release_date": date(2024, 9, 14),
            "poster_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=800&q=80",
            "description": "In the rain-drenched alleys of an unforgiving metropolis, an enigmatic vigilante navigates dangerous conspiracies and high-stakes criminal syndicates to protect the innocent."
        },
        {
            "title": "Chronicles of Dune",
            "genre": "Sci-Fi",
            "duration": 166,
            "release_date": date(2024, 3, 1),
            "poster_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
            "description": "A mythic and emotionally charged hero's journey, chronicling the rise of Paul Atreides as he unites with the Fremen to lead a rebellion across the desert planet Arrakis."
        },
        {
            "title": "Midnight in Venice",
            "genre": "Romance",
            "duration": 118,
            "release_date": date(2024, 5, 20),
            "poster_url": "https://images.unsplash.com/photo-1514890547357-a9ee288728e0?auto=format&fit=crop&w=800&q=80",
            "description": "Two strangers with complicated pasts cross paths during the Venetian Carnivale, sparking an enchanting romance amidst misty canals, candlelit palazzos, and secret masquerades."
        },
        {
            "title": "Quantum Paradox",
            "genre": "Thriller",
            "duration": 134,
            "release_date": date(2024, 8, 10),
            "poster_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80",
            "description": "A theoretical physicist invents a quantum temporal device that accidentally fractures reality into parallel timelines, triggering a race against time to prevent universal collapse."
        },
        {
            "title": "The Wild Kingdom",
            "genre": "Animation",
            "duration": 102,
            "release_date": date(2024, 11, 24),
            "poster_url": "https://images.unsplash.com/photo-1534188753412-3e26d0d618d6?auto=format&fit=crop&w=800&q=80",
            "description": "An adventurous young fox and a philosophical owl embark on a whimsical quest across enchanted ancient forests to restore harmony between mythical beasts."
        }
    ]

    created_movies = []
    for m_data in sample_movies:
        movie = Movie.objects.create(**m_data)
        created_movies.append(movie)

    # Schedule showtimes for today, tomorrow, and the day after
    today = date.today()
    screens = ["Screen 1 - IMAX 3D", "Screen 2 - Dolby Atmos", "Screen 3 - VIP Lounge"]
    times = [time(14, 0), time(17, 30), time(20, 45)]
    prices = [Decimal("12.50"), Decimal("14.00"), Decimal("16.50")]

    sample_showtimes = []
    for movie in created_movies:
        for day_offset in range(3):
            show_date = today + timedelta(days=day_offset)
            for idx, (t, screen, price) in enumerate(zip(times, screens, prices)):
                st = Showtime.objects.create(
                    movie=movie,
                    show_date=show_date,
                    show_time=t,
                    screen_number=screen,
                    ticket_price=price
                )
                sample_showtimes.append(st)

    # Add sample community reviews
    sample_reviews = [
        ("Christopher Vance", 5, "An absolute cinematic masterpiece! The score and visual effects left me completely breathless."),
        ("Elena Rostova", 5, "Hands down the best film I've seen all year. Incredible pacing, emotional depth, and stellar acting."),
        ("Marcus Brody", 4, "Brilliant cinematography and world-building. Third act was a bit fast, but overall a thrilling ride!"),
        ("Sophia Chen", 5, "Watched it twice in IMAX. The sound design alone is worth every penny of the ticket price."),
        ("Liam Patel", 4, "Very compelling storyline and great character arcs. Highly recommended for any cinema enthusiast!"),
        ("Hannah Davies", 3, "Solid popcorn entertainment. Fun visuals even though the plot is somewhat predictable."),
    ]

    for movie in created_movies:
        for name, rating, comment in sample_reviews[:3]:
            MovieReview.objects.create(
                movie=movie,
                reviewer_name=name,
                rating=rating,
                comment=comment
            )

    # Add a couple of sample bookings so the 5x8 grid demonstrates occupied seats
    if sample_showtimes:
        st1 = sample_showtimes[0]
        SeatBooking.objects.create(
            showtime=st1,
            customer_name="Alex Mercer",
            customer_email="alex.mercer@example.com",
            customer_phone="+1 555-234-5678",
            selected_seats="B3, B4",
            total_paid=st1.ticket_price * 2,
            booking_reference="CINE-7A9B1C"
        )

        SeatBooking.objects.create(
            showtime=st1,
            customer_name="Jessica Alba",
            customer_email="jessica@example.com",
            customer_phone="+1 555-876-5432",
            selected_seats="C4, C5",
            total_paid=st1.ticket_price * 2,
            booking_reference="CINE-3D8E2F"
        )

    print("Initial sample movies, showtimes, reviews, and bookings successfully seeded!")


if __name__ == "__main__":
    init_superuser()
    init_sample_data()
