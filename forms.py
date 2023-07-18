from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired



class UpdateMovie(FlaskForm):
    new_rating = StringField("Your Rating Out of 10 e.g 5.5")
    new_review = StringField("Your Review")
    submit = SubmitField("Done")


class SpecifyMovie(FlaskForm):
    new_movie = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")    