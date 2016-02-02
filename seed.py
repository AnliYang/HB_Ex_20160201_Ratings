"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
import datetime

from model import User, Movie
from model import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    Movie.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.item"):
        row = row.rstrip()
        tokens = row.split("|")

        movie_id = int(tokens[0])
        imdb_url = tokens[4]

        title_raw = tokens[1].rstrip()

        if title_raw[-6] == "(":
            title = title_raw[:-6].rstrip()
        elif max(title_raw.find("(1"), title_raw.find("(2")) > -1:
            index = max(title_raw.find("(1"), title_raw.find("(2"))
            title = title_raw[:index].rstrip()
            # stupid freaking dinosaurs, die already
        else:
            title = title_raw
        
        released_at_raw = tokens[2]
        if released_at_raw:
            released_at = datetime.datetime.strptime(released_at_raw, "%d-%b-%Y")
        else:
            released_at = None

        movie = Movie(movie_id=movie_id,
                      imdb_url=imdb_url,
                      title=title,
                      released_at=released_at)

        db.session.add(movie)

    db.session.commit()

    # CODE REVIEW QUESTION: why aren't we closing the file?


def load_ratings():
    """Load ratings from u.data into database."""


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
