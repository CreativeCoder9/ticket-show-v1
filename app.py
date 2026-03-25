import os, random, requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

# Creating a new flask application instance
app = Flask(
  __name__,
  template_folder='templates',  # Name of html file folder
  static_folder='static'  # Name of directory for static files
)

# Variables & Data
error_msg = "Unexpected error occurred!"
success_msg = "Process completed successfully!"
return_route = "/"

# Upload Directory
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# App config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticketshow.db'
app.config['SECRET_KEY'] = 'dfewfew123ashkajsksh121172538hd62@trgf'

#initializing Database
db = SQLAlchemy(app)


# Database Moddels
class User(db.Model):
  user_id = db.Column(db.Integer,
                      primary_key=True,
                      nullable=False,
                      autoincrement=True)
  user_name = db.Column(db.String(50), nullable=False)
  email = db.Column(db.String(50), unique=True, nullable=False)
  password = db.Column(db.String, nullable=False)
  is_admin = db.Column(db.Boolean)
  booking = db.relationship('Bookings', backref='user', cascade='all')


class Venue(db.Model):
  venue_id = db.Column(db.Integer,
                       primary_key=True,
                       nullable=False,
                       autoincrement=True)
  venue_name = db.Column(db.String(50))
  venue_location = db.Column(db.String(50))
  venue_capacity = db.Column(db.Integer, nullable=False)
  # is_active = db.Column(db.Boolean)
  venue_img = db.Column(db.String(50))
  shows = db.relationship('Show', backref='venue',cascade='all')



class Show(db.Model):
  show_id = db.Column(db.Integer,
                      primary_key=True,
                      nullable=False,
                      autoincrement=True)
  show_name = db.Column(db.String(50))
  show_rating = db.Column(db.Float, nullable=True)
  show_price = db.Column(db.Integer, nullable=False)
  show_starting_time = db.Column(db.String(50))
  show_ending_time = db.Column(db.String(50))
  show_tags = db.Column(db.String(100))
  show_img = db.Column(db.String(50))
  show_venue = db.Column(db.Integer,
                         db.ForeignKey('venue.venue_id'),
                         nullable=False)
  bookings = db.relationship('Bookings', backref='show', cascade='all')


class Bookings(db.Model):
  booking_id = db.Column(db.Integer,
                         primary_key=True,
                         nullable=False,
                         autoincrement=True)
  booking_user_id = db.Column(db.Integer,
                              db.ForeignKey('user.user_id'),
                              nullable=False)
  num_bookings = db.Column(db.Integer, nullable=False)
  booking_show_id = db.Column(db.Integer,
                              db.ForeignKey('show.show_id'),
                              nullable=False)


# Creating the database
with app.app_context():
  db.create_all()


# Allowed file types
def allowed_file(filename):
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# routes of the app
# home
@app.route("/")
@app.route("/home")
@app.route("/index.html")
@app.route("/index")
def home():
  logged_in = False
  logged_in_user = None
  url1 = url_for('venues', _external=True)
  url2 = url_for('shows', _external=True)
  response1 = requests.get(url1)
  response2 = requests.get(url2)
  venues = response1.json()
  shows = response2.json()

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])

  return render_template("home.html",
                         logged_in=logged_in,
                         shows=shows,
                         venues=venues)


#log-in page
@app.route("/login", methods=["GET", "POST"])
def login():
  logged_in = False
  logged_in_user = None

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])

  if logged_in:
    error_msg = "You are already logged in as " + logged_in_user.user_name + ". Please log out first to sign in as another user."
    return render_template('error.html', error_msg=error_msg, return_route="/")
  elif request.method == "POST":
    email = request.form["email"]
    password = request.form["password"]
    check = request.form.get("check", "off")
    user = User.query.filter_by(email=email, password=password).first()
    if user is None:
      return render_template('error.html',
                             error_msg="No account found!",
                             return_route="/login")
    else:
      session['user'] = user.user_id
      if check == "on":
        session.permanent = True
      return redirect(url_for('dashboard'))
  else:
    return render_template("login.html")


