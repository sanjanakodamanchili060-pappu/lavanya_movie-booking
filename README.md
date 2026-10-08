# CineVerse — Movie Ticket Booking & Community Review Portal
> **Django Full-Stack Capstone Project 5**  
> Built with Django 5.x, SQLite, Bootstrap 5, Vanilla JavaScript, WhiteNoise, and Gunicorn. Ready for deployment on Render.

---

## 1. Project Overview & Features

- **Bootstrap 5 Cinema-Style Interface**: Sleek dark theater aesthetic, curved illuminated screen banner, glowing accents, and responsive layout.
- **Interactive 5×8 Seat-Selection Matrix**: Visual grid (Rows A–E, Columns 1–8) with real-time seat availability, center aisle, and seat statuses:
  - *Available* (Selectable)
  - *Selected* (Highlighted in gold with real-time tally)
  - *Booked / Occupied* (Disabled and prevented from re-selection)
- **Dynamic Ticket Price Calculation**: Client-side JavaScript updates seat count and total amount in real time, reinforced with server-side validation.
- **Showtime Selection with Bootstrap Pills**: Organized by dates, showing times, screens, prices, and remaining seat counts.
- **Community Reviews (1–5 Stars)**: Interactive star rating selector, verified community comments, and dynamic average rating calculations.
- **Strict Server-Side Validation**:
  - Re-checks seat availability in the database to prevent duplicate seat bookings for the same showtime.
  - Recalculates ticket pricing on the backend (`seat_count * ticket_price`).
  - Validates review ratings (1 to 5).
  - Built-in CSRF protection on all forms.
- **Digital Cinema Pass / Ticket Confirmation**: Perforated boarding pass design with booking reference ID, screen details, seat list, simulated barcode/QR code, and PDF/print view.
- **Reservation Lookup**: Search bookings by unique reference code (`CINE-XXXXXX`) or customer email.

---

## 2. Technology Stack

- **Backend**: Python 3.10+ / 3.11+, Django 5.x / 6.x, Django ORM
- **Database**: SQLite (`db.sqlite3`)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Static Files & Server**: WhiteNoise 6.x, Gunicorn 26.x
- **Deployment Platform**: Render (`render.yaml`)

---

## 3. Local Setup & Execution

### Step 1: Clone and Navigate to Directory
```bash
cd jishitha
```

### Step 2: Activate Virtual Environment
- **Windows (PowerShell/CMD)**:
  ```powershell
  .\venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Apply Migrations & Seed Sample Data
```bash
python manage.py migrate
python create_superuser.py
```
*(Creates the default administrator account and populates movies, showtimes, sample reviews, and sample bookings)*

### Step 5: Start Local Development Server
```bash
python manage.py runserver
```

Open your browser at:
- **Cinema Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  - **Username**: `admin`
  - **Password**: `AdminPass123!`

---

## 4. Render Deployment Instructions (Mandatory)

The project includes `render.yaml` and `requirements.txt` pre-configured for one-click Render Web Service / Blueprint deployment.

### 1. Initialize Git & Push to GitHub
```bash
git init
git add .
git commit -m "Prepare Django project for Render"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

### 2. Deploy on Render
1. Log in to [Render](https://dashboard.render.com/).
2. Click **New +** &rarr; **Blueprint** (or **Web Service**).
3. Connect your GitHub repository.
4. Render will automatically detect `render.yaml` with the following configuration:
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py`
   - **Start Command**: `python manage.py migrate && python create_superuser.py && gunicorn jishitha.wsgi:application`
5. Set environment variable:
   - `SECRET_KEY`: `<your-random-production-secret-key>`
6. Click **Apply / Deploy**.

### 3. Verify Live Service
Once the build completes:
- Visit your live URL: `https://<service-name>.onrender.com/`
- Test the seat selection matrix, review posting, and ticket generation.
- Access admin at `https://<service-name>.onrender.com/admin/`.

> **Note on SQLite on Render**:  
> Render's free tier uses an ephemeral filesystem. If the free instance sleeps or restarts, SQLite (`db.sqlite3`) will reinitialize via `create_superuser.py` automatically. This is standard and expected for this assignment demonstration.
