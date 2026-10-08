import re
from django import forms
from .models import SeatBooking, MovieReview, Showtime


VALID_SEAT_REGEX = re.compile(r'^[A-E][1-8]$')


class SeatBookingForm(forms.ModelForm):
    class Meta:
        model = SeatBooking
        fields = ['customer_name', 'customer_email', 'customer_phone', 'selected_seats']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': True,
                'id': 'customer_name'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
                'required': True,
                'id': 'customer_email'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 000-0000',
                'required': True,
                'id': 'customer_phone'
            }),
            'selected_seats': forms.HiddenInput(attrs={
                'id': 'selected_seats_input',
                'required': True
            }),
        }

    def __init__(self, *args, showtime=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.showtime = showtime

    def clean_selected_seats(self):
        raw_seats = self.cleaned_data.get('selected_seats', '')
        if not raw_seats:
            raise forms.ValidationError("Please select at least one seat on the seating grid.")

        # Split and clean seat labels
        seats = [s.strip().upper() for s in raw_seats.split(',') if s.strip()]
        if not seats:
            raise forms.ValidationError("Please select at least one valid seat.")

        # Validate seat formatting (5x8 matrix: Rows A to E, Numbers 1 to 8)
        invalid_seats = [s for s in seats if not VALID_SEAT_REGEX.match(s)]
        if invalid_seats:
            raise forms.ValidationError(f"Invalid seat identifier(s): {', '.join(invalid_seats)}. Allowed seats are A1-A8 through E1-E8.")

        # Check for duplicates within the current selection
        if len(seats) != len(set(seats)):
            raise forms.ValidationError("Duplicate seats detected in selection.")

        # Crucial server-side check: Ensure none of the seats are already booked for this showtime
        if self.showtime:
            already_booked = set(self.showtime.get_booked_seats_list())
            conflicts = [s for s in seats if s in already_booked]
            if conflicts:
                raise forms.ValidationError(
                    f"Seat(s) {', '.join(conflicts)} have already been reserved for this showtime. Please pick available seats."
                )

        return ", ".join(sorted(seats))


class MovieReviewForm(forms.ModelForm):
    class Meta:
        model = MovieReview
        fields = ['reviewer_name', 'rating', 'comment']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name or Alias',
                'required': True,
                'id': 'reviewer_name'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select',
                'id': 'rating_select',
                'required': True
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your cinematic thoughts, direction, performance, and highlights...',
                'required': True,
                'id': 'comment_textarea'
            }),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None or rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be an integer between 1 and 5.")
        return rating