# log-out
@app.route("/logout")
def logout():
  logged_in = False
  logged_in_user = None
  is_admin = False
  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])
    if 'user' in session:
      session.pop('user')
    return render_template('success.html',
                           success_msg="Logged out successfully!",
                           return_route="/")
  else:
    return render_template('error.html',
                           error_msg="You are not logged in.",
                           return_route="/")


#registration page
@app.route("/register", methods=["GET", "POST"])
def registration():
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])

  if logged_in:
    error_msg = "You are already logged in as " + logged_in_user.user_name + ". Please log out first to sign in as another user."
    return render_template('error.html', error_msg=error_msg, return_route="/")
  elif (request.method == "POST"):
    email = request.form["email"]
    password = request.form["password"]
    check = request.form.get("check", "off")
    user_for_db = User(user_name=email,
                       email=email,
                       password=password,
                       is_admin=True)
    db.session.add(user_for_db)
    try:
      db.session.commit()
      user = User.query.filter_by(email=email, password=password).first()
      session['user'] = user.user_id
      if check == "on":
        session.permanent = True
      return redirect(url_for('dashboard'))
    except Exception as e:
      db.session.rollback()
      error_msg = "User exists already. Please login."
      return render_template('error.html',
                             error_msg=error_msg,
                             return_route="/register")
    finally:
      db.session.close()
  else:
    return render_template("register.html")


#admin-login
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])
    is_admin = logged_in_user.is_admin

  if logged_in and is_admin == False:
    error_msg = "You are already logged in as " + logged_in_user.user_name + ". Please log out first to sign in as another user."
    return render_template('error.html', error_msg=error_msg, return_route="/")
  elif request.method == "POST":
    email = request.form["email"]
    password = request.form["password"]
    check = request.form.get("check", "off")
    user = User.query.filter_by(email=email, password=password).first()
    if user is None:
      return render_template('error.html',
                             error_msg="No account found!",
                             return_route="/admin-login")
    else:
      session['user'] = user.user_id
      if check == "on":
        session.permanent = True
      return redirect(url_for('admin'))
  elif logged_in and is_admin:
    return redirect(url_for('admin'))
  else:
    return render_template("admin-login.html")


#admin dashboard page
@app.route("/admin")
def admin():
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])
    is_admin = logged_in_user.is_admin

  if logged_in and is_admin:
    venues = Venue.query.all()
    return render_template('admin-dashboard.html', venues=venues)
  elif (logged_in and not is_admin):
    error_msg = "ACCESS DENIED! You are not authorized to access this url. Please login with administritive credentials."
    return_route = "/"
    return render_template('error.html',
                           error_msg=error_msg,
                           return_route=return_route)
  else:
    error_msg = "Please login as Administrator to access the page!"
    return_route = "/admin-login"
    return render_template('error.html',
                           error_msg=error_msg,
                           return_route=return_route)


#update venue
@app.route("/venue/update/<int:venue_id>", methods=["GET", "POST"])
def update_venue(venue_id):
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])
    is_admin = logged_in_user.is_admin

  venue = Venue.query.get(venue_id)

  if request.method == "POST" and is_admin:
    name = request.form.get("name", venue.venue_name)
    location = request.form.get("location", venue.venue_location)
    capacity = request.form.get("capacity", venue.venue_capacity)
    img = venue.venue_img
    file = request.files["banner"]
    if file and allowed_file(file.filename):
      filename = name + "_" + secure_filename(file.filename)
      img = "../" + app.config['UPLOAD_FOLDER'] + "/" + str(filename)
      basedir = os.path.abspath(os.path.dirname(__file__))
      file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))

    venue.venue_name = name
    venue.venue_location = location
    venue.venue_capacity = capacity
    venue.venue_img = img
    db.session.commit()
    return render_template('success.html',
                           success_msg="Venue updated successfully!", logged_in=logged_in,
                           return_route="/admin")

  if request.method == "GET" and is_admin:
    return render_template("update-venue.html", venue=venue)
  
  return redirect(url_for('admin'))


