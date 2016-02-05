"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

import datetime

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/signup')
def signup():
    """Signup for new users."""

    return render_template("signup.html")

@app.route('/signup-process', methods=['POST',])
def process_signup():
    """Handle form submission for signup process.
    """
    # Logic for chekcing if user exists could be handled 
    # with javascript/AJAX in signup.

    requested_email = request.form.get('email').strip()
    requested_password = request.form.get('password')

    # get a user with that name, if none vs if exists
    existing_user= User.query.filter(User.email == requested_email).first()

    if (existing_user == None) and requested_email:
        # Add the user
        user = User(email=requested_email,
                    password=requested_password)
        db.session.add(user)
        db.session.commit()
        
        flash("User with email %s created. Please log in." % user.email)
    else:
        # return to homepage with scolding
        flash("""Already existing user, or invalid email entry. 
            Please log in, or retry signup.""")

    # question for help: re-direct or load homepage template
    return redirect('/')

@app.route('/login')
def login():
    """Page to enter credentials."""

    return render_template("login.html")

@app.route('/login-process', methods=['POST',])
def process_login():
    """Handle form submission for login process."""

    attempted_email = request.form.get('email').strip()
    attempted_password = request.form.get('password')

    # get a user with that name, if none vs if exists
    existing_user = User.query.filter(User.email == attempted_email).first()

    if (existing_user == None) or not attempted_email:
        # scold and return home, because user isnt there or they used a blank user
        flash("Nonexistent user. Please retry log in.")
        return redirect('/login')

    elif attempted_password == existing_user.password:
        # password is correct 
        session['logged_in_user_id'] = existing_user.user_id
        flash("Successful log in!")
        return redirect('/')

    else:
        # We think this only handles the case of valid user with invalid password
        flash("Invalid password")

        return redirect('/login')


@app.route('/logout-process')
def process_logout():
    """Handle form submission for logout process."""

    # delete session inofrmation
    # We provide a default so that the behavior for pop is NOT to 
    # raise and error if no user is logged in
    session.pop('logged_in_user_id', None)

    # flash message: logout successs
    flash("Successful log out. Goodbye!")
    return redirect('/')


@app.route('/users/<int:user_id>')
def user_lookup(user_id):
    """Display individual user information."""

    user = User.query.get(user_id)
    zipcode = user.zipcode
    age = user.age

    ratings = user.ratings

    return render_template('user.html', zipcode=zipcode, age=age, ratings=ratings)

@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<int:movie_id>')
def movie_lookup(movie_id):
    """Display individual movie information."""

    movie = Movie.query.get(movie_id)

    title = movie.title
    released_at = datetime.datetime.strftime(movie.released_at, "%d-%b-%Y")
    imdb_url = movie.imdb_url

    # binned_scores = Movie.query('score', db.func.count('score')).filter(Movie.movie_id==movie_id).group_by('score').all()
    binned_ratings = db.session.query(Rating.score, db.func.count(Rating.score)).filter(Rating.movie_id==movie_id).group_by('score').all()

    score_count = {int(r): int(c) for r,c in binned_ratings}

    # not all scores may have a rating, so loop through avalible 1-5 ratings adding zero if needed
    rating_bins = range(1,6)
    rating_counts = []
    for rating in rating_bins:
        rating_counts.append(score_count.get(rating, 0))

    # Make percentages
    rating_total_count = sum(rating_counts)
    rating_percent = [int(r*100/float(rating_total_count)) for r in rating_counts]

    # Create tuples for easy use in jinja
    ratings = zip(rating_bins, rating_percent)

    return render_template("movie.html",
                            title=title,
                            released_at=released_at,
                            imdb_url=imdb_url,
                            ratings=ratings,
                            rating_total_count=rating_total_count
                            )

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
