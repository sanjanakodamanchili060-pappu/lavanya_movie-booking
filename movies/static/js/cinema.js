/**
 * CINEVERSE CINEMA - JAVASCRIPT LOGIC
 * Handles 5x8 Seat Selection, Dynamic Price Calculation, and Review Stars
 */

document.addEventListener('DOMContentLoaded', () => {
    initSeatSelectionMatrix();
    initStarRatingWidget();
});

/**
 * 5x8 Seat Selection Matrix and Live Price Calculation
 */
function initSeatSelectionMatrix() {
    const seatGrid = document.getElementById('seatGridMatrix');
    if (!seatGrid) return;

    const ticketPrice = parseFloat(seatGrid.dataset.ticketPrice || "0");
    const selectedSeatsInput = document.getElementById('selected_seats_input');
    const selectedCountEl = document.getElementById('selectedCount');
    const totalPriceEl = document.getElementById('totalPriceDisplay');
    const selectedSeatsListEl = document.getElementById('selectedSeatsList');
    const submitBtn = document.getElementById('submitBookingBtn');
    const bookingForm = document.getElementById('seatBookingForm');

    let selectedSeats = [];

    // Pre-populate if form was reloaded with errors or initial selection
    if (selectedSeatsInput && selectedSeatsInput.value) {
        selectedSeats = selectedSeatsInput.value
            .split(',')
            .map(s => s.trim().toUpperCase())
            .filter(Boolean);
        
        // Highlight pre-selected seats
        selectedSeats.forEach(seatId => {
            const btn = document.querySelector(`.seat-btn[data-seat="${seatId}"]`);
            if (btn && !btn.disabled) {
                btn.classList.add('selected');
            }
        });
        updatePriceSummary();
    }

    // Handle seat click delegation
    seatGrid.addEventListener('click', (e) => {
        const seatBtn = e.target.closest('.seat-btn');
        if (!seatBtn) return;
        
        if (seatBtn.disabled || seatBtn.classList.contains('booked')) {
            return;
        }

        const seatId = seatBtn.dataset.seat;
        if (!seatId) return;

        if (selectedSeats.includes(seatId)) {
            // Deselect
            selectedSeats = selectedSeats.filter(id => id !== seatId);
            seatBtn.classList.remove('selected');
        } else {
            // Select
            selectedSeats.push(seatId);
            seatBtn.classList.add('selected');
        }

        // Sort alphabetically and numerically: A1, A2, B3...
        selectedSeats.sort((a, b) => {
            const rowA = a.charAt(0);
            const rowB = b.charAt(0);
            if (rowA !== rowB) return rowA.localeCompare(rowB);
            return parseInt(a.slice(1)) - parseInt(b.slice(1));
        });

        updatePriceSummary();
    });

    function updatePriceSummary() {
        const count = selectedSeats.length;
        const total = (count * ticketPrice).toFixed(2);

        // Update hidden input
        if (selectedSeatsInput) {
            selectedSeatsInput.value = selectedSeats.join(', ');
        }

        // Update seat count
        if (selectedCountEl) {
            selectedCountEl.textContent = count;
        }

        // Update total price display
        if (totalPriceEl) {
            totalPriceEl.textContent = `$${total}`;
        }

        // Update selected tags pills
        if (selectedSeatsListEl) {
            if (count === 0) {
                selectedSeatsListEl.innerHTML = '<span class="text-secondary small fst-italic">No seats selected yet. Click seats on the grid above.</span>';
            } else {
                selectedSeatsListEl.innerHTML = selectedSeats
                    .map(seat => `<span class="selected-seat-tag"><i class="bi bi-ticket-fill me-1"></i>${seat}</span>`)
                    .join(' ');
            }
        }

        // Update submit button state
        if (submitBtn) {
            if (count === 0) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-cart-x me-2"></i>Select Seats to Proceed';
            } else {
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<i class="bi bi-shield-check me-2"></i>Confirm & Pay $${total}`;
            }
        }
    }

    // Client-side form submit guard
    if (bookingForm) {
        bookingForm.addEventListener('submit', (e) => {
            if (selectedSeats.length === 0) {
                e.preventDefault();
                alert('Please select at least one seat before confirming your booking.');
            }
        });
    }
}

/**
 * 1-5 Star Interactive Rating Widget
 */
function initStarRatingWidget() {
    const starWidget = document.querySelector('.star-rating-widget');
    const labelFeedback = document.getElementById('starFeedbackText');
    if (!starWidget) return;

    const labels = {
        5: '5 - Masterpiece 🌟🌟🌟🌟🌟',
        4: '4 - Very Good ⭐⭐⭐⭐',
        3: '3 - Average ⭐⭐⭐',
        2: '2 - Poor ⭐⭐',
        1: '1 - Terrible ⭐'
    };

    const inputs = starWidget.querySelectorAll('input[type="radio"]');
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            if (labelFeedback && labels[input.value]) {
                labelFeedback.textContent = labels[input.value];
            }
        });
    });
}