#Add venue page
@app.route("/add-venue", methods=["GET", "POST"])
def add_venue():
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])
    is_admin = logged_in_user.is_admin

  if request.method == "POST" and is_admin:
    name = request.form["name"]
    location = request.form["location"]
    capacity = request.form["capacity"]
    file = request.files["banner"]
    if file and allowed_file(file.filename):
      filename = name + "_" + secure_filename(file.filename)
    else:
      msg = "File not supportted"
      return_route = "/add-show"
      return render_template('error.html',
                             error_msg=msg,
                             return_route=return_route)
    basedir = os.path.abspath(os.path.dirname(__file__))
    file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
    venue_for_db = Venue(venue_name=name,
                         venue_location=location,
                         venue_capacity=capacity,
                         venue_img="../" + app.config['UPLOAD_FOLDER'] + "/" +
                         filename)

    db.session.add(venue_for_db)
    try:
      db.session.commit()
    except Exception as e:
      db.session.rollback()
      error_msg = e
      return render_template('error.html',
                             error_msg=error_msg,
                             return_route="/register")
    finally:
      db.session.close()

    return render_template('success.html',
                           success_msg="Venue added successfully!",logged_in=logged_in,
                           return_route="/admin")
  elif logged_in and is_admin:
    url = url_for('venues', _external=True)
    response = requests.get(url)
    venues = response.json()
    return render_template('add-venue.html')
  else:
    error_msg = "ACCESS DENIED! You are not authorized to access this url. Please login with administritive credentials."
    return_route = "/"
    return render_template('error.html',
                           error_msg=error_msg,
                           return_route=return_route)


# Venues api
# Create a venue & get all venues
@app.route("/api/venues", methods=["GET", "POST"])
def venues():
  if request.method == "POST":
    venue_data = request.get_json()
    venue = Venue(venue_name=venue_data['venue_name'],
                  venue_location=venue_data['venue_location'],
                  venue_capacity=venue_data['venue_capacity'],
                  venue_img=venue_data['venue_img'])
    db.session.add(venue)
    try:
      db.session.commit()
    except Exception as e:
      db.session.rollback()
      error_msg = e
      return jsonify({'message': error_msg}), 500
    finally:
      db.session.close()
    return jsonify({'message': 'Venue created successfully!'}), 201
  else:
    all_venues = Venue.query.all()
    venue_list = []

    for venue in all_venues:
      venue_dict = {
        "venue_id": venue.venue_id,
        "venue_name": venue.venue_name,
        "venue_location": venue.venue_location,
        "venue_capacity": venue.venue_capacity,
        "venue_img": venue.venue_img
      }
      venue_list.append(venue_dict)

  return jsonify(venue_list), 200


# retrieve a specific venue
@app.route('/api/venues/<int:venue_id>', methods=['GET', 'PUT', 'DELETE'])
def get_venue(venue_id):
  if request.method == 'DELETE':
    venue = Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    return jsonify({'message': 'Venue deleted successfully!'}), 200

  elif request.method == 'PUT':
    venue = Venue.query.get_or_404(venue_id)
    venue_data = request.get_json()
    venue.venue_name = venue_data['venue_name']
    venue.venue_location = venue_data['venue_location']
    venue.venue_capacity = venue_data['venue_capacity']
    venue.venue_img = venue_data['venue_img']
    try:
      db.session.commit()
    except Exception as e:
      db.session.rollback()
      error_msg = e
      return jsonify({'message': error_msg}), 500
    finally:
      db.session.close()
      return jsonify({'message': 'Venue updated successfully!'}), 200
  else:
    venue = Venue.query.get(venue_id)
    if venue is None:
      return jsonify({"error": "Venue not found"}), 404
    venue_data = {}
    venue_data['venue_id'] = venue.venue_id
    venue_data['venue_name'] = venue.venue_name
    venue_data['venue_location'] = venue.venue_location
    venue_data['venue_capacity'] = venue.venue_capacity
    venue_data['venue_img'] = venue.venue_img
    return jsonify(venue_data), 200


