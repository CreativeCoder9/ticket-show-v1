# Ticket Show v1

Ticket Show v1 is a Flask-based web application for managing venues, shows, and ticket bookings. It includes a browser UI for users and admins, a SQLite-backed data layer, and REST-style API endpoints for venues and shows. It's an upgraded version of Ticket Show application developed for the MAD-1 course of IITM BS Degree.

## Features

- User registration, login, logout, and session-based access
- Admin dashboard for managing venues and shows
- Venue creation, update, and deletion
- Show creation, update, and deletion
- Ticket booking flow with seat availability checks
- Search by show name, tags, venue name, or location
- Time-based show search
- File upload support for venue/show images
- JSON API endpoints for venue and show CRUD operations

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Jinja2 templates
- Bootstrap CSS

## Project Structure

```text
ticket-show-v2/
|-- app.py
|-- requirement.txt
|-- swagger.yaml
|-- instance/
|   `-- ticketshow.db
|-- static/
|   |-- css/
|   |-- images/
|   `-- uploads/
`-- templates/
```

## Prerequisites

- Python 3.9+ recommended
- `pip`

## Installation

1. Clone or download the project.
2. Create and activate a virtual environment.
3. Install dependencies from `requirement.txt`.

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirement.txt
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
```

## Running the App

Start the Flask application with:

```powershell
python app.py
```

By default, the app runs in debug mode and uses the SQLite database at `instance/ticketshow.db`.

Open the app in your browser at:

```text
http://127.0.0.1:5000/
```

## Database

- The app uses SQLite through Flask-SQLAlchemy.
- The configured database URI is `sqlite:///ticketshow.db`.
- Tables are created automatically on startup with `db.create_all()`.
- A sample database file is already present in `instance/ticketshow.db`.

## Main Routes

### User Pages

- `/` or `/home` - Home page
- `/register` - User registration
- `/login` - User login
- `/logout` - User logout
- `/dashboard` - Logged-in user dashboard
- `/bookings` - View booked shows
- `/bookings/<show_id>/confirm` - Confirm and place a booking
- `/search` - Search by text
- `/search/time` - Search shows by time range

### Admin Pages

- `/admin-login` - Admin login
- `/admin` - Admin dashboard
- `/add-venue` - Add a venue
- `/venue/update/<venue_id>` - Update a venue
- `/venue/delete/<venue_id>` - Delete a venue
- `/add-show` - Add a show
- `/show/update/<show_id>` - Update a show
- `/show/delete/<show_id>` - Delete a show

## API Endpoints

The project also exposes JSON endpoints for venues and shows.

### Venues

- `GET /api/venues` - List all venues
- `POST /api/venues` - Create a venue
- `GET /api/venues/<venue_id>` - Get a single venue
- `PUT /api/venues/<venue_id>` - Update a venue
- `DELETE /api/venues/<venue_id>` - Delete a venue

### Shows

- `GET /api/shows` - List all shows
- `POST /api/shows` - Create a show
- `GET /api/shows/<show_id>` - Get a single show
- `PUT /api/shows/<show_id>` - Update a show
- `DELETE /api/shows/<show_id>` - Delete a show

API examples and schema notes are also available in `swagger.yaml`.

## Booking Logic

- Seat availability is derived from venue capacity and the number of shows assigned to that venue.
- Booking price may increase based on demand during confirmation.
- A booking is rejected if requested seats exceed available seats.

## Notes

- Uploaded images are stored under `static/uploads/`.
- The current app stores passwords in plain text and uses a hardcoded secret key, so it should not be used as-is in production.
- The dependency file is named `requirement.txt` in this repository, not the more common `requirements.txt`.

## Future Improvements

- Hash passwords before storing them
- Move secret configuration to environment variables
- Add automated tests
- Add database migrations
- Improve input validation and error handling
- Add role-based authorization checks for admin-only actions

## Documentation

- API spec: `swagger.yaml`
- Project report: `MAD-1 Project Report.pdf`

## License

No license file is currently included in this repository.
