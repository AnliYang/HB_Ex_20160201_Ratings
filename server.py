"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

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

@app.route('/signup-process')
def process_signup():
    """Handle form submission for signup process.
    """
    # Logic for chekcing if user exists could be handled 
    # with javascript/AJAX in signup.

    # flash message: signup success (possibly: or already existing user)

    # question for help: re-direct or load homepage template
    return render_template("homepage.html")

@app.route('/login')
def login():
    """Page to enter credentials."""

    return render_template("login.html")

@app.route('/login-process')
def process_login():
    """Handle form submission for login process."""

    # add user info to session
    # flash message: login success (or other)
    return render_template("homepage.html")

@app.route('/logout-process')
def process_logout():
    """Handle form submission for logout process."""

    # delete session inofrmation
    # flash message: logout successs
    return render_template("homepage.html")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