# Shows api
@app.route("/api/shows", methods=["GET", "POST"])
def shows():
  if request.method == "POST":
    show_data = request.get_json()
    show = Show(show_name=show_data['show_name'],
                show_rating=show_data['show_rating'],
                show_price=show_data['show_price'],
                show_starting_time=show_data['show_starting_time'],
                show_ending_time=show_data['show_ending_time'],
                show_tags=show_data['show_tags'],
                show_img=show_data['show_img'],
                show_venue=show_data['show_venue'])
    db.session.add(show)
    db.session.commit()
    return jsonify({'message': 'Show created successfully!'}), 201
  else:
    all_shows = Show.query.all()
    shows_list = []

    for show in all_shows:
      show_dict = {
        "show_id": show.show_id,
        "show_name": show.show_name,
        "show_price": show.show_price,
        "show_starting_time": show.show_starting_time,
        "show_ending_time": show.show_ending_time,
        "show_img": show.show_img,
        "show_venue": show.show_venue,
        "show_rating": show.show_rating,
        "show_tags": show.show_tags
      }
      shows_list.append(show_dict)
    return jsonify(shows_list)


# retrieving a specificshow
@app.route('/api/shows/<int:show_id>', methods=['GET', 'PUT', 'DELETE'])
def get_show(show_id):
  if request.method == "PUT":
    show = Show.query.get_or_404(show_id)
    show_data = request.get_json()
    show.show_name = show_data['show_name']
    show.show_rating = show_data['show_rating']
    show.show_price = show_data['show_price']
    show.show_starting_time = show_data['show_starting_time']
    show.show_ending_time = show_data['show_ending_time']
    show.show_tags = show_data['show_tags']
    show.show_img = show_data['show_img']
    show.show_venue = show_data['show_venue']
    db.session.commit()
    return jsonify({'message': 'Show updated successfully!'}), 201

  elif request.method == 'DELETE':
    show = Show.query.get_or_404(show_id)
    db.session.delete(show)
    db.session.commit()
    return jsonify({'message': 'Show deleted successfully!'}), 200

  else:
    show = Show.query.get_or_404(show_id)
    show_data = {}
    show_data['show_id'] = show.show_id
    show_data['show_name'] = show.show_name
    show_data['show_rating'] = show.show_rating
    show_data['show_price'] = show.show_price
    show_data['show_starting_time'] = show.show_starting_time
    show_data['show_ending_time'] = show.show_ending_time
    show_data['show_tags'] = show.show_tags
    show_data['show_img'] = show.show_img
    show_data['show_venue'] = show.show_venue
    return jsonify(show_data)

# Delete Venue
@app.route("/venue/delete/<int:venue_id>", methods=["GET", "POST"])
def delete_venue(venue_id):
    logged_in = False
    logged_in_user = None
    is_admin = False

    if session.get('user'):
        logged_in = True
        logged_in_user = User.query.get(session['user'])
        is_admin = logged_in_user.is_admin

    venue = Venue.query.get(venue_id)

    if logged_in and is_admin:
        if request.method == "POST":
            db.session.delete(venue)
            db.session.commit()
            return render_template('success.html',
                                   success_msg="Venue deleted successfully!",logged_in=logged_in,
                                   return_route="/admin")
        if request.method == "GET":
            url = url_for('delete_venue', venue_id=venue_id)
            return render_template('confirm.html', url=url)
    else:
        return render_template('error.html',
                               error_msg="You are not authorized to perform this action.")



#Delete_show
@app.route("/show/delete/<int:show_id>", methods=["GET", "post"])
def delete_show(show_id):
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])
    is_admin = logged_in_user.is_admin

  show = Show.query.get(show_id)

  if logged_in and is_admin:
    if request.method == "POST":
      db.session.delete(show)
      db.session.commit()
      return render_template('success.html',
                             success_msg="Show deleted successfully!",logged_in=logged_in,
                             return_route="/admin")
    if request.method == "GET":
      url = url_for('delete_show', show_id=show_id)
      return render_template('confirm.html', url=url)


