from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, FileField
from wtforms.validators import InputRequired

class newtitleform(FlaskForm):
    title = StringField('title', validators=[InputRequired()])
    authorF= StringField('authorF', validators=[InputRequired()])
    authorL= StringField('authorL', validators=[InputRequired()])
    subtitle = StringField('subtitle', validators=[InputRequired()])
    description = StringField('description', validators=[InputRequired()])

class registerform(FlaskForm):
    fname = StringField('fname', validators=[InputRequired()])
    lname= StringField('lname', validators=[InputRequired()])
    role = SelectField('role', choices=[('Gmanager','fmanager','mmanager','mofficer','editor_in_chief','accountant','pubassistant')])
    email = StringField('email', validators=[InputRequired()])