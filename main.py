from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
import requests
from forms import UpdateMovie, SpecifyMovie
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
Bootstrap5(app)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-list.db'
db = SQLAlchemy(app)


# API URL
url = "https://api.themoviedb.org/3/account/20137302"



# Create a Movie model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __init__(self, title, year, description, rating, ranking, review, img_url):
        self.title = title
        self.year = year
        self.description = description
        self.rating = rating
        self.ranking = ranking
        self.review = review
        self.img_url = img_url



@app.route("/")
def home():
    # Retrieve all movies from database, ordered by rating in descending order
    movies = Movie.query.order_by(Movie.rating.asc()).all()
    # Render the home template passing in movies
    return render_template("index.html", movies=movies)



@app.route("/update/<int:movie_id>", methods=["GET", "POST"])
def update_movie(movie_id):
    if request.method == "POST":
        # Find movie to update
        movie_to_update = Movie.query.filter_by(id=movie_id).first()
        new_rating = request.form.get("new_rating")
        new_review = request.form.get("new_review")
        if new_rating:
            # Update rating if user new_rating field in form is not blank
            movie_to_update.rating = new_rating
            db.session.commit()
        if new_review:
            # Update review if user new_review field in form is not blank
            movie_to_update.review = new_review
            db.session.commit()
        return redirect(url_for('home'))

    # If it's a get request, render update_form
    update_form = UpdateMovie()
    return render_template('edit.html', update_form=update_form, movie_id=movie_id)



@app.route("/specify", methods=["GET", "POST"])
def specify_movie():
    # Render the specify_movie form
    specify_movie_form = SpecifyMovie()
    return render_template('specify_movie.html', specify_movie_form=specify_movie_form)



@app.route("/select", methods=["GET", "POST"])
def select_movie():
    # Handle movie selection from API
    specify_movie_form = SpecifyMovie()
    if request.method == "POST":
        # Get API key from environment variables
        api_key = os.getenv("MY_API_KEY")
        new_movie = specify_movie_form.new_movie.data
        # Set query parameters
        params = {
            "api_key": api_key,
            "query": new_movie,
        }

        # API endpoint
        url = "https://api.themoviedb.org/3/search/movie"

        # Make a request to the API
        response = requests.get(url, params=params)
        movie_data = response.json()
        movie_list = movie_data["results"]
        
        # Render select_movie.html passing in all movies which come up from search
        return render_template('select_movie.html', movie_list=movie_list)



@app.route("/add/<int:movie_id>", methods=["GET", "POST"])
def add_movie(movie_id):
    # Fetch movie data from the API
    api_key = os.getenv("MY_API_KEY")
    params = {"api_key": api_key}
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    response = requests.get(url, params=params)
    movie_data = response.json()
    title = movie_data['title']
    # Base URL for the image server provided by the API
    base_image_url = "https://image.tmdb.org/t/p/w500"

    # Extract movie data an create new entry in database with that data
    poster_path = movie_data['poster_path']
    img_url = base_image_url + poster_path
    year = int(movie_data['release_date'][:4])  
    description = movie_data['overview']
    new_movie = Movie(title=title, year=year, description=description, rating=0, ranking=0, review='', img_url=img_url)
    # Add new_movie to database session
    db.session.add(new_movie)
    # Commit the changes to the database
    db.session.commit()

    return redirect(url_for("update_movie", movie_id=new_movie.id))


@app.route("/delete/<int:movie_id>", methods=["GET", "POST"])
def delete_movie(movie_id):
    # Find movie to delete
    movie_to_delete = Movie.query.get(movie_id)
    # Delete movie from the database if it exists
    if movie_to_delete:
        db.session.delete(movie_to_delete)
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)