#update_show
@app.route("/show/update/<int:show_id>", methods=["GET", "POST"])
def update_show(show_id):
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])
    is_admin = logged_in_user.is_admin

  show = Show.query.get(show_id)

  if logged_in and is_admin:
    if request.method == "POST":

      name = request.form.get("showName", show.show_name)
      rating = request.form.get("rating", show.show_rating)
      price = request.form.get("price", show.show_price)
      starting_time = request.form.get("startingTime", show.show_starting_time)
      ending_time = request.form.get("endingTime", show.show_ending_time)
      tags = request.form.get("tags", show.show_tags)
      venue = request.form.get("venue", show.show_venue)
      file = request.files['poster']
      img_url = show.show_img
      file = request.files["poster"]
      if file and allowed_file(file.filename):
        filename = name + "_" + secure_filename(file.filename)
        img_url = "../" + app.config['UPLOAD_FOLDER'] + "/" + str(filename)
        basedir = os.path.abspath(os.path.dirname(__file__))
        file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))

      show.show_name = name
      show.show_rating = rating
      show.show_price = price
      show.show_starting_time = starting_time
      show.show_ending_time = ending_time
      show.show_tags = tags
      show.show_img = img_url
      show.show_venue = venue

      try:
        db.session.commit()
      except Exception as e:
        db.session.rollback()
        error_msg = e
        return render_template('error.html',
                               error_msg=error_msg,
                               return_route="/register")
      finally:
        db.session.close()
        return render_template('success.html',
                               success_msg="Venue updated successfully!",
                               logged_in=logged_in,
                               return_route="/admin")
    if request.method == "GET":
      url = url_for('venues', _external=True)
      response = requests.get(url)
      venues = response.json()
      return render_template('update-show.html', show=show, venues=venues)
  else:
    error_msg = "ACCESS DENIED! You are not authorized to access this url. Please login with administritive credentials."
    return_route = "/"
    return render_template('error.html',
                           error_msg=error_msg,
                           return_route=return_route)


#Add show page
@app.route("/add-show", methods=["GET", "POST"])
def add_show():
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])
    is_admin = logged_in_user.is_admin

  if logged_in and is_admin:
    if request.method == "POST":
      name = request.form["showName"]
      rating = request.form["rating"]
      price = request.form["price"]
      starting_time = request.form["startingTime"]
      ending_time = request.form["endingTime"]
      tags = request.form["tags"]
      venue = request.form["venue"]
      file = request.files['poster']
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
      else:
        msg = "File not supportted"
        return_route = "/add-show"
        return render_template('error.html', error_msg=msg)
      basedir = os.path.abspath(os.path.dirname(__file__))
      file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))

      app.logger.info(venue)
      show_for_db = Show(show_name=name,
                         show_rating=rating,
                         show_price=price,
                         show_starting_time=starting_time,
                         show_ending_time=ending_time,
                         show_tags=tags,
                         show_img="../" + app.config['UPLOAD_FOLDER'] + "/" +
                         filename,
                         show_venue=venue)
      db.session.add(show_for_db)
      try:
        db.session.commit()
      except Exception as e:
        db.session.rollback()
        error_msg = e
        return render_template('error.html',
                               error_msg=error_msg,
                               return_route="/register")
      finally:
        db.session.close()
        return render_template('success.html',
                           success_msg="Show added successfully!",
                           return_route="/admin")
    else:
      url = url_for('venues', _external=True)
      response = requests.get(url)
      venues = response.json()
      return render_template('add-show.html', venues=venues)
  else:
    error_msg = "ACCESS DENIED! You are not authorized to access this url. Please login with administritive credentials."
    return_route = "/"
    return render_template('error.html',
                           error_msg=error_msg,
                           return_route=return_route)


#Venue page
@app.route('/venues/<int:venue_id>', methods=['GET'])
def venue_page(venue_id):
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])
    is_admin = logged_in_user.is_admin

  url = url_for('get_venue', venue_id=venue_id, _external=True)
  response = requests.get(url)
  venue = response.json()
  shows = shows = Show.query.filter_by(show_venue=venue_id).all()
  app.logger.info(shows)
  return render_template('venue.html',
                         venue=venue,
                         shows=shows,
                         logged_in=logged_in)


#Dashboard page
@app.route("/dashboard")
def dashboard():
  logged_in = False
  logged_in_user = None

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])

  if logged_in:
    venues = Venue.query.all()
    return render_template('dashboard.html',
                           username=logged_in_user.user_name,
                           venues=venues)
  else:
    return redirect(url_for('login'))


#bookings page
@app.route("/bookings")
def bookings():
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])
    
  shows_booked = Bookings.query.filter_by(booking_user_id=session['user']).all()
  app.logger.info(shows_booked)
  if logged_in:
    return render_template('bookings.html', shows=shows_booked)
  else:
    return render_template("bookings.html")


#bookings confirmation page
@app.route("/bookings/<int:show_id>/confirm", methods=['GET', 'POST'])
def confirmBookings(show_id):
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])

  show = Show.query.get_or_404(show_id)
  venue = show.venue
#   venue_id = show.venue.venue_id
  capacity = venue.venue_capacity
  num_shows = len(venue.shows)
  seats = capacity // num_shows
  num_bookings = total_bookings = db.session.query(db.func.sum(Bookings.num_bookings)).\
                filter(Bookings.booking_show_id == show_id).scalar() or 0

  available_seats = seats - num_bookings
  if available_seats < 0:
    available_seats = 0
    return render_template('error.html', error_msg="You missed the show! Show is houseful!", return_route="/")
  ticket_price = show.show_price

  if logged_in:
    if request.method == 'GET':
      if num_bookings > seats//2:
        ticket_price = ticket_price + 50
      elif num_bookings > seats*0.85:
        ticket_price = ticket_price + 100
      else:
        ticket_price = ticket_price

    #   bookings = Booking.query.filter_by(booking_show_id = show_id).all()
      return render_template('confirm-booking.html', show=show, ticket_price=ticket_price, available_seats=available_seats)
    if request.method == 'POST':
      booking_user_id = session['user']
      booking_show_id = request.form['show_id']
      bookings_num = request.form['num_bookings']
      if available_seats< int(bookings_num):
        return render_template('error.html', error_msg="We don't have that no of seats :(", return_route="/")

      booking = Bookings(booking_user_id=booking_user_id, booking_show_id=booking_show_id, num_bookings=bookings_num)
      db.session.add(booking)
      db.session.commit()

      return render_template('success.html',
                           success_msg="Show booked     successfully!",
                           return_route="/")


#Search resukt page
@app.route("/search", methods=['GET', 'POST'])
def search():
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])

  if request.method == "POST":
    search_term = request.form['query']
    shows_name = Show.query.filter((Show.show_name.like(f"%{search_term}%")) | (Show.show_tags.like(f"%{search_term}%"))).all()
    venue_name = Venue.query.filter((Venue.venue_name.like(f"%{search_term}%")) | (Venue.venue_location.like(f"%{search_term}%"))).all()
    
    return render_template('search-results.html', shows=shows_name, venues=venue_name, logged_in=logged_in)
  else:
    return redirect(url_for('dashboard'))

#Search by time
@app.route("/search/time", methods=['GET', 'POST'])
def searchbytime():
  logged_in = False
  logged_in_user = None
  is_admin = False

  if session.get('user'):
    logged_in = True
    logged_in_user = User.query.get(session['user'])

  if request.method == "POST":

    start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
    end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
    shows = Show.query.all()
    shows_list = []
    datetime_format = '%H:%M'

    for show in shows:
        datetime_start = datetime.strptime(show.show_starting_time, '%H:%M').time()

        datetime_end = datetime.strptime(show.show_starting_time, '%H:%M').time()

        show_dict = {
            "show_id": show.show_id,
            "show_name": show.show_name,
            "show_rating": show.show_rating,
            "show_price": show.show_price,
            "show_starting_time": datetime_start,
            "show_ending_time": datetime_end,
            "show_tags": show.show_tags,
            "show_img": show.show_img,
            "show_venue": show.show_venue
        }
        shows_list.append(show_dict)

    filtered_shows = []

    for show in shows_list:
      if show["show_starting_time"] >= start_time or show["show_ending_time"] <= end_time:
        filtered_shows.append(show)

    app.logger.info(filtered_shows)
    return render_template('search-by-time.html', shows=filtered_shows, logged_in=logged_in)

  else:
    return redirect(url_for('dashboard'))

# Starting the site
if __name__ == "__main__":
  # port = random.randint(2000, 9000)
#   port = 8210
  # host = '0.0.0.0'
  # app.run(host=host, port=port, debug=True)
    app.run(debug=True)


